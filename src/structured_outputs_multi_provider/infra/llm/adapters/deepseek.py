import json
from datetime import datetime, timezone
from typing import List

import httpx
from httpx import AsyncClient
from pydantic import BaseModel

from structured_outputs_multi_provider.config.env import settings
from structured_outputs_multi_provider.decorators.http_client import http_client
from structured_outputs_multi_provider.infra.llm.interfaces.llm_adapter import (
    ILLMAdapter,
)
from structured_outputs_multi_provider.schemas.llm.llm_adapter_result import (
    LLMAdapterResult,
)
from structured_outputs_multi_provider.utils.s_to_ms import s_to_ms


class DeepseekResponseUsage(BaseModel):
    total_tokens: int
    prompt_cache_hit_tokens: int
    prompt_cache_miss_tokens: int
    completion_tokens: int


class DeepseekResponseMessage(BaseModel):
    content: str


class DeepseekResponseChoice(BaseModel):
    message: DeepseekResponseMessage


class DeepseekResponse(BaseModel):
    usage: DeepseekResponseUsage
    choices: List[DeepseekResponseChoice]


class DeepseekAdapter(ILLMAdapter):
    @http_client()
    async def execute(
        self, client: AsyncClient, user_prompt: str, system_prompt: str
    ) -> LLMAdapterResult | str:
        print("DeepseekAdapter execute")

        try:
            started_at = datetime.now(timezone.utc).timestamp()
            response = await client.post(
                f"{settings.deepseek_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.deepseek_api_key}"},
                json={
                    "model": settings.deepseek_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                },
            )
            ended_at = datetime.now(timezone.utc).timestamp()

            deepseek_response = DeepseekResponse.model_validate(
                response.json(), strict=False
            )
            text = deepseek_response.choices[0].message.content
            if not text:
                raise ValueError(
                    "Gemini returned no text in choices[0].message.content"
                )

            result = json.loads(text)
            return LLMAdapterResult(
                feeling=result["feeling"],
                topics=result["topics"],
                summary=result["summary"],
                tokens=deepseek_response.usage.total_tokens,
                cost=self.__calculate_cost(deepseek_response.usage),
                latency=s_to_ms(ended_at - started_at),
            )
        except AttributeError as e:
            return str(e)
        except httpx.TimeoutException:
            return "Timeout during fetching OllamaResponse"
        except httpx.HTTPError:
            return "Error fetching response"
        except Exception:
            return "Error fetching response"

    def __calculate_cost(self, usage: DeepseekResponseUsage) -> float:
        input_cache_hit_cost = (
            usage.prompt_cache_hit_tokens
            / 1_000_000
            * settings.deepseek_input_cache_hit_cost
        )
        input_cache_miss_cost = (
            usage.prompt_cache_miss_tokens
            / 1_000_000
            * settings.deepseek_input_cache_miss_cost
        )
        output_cost = (
            usage.completion_tokens / 1_000_000 * settings.deepseek_output_cost
        )
        return input_cache_hit_cost + input_cache_miss_cost + output_cost

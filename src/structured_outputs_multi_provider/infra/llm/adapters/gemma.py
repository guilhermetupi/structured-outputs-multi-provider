import json

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
from structured_outputs_multi_provider.utils.ns_to_ms import ns_to_ms


class OllamaResponse(BaseModel):
    response: str
    total_duration: int
    prompt_eval_count: int
    eval_count: int


class GemmaAdapter(ILLMAdapter):
    @http_client(timeout=120.0)
    async def execute(
        self, client: AsyncClient, user_prompt: str, system_prompt: str
    ) -> LLMAdapterResult | str:
        print("GemmaAdapter execute")

        try:
            response = await client.post(
                f"{settings.ollama_url}/generate",
                json={
                    "prompt": user_prompt,
                    "system": system_prompt,
                    "model": settings.ollama_model,
                    "stream": False,
                    "format": "json",
                },
            )
            ollama_response = OllamaResponse.model_validate(
                response.json(), strict=False
            )
            result = json.loads(ollama_response.response)
            return LLMAdapterResult(
                feeling=result["feeling"],
                topics=result["topics"],
                summary=result["summary"],
                tokens=ollama_response.prompt_eval_count + ollama_response.eval_count,
                cost=0.0,
                latency=ns_to_ms(ollama_response.total_duration),
            )
        except AttributeError as e:
            return str(e)
        except httpx.TimeoutException:
            return "Timeout during fetching OllamaResponse"
        except httpx.HTTPError:
            return "Error fetching response"
        except Exception:
            return "Error fetching response"

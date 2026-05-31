import json
from datetime import datetime, timezone
from typing import List, Optional

import httpx
from httpx import AsyncClient
from pydantic import BaseModel, ConfigDict, Field

from structured_outputs_multi_provider.config.env import settings
from structured_outputs_multi_provider.decorators.http_client import http_client
from structured_outputs_multi_provider.infra.llm.interfaces.llm_adapter import (
    ILLMAdapter,
)
from structured_outputs_multi_provider.schemas.llm.llm_adapter_result import (
    LLMAdapterResult,
)
from structured_outputs_multi_provider.utils.s_to_ms import s_to_ms


class GeminiResponseUsage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_token_count: int = Field(default=0, alias="totalTokenCount")
    cached_content_token_count: int = Field(default=0, alias="cachedContentTokenCount")
    candidates_token_count: int = Field(default=0, alias="candidatesTokenCount")
    prompt_token_count: int = Field(default=0, alias="promptTokenCount")
    thoughts_token_count: int = Field(default=0, alias="thoughtsTokenCount")


class GeminiResponsePart(BaseModel):
    text: Optional[str] = None


class GeminiResponseContent(BaseModel):
    parts: List[GeminiResponsePart]


class GeminiResponseCandidate(BaseModel):
    finish_reason: Optional[str] = Field(default=None, alias="finishReason")
    content: GeminiResponseContent


class GeminiResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    usage_metadata: GeminiResponseUsage = Field(alias="usageMetadata")
    candidates: List[GeminiResponseCandidate]


class GeminiAdapter(ILLMAdapter):
    @http_client()
    async def execute(self, client: AsyncClient, user_prompt: str, system_prompt: str):
        print("GeminiAdapter execute")

        try:
            started_at = datetime.now(timezone.utc).timestamp()
            response = await client.post(
                f"{settings.gemini_url}/{settings.gemini_model}:generateContent",
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": settings.gemini_api_key,
                },
                json={
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": user_prompt}],
                        }
                    ],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "responseSchema": {
                            "type": "object",
                            "properties": {
                                "feeling": {
                                    "type": "string",
                                    "enum": ["positive", "negative", "neutral"],
                                    "description": "The feeling about the user prompt.",
                                },
                                "topics": {
                                    "type": "array",
                                    "description": "Topics about the user prompt.",
                                    "items": {"type": "string"},
                                },
                                "summary": {
                                    "type": "string",
                                    "description": "User prompt summary.",
                                },
                            },
                            "required": ["feeling", "topics", "summary"],
                        },
                    },
                },
            )
            ended_at = datetime.now(timezone.utc).timestamp()

            gemini_response = GeminiResponse.model_validate(
                response.json(), strict=False
            )
            text = gemini_response.candidates[0].content.parts[0].text
            if not text:
                raise ValueError(
                    "Gemini returned no text in candidates[0].content.parts[0].text"
                )

            result = json.loads(text)

            return LLMAdapterResult(
                feeling=result["feeling"],
                topics=result["topics"],
                summary=result["summary"],
                tokens=gemini_response.usage_metadata.total_token_count,
                cost=self.__calculate_cost(gemini_response.usage_metadata),
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

    def __calculate_cost(self, usage: GeminiResponseUsage) -> float:
        input_cache_hit_cost = (
            usage.cached_content_token_count
            / 1_000_000
            * settings.gemini_input_cache_hit_cost
        )
        input_cache_miss_cost = (
            (usage.prompt_token_count - usage.cached_content_token_count)
            / 1_000_000
            * settings.gemini_input_cache_miss_cost
        )
        output_cost = (
            usage.candidates_token_count / 1_000_000 * settings.gemini_output_cost
        )
        return input_cache_hit_cost + input_cache_miss_cost + output_cost

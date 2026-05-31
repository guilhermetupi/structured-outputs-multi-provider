from typing import List

from pydantic import BaseModel

from structured_outputs_multi_provider.infra.llm.llm_provider import Provider
from structured_outputs_multi_provider.schemas.llm.llm_adapter_result import LLM_FEELING


class LLMResult(BaseModel):
    provider: Provider
    feeling: LLM_FEELING | None = None
    topics: List[str] | None = None
    summary: str | None = None
    latency: float | None = None
    tokens: int | None = None
    cost: float | None = None
    error: str | None = None

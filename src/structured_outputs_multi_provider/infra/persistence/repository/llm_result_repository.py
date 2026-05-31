import json
from typing import List

from structured_outputs_multi_provider.infra.persistence.interfaces.llm_result_repository import (
    ILLMResultRepository,
)
from structured_outputs_multi_provider.infra.persistence.interfaces.persistence_provider import (
    IPersistenceProvider,
)
from structured_outputs_multi_provider.schemas.persistence.llm_result import LLMResult


class LLMResultRepository(ILLMResultRepository):
    def __init__(self, persistence_provider: IPersistenceProvider):
        self.persistence_provider = persistence_provider

    def save_many(self, data: List[LLMResult]) -> None:
        self.persistence_provider.save_many(
            [
                "provider",
                "feeling",
                "topics",
                "summary",
                "latency",
                "tokens",
                "cost",
                "error",
            ],
            [
                {
                    **item.model_dump(),
                    "topics": json.dumps(item.topics, ensure_ascii=False),
                }
                for item in data
            ],
        )

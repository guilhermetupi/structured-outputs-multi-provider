from abc import ABC, abstractmethod
from typing import List

from structured_outputs_multi_provider.schemas.persistence.llm_result import LLMResult


class ILLMResultRepository(ABC):
    @abstractmethod
    def save_many(self, data: List[LLMResult]) -> None:
        pass

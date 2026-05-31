from abc import ABC, abstractmethod

from structured_outputs_multi_provider.schemas.llm.llm_adapter_result import (
    LLMAdapterResult,
)


class ILLMAdapter(ABC):
    @abstractmethod
    async def execute(
        self, user_prompt: str, system_prompt: str
    ) -> LLMAdapterResult | str:
        pass

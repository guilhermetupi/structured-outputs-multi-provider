from abc import ABC, abstractmethod
from typing import Literal

from structured_outputs_multi_provider.schemas.llm.llm_provider_result import (
    LLMProviderResult,
)

Provider = Literal["DEEPSEEK", "GEMINI", "GEMMA"]


class ILLMProvider(ABC):
    @abstractmethod
    async def execute(self, prompt: str, provider: Provider) -> LLMProviderResult:
        pass

from typing import List

from structured_outputs_multi_provider.infra.llm.interfaces.llm_provider import (
    ILLMProvider,
)
from structured_outputs_multi_provider.infra.persistence.interfaces.llm_result_repository import (
    ILLMResultRepository,
)
from structured_outputs_multi_provider.schemas.persistence.llm_result import LLMResult
from structured_outputs_multi_provider.infra.llm.interfaces.llm_provider import Provider

PROVIDERS: List[Provider] = ["GEMMA", "DEEPSEEK", "GEMINI"]


class BenchService:
    def __init__(
        self, llm_provider: ILLMProvider, llm_result_repository: ILLMResultRepository
    ):
        self.llm_provider = llm_provider
        self.llm_result_repository = llm_result_repository

    async def execute(self, prompt: str):
        all_results: List[LLMResult] = []

        for provider in PROVIDERS:
            result = await self.llm_provider.execute(prompt, provider)
            for res in result:
                if type(res) is str:
                    all_results.append(LLMResult(provider=provider, error=res))
                else:
                    all_results.append(LLMResult(provider=provider, **res.model_dump()))

        self.llm_result_repository.save_many(all_results)
        return None

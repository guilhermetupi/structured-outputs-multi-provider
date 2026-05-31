from typing import List

from pydantic import BaseModel

from structured_outputs_multi_provider.infra.llm.interfaces.llm_provider import (
    ILLMProvider,
    Provider,
)
from structured_outputs_multi_provider.infra.persistence.interfaces.llm_result_repository import (
    ILLMResultRepository,
)
from structured_outputs_multi_provider.schemas.persistence.llm_result import LLMResult

PROVIDERS: List[Provider] = ["GEMMA", "DEEPSEEK", "GEMINI"]


class ProviderResult(BaseModel):
    done: bool = False
    results: List[LLMResult] = []


class ChainService:
    def __init__(
        self, llm_provider: ILLMProvider, llm_result_repository: ILLMResultRepository
    ):
        self.llm_provider = llm_provider
        self.llm_result_repository = llm_result_repository

    async def execute(self, prompt: str):
        all_results: List[LLMResult] = []

        for provider in PROVIDERS:
            result = await self.__execute_provider(prompt, provider)
            [all_results.append(res) for res in result.results]
            if result.done:
                self.llm_result_repository.save_many(all_results)
                return None

        return None

    async def __execute_provider(
        self, prompt: str, provider: Provider
    ) -> ProviderResult:
        provider_result = ProviderResult()

        llm_results = await self.llm_provider.execute(prompt, provider)
        if llm_results:
            for res in llm_results:
                if type(res) is str:
                    provider_result.results.append(
                        LLMResult(provider=provider, error=res)
                    )
                else:
                    provider_result.results.append(
                        LLMResult(provider=provider, **res.model_dump())
                    )
                    provider_result.done = True

        return provider_result

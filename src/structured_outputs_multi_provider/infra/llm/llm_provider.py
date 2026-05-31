from structured_outputs_multi_provider.infra.llm.interfaces.llm_adapter import (
    ILLMAdapter,
)
from structured_outputs_multi_provider.infra.llm.interfaces.llm_provider import (
    ILLMProvider,
    Provider,
)
from structured_outputs_multi_provider.schemas.llm.llm_adapter_result import (
    LLMAdapterResult,
)
from structured_outputs_multi_provider.schemas.llm.llm_provider_result import (
    LLMProviderResult,
)

SYSTEM_PROMPT = """"
    Return the following JSON schema
    {{
       feeling: 'positive' | 'negative' | 'neutral'; // The feeling about the user prompt, example: Do not work -> negative
       topics: string[]; // Topics about the user prompt, example: The app keeps crashing -> ['app', 'crashing', 'support']
       summary: string; // User prompt summary, example: I have a MacBook -> The text informs the user's computer
    }}
"""


class LLMProvider(ILLMProvider):
    def __init__(
        self,
        deepseek_adapter: ILLMAdapter,
        gemini_adapter: ILLMAdapter,
        gemma_adapter: ILLMAdapter,
    ):
        self.deepseek_adapter = deepseek_adapter
        self.gemini_adapter = gemini_adapter
        self.gemma_adapter = gemma_adapter

    async def execute(self, prompt: str, provider: Provider) -> LLMProviderResult:
        attempts: LLMProviderResult = []
        attempts_count = 0

        while attempts_count < 3:
            attempts_count += 1

            response = await self.__get_provider_implementation(provider).execute(
                prompt, SYSTEM_PROMPT
            )
            attempts.append(response)

            if type(response) is LLMAdapterResult:
                break

        return attempts

    def __get_provider_implementation(self, provider: Provider) -> ILLMAdapter:
        match provider:
            case "GEMMA":
                return self.gemma_adapter
            case "DEEPSEEK":
                return self.deepseek_adapter
            case "GEMINI":
                return self.gemini_adapter
            case _:
                raise Exception("Unknown provider")

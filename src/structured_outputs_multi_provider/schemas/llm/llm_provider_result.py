from typing import List

from structured_outputs_multi_provider.schemas.llm.llm_adapter_result import (
    LLMAdapterResult,
)

LLMProviderResult = List[LLMAdapterResult | str]

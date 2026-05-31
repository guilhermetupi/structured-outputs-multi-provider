from structured_outputs_multi_provider.infra.llm.adapters.deepseek import (
    DeepseekAdapter,
)
from structured_outputs_multi_provider.infra.llm.adapters.gemini import GeminiAdapter
from structured_outputs_multi_provider.infra.llm.adapters.gemma import GemmaAdapter
from structured_outputs_multi_provider.infra.llm.llm_provider import LLMProvider

deepseek_adapter = DeepseekAdapter()
gemini_adapter = GeminiAdapter()
gemma_adapter = GemmaAdapter()

llm_provider = LLMProvider(
    deepseek_adapter=deepseek_adapter,
    gemini_adapter=gemini_adapter,
    gemma_adapter=gemma_adapter,
)

from structured_outputs_multi_provider.infra.persistence.persistence_provider import (
    PersistenceProvider,
)
from structured_outputs_multi_provider.infra.persistence.repository.llm_result_repository import (
    LLMResultRepository,
)

persistence_provider = PersistenceProvider()

llm_result_repository = LLMResultRepository(persistence_provider=persistence_provider)

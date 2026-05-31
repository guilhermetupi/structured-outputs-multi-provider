from structured_outputs_multi_provider.dependencies.infra.llm import llm_provider
from structured_outputs_multi_provider.dependencies.infra.persistence import (
    llm_result_repository,
)
from structured_outputs_multi_provider.services.chain import ChainService

chain_service = ChainService(
    llm_provider=llm_provider, llm_result_repository=llm_result_repository
)

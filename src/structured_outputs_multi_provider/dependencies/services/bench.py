from structured_outputs_multi_provider.dependencies.infra.llm import llm_provider
from structured_outputs_multi_provider.dependencies.infra.persistence import (
    llm_result_repository,
)
from structured_outputs_multi_provider.services.bench import BenchService

bench_service = BenchService(
    llm_provider=llm_provider, llm_result_repository=llm_result_repository
)

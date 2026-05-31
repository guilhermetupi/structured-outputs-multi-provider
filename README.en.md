# Structured Outputs Multi Provider

CLI that performs sentiment analysis via **structured outputs** comparing multiple LLM providers — Gemma (Ollama), DeepSeek, and Gemini — with two different strategies: parallel benchmark and chain fallback.

## Features

- **Bench Mode** — Runs analysis on **all** providers and persists results as CSV, allowing comparison of latency, tokens, and cost across them.
- **Chain Mode** — Runs providers sequentially; the first one to respond successfully ends the flow.
- **Structured Output** — All providers respond following the same JSON schema with Pydantic validation:
  - `feeling`: `positive`, `negative`, or `neutral`
  - `topics`: list of topics mentioned in the prompt
  - `summary`: summary of the user prompt
- **Persistence** — Results saved to `data/result_<timestamp>.csv`.

## Stack

| Layer | Technology |
|--------|-----------|
| CLI | `argparse`, `asyncio` |
| HTTP Client | `httpx` (async) |
| Configuration | `pydantic-settings` with `.env` |
| Validation | `pydantic` |
| Runtime | Python ≥ 3.13, `uv` |

## Project Structure

```
src/structured_outputs_multi_provider/
├── main.py                     # CLI entry point
├── config/
│   └── env.py                  # Settings via .env (pydantic-settings)
├── services/
│   ├── bench.py                # Service: parallel benchmark (all providers)
│   └── chain.py                # Service: chain fallback (first to respond)
├── infra/
│   ├── llm/
│   │   ├── interfaces/         # ILLMAdapter, ILLMProvider (ABCs)
│   │   ├── adapters/           # GemmaAdapter, DeepseekAdapter, GeminiAdapter
│   │   └── llm_provider.py     # Orchestrator: retry 3x, provider routing
│   └── persistence/
│       ├── interfaces/         # IPersistenceProvider, ILLMResultRepository (ABCs)
│       ├── persistence_provider.py  # CSV implementation
│       └── repository/         # LLMResultRepository
├── schemas/
│   ├── llm/
│   │   ├── llm_adapter_result.py    # Adapter response schema
│   │   └── llm_provider_result.py   # Alias for result list
│   └── persistence/
│       └── llm_result.py            # Persisted record schema
├── dependencies/               # Manual wiring (dependency injection)
│   ├── infra/                  # Instantiates adapters, providers, repositories
│   └── services/               # Instantiates bench_service, chain_service
├── decorators/
│   └── http_client.py          # Decorator that injects httpx.AsyncClient
└── utils/
    ├── ns_to_ms.py             # Nanoseconds → milliseconds conversion
    └── s_to_ms.py              # Seconds → milliseconds conversion
```

## Prerequisites

- **Python ≥ 3.13**
- **uv** (package manager)
- **Ollama** installed with the `gemma3:1b` model (or configure the desired model in `.env`)
- **DeepSeek API key**
- **Google Gemini API key**

## Configuration

1. Clone the repository and enter the directory:

```bash
cd structured-outputs-multi-provider
```

2. Create a `.env` file at the project root:

```env
# Ollama (Gemma)
OLLAMA_URL=http://localhost:11434/api
OLLAMA_MODEL=gemma3:1b

# Google Gemini
GEMINI_URL=https://generativelanguage.googleapis.com/v1beta/models
GEMINI_MODEL=gemini-2.5-flash
GEMINI_API_KEY=your-api-key-here
GEMINI_INPUT_CACHE_HIT_COST=0.0
GEMINI_INPUT_CACHE_MISS_COST=0.15
GEMINI_OUTPUT_COST=0.60

# DeepSeek
DEEPSEEK_URL=https://api.deepseek.ai
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_INPUT_CACHE_HIT_COST=0.14
DEEPSEEK_INPUT_CACHE_MISS_COST=0.35
DEEPSEEK_OUTPUT_COST=1.10
```

> The cost values above are per 1M tokens (USD) and may be outdated. Check each provider's official documentation.

## Usage

### Bench Mode (compares all providers)

```bash
uv run structured-outputs-multi-provider --bench --prompt "Your prompt here"
```

Output:
```
Welcome to Structured Outputs Multi Provider
DeepseekAdapter execute
GeminiAdapter execute
GemmaAdapter execute
```

Results saved to `data/result_<timestamp>.csv`:

| provider | feeling | topics    | summary       | latency | tokens | cost | error |
|----------|---------|-----------|---------------|---------|--------|------|-------|
| DEEPSEEK | positive | Prompt | Your prompt... | 1234.5 | 150 | 0.000165 | |
| GEMINI | positive | Prompt| Your prompt... | 890.2 | 95 | 0.000057 | |
| GEMMA | positive | Prompt| Your prompt... | 1500.1 | 220 | 0.0 | |

### Chain Mode (first to respond)

```bash
uv run structured-outputs-multi-provider --prompt "Your prompt here"
```

Tries Gemma first, then DeepSeek, then Gemini. Stops at the first success.

### Running the script directly

```bash
uv run src/structured_outputs_multi_provider/main.py --bench --prompt "Your text here"
```

## How it works

### Execution flow

```
CLI (main.py)
  └─ bench_service / chain_service
       └─ LLMProvider.execute(prompt, provider)
            ├─ retry (up to 3 attempts)
            ├─ routes to the correct adapter (GEMMA | DEEPSEEK | GEMINI)
            └─ adapter.execute(prompt, system_prompt)  ← @http_client injects AsyncClient
                 └─ POST to the provider's API
                      └─ validates response with LLMAdapterResult (Pydantic)
                           └─ returns result with latency, tokens, cost
```

### Structured Output

The `system_prompt` instructs each LLM to return JSON with the schema:

```json
{
  "feeling": "positive" | "negative" | "neutral",
  "topics": ["topic1", "topic2"],
  "summary": "Summary of the user prompt"
}
```

### Dependency Injection

Wiring is manual, done in `dependencies/`. Each module instantiates objects and injects their dependencies:

```python
# dependencies/infra/llm.py
deepseek_adapter = DeepseekAdapter()
gemma_adapter = GemmaAdapter()
llm_provider = LLMProvider(deepseek=deepseek_adapter, gemma=gemma_adapter, ...)
```

### `@http_client` Decorator

Injects an `httpx.AsyncClient` managed by a context manager into the first argument of the decorated method, eliminating `async with` boilerplate:

```python
@http_client(timeout=120.0)
async def execute(self, client: AsyncClient, user_prompt: str, system_prompt: str):
    response = await client.post(url, json={...})
```

## License

MIT

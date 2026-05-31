# Structured Outputs Multi Provider

CLI que executa análise de sentimento via **structured outputs** comparando múltiplos provedores de LLM — Gemma (Ollama), DeepSeek e Gemini — com duas estratégias diferentes: benchmark paralelo e fallback em cadeia.

## Funcionalidades

- **Modo Bench** — Executa análise em **todos** os provedores e persiste os resultados como CSV, permitindo comparar latência, tokens e custo entre eles.
- **Modo Chain** — Executa os provedores em sequência; o primeiro que responder com sucesso encerra o fluxo.
- **Structured Output** — Todos os provedores respondem seguindo o mesmo schema JSON com validação Pydantic:
  - `feeling`: `positive`, `negative` ou `neutral`
  - `topics`: lista de tópicos mencionados no prompt
  - `summary`: resumo do prompt do usuário
- **Persistência** — Resultados salvos em `data/result_<timestamp>.csv`.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| CLI | `argparse`, `asyncio` |
| HTTP Client | `httpx` (async) |
| Configuração | `pydantic-settings` com `.env` |
| Validação | `pydantic` |
| Runtime | Python ≥ 3.13, `uv` |

## Estrutura do Projeto

```
src/structured_outputs_multi_provider/
├── main.py                     # Ponto de entrada da CLI
├── config/
│   └── env.py                  # Settings via .env (pydantic-settings)
├── services/
│   ├── bench.py                # Serviço: benchmark paralelo (todos os providers)
│   └── chain.py                # Serviço: fallback em cadeia (primeiro que responder)
├── infra/
│   ├── llm/
│   │   ├── interfaces/         # ILLMAdapter, ILLMProvider (ABCs)
│   │   ├── adapters/           # GemmaAdapter, DeepseekAdapter, GeminiAdapter
│   │   └── llm_provider.py     # Orquestrador: retry 3x, roteamento por provider
│   └── persistence/
│       ├── interfaces/         # IPersistenceProvider, ILLMResultRepository (ABCs)
│       ├── persistence_provider.py  # Implementação CSV
│       └── repository/         # LLMResultRepository
├── schemas/
│   ├── llm/
│   │   ├── llm_adapter_result.py    # Schema da resposta do adapter
│   │   └── llm_provider_result.py   # Alias para lista de resultados
│   └── persistence/
│       └── llm_result.py            # Schema do registro persistido
├── dependencies/               # Wiring manual (injeção de dependências)
│   ├── infra/                  # Instancia adapters, providers, repositories
│   └── services/               # Instancia bench_service, chain_service
├── decorators/
│   └── http_client.py          # Decorator que injeta httpx.AsyncClient
└── utils/
    ├── ns_to_ms.py             # Conversão nanossegundos → milissegundos
    └── s_to_ms.py              # Conversão segundos → milissegundos
```

## Pré-requisitos

- **Python ≥ 3.13**
- **uv** (gerenciador de pacotes)
- **Ollama** instalado com o modelo `gemma3:1b` (ou configure o modelo desejado no `.env`)
- **Chave de API** do DeepSeek
- **Chave de API** do Google Gemini

## Configuração

1. Clone o repositório e entre no diretório:

```bash
cd structured-outputs-multi-provider
```

2. Crie um arquivo `.env` na raiz do projeto:

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

> Os valores de custo acima são por 1M tokens (USD) e podem estar desatualizados. Consulte a documentação oficial de cada provedor.

## Uso

### Modo Bench (compara todos os provedores)

```bash
uv run structured-outputs-multi-provider --bench --prompt "Seu prompt aqui"
```

Saída:
```
Welcome to Structured Outputs Multi Provider
DeepseekAdapter execute
GeminiAdapter execute
GemmaAdapter execute
```

Resultados salvos em `data/result_<timestamp>.csv`:

| provider | feeling | topics    | summary       | latency | tokens | cost | error |
|----------|---------|-----------|---------------|---------|--------|------|-------|
| DEEPSEEK | positive | Prompt | Seu prompt... | 1234.5 | 150 | 0.000165 | |
| GEMINI | positive | Prompt| Seu prompt... | 890.2 | 95 | 0.000057 | |
| GEMMA | positive | Prompt| Seu prompt... | 1500.1 | 220 | 0.0 | |

### Modo Chain (primeiro que responder)

```bash
uv run structured-outputs-multi-provider --prompt "Seu prompt aqui"
```

Tenta Gemma primeiro, depois DeepSeek, depois Gemini. Para no primeiro sucesso.

### Executando o script diretamente

```bash
uv run src/structured_outputs_multi_provider/main.py --bench --prompt "Seu texto aqui"
```

## Como funciona

### Fluxo de execução

```
CLI (main.py)
  └─ bench_service / chain_service
       └─ LLMProvider.execute(prompt, provider)
            ├─ retry (até 3 tentativas)
            ├─ roteia para o adapter correto (GEMMA | DEEPSEEK | GEMINI)
            └─ adapter.execute(prompt, system_prompt)  ← @http_client injeta AsyncClient
                 └─ POST para a API do provedor
                      └─ valida resposta com LLMAdapterResult (Pydantic)
                           └─ retorna resultado com latência, tokens, custo
```

### Structured Output

O `system_prompt` instrui cada LLM a retornar JSON com o schema:

```json
{
  "feeling": "positive" | "negative" | "neutral",
  "topics": ["tópico1", "tópico2"],
  "summary": "Resumo do prompt do usuário"
}
```

### Injeção de Dependências

O wiring é manual, feito em `dependencies/`. Cada módulo instancia os objetos e injeta suas dependências:

```python
# dependencies/infra/llm.py
deepseek_adapter = DeepseekAdapter()
gemma_adapter = GemmaAdapter()
llm_provider = LLMProvider(deepseek=deepseek_adapter, gemma=gemma_adapter, ...)
```

### Decorator `@http_client`

Injeta um `httpx.AsyncClient` gerenciado por context manager no primeiro argumento do método decorado, eliminando boilerplate de `async with`:

```python
@http_client(timeout=120.0)
async def execute(self, client: AsyncClient, user_prompt: str, system_prompt: str):
    response = await client.post(url, json={...})
```

## Licença

MIT

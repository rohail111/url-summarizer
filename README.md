# URL Summarizer

Production-ready AI URL summarizer powered by **LangChain** and **Groq**.

Paste a public URL → fetch page text → summarize with a LangChain LCEL pipeline (direct or map-reduce) → structured JSON output.

## Features

- **LangChain LCEL chains** with map-reduce for long pages
- **Structured output** (`title` + bullet points) via Pydantic
- **FastAPI REST API** with health checks and optional API key auth
- **Streamlit UI** and **CLI** for local use
- **SSRF-safe URL validation**, fetch retries, and configurable limits
- **Docker** support for deployment

## Architecture

```mermaid
flowchart LR
    Client --> API[FastAPI / CLI / Streamlit]
    API --> Validate[URL Validation]
    Validate --> Fetch[Fetch + Extract Text]
    Fetch --> Chain{Content length}
    Chain -->|Short| Direct[Direct LangChain Chain]
    Chain -->|Long| MapReduce[Map-Reduce Chain]
    Direct --> LLM[Groq via ChatGroq]
    MapReduce --> LLM
    LLM --> Output[Structured SummaryResult]
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Put your Groq API key in .env as GROQ_API_KEY=...
```

## Run

### REST API

```bash
uvicorn url_summarizer.api.app:app --reload --port 8000
```

```bash
curl -X POST http://localhost:8000/api/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Streamlit UI

```bash
streamlit run app.py
```

### CLI

```bash
python main.py https://example.com
python main.py https://example.com --json
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | _(required)_ | Groq API key |
| `GROQ_MODEL` | `openai/gpt-oss-20b` | Groq model name |
| `FETCH_TIMEOUT_SECONDS` | `15` | HTTP fetch timeout |
| `MAX_CONTENT_CHARS` | `50000` | Max extracted text length |
| `MAP_REDUCE_THRESHOLD` | `6000` | Use map-reduce above this char count |
| `API_KEY` | _(unset)_ | If set, requires `X-API-Key` header |
| `LOG_LEVEL` | `INFO` | Logging level |

## Docker

```bash
export GROQ_API_KEY=gsk_your_key_here
docker compose up --build
```

## Tests

```bash
pytest
```

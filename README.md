# StatVisor

Multi-agent AI analytics POC: **LangGraph** orchestration, **hybrid FAISS + BM25 RAG**, **FastAPI**, **Streamlit**, and a **Microsoft Copilot Studio** OpenAPI entry point. Mock LLM works with no API keys; Azure OpenAI / OpenAI-compatible providers are env-ready.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make ingest
make test
make api    # :8000
make ui     # Streamlit
```

## Docs

Full architecture, tradeoffs, bottlenecks, and resume mapping: **[docs/STATVISOR_GUIDE.md](docs/STATVISOR_GUIDE.md)**

Copilot Studio setup: **[integrations/copilot-studio/SETUP.md](integrations/copilot-studio/SETUP.md)**

## LLM later

Keep `LLM_PROVIDER=mock` until you have a key. Then set `azure` or `openai_compatible` in `.env` (see `.env.example`).

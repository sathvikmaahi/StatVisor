# StatVisor POC Design

**Date:** 2026-09-16  
**Status:** Approved  
**Repo:** https://github.com/sathvikmaahi/StatVisor.git

## Goal

Rebuild StatVisor as a production-oriented personal GitHub POC that honestly demonstrates every resume bullet: LangGraph multi-agent orchestration, Azure OpenAI–ready LLM adapter, FAISS + BM25 hybrid RAG, prompt grounding/tool schemas, LLM summarization for research/infrastructure insights, Streamlit visualizations, and a Microsoft Copilot Studio OpenAPI entry point (contract + setup guide only).

## Decisions

| Decision | Choice |
|---|---|
| Shape | Lean monorepo (Approach 1) |
| LLM | Mock by default; Azure + OpenAI-compatible env wiring for later |
| Copilot Studio | Option A — OpenAPI v2 + SETUP.md, no live tenant |
| Git | Trunk-based: `main` + short-lived feature branches, honest dates |
| Docs | Short README + single learning guide `docs/STATVISOR_GUIDE.md` |

## Architecture

```text
Streamlit UI ──────────────┐
                           ├── FastAPI ── LangGraph
Copilot Studio (OpenAPI) ──┘      │
                                  ├ Router → Retrieval (FAISS + BM25)
                                  ├ Analyst → Summarizer → (optional) Visualizer
                                  ├ LLM adapter (mock | azure | openai_compatible)
                                  └ SQLite audit + on-disk FAISS/chunks
```

## Components

- `backend/app/config.py` — env settings
- `backend/app/llm.py` — chat + embeddings adapter
- `backend/app/retrieval.py` — chunking, FAISS, BM25, fusion
- `backend/app/tools.py` — tool/function schemas
- `backend/app/agents/` — state, nodes, graph
- `backend/app/main.py` — FastAPI routes
- `backend/app/db.py` — SQLite audit
- `frontend/streamlit_app.py` — UI
- `integrations/copilot-studio/` — OpenAPI + SETUP
- `data/sample_docs/` — demo corpus
- `tests/` — retrieval, tools, API
- `docs/STATVISOR_GUIDE.md` — learning document

## Data flow

1. `POST /v1/ask` with question + session_id  
2. Router classifies: research | analysis | summarization | visualization  
3. Hybrid retrieval always runs; citations returned  
4. Analyst and/or summarizer produce grounded answer + insights  
5. Visualizer emits frontend-neutral chart JSON when route needs it  
6. Audit row persisted  

## Error handling

- Mock mode needs no secrets  
- Non-local env requires `STATVISOR_API_KEY`  
- Empty retrieval → insufficient-evidence answer  
- 401 / 422 / safe 500s  

## Testing

- Unit: fusion scoring, tools  
- API: health, ingest, ask (mock LLM)  
- `make test`, `make ingest`, `make run`  

## Git workflow

Trunk-based on `main`. Short-lived branches merged often:

1. `feat/scaffold-core`  
2. `feat/hybrid-rag`  
3. `feat/langgraph-agents`  
4. `feat/fastapi-api`  
5. `feat/streamlit-ui`  
6. `feat/copilot-contract`  
7. `docs/learning-guide`  
8. `test/core-coverage`  

Commits: conventional, lowercase, ≤6 words. No backdated history.

## Out of scope

Real Copilot tenant, multi-tenant auth, K8s, managed vector DB (documented as migration path only).

## Success criteria

- `make ingest && make test` pass with mock LLM  
- Streamlit can ask a question and show answer, citations, trace, chart  
- Copilot OpenAPI + SETUP present  
- Learning guide covers architecture, usage, pros/cons, tradeoffs, bottlenecks, why this design  
- Code pushed to personal GitHub on `main`  

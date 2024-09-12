# StatVisor POC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild a working StatVisor multi-agent analytics POC matching the approved design and resume bullets.

**Architecture:** FastAPI + LangGraph agents + hybrid FAISS/BM25 RAG + Streamlit + Copilot OpenAPI contract; mock LLM default.

**Tech Stack:** Python 3.11+, FastAPI, LangGraph, LangChain-core, OpenAI SDK, FAISS, rank-bm25, Streamlit, Plotly, SQLite, pytest, Docker.

## Global Constraints

- Commits: conventional, lowercase, ≤6 words
- Trunk-based: branch from `main`, merge often, delete branch
- Mock LLM must work with zero API keys
- Rebuild from scratch (replace prior scaffold cleanly)
- Honest git dates only
- Single learning doc at `docs/STATVISOR_GUIDE.md`

## File map

```text
backend/app/{config,llm,retrieval,tools,schemas,db,main}.py
backend/app/agents/{state,nodes,graph}.py
frontend/streamlit_app.py
integrations/copilot-studio/{statvisor-openapi-v2.yaml,SETUP.md}
data/sample_docs/*.txt
scripts/ingest_sample_data.py
tests/{test_retrieval,test_tools,test_api}.py
docs/STATVISOR_GUIDE.md
README.md, .env.example, requirements.txt, Makefile, Dockerfile, docker-compose.yml
```

---

### Task 1: Scaffold core

**Branch:** `feat/scaffold-core`

**Files:**
- Create: `requirements.txt`, `.gitignore`, `.env.example`, `pytest.ini`, `Makefile`, `backend/__init__.py`, `backend/app/__init__.py`, `backend/app/config.py`, `backend/app/schemas.py`

- [ ] Remove obsolete scaffold files that will be replaced (`ARCHITECTURE.md`, bloated README, `PROJECT_MANIFEST.txt`)
- [ ] Write minimal package layout + settings + pydantic schemas
- [ ] Commit: `feat: add project scaffold`
- [ ] Merge to `main`, delete branch

### Task 2: Hybrid RAG

**Branch:** `feat/hybrid-rag`

**Files:**
- Create: `backend/app/llm.py`, `backend/app/retrieval.py`, `data/sample_docs/*.txt`, `scripts/ingest_sample_data.py`, `tests/test_retrieval.py`

- [ ] Write failing retrieval fusion test
- [ ] Implement mock embeddings + hybrid retriever
- [ ] Add sample docs + ingest script
- [ ] Commit: `feat: add hybrid rag`
- [ ] Merge to `main`

### Task 3: LangGraph agents

**Branch:** `feat/langgraph-agents`

**Files:**
- Create: `backend/app/tools.py`, `backend/app/agents/{state,nodes,graph}.py`, `tests/test_tools.py`

- [ ] Implement router/retrieval/analyst/summarizer/visualizer nodes
- [ ] Compile StateGraph with conditional edges
- [ ] Commit: `feat: add langgraph agents`
- [ ] Merge to `main`

### Task 4: FastAPI API

**Branch:** `feat/fastapi-api`

**Files:**
- Create: `backend/app/db.py`, `backend/app/main.py`, `tests/test_api.py`, `Dockerfile`, `docker-compose.yml`

- [ ] Endpoints: `/health`, `/v1/ingest`, `/v1/ask`, `/v1/audit/recent`
- [ ] API tests with TestClient + mock LLM
- [ ] Commit: `feat: add fastapi api`
- [ ] Merge to `main`

### Task 5: Streamlit UI

**Branch:** `feat/streamlit-ui`

**Files:**
- Create: `frontend/streamlit_app.py`

- [ ] Ask form, answer, citations, trace, Plotly chart from viz JSON
- [ ] Commit: `feat: add streamlit ui`
- [ ] Merge to `main`

### Task 6: Copilot contract

**Branch:** `feat/copilot-contract`

**Files:**
- Create: `integrations/copilot-studio/statvisor-openapi-v2.yaml`, `integrations/copilot-studio/SETUP.md`

- [ ] OpenAPI v2 for `/v1/ask` + health
- [ ] Setup guide for Copilot Studio custom connector
- [ ] Commit: `feat: add copilot contract`
- [ ] Merge to `main`

### Task 7: Learning guide + README

**Branch:** `docs/learning-guide`

**Files:**
- Create: `docs/STATVISOR_GUIDE.md`
- Modify: `README.md` (short quickstart only)

- [ ] Full learning doc: architecture, usage, pros/cons, tradeoffs, bottlenecks, why, resume map
- [ ] Commit: `docs: add learning guide`
- [ ] Merge to `main`

### Task 8: Verify + push

**Branch:** `test/core-coverage` (if gaps) or work on `main` for final verify

- [ ] `python -m venv .venv && pip install -r requirements.txt`
- [ ] `make ingest && make test`
- [ ] Fix failures
- [ ] Push `main` to origin

---

## Spec coverage check

| Spec item | Task |
|---|---|
| LangGraph multi-agent | 3 |
| Azure/OpenAI-compatible adapter | 2 (`llm.py`) |
| Hybrid FAISS+BM25 | 2 |
| Tools/grounding | 3 |
| Summarization insights | 3 |
| Streamlit viz | 5 |
| Copilot OpenAPI A | 6 |
| Learning doc | 7 |
| Trunk-based git | all |
| Mock-first LLM | 2–4 |

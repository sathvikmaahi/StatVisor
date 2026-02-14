# StatVisor — Learning Guide

Single document for architecture, usage, tradeoffs, bottlenecks, and resume mapping. Read this for learning; use `README.md` only for quickstart.

## 1. What this project is

StatVisor is a **production-oriented proof of concept** for a multi-agent AI analytics platform. It shows how an R&D team can ask research/infrastructure questions, retrieve grounded evidence, generate insights, and visualize results — through either:

- a **Streamlit** UI for technical users, or
- **Microsoft Copilot Studio** as a low-code business entry point (OpenAPI contract + setup guide).

It is intentionally runnable with **zero cloud API keys** via `LLM_PROVIDER=mock`, while remaining ready for Azure OpenAI or any OpenAI-compatible endpoint (NVIDIA Build, Groq, OpenRouter, etc.).

## 2. Experience points mapped to code

| Resume claim | Where it lives |
|---|---|
| Multi-agent system with LangGraph + LangChain ecosystem + Azure OpenAI | `backend/app/agents/`, `backend/app/llm.py` |
| Copilot Studio front end calling LangGraph/Azure path | `integrations/copilot-studio/` |
| FAISS RAG + hybrid BM25 + dense retrieval | `backend/app/retrieval.py` |
| Prompt engineering, tools/function calling, grounding | `backend/app/agents/nodes.py`, `backend/app/tools.py` |
| Prompt-based research/infra summarization | summarizer node in `nodes.py` |
| Streamlit dynamic visualizations | `frontend/streamlit_app.py` + visualizer node |

## 3. Architecture

```text
┌─────────────┐     ┌──────────────────┐
│  Streamlit  │────►│                  │
└─────────────┘     │     FastAPI      │
┌─────────────┐     │  /v1/ask ingest  │
│ Copilot     │────►│  /health audit   │
│ Studio tool │     └────────┬─────────┘
└─────────────┘              │
                             ▼
                    ┌─────────────────┐
                    │ LangGraph graph │
                    │ router → retrieve│
                    │ → analyst? →    │
                    │ summarizer →    │
                    │ visualizer?     │
                    └────────┬────────┘
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
        Hybrid RAG     LLM adapter     SQLite audit
     FAISS + BM25   mock/azure/compat   query log
```

### Why this architecture

1. **API boundary first** — Streamlit and Copilot share one FastAPI contract. UI churn does not rewrite agent logic.
2. **Explicit LangGraph topology** — router + nodes beat a single mega-prompt for debugging, tests, and demos.
3. **Retrieve-always** — analysis cannot answer from model memory alone; citations are first-class.
4. **Frontend-neutral chart JSON** — visualizer does not emit Plotly code; Streamlit (or a future React app) renders the same spec.
5. **Mock-first LLM adapter** — interviewers and clone-and-run users get a working path without secrets; Azure remains the resume-aligned production target.

## 4. Usage

### Local quick path

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make ingest
make test
make api          # terminal 1
make ui           # terminal 2
```

Open the Streamlit URL, ask: *“Compare hybrid retrieval quality versus dense-only and note bottlenecks.”*

### API examples

```bash
curl -s localhost:8000/health | jq
curl -s -X POST localhost:8000/v1/ask \
  -H 'content-type: application/json' \
  -d '{"question":"Summarize infrastructure risks","session_id":"demo"}' | jq
```

### Enabling real LLMs later

Set in `.env`:

- **Azure OpenAI:** `LLM_PROVIDER=azure` plus endpoint, key, API version, chat + embedding deployments.
- **NVIDIA Build / Groq / OpenRouter:** `LLM_PROVIDER=openai_compatible` plus base URL, key, model names.

Embeddings and chat must both work for hybrid RAG + agents.

### Copilot Studio

Follow `integrations/copilot-studio/SETUP.md`. Upload the OpenAPI v2 file, point host at your API, map `AskStatVisor` into a topic.

## 5. Multi-agent design details

| Node | Job |
|---|---|
| Router | Classifies into research / analysis / summarization / visualization |
| Retrieval | Dense FAISS + sparse BM25, score fusion, top-k chunks |
| Analyst | Interprets evidence: drivers, bottlenecks, uncertainty |
| Summarizer | Concise answer + research/infrastructure insights |
| Visualizer | Bar chart JSON from extracted or sample metrics |

Conditional edges: analysis/visualization routes visit analyst; only visualization visits visualizer after summary.

## 6. Hybrid retrieval

```text
combined = dense_weight * norm(dense) + sparse_weight * norm(bm25)
```

Defaults: dense `0.65`, sparse `0.35`. Dense catches semantic paraphrase; BM25 helps acronyms, IDs, and rare tokens.

Index artifacts: `data/index/faiss.index` + `data/index/chunks.json`. BM25 rebuilds from chunks on load.

## 7. Pros and cons

### Pros

- End-to-end demo of a real multi-agent analytics pattern
- Grounded answers with citations
- Works offline with mock LLM
- Clear split between orchestration, retrieval, and UI
- Copilot-ready contract without locking logic into Power Platform
- Tests cover fusion, tools, and API happy path

### Cons

- POC persistence (SQLite + local FAISS) is not multi-instance safe
- Mock LLM is deterministic/demo-quality, not research-grade
- Copilot Studio integration is contract-level (no live tenant in-repo)
- Chunking is simple fixed-window (not semantic/hierarchical)
- No authN/Z beyond optional API key header

## 8. Benefits and tradeoffs

| Choice | Benefit | Tradeoff |
|---|---|---|
| LangGraph | Inspectable routes/traces | More code than one prompt chain |
| Hybrid RAG | Better keyword + semantic recall | Two indexes to maintain; weights need tuning |
| Streamlit | Fast internal UI | Less polish than a product frontend |
| FastAPI | Typed OpenAPI, easy Copilot tools | You operate an API process |
| SQLite/FAISS local | Zero infra to start | Weak for HA, tenancy, huge corpora |
| Mock default | Clone-and-run | Real quality needs a paid/free LLM key |

## 9. Bottlenecks

1. **Re-indexing** — embedding all chunks on ingest is CPU/API heavy above ~10k chunks.
2. **Chat latency** — multi-node graphs mean multiple LLM calls per ask (router + analyst + summarizer).
3. **Single-node FAISS** — no distributed writers; rolling deploys need shared vector store.
4. **SQLite audit** — fine for demos; locks under concurrent write load.
5. **Context window** — naively stuffing many chunks will degrade quality; top-k and chunk size matter.

## 10. Production migration path

- Identity: Entra ID / API gateway auth instead of shared API key
- Data: Postgres for audit/sessions; Azure AI Search or pgvector for retrieval
- Models: Azure OpenAI / Microsoft Foundry private networking
- Observability: OpenTelemetry traces per graph node; prompt/version logging
- Eval: golden questions + citation faithfulness checks in CI
- UI: keep FastAPI contract; optionally replace Streamlit with React for customers

## 11. Security notes (POC)

- Secrets only via environment variables (never commit `.env`)
- Non-`local` environments require `x-api-key`
- Retrieved text is the only allowed factual basis in prompts
- Treat user questions as untrusted input (no shell tools in this POC)

## 12. Repository map

```text
backend/app/          FastAPI, LLM, RAG, agents
frontend/             Streamlit UI
integrations/         Copilot Studio OpenAPI + setup
data/sample_docs/     Demo corpus
scripts/              Ingest helper
tests/                pytest suite
docs/STATVISOR_GUIDE.md  This file
docs/superpowers/     Design + implementation plan
```

## 13. Git workflow used

Trunk-based development on `main` with short-lived feature branches (`feat/*`, `docs/*`), conventional lowercase commits, frequent merges. History reflects real work order — not fabricated dates.

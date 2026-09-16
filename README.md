# StatVisor

A production-oriented proof of concept for **multi-agent AI analytics**: ask research and infrastructure questions, retrieve grounded evidence, generate insights, and visualize results — through a technical UI or a business-facing Copilot entry point.

## Why this project

Research and platform teams often have the same problem: answers live in scattered notes, metrics, and decision logs, while stakeholders want a clear summary they can trust.

StatVisor was built to demonstrate a practical pattern for that problem:

- **Grounded answers** — retrieval runs before generation so responses cite evidence instead of inventing it
- **Inspectable agents** — routing and analysis are explicit graph nodes, not one opaque mega-prompt
- **Two audiences, one API** — engineers use Streamlit; business users can reach the same backend through Microsoft Copilot Studio
- **Clone-and-run** — works with a mock LLM and no cloud keys, while staying ready for Azure OpenAI or any OpenAI-compatible provider

It is intentionally a lean POC: enough architecture to show real production decisions, without pretending to be a full multi-tenant product.

## Who it is for

| Audience | How they use it |
|---|---|
| **R&D / platform engineers** | Ask technical questions, inspect citations, run the API and agent graph locally |
| **Analytics / research leads** | Summarize infrastructure risks, compare approaches, and review insight quality |
| **Low-code / business users** | Call the same ask endpoint from Microsoft Copilot Studio via the OpenAPI contract |
| **Hiring managers / reviewers** | Clone the repo, run without secrets, and see LangGraph, hybrid RAG, and API design in one place |

## What you can do with it

1. Ingest a small research/infrastructure corpus into a local hybrid index (FAISS + BM25)
2. Ask natural-language questions over `POST /v1/ask`
3. Get a grounded answer, optional insights, citations, and chart-ready JSON
4. Use **Streamlit** for an interactive UI, or wire **Copilot Studio** to the same OpenAPI surface

### Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make ingest
make test
make api    # http://localhost:8000
make ui     # Streamlit
```

Example ask:

```bash
curl -s -X POST localhost:8000/v1/ask \
  -H 'content-type: application/json' \
  -d '{"question":"Summarize infrastructure risks","session_id":"demo"}'
```

Keep `LLM_PROVIDER=mock` until you have a key. For Azure OpenAI or NVIDIA Build / Groq / OpenRouter, set `azure` or `openai_compatible` in `.env` (see `.env.example`).

Copilot Studio setup: [`integrations/copilot-studio/SETUP.md`](integrations/copilot-studio/SETUP.md)

## Decisions we took

| Decision | Choice | Why |
|---|---|---|
| Shape | Lean monorepo | One clone, one mental model; backend, UI, and integrations stay aligned |
| Orchestration | LangGraph multi-node graph | Clear routes for debugging, demos, and tests vs a single prompt chain |
| Retrieval | Hybrid FAISS + BM25 | Dense search for paraphrase; sparse search for acronyms, IDs, and rare tokens |
| LLM default | Mock provider | Anyone can run the POC without secrets; Azure / compatible providers are env-ready |
| UI strategy | Streamlit + shared FastAPI | Fast internal UX without locking agent logic into a frontend framework |
| Business entry | Copilot Studio OpenAPI contract | Low-code access without embedding orchestration inside Power Platform |
| Persistence | SQLite + on-disk FAISS | Zero infra to start; honest ceiling for HA / multi-instance later |
| Docs | Short README + deep learning guide | README for orientation; [`docs/STATVISOR_GUIDE.md`](docs/STATVISOR_GUIDE.md) for depth |

## Architectural decisions (high level)

```text
Streamlit UI ──────────────┐
                           ├── FastAPI ── LangGraph
Copilot Studio (OpenAPI) ──┘      │
                                  ├ Router → Retrieval (FAISS + BM25)
                                  ├ Analyst → Summarizer → (optional) Visualizer
                                  ├ LLM adapter (mock | azure | openai_compatible)
                                  └ SQLite audit + on-disk FAISS / chunks
```

1. **API boundary first** — Streamlit and Copilot share one FastAPI contract. UI changes do not rewrite agent logic.
2. **Retrieve-always** — analysis cannot answer from model memory alone; citations are first-class.
3. **Explicit graph topology** — router, retrieval, analyst, summarizer, and visualizer are separate nodes with conditional edges.
4. **Frontend-neutral chart JSON** — the visualizer emits a renderable spec, not Plotly-specific code, so Streamlit or a future web app can consume it.
5. **Adapter-shaped LLM layer** — chat and embeddings swap between mock, Azure OpenAI, and OpenAI-compatible endpoints without touching the graph.
6. **POC-honest storage** — local SQLite and FAISS keep demos simple; production would move to managed auth, Postgres, and a shared vector store.

## Repository map

```text
backend/app/          FastAPI, LLM adapter, hybrid RAG, LangGraph agents
frontend/             Streamlit UI
integrations/         Copilot Studio OpenAPI + setup
data/sample_docs/     Demo corpus
scripts/              Ingest helper
tests/                pytest suite
docs/STATVISOR_GUIDE.md
```

## Learn more

Full architecture, tradeoffs, bottlenecks, and production migration notes: **[docs/STATVISOR_GUIDE.md](docs/STATVISOR_GUIDE.md)**

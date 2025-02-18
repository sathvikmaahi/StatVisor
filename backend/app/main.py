from fastapi import FastAPI, Header, HTTPException

from backend.app.agents import nodes
from backend.app.agents.graph import graph
from backend.app.config import get_settings
from backend.app.db import init_db, log_query, recent_queries
from backend.app.schemas import AskRequest, AskResponse, Citation, IngestRequest, IngestResponse

app = FastAPI(
    title="StatVisor API",
    version="0.1.0",
    description="Multi-agent AI analytics POC with LangGraph and hybrid RAG.",
)
settings = get_settings()
init_db()


def check_key(x_api_key: str | None) -> None:
    if settings.app_env != "local" and x_api_key != settings.statvisor_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "indexed_chunks": len(nodes.retriever.chunks),
    }


@app.post("/v1/ingest", response_model=IngestResponse)
def ingest(body: IngestRequest, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    docs = [d.model_dump() for d in body.documents]
    chunks = nodes.retriever.build(docs)
    return IngestResponse(documents_received=len(body.documents), chunks_indexed=chunks)


@app.post("/v1/ask", response_model=AskResponse)
def ask(body: AskRequest, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    result = graph.invoke(
        {
            "question": body.question,
            "session_id": body.session_id,
            "trace": [],
        }
    )
    log_query(
        body.session_id,
        body.question,
        result.get("route", "research"),
        result.get("answer", ""),
        result.get("trace", []),
    )
    citations = [
        Citation(
            source=d["source"],
            chunk_id=d["chunk_id"],
            score=d["score"],
            text=d["text"][:420],
        )
        for d in result.get("retrieved", [])
    ]
    return AskResponse(
        answer=result.get("answer", ""),
        route=result.get("route", "research"),
        citations=citations,
        insights=result.get("insights", []),
        visualization=result.get("visualization"),
        trace=result.get("trace", []),
    )


@app.get("/v1/audit/recent")
def audit_recent(limit: int = 20, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    return {"items": recent_queries(min(max(limit, 1), 100))}

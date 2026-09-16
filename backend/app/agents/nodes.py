from __future__ import annotations

import re

from backend.app.agents.state import StatVisorState
from backend.app.llm import LLMService
from backend.app.retrieval import HybridRetriever
from backend.app.tools import build_bar_chart_spec, compute_basic_stats

llm = LLMService()
retriever = HybridRetriever.empty(llm=llm)
retriever.load()

ROUTER_SYSTEM = (
    "Classify the user question into exactly one route token: "
    "research, analysis, summarization, or visualization. Reply with only the token."
)

ANALYST_SYSTEM = (
    "You are StatVisor's analysis agent. Use ONLY the provided evidence. "
    "Call out drivers, bottlenecks, and uncertainty. Do not invent metrics."
)

SUMMARIZER_SYSTEM = (
    "You are StatVisor's summarization agent. Produce a concise grounded answer "
    "and 2-4 short research or infrastructure insights. Use only provided evidence."
)


def _context(state: StatVisorState) -> str:
    docs = state.get("retrieved") or []
    if not docs:
        return "No evidence retrieved."
    return "\n\n".join(f"[{d['source']} | {d['chunk_id']} | score={d['score']}]\n{d['text']}" for d in docs)


def router_node(state: StatVisorState) -> StatVisorState:
    route = llm.chat(ROUTER_SYSTEM, state["question"]).strip().lower()
    if route not in {"research", "analysis", "summarization", "visualization"}:
        route = "research"
    trace = list(state.get("trace") or [])
    trace.append(f"router -> {route}")
    return {"route": route, "trace": trace}


def retrieval_node(state: StatVisorState) -> StatVisorState:
    hits = retriever.search(state["question"])
    trace = list(state.get("trace") or [])
    trace.append(f"retrieval -> {len(hits)} chunks")
    return {"retrieved": hits, "trace": trace}


def analyst_node(state: StatVisorState) -> StatVisorState:
    user = f"Question:\n{state['question']}\n\nEvidence:\n{_context(state)}"
    analysis = llm.chat(ANALYST_SYSTEM, user)
    if not (state.get("retrieved") or []):
        analysis = "Insufficient evidence in the index to support a detailed analysis."
    trace = list(state.get("trace") or [])
    trace.append("analyst -> complete")
    return {"analysis": analysis, "trace": trace}


def summarizer_node(state: StatVisorState) -> StatVisorState:
    analysis = state.get("analysis") or ""
    user = (
        f"Question:\n{state['question']}\n\nAnalysis:\n{analysis}\n\nEvidence:\n{_context(state)}\n\n"
        "Return a short answer paragraph, then lines starting with 'Insight:'."
    )
    raw = llm.chat(SUMMARIZER_SYSTEM, user)
    if not (state.get("retrieved") or []):
        raw = (
            "Insufficient evidence to produce a grounded summary.\n"
            "Insight: Ingest domain documents before trusting answers.\n"
            "Insight: Hybrid retrieval needs a populated FAISS/BM25 index."
        )
    insights = [line.split(":", 1)[1].strip() for line in raw.splitlines() if line.lower().startswith("insight:")]
    answer_lines = [line for line in raw.splitlines() if not line.lower().startswith("insight:")]
    answer = "\n".join(answer_lines).strip() or raw.strip()
    if not insights:
        insights = [
            "Ground answers in retrieved citations.",
            "Tune dense/sparse weights with an evaluation set.",
        ]
    trace = list(state.get("trace") or [])
    trace.append("summarizer -> complete")
    return {"answer": answer, "insights": insights[:4], "trace": trace}


def visualizer_node(state: StatVisorState) -> StatVisorState:
    text = " ".join(d["text"] for d in (state.get("retrieved") or []))
    numbers = [float(x) for x in re.findall(r"\b0?\.\d+\b|\b\d+\.\d+\b", text)]
    # ponytail: demo chart from first numeric mentions; replace with structured metrics table when available
    if len(numbers) >= 2:
        stats = compute_basic_stats(numbers[:8])
        labels = ["mean", "median", "stdev"]
        values = [stats["mean"], stats["median"], stats["stdev"]]
        title = "Extracted metric snapshot"
    else:
        labels = ["dense_only_recall@5", "hybrid_recall@5"]
        values = [0.61, 0.78]
        title = "Sample retrieval quality"
    viz = build_bar_chart_spec(title, labels, values)
    trace = list(state.get("trace") or [])
    trace.append("visualizer -> chart_spec")
    return {"visualization": viz, "trace": trace}

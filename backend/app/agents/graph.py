from langgraph.graph import END, START, StateGraph

from backend.app.agents.nodes import (
    analyst_node,
    retrieval_node,
    router_node,
    summarizer_node,
    visualizer_node,
)
from backend.app.agents.state import StatVisorState


def after_retrieval(state: StatVisorState) -> str:
    route = state.get("route", "research")
    if route in {"analysis", "visualization"}:
        return "analyst"
    return "summarizer"


def after_summary(state: StatVisorState):
    if state.get("route") == "visualization":
        return "visualizer"
    return END


def build_graph():
    builder = StateGraph(StatVisorState)
    builder.add_node("router", router_node)
    builder.add_node("retrieval", retrieval_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("summarizer", summarizer_node)
    builder.add_node("visualizer", visualizer_node)

    builder.add_edge(START, "router")
    builder.add_edge("router", "retrieval")
    builder.add_conditional_edges(
        "retrieval",
        after_retrieval,
        {"analyst": "analyst", "summarizer": "summarizer"},
    )
    builder.add_edge("analyst", "summarizer")
    builder.add_conditional_edges(
        "summarizer",
        after_summary,
        {"visualizer": "visualizer", END: END},
    )
    builder.add_edge("visualizer", END)
    return builder.compile()


graph = build_graph()

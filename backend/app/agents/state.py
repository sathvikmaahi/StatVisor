from typing import Any, TypedDict


class StatVisorState(TypedDict, total=False):
    question: str
    session_id: str
    route: str
    retrieved: list[dict[str, Any]]
    analysis: str
    answer: str
    insights: list[str]
    visualization: dict[str, Any] | None
    trace: list[str]

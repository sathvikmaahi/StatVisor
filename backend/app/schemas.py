from typing import Any

from pydantic import BaseModel, Field


class DocumentIn(BaseModel):
    source: str
    text: str


class IngestRequest(BaseModel):
    documents: list[DocumentIn]


class IngestResponse(BaseModel):
    documents_received: int
    chunks_indexed: int


class AskRequest(BaseModel):
    question: str = Field(min_length=3)
    session_id: str = "default"


class Citation(BaseModel):
    source: str
    chunk_id: str
    score: float
    text: str


class AskResponse(BaseModel):
    answer: str
    route: str
    citations: list[Citation]
    insights: list[str]
    visualization: dict[str, Any] | None = None
    trace: list[str]

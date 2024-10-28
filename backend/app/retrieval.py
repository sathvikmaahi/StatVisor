from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from backend.app.config import Settings, get_settings
from backend.app.llm import LLMService


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def chunk_text(text: str, source: str, chunk_size: int = 700, overlap: int = 120) -> list[dict]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        piece = text[start:end].strip()
        if piece:
            chunks.append(
                {
                    "chunk_id": f"{source}::{idx}",
                    "source": source,
                    "text": piece,
                }
            )
            idx += 1
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _normalize(scores: list[float]) -> list[float]:
    if not scores:
        return []
    lo, hi = min(scores), max(scores)
    if hi - lo < 1e-9:
        return [1.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


@dataclass
class HybridRetriever:
    settings: Settings
    llm: LLMService
    chunks: list[dict]
    index: faiss.IndexFlatIP | None
    bm25: BM25Okapi | None

    @classmethod
    def empty(cls, settings: Settings | None = None, llm: LLMService | None = None) -> HybridRetriever:
        settings = settings or get_settings()
        llm = llm or LLMService(settings)
        return cls(settings=settings, llm=llm, chunks=[], index=None, bm25=None)

    def build(self, documents: list[dict]) -> int:
        chunks: list[dict] = []
        for doc in documents:
            chunks.extend(chunk_text(doc["text"], doc["source"]))
        self.chunks = chunks
        if not chunks:
            self.index = None
            self.bm25 = None
            return 0
        vectors = np.array(self.llm.embed([c["text"] for c in chunks]), dtype=np.float32)
        faiss.normalize_L2(vectors)
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)
        self.bm25 = BM25Okapi([_tokenize(c["text"]) for c in chunks])
        self.persist()
        return len(chunks)

    def persist(self) -> None:
        path = Path(self.settings.index_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / "chunks.json").write_text(json.dumps(self.chunks, indent=2), encoding="utf-8")
        if self.index is not None:
            faiss.write_index(self.index, str(path / "faiss.index"))

    def load(self) -> bool:
        path = Path(self.settings.index_dir)
        chunks_path = path / "chunks.json"
        index_path = path / "faiss.index"
        if not chunks_path.exists() or not index_path.exists():
            return False
        self.chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
        self.index = faiss.read_index(str(index_path))
        self.bm25 = BM25Okapi([_tokenize(c["text"]) for c in self.chunks]) if self.chunks else None
        return True

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        if not self.chunks or self.index is None or self.bm25 is None:
            return []
        k = top_k or self.settings.top_k
        k = min(k, len(self.chunks))
        q = np.array(self.llm.embed([query]), dtype=np.float32)
        faiss.normalize_L2(q)
        dense_scores, dense_ids = self.index.search(q, k)
        dense_map = {int(i): float(s) for i, s in zip(dense_ids[0], dense_scores[0]) if i >= 0}
        sparse_raw = list(self.bm25.get_scores(_tokenize(query)))
        sparse_norm = _normalize(sparse_raw)
        dense_norm_vals = _normalize([dense_map.get(i, 0.0) for i in range(len(self.chunks))])

        fused: list[tuple[float, int]] = []
        for i in range(len(self.chunks)):
            score = (
                self.settings.dense_weight * dense_norm_vals[i]
                + self.settings.sparse_weight * sparse_norm[i]
            )
            fused.append((score, i))
        fused.sort(reverse=True)
        results = []
        for score, i in fused[:k]:
            item = dict(self.chunks[i])
            item["score"] = round(float(score), 4)
            results.append(item)
        return results


def fuse_scores(dense: list[float], sparse: list[float], dense_w: float, sparse_w: float) -> list[float]:
    """Pure fusion helper for tests."""
    dn = _normalize(dense)
    sn = _normalize(sparse)
    return [dense_w * d + sparse_w * s for d, s in zip(dn, sn)]

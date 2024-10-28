from pathlib import Path

from backend.app.llm import LLMService
from backend.app.retrieval import HybridRetriever


def main() -> None:
    root = Path("data/sample_docs")
    docs = [{"source": p.name, "text": p.read_text(encoding="utf-8")} for p in sorted(root.glob("*.txt"))]
    retriever = HybridRetriever.empty(llm=LLMService())
    n = retriever.build(docs)
    print(f"indexed {len(docs)} documents into {n} chunks at data/index")


if __name__ == "__main__":
    main()

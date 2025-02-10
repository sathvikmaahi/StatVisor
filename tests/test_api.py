from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ingest_and_ask():
    ingest = client.post(
        "/v1/ingest",
        json={
            "documents": [
                {
                    "source": "demo.txt",
                    "text": "Hybrid FAISS and BM25 improved recall@5 from 0.61 to 0.78. Latency stayed under 1.8s.",
                }
            ]
        },
    )
    assert ingest.status_code == 200
    assert ingest.json()["chunks_indexed"] >= 1

    ask = client.post(
        "/v1/ask",
        json={"question": "Compare hybrid retrieval quality and latency", "session_id": "test"},
    )
    assert ask.status_code == 200
    body = ask.json()
    assert body["answer"]
    assert body["route"] in {"research", "analysis", "summarization", "visualization"}
    assert isinstance(body["citations"], list)
    assert isinstance(body["trace"], list)
    assert body["trace"]

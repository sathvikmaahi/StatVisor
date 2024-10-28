from __future__ import annotations

import hashlib
import math
import re
from typing import Any

from openai import AzureOpenAI, OpenAI

from backend.app.config import Settings, get_settings


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class LLMService:
    """Chat + embeddings adapter. mock | azure | openai_compatible."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.provider = self.settings.llm_provider.lower().strip()
        self._client: Any = None
        if self.provider == "azure":
            if not self.settings.azure_openai_endpoint or not self.settings.azure_openai_api_key:
                raise ValueError("Azure mode requires AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")
            self._client = AzureOpenAI(
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_key=self.settings.azure_openai_api_key,
                api_version=self.settings.azure_openai_api_version,
            )
        elif self.provider == "openai_compatible":
            if not self.settings.openai_compatible_base_url or not self.settings.openai_compatible_api_key:
                raise ValueError("openai_compatible mode requires base URL and API key")
            self._client = OpenAI(
                base_url=self.settings.openai_compatible_base_url,
                api_key=self.settings.openai_compatible_api_key,
            )
        elif self.provider != "mock":
            raise ValueError(f"Unknown LLM_PROVIDER: {self.provider}")

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self.provider == "mock":
            return [self._mock_embed(t) for t in texts]
        if self.provider == "azure":
            resp = self._client.embeddings.create(
                model=self.settings.azure_openai_embedding_deployment,
                input=texts,
            )
            return [item.embedding for item in resp.data]
        resp = self._client.embeddings.create(
            model=self.settings.openai_compatible_embedding_model,
            input=texts,
        )
        return [item.embedding for item in resp.data]

    def chat(self, system: str, user: str) -> str:
        if self.provider == "mock":
            return self._mock_chat(system, user)
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        if self.provider == "azure":
            resp = self._client.chat.completions.create(
                model=self.settings.azure_openai_chat_deployment,
                messages=messages,
                temperature=0.2,
            )
        else:
            resp = self._client.chat.completions.create(
                model=self.settings.openai_compatible_chat_model,
                messages=messages,
                temperature=0.2,
            )
        return (resp.choices[0].message.content or "").strip()

    def _mock_embed(self, text: str, dims: int = 64) -> list[float]:
        vec = [0.0] * dims
        for token in _tokenize(text):
            digest = hashlib.sha256(token.encode()).digest()
            idx = digest[0] % dims
            sign = 1.0 if digest[1] % 2 == 0 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def _mock_chat(self, system: str, user: str) -> str:
        lowered = (system + "\n" + user).lower()
        if "route" in lowered or "classify" in lowered:
            if any(k in user.lower() for k in ("chart", "plot", "visual", "graph")):
                return "visualization"
            if any(k in user.lower() for k in ("compare", "analyze", "driver", "bottleneck")):
                return "analysis"
            if any(k in user.lower() for k in ("summary", "summarize", "insight")):
                return "summarization"
            return "research"
        if "insight" in lowered or "summar" in lowered:
            return (
                "Grounded summary: evidence points to latency and cost as primary drivers. "
                "Insight: prioritize retrieval quality before scaling model size. "
                "Insight: document infrastructure SLOs next to experiment metrics."
            )
        return (
            "Based only on retrieved evidence, the key findings are documented in the citations. "
            "No unsupported metrics were invented."
        )

from __future__ import annotations

import statistics
from typing import Any


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "compute_basic_stats",
            "description": "Compute mean, median, and stdev for a numeric series.",
            "parameters": {
                "type": "object",
                "properties": {
                    "values": {"type": "array", "items": {"type": "number"}},
                },
                "required": ["values"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_bar_chart_spec",
            "description": "Build a frontend-neutral bar chart specification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "labels": {"type": "array", "items": {"type": "string"}},
                    "values": {"type": "array", "items": {"type": "number"}},
                },
                "required": ["title", "labels", "values"],
            },
        },
    },
]


def compute_basic_stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "median": 0.0, "stdev": 0.0}
    return {
        "mean": float(statistics.mean(values)),
        "median": float(statistics.median(values)),
        "stdev": float(statistics.pstdev(values)) if len(values) > 1 else 0.0,
    }


def build_bar_chart_spec(title: str, labels: list[str], values: list[float]) -> dict[str, Any]:
    return {
        "type": "bar",
        "title": title,
        "data": {"labels": labels, "values": values},
    }

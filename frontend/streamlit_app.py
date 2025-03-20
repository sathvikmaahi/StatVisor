import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = os.getenv("STATVISOR_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="StatVisor", layout="wide")
st.title("StatVisor")
st.caption("Multi-agent AI analytics POC — LangGraph + hybrid RAG")

with st.sidebar:
    st.subheader("Connection")
    api_url = st.text_input("API URL", API_URL)
    session_id = st.text_input("Session ID", "demo")
    if st.button("Check health"):
        try:
            health = requests.get(f"{api_url}/health", timeout=10).json()
            st.success(health)
        except Exception as exc:  # noqa: BLE001
            st.error(str(exc))
    if st.button("Recent audit"):
        try:
            items = requests.get(f"{api_url}/v1/audit/recent", params={"limit": 5}, timeout=10).json()
            st.json(items)
        except Exception as exc:  # noqa: BLE001
            st.error(str(exc))

question = st.text_area(
    "Ask a research or infrastructure question",
    "Compare hybrid retrieval quality versus dense-only and note bottlenecks",
    height=120,
)

if st.button("Run agents", type="primary") and question.strip():
    with st.spinner("Running LangGraph workflow..."):
        resp = requests.post(
            f"{api_url}/v1/ask",
            json={"question": question.strip(), "session_id": session_id},
            timeout=120,
        )
    if resp.status_code != 200:
        st.error(resp.text)
    else:
        data = resp.json()
        st.subheader("Answer")
        st.write(data.get("answer", ""))
        cols = st.columns(3)
        cols[0].metric("Route", data.get("route", "-"))
        cols[1].metric("Citations", len(data.get("citations") or []))
        cols[2].metric("Insights", len(data.get("insights") or []))

        st.subheader("Insights")
        for insight in data.get("insights") or []:
            st.write(f"- {insight}")

        st.subheader("Citations")
        for cite in data.get("citations") or []:
            with st.expander(f"{cite['source']} ({cite['chunk_id']}) score={cite['score']}"):
                st.write(cite["text"])

        st.subheader("Agent trace")
        for step in data.get("trace") or []:
            st.code(step)

        viz = data.get("visualization")
        if viz and viz.get("type") == "bar":
            st.subheader(viz.get("title") or "Visualization")
            frame = pd.DataFrame(
                {
                    "label": viz["data"]["labels"],
                    "value": viz["data"]["values"],
                }
            )
            fig = px.bar(frame, x="label", y="value", title=viz.get("title"))
            st.plotly_chart(fig, use_container_width=True)

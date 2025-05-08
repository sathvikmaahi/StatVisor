# Connect StatVisor to Microsoft Copilot Studio

This guide wires Copilot Studio as a **low-code business-user entry point** that calls the same FastAPI backend used by Streamlit. Core analytics stay in LangGraph; Copilot only orchestrates conversation topics/actions.

## Prerequisites

- StatVisor API reachable over HTTPS (local demos can use a tunnel such as ngrok)
- Copilot Studio access in a Microsoft tenant
- Optional: `STATVISOR_API_KEY` when `APP_ENV` is not `local`

## Steps

1. Deploy or run the StatVisor API (`make api` or Docker Compose).
2. In Copilot Studio, create or open an agent.
3. Add a **REST API** / custom connector tool.
4. Upload `statvisor-openapi-v2.yaml` (OpenAPI v2).
5. Set the host to your public API hostname (replace `localhost:8000`).
6. Configure the `x-api-key` header if your environment requires it.
7. Create a topic such as **Ask analytics** that collects a question and calls `AskStatVisor`.
8. Map the tool response fields (`answer`, `insights`, `route`) into the bot message.

## Design rule

Do **not** put retrieval, prompting, or business analytics logic inside Copilot topics. Keep that in LangGraph so it remains testable and portable across Streamlit, Copilot, and future UIs.

## Verification

- Copilot topic returns a grounded answer for a sample question after ingest.
- `/health` succeeds from the connector test panel.
- Audit rows appear via `GET /v1/audit/recent` for Copilot `session_id` values.

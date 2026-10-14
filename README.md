# AgentDesk — Enterprise Agent Platform (foundation)

An enterprise customer support agent platform with multi-turn conversations,
agent orchestration, tool calling, and RAG, built incrementally from a runnable
foundation.

企业级智能客服 Agent 项目：围绕多轮对话、Agent 编排、工具调用和 RAG 构建完整业务闭环。

> **Scope:** runnable **foundation**, not a finished production support product. The current demonstration covers conversation identity, persistent task state, deterministic dialogue decisions, replay-safe request IDs and tests. Real LLM routing, order/refund tools, RAG, auth, UI and observability are staged integration work, **not present yet**.

## Design choices

- FastAPI / Pydantic v2 / Python 3.12, SQLAlchemy 2.x async + Alembic
- MySQL 8.4 **source of truth** (conversations, turns, task state); Redis for future caching / streams / ephemeral locks
- Existing Milvus 2.6.x **reused** as an external service for future RAG (not modified by this Compose)
- Pure Python Dialogue Manager and deterministic business FSM; pluggable LLM interpreter for ambiguous cases later
- API is a modular monolith. Avoid unnecessary separate Agent services and duplicated state stores.

## Local startup

```bash
git clone https://github.com/Acxxxq/agentdesk.git
cd agentdesk
# from repository root: isolated local ports 18000 / 53306 / 56379
docker compose -f infra/compose.yaml up -d --build
curl http://127.0.0.1:18000/health
```

For Windows PowerShell use `curl.exe` instead of `curl` if the alias behaves differently.

Create a conversation (DEMO AUTH only, **never expose publicly**):

```bash
curl -s http://127.0.0.1:18000/api/v1/conversations \
  -H 'X-Demo-User: user_001' -H 'Content-Type: application/json' -d '{}'
# Copy the returned id to CONV_ID
```

Post a turn (replace `<CONV_ID>` and pass a distinct `request_id` per user turn):

```bash
curl -s http://127.0.0.1:18000/api/v1/conversations/<CONV_ID>/turns \
  -H 'X-Demo-User: user_001' -H 'Content-Type: application/json' \
  -d '{"request_id":"req-001","message":"我要退款"}'
```

Follow with `{"request_id":"req-002","message":"A1001"}`. Repeating the same request ID returns the stored response rather than processing twice. This does **not** make external side-effecting tools idempotent; that needs a durable tool execution ledger / provider idempotency key.

Try stopping & restarting the API container: MySQL retains the dialogue state. No refund is ever submitted by this demo.

## Dev

```bash
cd backend
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
```

Copy `backend/.env.example` to `backend/.env` and set `DATABASE_URL` pointing at
a MySQL 8.4 instance before running the API outside Docker. From `backend/`,
apply migrations with `python -m alembic upgrade head`.

## Important safety + durability boundaries

- `X-Demo-User` is accepted **only** when `APP_ENV=development`. Production explicitly rejects it until a real JWT/OIDC authentication adapter and tenant authorization are implemented.
- Persisted relational records are the source of truth. Do not use Redis TTL as the sole copy of active tasks.
- `SELECT FOR UPDATE` is used for this **short, deterministic demo transaction**. Do not hold a DB transaction open across remote LLM/tool calls in later phases; use leases + optimistic version checks / orchestration run IDs.
- The demo does not run business-effect tools. Refund eligibility and confirmation must be verified through trusted services, and any submit operation needs approval, idempotency, audit, and recovery logic.
- This Compose uses a separate project network and local-only, nonstandard host ports; it does not start, stop, or modify an existing Milvus / Redis / EchoMind deployment.

More detail: `docs/ARCHITECTURE.md`, `docs/ADR-001-stack.md`, `docs/ROADMAP.md`.

## Development history and contributions

- [Development log](docs/DEVLOG.md): milestones, decisions and lessons.
- [Roadmap](docs/ROADMAP.md): delivery stages and planned features.
- [Contributing](CONTRIBUTING.md): local development and pull request workflow.

## License

[MIT](LICENSE) © 2026 Acxxxq.

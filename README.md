# AgentDesk

An enterprise customer support agent platform with multi-turn conversations,
agent orchestration, tool calling, and RAG, built incrementally from a runnable
foundation.

企业级智能客服 Agent 项目，围绕多轮对话、Agent 编排、工具调用和 RAG 构建完整业务闭环。

**Current scope:** a deterministic dialogue/task demo with MySQL conversation
state, request deduplication, an isolated Docker environment and dependency
diagnostics. Real LLM routing, order/refund tools, RAG pipelines, authentication,
long-term memory, workers and frontend are planned features.

## Quick start

Install Git and Docker with Linux containers (Windows: Docker Desktop with WSL 2).
Python, MySQL, Redis and Milvus run inside containers. Run these commands in
PowerShell or a Linux/macOS shell:

```bash
git clone https://github.com/Acxxxq/agentdesk.git
cd agentdesk
docker run --rm --mount "type=bind,source=${PWD},target=/workspace" -w /workspace python:3.12-slim python scripts/generate_env.py
docker compose config --quiet
docker compose up -d --build --wait
```

The generator creates an ignored `.env` with independent random passwords and
refuses to replace existing credentials. If `.env` already exists, skip that
command. See [Docker guide](docs/DOCKER.md) for startup and troubleshooting.

Open [API documentation](http://127.0.0.1:18000/docs) or check:

```bash
curl http://127.0.0.1:18000/health/ready
curl http://127.0.0.1:18000/health/dependencies
```

In Windows PowerShell, use `curl.exe` if `curl` resolves to a PowerShell alias.

## Development and testing

Use source mounts and automatic reload for backend development:

```bash
docker compose -f compose.yaml -f compose.dev.yaml up -d --build --wait
docker compose logs -f api
```

Run the test image without starting the infrastructure:

```bash
docker compose --profile test build tests
docker compose --profile test run --rm --no-deps tests
```

GitHub Actions uses the same container commands. Tests cover deterministic
dialogue transitions and readiness behavior; live infrastructure validation
is separate from these offline checks.

## Conversation demo

Create a conversation using the local development identity header, then send
`我要退款` and `A1001` with distinct request IDs. The API documentation includes
the request schemas and interactive examples.

```bash
curl http://127.0.0.1:18000/api/v1/conversations -H 'X-Demo-User: user_001' -H 'Content-Type: application/json' -d '{}'
```

Repeating a request ID with the same message avoids processing it twice. This
does not make external business tools idempotent. No refund is submitted by
the current demo.

## Architecture and deployment

- Python 3.12 / FastAPI / Pydantic v2 / SQLAlchemy async / Alembic.
- MySQL 8.4 holds authoritative business state; Redis provides cache/queue infrastructure.
- Milvus 2.6.24 with etcd and dedicated MinIO; a separate MinIO stores documents.
- A modular monolith with deterministic task transitions and future model/tool adapters.
- One-shot services apply migrations and initialize the private document bucket.
- Optional Attu administration UI: `docker compose --profile admin up -d attu`.

Services use an isolated `agentdesk` network and named volumes. Host ports bind
to loopback. Existing EchoMind and Milvus instances keep their own data and ports.
The development API uses a demo identity header; replace it with real identity
and tenant authorization before Internet deployment.

## Project records

- [Architecture](docs/ARCHITECTURE.md)
- [Technology decisions](docs/ADR-001-stack.md)
- [Roadmap](docs/ROADMAP.md)
- [Development log](docs/DEVLOG.md)
- [Contributing](CONTRIBUTING.md)

## License

[MIT](LICENSE) © 2026 Acxxxq.

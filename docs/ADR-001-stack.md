# ADR-001: Technology selections (2026-10)

## Accepted

| Area | Choice | Reason |
|---|---|---|
| Architecture | Modular monolith + replaceable Ports/Adapters | Easy local deployment and debugging; preserves extraction boundary |
| Runtime | Python 3.12 / FastAPI / Pydantic v2 | Type-safe APIs; matches existing learning path |
| Dependencies | venv / pip / pyproject.toml | Isolated local environment with matching CI install commands; dependency locking is planned |
| Transactional data | MySQL 8.4 / SQLAlchemy 2 async (`asyncmy`) / Alembic | Familiar transactional store for auth, ownership, conversation state, task events and idempotency |
| Ephemeral + events | Redis | Cache/rate limiting/short-lived streams; never only durable state holder |
| RAG vector store | Existing Milvus 2.6.x, accessed via gateway adapter | Already deployed, supports filtered/vector and hybrid search |
| Docs and attachments | MinIO (phase 2) | Object storage for file originals, outside vector DB |
| Agent | Explicit dialogue/task state machine + bounded tool loop (phase 2) | Predictable business transitions and readable interview-ready internals |
| Model | OpenAI-compatible API through own ModelGateway | Start with one model; configurable provider, trace, token and timeout budget |
| UI | React + Vite + TypeScript + Tailwind/shadcn (phase 2) | Lightweight interactive customer + operator console |
| Observability | OpenTelemetry + Langfuse (phase 2) | Provider-neutral tracing; full LLM/tool decision trail |
| Testing | pytest + golden multi-turn fixtures + offline evals | Test action/slot/task completion and replay; LLM judge is supplemental |
| Workers | Celery + Redis, optional phase 3 | Index documents and run evals asynchronously, not request-path side effects |

## Not selected as v1 mandatory infrastructure

- LangGraph: excellent checkpointer / human-in-the-loop graph runtime. Do not add until execution graphs, graph checkpoints or resumable interrupts justify it. A future adapter can map `conversation_id` to `thread_id`, without replacing business truth in MySQL.
- Temporal/DBOS: useful for *durable long-running runs*; a different problem from storing chat transcripts. Adopt when real requirements (hour-long workflows, scheduled compensation) appear.
- Kafka, Kubernetes, multiple agent microservices: overhead without present throughput/scale requirements.
- ChromaDB: superseded for new RAG in this project, but an export/import migration can be added separately; do **not** delete existing EchoMind collections.

## Critical invariants

1. `tenant_id + user_id` authorizes all conversation reads/writes, not just `conversation_id`.
2. Each client turn has a stable request ID and a single recorded result.
3. History is not authoritative task state. The Task State contains business parameters, stage, approvals and expected slots.
4. LLM output is *untrusted input*. Schema validation and business authorization precede action.
5. An agent change does not imply creating another customer conversation.
6. Model, Milvus, Redis, background worker failures must degrade gracefully without loss of authoritative business records.

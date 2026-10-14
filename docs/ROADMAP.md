# Delivery plan

## P0 — runnable business vertical slice (included here)
- Compose (MySQL 8.4, Redis, API) isolated from existing deployments
- Health endpoint, create/read conversation, send turn endpoint
- Auth **demo-only**; tenant scope; DB migrations
- Task state FSM demo for refund/logistics, correction/cancellation/task switching
- Idempotent request IDs and pure unit tests

## P1 — real conversation engine
- JWT/OIDC auth, RBAC and tenant-scoped queries
- Structured LLM dialogue understanding with Pydantic; deterministic fallback
- Explicit pending inputs, clarifications, task resume and cancel policies
- Per-conversation run lease + short DB transactions, event log and recovery
- Agent Runtime bounded tool loop; tool registry/ACL, timeout/retry policy
- End-to-end scenarios and integration tests against a test MySQL instance

## P2 — RAG + customer experience
- Reuse *existing* Milvus, collection versioning and tenant filters
- File pipeline + MinIO; hybrid search, rerank, evidence citations
- Frontend customer chat + operator traces + tool approval UI
- SSE streaming, reconnect using persisted event IDs (no false replay promises)
- OpenTelemetry/Langfuse integration, PII redaction and retention policies

## P3 — production hardening and benchmark
- Async document indexing / eval workers, outbox and DLQ; Celery optional
- Idempotent external order and refund providers + reconciliation/saga paths
- Load/chaos tests, migrations, backups, alerts, deployment and CI quality gates
- Public reproducible evals, golden multi-turn datasets, latency/cost dashboard

## Definition of done before public Internet exposure
- Replace demo auth; real user identity and tenant row-level checks
- Secret management, token redaction, CORS/rate limits, file scanning, input bounds
- Tool audit log, tool action approvals, idempotency and uncertain-result recovery
- Data retention/deletion, MySQL backups, security tests, observability

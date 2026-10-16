# AgentOrbis development log

This log records milestones and engineering decisions. Git commits provide
the detailed change history; issues track planned work.

## 2026-10-14 — Initial AgentOrbis foundation

- Selected the AgentDesk name (renamed to AgentOrbis on 2026-10-16) and MIT License.
- Renamed the Python package and application configuration to `agentorbis`.
- Selected MySQL 8.4 with SQLAlchemy async, asyncmy and Alembic for business state.
- Added the conversation API, JSON conversation state, request deduplication
  and a deterministic dialogue/task demo to the initial repository snapshot.
- Organized architecture decisions and the delivery roadmap under `docs/`.
- Validation: 10 dialogue tests passed; Ruff checks, Compose configuration
  validation and offline MySQL migration SQL generation passed.

The foundation has no real LLM routing, business-effect tools, authentication
adapter, RAG or frontend yet. MySQL integration still needs live validation.

## Entry format

For each meaningful milestone, record the date, problem, change, validation,
and next step. Link the corresponding issue or pull request when available.

## 2026-10-14 — Unified Docker development environment

- Integrated the supplied infrastructure starter into the existing AgentOrbis API.
- Moved Compose to the repository root; added source reload and container tests.
- Added independent Milvus/etcd/internal MinIO and document MinIO instances.
- Explicitly selected embedded Woodpecker with a compatible MinIO image.
- Added random local credentials, one-shot migration and document bucket setup.
- Separated process liveness, MySQL readiness and optional dependency diagnostics.
- Switched CI and contributor instructions to the container test workflow.
- Live MySQL validation exposed message inserts preceding their parent turn;
  an explicit flush now establishes the turn within the same transaction.
- Added an opt-in running-stack API regression alongside the offline tests.

### 2026-10-15 — Final Docker validation

- Runtime, migration, bucket initializer and development/test images built successfully.
- All 14 tests passed with the live MySQL/API regression enabled; Ruff and
  offline MySQL migration generation passed.
- MySQL, Redis, Milvus and document bucket connectivity checks returned `ok`.
- Conversation state survived recreation of the MySQL and API containers.
- Added the missing editable-install build dependency and documented Attu's
  local administrator setup at `/login`.
- The test client emits one upstream HTTPX deprecation warning; tests pass.

## 2026-10-16 — Rename to AgentOrbis

- Renamed the project brand and Python package to AgentOrbis / `agentorbis`.
- Updated imports, container entry points, and bilingual documentation.
- Preserved existing Compose/storage identifiers and Git remote for compatibility.

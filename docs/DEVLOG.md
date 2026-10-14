# AgentDesk development log

This log records milestones and engineering decisions. Git commits provide
the detailed change history; issues track planned work.

## 2026-10-14 — Initial AgentDesk foundation

- Selected the AgentDesk name and MIT License.
- Renamed the Python package and application configuration to `agentdesk`.
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

# AgentOrbis development log

**Languages:** English | [简体中文](zh/DEVLOG.md)

## 2026-10-19 — Intent recognition becomes the first project module

- Reframed the repository around the read-only intent interpreter as the first implemented AgentOrbis capability.
- Removed the earlier conversation FSM, database models, migrations, and infrastructure diagnostics from the application.
- Kept the chat demo, strict output contract, Anthropic-compatible provider adapter, and offline mocked-provider tests.
- Reduced the default Docker environment to the API container; persistence and related infrastructure return when the next modules need them.
- Moved frozen datasets and immutable evaluation runs to the root `evaluation/` directory.
- Evaluation on the current author-written synthetic development sets: 80/80 original cases and 24/24 edge cases passed after one bounded structured-output repair was added. This is not a blind or production benchmark.
- Next: deterministic dialogue policy, clarification state, and pure state reducer.

## Entry format

Record meaningful milestones, decisions, evidence, and the next development step. Historical Git commits retain the detail of earlier scaffolding work.

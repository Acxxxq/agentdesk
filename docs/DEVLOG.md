# AgentOrbis development log

**Languages:** English | [简体中文](zh/DEVLOG.md)

## 2026-10-19 — Intent recognition becomes the first project module

- Reframed the repository around the read-only intent interpreter as the first implemented AgentOrbis capability.
- Removed the earlier conversation FSM, database models, migrations, and infrastructure diagnostics from the application.
- Kept the chat demo, strict output contract, Anthropic-compatible provider adapter, and offline mocked-provider tests.
- Reduced the default Docker environment to the API container; persistence and related infrastructure return when the next modules need them.
- Moved frozen datasets and immutable evaluation runs to the root `evaluation/` directory.
- Evaluation on the current author-written synthetic development sets: 80/80 original cases and 24/24 edge cases passed after one bounded structured-output repair was added. This is not a blind or production benchmark.
- Work then moved into the dialogue policy and state reducer stage.

## 2026-10-19 — First dialogue policy and pure state reducer

- Added in-memory conversation, task, focus, and pending-slot state models.
- Added deterministic decisions for task creation, pending-slot answers, resume, correction, cancellation, and policy questions; ambiguous task targets are clarified first.
- Preserved original acts, confirmed entities, and ambiguity indexes for sequential clarification; an explicit new task can interrupt clarification.
- Added an atomic pure reducer that returns updated state and domain events without database or external tool calls.
- The policy and reducer are not connected to the chat API and have no Stage 2 evaluation yet; next, add evaluation cases before wiring the API workflow.

## 2026-10-19 — Chat workspace connected to dialogue state

- Reworked the existing intent chat page into the AgentOrbis workspace while retaining its visual style and adding live task state.
- Added `POST /api/v1/chat` to connect context construction, intent interpretation, dialogue policy, state reduction, and clear Chinese replies that do not claim external execution.
- Development sessions are stored in API process memory, serialize requests per conversation, restore recent messages after refresh, and support starting a new conversation.
- The workspace displays task slots, pending clarification, semantic interpretation, and state events. Real tools and MySQL remain unconnected.

## Entry format

Record meaningful milestones, decisions, evidence, and the next development step. Historical Git commits retain the detail of earlier scaffolding work.

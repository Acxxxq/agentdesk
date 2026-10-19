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

## 2026-10-19 — Randomized intent evaluation expansion

- Added a fixed-seed generator and 110 randomized synthetic cases spanning refunds, logistics, policy questions, ambiguous orders, and out-of-scope inputs.
- The revised dataset passed 110/110 calls against the local API using `deepseek-v4-pro`; HTTP P50/P95 were about 1.90/2.54 seconds.
- Reviewed the initial annotation rules to count explicit refund reasons and allow parameter ambiguity when an order ID is missing. No model or prompt change was made between the two randomized runs.
- The dataset is synthetic, generated from known templates, and not independently reviewed; the result is a regression check, not a generalization or production accuracy claim.

## 2026-10-19 — Intent taxonomy v1

- Defined three canonical business IDs with current API aliases, required slots, dialogue acts, and capability requirements.
- Added a read-only registry and bilingual documents distinguishing missing slots, conflicting values, task ambiguity, and unclear business goals.
- Defined local workflow abandonment separately from external application withdrawal; canonical API migration and multi-agent routing follow later.
- Registry compatibility and evaluation tests passed 21/21.

## 2026-10-19 — Canonical intent IDs and regression evaluation

- Migrated the model contract, prompt, policy, API responses, and chat UI to canonical IDs with taxonomy version `1.0`.
- Preserved explicit legacy semantic and knowledge-focus mappings; stable task types read required slots from the registry.
- Created five versioned datasets with a SHA-256 migration manifest while preserving historical data and evidence.
- Prevented order IDs from crossing business clarification boundaries; explicit new goals may suspend older clarification even when parameters are missing.
- Added fixed-category evidence repair hints with the same single-repair limit and unchanged evidence validation.
- All 62 offline tests passed. Complete model and dialogue results are in the [migration evaluation report](../evaluation/results/taxonomy-migration.md).

## Entry format

Record meaningful milestones, decisions, evidence, and the next development step. Historical Git commits retain the detail of earlier scaffolding work.

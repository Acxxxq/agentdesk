# Roadmap

**Languages:** English | [简体中文](zh/ROADMAP.md)

## Stage 1 — Intent recognition (current)

- Define strict message, action, entity, relation, and ambiguity contracts.
- Interpret topic switches, follow-up answers, corrections, multiple acts, and underspecified requests.
- Validate model output and evidence before returning it to the caller.
- Keep datasets frozen and record raw requests, responses, source snapshots, and metrics.
- Collect manually reviewed and real-world anonymized examples before making accuracy claims.

## Stage 2 — Dialogue policy and state reducer

- Decide whether an interpreted act starts, answers, resumes, corrects, or cancels a task.
- Ask a targeted clarification when intent, task target, or required parameters remain ambiguous.
- Preserve the original pending request when unrelated topics interrupt it.
- Implement a pure reducer that returns the next state and domain events without I/O.
- Evaluate safety rules for task switching, negation, alternatives, and multi-act messages.

## Stage 3 — Persistence and API workflow

- Add MySQL-backed conversations, tasks, messages, and event history after state behavior is defined.
- Keep model calls outside database transactions; use version checks and idempotency at write boundaries.
- Add authentication, tenant authorization, retention, and audit rules before deployment.

## Stage 4 — Tools and agent runtime

- Add typed, permission-scoped business tools with timeout and idempotency policies.
- Require confirmation for consequential actions and record execution outcomes.
- Add recovery for uncertain external outcomes and background work when a real use case requires it.

## Stage 5 — RAG, memory, and production evaluation

- Add document ingestion and retrieval only after the support workflow needs it.
- Separate authoritative task state from searchable memory and vector indexes.
- Expand evaluation with held-out, human-reviewed examples, regression gates, latency, and cost.

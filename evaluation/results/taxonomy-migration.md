# Intent taxonomy v1 integration and evaluation

**Languages:** English | [简体中文](taxonomy-migration.zh-CN.md)

## Delivered behavior

The model contract, prompt, policy, API responses, and chat UI now use `refund.apply`, `logistics.track`, and `policy.consult`, with `taxonomy_version: "1.0"`. Legacy semantic labels are accepted on input and serialized canonically.

Task types remain `refund` and `logistics`. The registry maps intent IDs to stable task types and required slots, and historical knowledge focus has an explicit compatibility mapping. No new executable business goals, external tools, or multi-agent routing were added.

The [migration script](../scripts/migrate_intent_taxonomy.py) creates five datasets. Its [manifest](../datasets/taxonomy_v1_migration.json) records source and target SHA-256 values. Messages, order parameters, task types, and scoring rules are unchanged; previous evidence is preserved.

## Final results

| Check | Result | Evidence |
|---|---:|---|
| Base intent and input validation | 80/80 | [Report](2026-10-19-taxonomy-intent-v4/report.zh-CN.md) |
| Edge intent cases | 24/24 | [Report](2026-10-19-taxonomy-edge-v4/report.zh-CN.md) |
| Randomized expressions | 110/110 | [Report](2026-10-19-taxonomy-random-v4/report.zh-CN.md) |
| Fixed-semantics dialogue policy | 14/14 turns, 7/7 scenarios | [Report](2026-10-19-taxonomy-dialogue-v2/report.zh-CN.md) |
| Real chat end-to-end | 24/25 turns, 9/10 scenarios | [Report](2026-10-19-taxonomy-chat-v4/report.zh-CN.md) |
| Complete offline suite | 62 passed | Mocked SDK, contract, registry, migration, and policy checks |

The 214 intent cases include 208 valid semantic inputs and 6 request-validation cases. Final intent and chat runs had no HTTP/network errors. Chat HTTP P50/P95 were approximately 1.75/2.51 seconds. Ruff, JavaScript syntax, and Compose configuration checks passed.

Final response versions and IDs were verified. Archived source snapshots retain the exact tested bytes and SHA-256 hashes. Regular source files follow repository LF normalization; use the archived snapshots for byte-exact replay. The configured model was `deepseek-v4-pro`. Evaluation used a temporary local API on `127.0.0.1:18001`, stopped afterward; no new container was needed.

## Retained failure

For a request to book a train ticket, the existing chat annotation requires intent ambiguity and clarification. The current explicit out-of-scope rule returns no business acts or ambiguities and provides a capability fallback, without creating a task. Task-state assertions pass, while clarification and reply assertions fail. The strict score remains 24/25.

This behavior-versus-annotation difference needs an explicit decision and a new dataset version. The original label was not edited or counted as passed. The current contract still does not separately classify social and out-of-scope messages.

## Recorded iterations

All rounds used identical migrated datasets and labels. Each HTTP case was sent once per round; failures were preserved. The interpreter permits at most one internal structured-output repair.

| Run | Base | Edge | Randomized | Chat turns |
|---|---:|---:|---:|---:|
| v1: canonical ID integration | [76/80](2026-10-19-taxonomy-intent-v1/report.zh-CN.md) | [24/24](2026-10-19-taxonomy-edge-v1/report.zh-CN.md) | [110/110](2026-10-19-taxonomy-random-v1/report.zh-CN.md) | [24/25](2026-10-19-taxonomy-chat-v1/report.zh-CN.md) |
| v2: ambiguity and negation boundaries | [79/80](2026-10-19-taxonomy-intent-v2/report.zh-CN.md) | [23/24](2026-10-19-taxonomy-edge-v2/report.zh-CN.md) | [109/110](2026-10-19-taxonomy-random-v2/report.zh-CN.md) | [22/25](2026-10-19-taxonomy-chat-v2/report.zh-CN.md) |
| v3: new-goal priority and cross-business protection | [77/80](2026-10-19-taxonomy-intent-v3/report.zh-CN.md) | [20/24](2026-10-19-taxonomy-edge-v3/report.zh-CN.md) | [107/110](2026-10-19-taxonomy-random-v3/report.zh-CN.md) | [23/25](2026-10-19-taxonomy-chat-v3/report.zh-CN.md) |
| v4: evidence repair and out-of-scope rules | [80/80](2026-10-19-taxonomy-intent-v4/report.zh-CN.md) | [24/24](2026-10-19-taxonomy-edge-v4/report.zh-CN.md) | [110/110](2026-10-19-taxonomy-random-v4/report.zh-CN.md) | [24/25](2026-10-19-taxonomy-chat-v4/report.zh-CN.md) |

General prompt rules address lost acts under task ambiguity, negated mentions, and guessing logistics from an order ID. Policy validates candidate tasks against conversation state rather than selecting an arbitrary target.

Policy now suspends old clarification for an explicit new goal even when the new goal lacks parameters, and prevents a refund order ID from filling an old logistics question. Regression tests cover cross-business protection, normal same-business completion, and global-ambiguity blocking.

Parallel-order diagnostics found reconstructed evidence spans that were not contiguous input text. Multiple acts may now cite the same full original sentence. A fixed validation category guides the single repair call; evidence validation and retry limits were not relaxed, and raw provider errors are not returned to users.

## Limits

These are synthetic development regression datasets, partly used to refine the prompt. They are not independent held-out benchmarks. Scores measure the complete interpreter including one possible repair, not first-call or production accuracy. Diagnostic calls do not replace failed evaluation records.

MySQL, real business execution, authentication, and multi-agent orchestration are outside this evaluation. Missing-slot and ambiguity state representations still need continued standardization. Planned catalog entries and capability declarations are not implemented business operations.

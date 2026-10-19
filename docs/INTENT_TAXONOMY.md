# Intent taxonomy v1

**Languages:** English | [简体中文](zh/INTENT_TAXONOMY.md)

Catalog version: `1.0`. Definitions live in [`intent_registry.py`](../backend/src/agentorbis/domain/intent_registry.py).

## Scope and implementation status

The registry defines business goals, dialogue acts, required slots, aliases, and capability requirements. It provides metadata and lookup; it does not execute routing, tools, or external operations.

The API, model output contract, prompt, policy, and UI now use canonical business IDs. Results include `taxonomy_version: "1.0"`. Legacy semantic inputs accept `refund`, `logistics`, and `policy_qa` aliases and serialize canonical IDs. Task types remain `refund` and `logistics`; knowledge focus retains kind `policy_qa` with intent `policy.consult`. These state fields are distinct from business intent. MySQL, external tools, and multi-agent routing remain future work.

## Classification layers

| Layer | Responsibility | Example |
|---|---|---|
| Business intent | User's business goal | `refund.apply` |
| Dialogue act | How the user advances a goal | `answer_pending`, `correct` |
| Entities and target | Explicit parameters and referenced task | Order A100, existing refund task |
| Dialogue policy | Resolve targets, collect slots, clarify, or plan operations | Fill a refund task's order ID |
| Capability orchestration | Choose an authorized tool or Agent | `logistics.tracking` |

Each message can contain multiple acts with separate evidence, targets, parameters, and ambiguities. Recognizing an intent does not authorize external execution.

## Supported business catalog

| Canonical API ID | Accepted legacy alias | Goal | Required task slots | Capability requirement |
|---|---|---|---|---|
| `refund.apply` | `refund` | Collect a refund application | `order_id`, `reason` | `refund.application` |
| `logistics.track` | `logistics` | Track an order | `order_id` | `logistics.tracking` |
| `policy.consult` | `policy_qa` | Ask about commerce after-sales rules | No fixed task slots | `policy.retrieval` |

Refund requirements match the existing implementation. A `ready` task means its slots are complete, not that a refund was submitted. Capabilities declare future requirements and do not imply available tools.

Policy retrieval should retain the full question. Topics such as `refund_timeline`, `return_policy`, and `shipping_fee` may be added as optional metadata; individual FAQs do not require separate intents. The current entity contract has no topic field.

## Dialogue act catalog

Existing IDs are retained to avoid changing contracts solely for naming preferences.

| ID | Meaning | Boundary |
|---|---|---|
| `start_task` | Introduce a new business goal | Explicit new business takes precedence over an old pending question |
| `answer_pending` | Supply information or answer clarification | The target or selected candidate must be resolvable |
| `correct` | Correct supplied information | Extract only the new value from the current message |
| `resume` | Continue a prior task or clarification | Clarify multiple plausible targets |
| `cancel` | Request abandonment of the local workflow | Does not withdraw a submitted real-world application |
| `ask_question` | Ask about rules or policy | Does not overwrite the active task |
| `confirm` | Confirm a specific proposal or operation | Requires an explicit pending confirmation target |
| `reject` | Reject a candidate or proposal | Negated mentions do not automatically cancel another task |
| `other` | No specific act classification | Cannot authorize external business execution |

These are semantic definitions, not a claim that confirmation authorization, candidate selection, or external execution policies are complete. Candidate selection can currently use `answer_pending` with an explicit target. Task switching is derived from acts and state; no new `select_option` or `switch_task` label is required yet.

## Missing information and ambiguity

| Situation | Example | Target behavior |
|---|---|---|
| Missing required slot | I want a refund | Retain the refund goal; collect order ID and reason in policy |
| Mutually exclusive values | Track A100 or B200; I am unsure | One logistics act; no confirmed order ID; explicit parameter ambiguity |
| Unclear task target | Two refunds exist; continue that refund | Task ambiguity; no arbitrary task selection |
| Unclear business goal | Look at order A100 | Intent ambiguity; do not assume logistics |

Missing information does not make the business goal unclear. During migration, both a missing-slot act and an act with `parameter` ambiguity are accepted; policy must collect the same information safely. Conflicting candidates must remain explicit ambiguities.

An explicit new business goal can suspend an earlier clarification even when the new goal also lacks parameters. Its order ID cannot answer another business goal's pending question. For task ambiguity, policy can list existing conversation tasks even if the model omitted candidate IDs; it asks the user rather than choosing a target.

`unknown` is a compatibility fallback, not a registered executable intent. Unclear goals, out-of-scope requests, social messages, and invalid model output require different treatment; invalid output remains an API error. The current contract does not fully distinguish social and out-of-scope input. Future classification must preserve mixed messages where some acts are clear and others ambiguous.

## Abandonment versus business withdrawal

Before any external operation, “never mind the refund” can end local data collection. After submission, withdrawal is a separate goal, `refund.withdraw`, requiring status, permission, and external outcome checks. Uncertain external outcomes must be checked; changing local status is insufficient evidence of withdrawal.

There is currently no real refund service or withdrawal operation. Submission phases and withdrawal policy must be implemented before external tools are connected.

## Multi-agent association

The processing order is interpretation → dialogue policy → task and capability plan → orchestrator → tool or Agent.

The intent registry declares capabilities rather than a fixed agent ID. The orchestrator considers permissions, task state, and capability availability. Policy consultation may use a retrieval service directly; a refund task may request technical diagnosis when required. Adding an Agent does not automatically create an intent category.

## Planned catalog

The following IDs are planning entries and are rejected by the supported-intent resolver:

`refund.status`, `refund.withdraw`, `order.detail`, `order.cancel`, `order.change_address`, `after_sales.exchange`, `after_sales.repair`, `support.complaint`, `support.handoff`.

A new intent requires a materially different goal, workflow, parameters, or permission boundary, plus positive, negative, confusion, and multi-turn examples. Synonyms, individual FAQs, and Agent names are insufficient reasons to add an intent.

## Migration and acceptance

1. Definitions, aliases, and boundaries are registered. Required task slots are read from the registry; tests check agreement with semantic enums.
2. Model output, policy input, API documentation, and UI now use canonical IDs. Explicit alias normalization restores legacy acts and knowledge focus; task types remain stable.
3. Five canonical-label datasets and a source/target SHA-256 manifest are generated. Migration changes intent fields without changing messages, parameters, or scoring rules. Older evidence is preserved. Missing-slot and conflicting-candidate evaluation still needs expansion; nullable intents require coordinated target-resolution changes.
4. Evaluate cancellation during collection, before submission, after submission, and with uncertain outcomes before connecting external tools.
5. Add routing tests for canonical IDs, permissions, unavailable capabilities, and task references across Agents.

The migration script is `evaluation/scripts/migrate_intent_taxonomy.py`; its manifest is `evaluation/datasets/taxonomy_v1_migration.json`. Historical randomized v2 results measure the earlier API; canonical-ID regression runs are archived separately. Neither validates planned business goals or future Agent routing.

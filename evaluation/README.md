# AgentOrbis evaluation archive

**Languages:** English | [简体中文](README.zh-CN.md)

This directory contains versioned synthetic datasets and immutable HTTP evaluation runs. Keeping it at the repository root makes evaluation evidence independent of the application package and easy to review alongside code changes.

## Current datasets

- [`datasets/intent_v1.jsonl`](datasets/intent_v1.jsonl): 80 fixed cases covering single intents, policy questions, topic switches, pending answers, multiple acts, negation, corrections, cancel/resume, ambiguity, history context, out-of-scope input, prompt injection in data, and request validation.
- [`datasets/intent_edge_v1.jsonl`](datasets/intent_edge_v1.jsonl): 24 frozen challenge cases for underspecified requests, mutually exclusive order candidates, parallel orders, unique pending context, explicit topic switches, and negated mentions.
- [`datasets/dialogue_policy_v1.jsonl`](datasets/dialogue_policy_v1.jsonl): 7 multi-turn policy scenarios for concurrent cancellation and task start, cross-topic completion of older task slots, isolated clarification and resumption, global ambiguity, conditional actions, and unresolved task targets.
- [`datasets/chat_e2e_v1.jsonl`](datasets/chat_e2e_v1.jsonl): 10 end-to-end multi-turn scenarios against the real chat API, checking model understanding, policy decisions, domain events, task state, pending slots, and replies.

These datasets were authored for development and have not been independently human-reviewed. They include cases used while shaping the system prompt, so they are regression data rather than blind generalization benchmarks.

## Recorded results

The [optimization comparison](results/optimization-comparison.zh-CN.md) summarizes all runs. Each run directory preserves a dataset copy, request/response records, summary, report, model and source hashes, and the source files needed to interpret that version.

| Run | Cases passed | Purpose |
|---|---:|---|
| [baseline v1](results/2026-10-19-baseline-v1/report.zh-CN.md) | 74/80 | Initial measurement |
| [edge before optimization](results/2026-10-19-edge-before/report.zh-CN.md) | 20/24 | Frozen challenge set before prompt changes |
| [optimized v2](results/2026-10-19-optimized-v2/report.zh-CN.md) | 79/80 | Semantic prompt refinements |
| [edge after v2](results/2026-10-19-edge-after-v2/report.zh-CN.md) | 24/24 | Challenge regression after prompt refinements |
| [optimized v3](results/2026-10-19-optimized-v3/report.zh-CN.md) | 80/80 | One bounded repair for invalid structured output |
| [edge after v3](results/2026-10-19-edge-after-v3/report.zh-CN.md) | 24/24 | Final challenge regression |
| [dialogue policy v1](results/2026-10-19-dialogue-policy-v1/report.zh-CN.md) | 14/14 turns | Policy, reduction, and reply regression with fixed semantic inputs |
| [chat end-to-end v4](results/2026-10-19-chat-e2e-v4/report.zh-CN.md) | 25/25 turns | Real chat API, model understanding, and state transitions |

The final result measures the full interpreter, including up to one structured-output repair call. It is not first-call accuracy, production accuracy, or a guarantee for new user messages.

The dialogue policy run fixes interpreter outputs and makes no model calls. It evaluates task selection, clarification storage, event ordering, state transitions, and replies. Natural-language interpretation remains covered by the intent datasets above.

The chat end-to-end evaluator sends each scenario's turns sequentially to `/api/v1/chat`, reusing one conversation ID within a scenario and creating a fresh conversation between scenarios. It checks the full path from natural-language interpretation through state transition. Model output is stochastic, so preserve per-turn records; failed turns are not retried or removed from the denominator. The synthetic development set has not been independently reviewed and does not establish production accuracy.

Run it from the local virtual environment:

```powershell
cd backend
$env:PYTHONPATH = "src"
..\.venv-intent\Scripts\python.exe -m agentorbis.evaluation.dialogue --dataset ..\evaluation\datasets\dialogue_policy_v1.jsonl --output ..\evaluation\results\new-dialogue-run
```

## Reproduce a run in Docker

Start the API with a provider key in the ignored root `.env`. Then run the evaluator profile, which mounts this repository so new evidence is written here:

```bash
docker compose up -d --build --wait api
docker compose --profile evaluation run --build --rm evaluator --dataset evaluation/datasets/intent_v1.jsonl --output evaluation/results/new-run-id --model deepseek-v4-pro --endpoint http://api:8000/api/v1/interpret --concurrency 2

# Multi-turn chat end-to-end evaluation; makes model calls for each turn
docker compose --profile evaluation run --build --rm chat-evaluator --dataset evaluation/datasets/chat_e2e_v1.jsonl --output evaluation/results/new-chat-e2e-run --model deepseek-v4-pro --endpoint http://api:8000/api/v1/chat
```

The recorded end-to-end run can be repeated locally with:

```powershell
# Start the API from the repository root so it reads the root .env file
$env:PYTHONPATH = "backend/src"
.\.venv-intent\Scripts\python.exe -m uvicorn agentorbis.main:app --host 127.0.0.1 --port 18001
```

In a second terminal:

```powershell
$env:PYTHONPATH = "backend/src"
.\.venv-intent\Scripts\python.exe -m agentorbis.evaluation.chat --dataset evaluation/datasets/chat_e2e_v1.jsonl --output evaluation/results/2026-10-19-chat-e2e-v4 --model deepseek-v4-pro --endpoint http://127.0.0.1:18001/api/v1/chat --concurrency 3
```

Use a new output directory for every run. The evaluator refuses to overwrite an existing one. It makes one HTTP request per case without retrying; malformed model output may still trigger the interpreter's documented single repair call. The `model` label is recorded for audit, while the API uses the model configured in its environment, so keep the label and running service configuration consistent.

## Add data safely

The generators create the initial files only when the destination does not exist. For changed labels or new challenge cases, create a new versioned dataset file and keep earlier data and scores unchanged. Avoid real customer conversations unless they have been approved and de-identified for this purpose.

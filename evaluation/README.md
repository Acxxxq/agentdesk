# AgentOrbis evaluation archive

**Languages:** English | [简体中文](README.zh-CN.md)

This directory contains versioned synthetic datasets and immutable HTTP evaluation runs. Keeping it at the repository root makes evaluation evidence independent of the application package and easy to review alongside code changes.

## Current datasets

- [`datasets/intent_v1.jsonl`](datasets/intent_v1.jsonl): 80 fixed cases covering single intents, policy questions, topic switches, pending answers, multiple acts, negation, corrections, cancel/resume, ambiguity, history context, out-of-scope input, prompt injection in data, and request validation.
- [`datasets/intent_edge_v1.jsonl`](datasets/intent_edge_v1.jsonl): 24 frozen challenge cases for underspecified requests, mutually exclusive order candidates, parallel orders, unique pending context, explicit topic switches, and negated mentions.

Both sets were authored for development and have not been independently human-reviewed. They include cases used while shaping the system prompt, so they are regression data rather than blind generalization benchmarks.

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

The final result measures the full interpreter, including up to one structured-output repair call. It is not first-call accuracy, production accuracy, or a guarantee for new user messages.

## Reproduce a run in Docker

Start the API with a provider key in the ignored root `.env`. Then run the evaluator profile, which mounts this repository so new evidence is written here:

```bash
docker compose up -d --build --wait api
docker compose --profile evaluation run --build --rm evaluator --dataset evaluation/datasets/intent_v1.jsonl --output evaluation/results/new-run-id --model deepseek-v4-pro --endpoint http://api:8000/api/v1/interpret --concurrency 2
```

Use a new output directory for every run. The evaluator refuses to overwrite an existing one. It makes one HTTP request per case without retrying; malformed model output may still trigger the interpreter's documented single repair call. The `model` label is recorded for audit, while the API uses the model configured in its environment, so keep the label and running service configuration consistent.

## Add data safely

The generators create the initial files only when the destination does not exist. For changed labels or new challenge cases, create a new versioned dataset file and keep earlier data and scores unchanged. Avoid real customer conversations unless they have been approved and de-identified for this purpose.

# Intent recognition module

**Languages:** English | [简体中文](zh/INTENT_DEMO.md)

This is the first implemented AgentOrbis module. It reads the current message and optional caller-supplied context, then returns structured business acts, candidate entities, relations, and ambiguities. It has no write access to task state and runs no business tools.

## Run

Create `.env` from the template, set `ANTHROPIC_API_KEY`, and start the API in Docker:

```bash
docker run --rm --mount "type=bind,source=${PWD},target=/workspace" -w /workspace python:3.12-slim python scripts/generate_env.py
docker compose up -d --build --wait api
```

Open [the chat page](http://127.0.0.1:18000/demo), or call `POST /api/v1/interpret` in [API docs](http://127.0.0.1:18000/docs):

```json
{"message": "先查 A1001 物流，再申请 A2002 退款"}
```

Example requests with context are in `backend/examples/intent/`. From inside the container they can be submitted with:

```bash
docker compose exec api python -m agentorbis.intent_demo --request examples/intent/topic_switch.json
```

The local demo route is available only when `APP_ENV=development`. The caller supplies context; the interpreter does not load or authorize real tasks.

## Contract and limits

Input accepts a current message, up to ten recent messages, conversation pointers, and up to twenty task summaries. Output contains zero or more acts, ambiguities, and relationships between acts. Supported intents are `refund`, `logistics`, `policy_qa`, and `unknown`. Entity candidates are limited to `order_id` and `reason` and must appear literally in the current message. Structural validation does not guarantee semantic correctness.

The provider adapter uses `anthropic.AsyncAnthropic` and a named data-only tool schema. It does not execute tools. SDK retries are disabled. Invalid structured output allows one bounded repair call; timeout and provider errors are not retried. The API returns sanitized error codes.

## Evaluation and tests

The frozen datasets, scoring implementation, all run records, and comparison report are in [`evaluation/`](../evaluation/README.md). Current results are 80/80 on the original synthetic set and 24/24 on the edge set, with one possible structure repair. These are development regression results, not production accuracy estimates.

Run mocked-provider unit tests and lint in Docker without a model key:

```bash
docker compose --profile test run --build --rm tests
```

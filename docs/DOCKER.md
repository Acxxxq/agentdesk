# Docker development

**Languages:** English | [简体中文](zh/DOCKER.md)

The intent recognition stage needs one application container. MySQL, Redis, and Milvus will be introduced when later modules require them.

## First setup

Create the local environment file once:

```bash
docker run --rm --mount "type=bind,source=${PWD},target=/workspace" -w /workspace python:3.12-slim python scripts/generate_env.py
```

Set `ANTHROPIC_API_KEY` in `.env`. The template uses DeepSeek's Anthropic-compatible API by default; change the model and base URL there if needed.

## Start and inspect

```bash
docker compose config --quiet
docker compose up -d --build --wait api
docker compose ps
docker compose logs -f api
```

Open `http://127.0.0.1:18000/demo` for the chat page and `http://127.0.0.1:18000/docs` for the API schema. The API binds to localhost by default.

## Offline checks

The test profile runs unit and mocked-provider tests without a model key:

```bash
docker compose --profile test run --build --rm tests
```

This project stage does not mount infrastructure data volumes. If an older checkout created MySQL, Redis, or Milvus volumes, this Compose file does not reference or remove them.

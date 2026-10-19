# Intent recognition service

**Languages:** English | [简体中文](README.zh-CN.md)

The backend exposes `POST /api/v1/interpret` and serves the Chinese chat demo at `/demo`. It uses a strict Pydantic contract and the Anthropic Python SDK. The endpoint interprets a message and optional read-only context; it does not persist or execute business tasks.

Run it through the repository root Docker Compose configuration. See the [intent guide](../docs/INTENT_DEMO.md) and [evaluation records](../evaluation/README.md).

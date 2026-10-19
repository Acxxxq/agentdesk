# Intent recognition service

**Languages:** English | [简体中文](README.zh-CN.md)

The backend exposes `POST /api/v1/interpret` for semantic parsing and `POST /api/v1/chat` for the full chat workflow. `/demo` is the AgentOrbis front-end workspace, connecting interpretation, dialogue policy, and the pure state reducer while displaying tasks and state events. Sessions currently live in API process memory and are cleared on restart. MySQL persistence and real refund, logistics, or policy services are not connected yet.

Run it through the repository root Docker Compose configuration. See the [intent guide](../docs/INTENT_DEMO.md) and [evaluation records](../evaluation/README.md).

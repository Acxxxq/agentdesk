# AgentOrbis

**Enterprise AI Agent Platform**

Build reliable agents for real-world business workflows.

**Languages:** English | [简体中文](README.zh-CN.md)

AgentOrbis starts with a focused, testable intent recognition module. It reads the current message with optional read-only conversation context, identifies one or more business acts, extracts evidence-backed entities, and reports ambiguity. It does not execute tasks or change business state.

## First module: intent recognition

- FastAPI endpoint: `POST /api/v1/interpret`
- Anthropic Python SDK with an Anthropic-compatible endpoint such as DeepSeek
- Strict Pydantic output contracts and evidence checks
- Topic and intent switching, multiple acts, task references, and ambiguity handling
- Local Chinese chat page at `/demo`
- Fixed synthetic datasets and reproducible evaluation records in [`evaluation/`](evaluation/README.md)

The current evaluation is a development set written by the project author. Its scores guide iteration; they are not production accuracy claims or a blind benchmark.

## Run with Docker

Install Git and Docker Desktop or Docker Engine, then run:

```bash
git clone https://github.com/Acxxxq/agentdesk.git agentorbis
cd agentorbis
docker run --rm --mount "type=bind,source=${PWD},target=/workspace" -w /workspace python:3.12-slim python scripts/generate_env.py
```

Add your provider key to the ignored `.env` file, then start the API:

```bash
docker compose up -d --build --wait api
```

Open [the chat demo](http://127.0.0.1:18000/demo) or [the API docs](http://127.0.0.1:18000/docs). The default port is `18000`; set `API_PORT` in `.env` to change it.

For offline tests and lint in a container:

```bash
docker compose --profile test run --build --rm tests
```

See the [Docker guide](docs/DOCKER.md) and [intent demo guide](docs/INTENT_DEMO.md) for details.

## Project direction

The intent interpreter is the first real project module. The roadmap builds the next layer as a deterministic dialogue policy and state reducer, then persistence and tool execution. The broader target architecture is documented in [the platform plan](docs/PLATFORM_PLAN.md).

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Development log](docs/DEVLOG.md)
- [Code style and Chinese comments](docs/CODE_STYLE.md)
- [Evaluation datasets and results](evaluation/README.md)
- [Contributing](CONTRIBUTING.md)

## License

[MIT](LICENSE) © 2026 Acxxxq.

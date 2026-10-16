# Contributing to AgentOrbis

**Languages:** English | [简体中文](CONTRIBUTING.zh-CN.md)

Start with the README and [roadmap](docs/ROADMAP.md). Open an issue describing
the problem and expected behavior before proposing a large architectural change.
Follow the [code style](docs/CODE_STYLE.md), including Chinese comments and
docstrings for new or modified code.

## Development environment

Use Git and Docker. Generate the root `.env` as described in the README, then:

```bash
docker compose -f compose.yaml -f compose.dev.yaml up -d --build --wait
docker compose --profile test build tests
docker compose --profile test run --rm --no-deps tests
```

Changes under `backend/src/` reload automatically. Dependency changes require
rebuilding the images. When tests change, rebuild the test image as well.
The test command runs pytest, Ruff and offline MySQL migration SQL generation.
It does not require model credentials or running databases.

Keep real credentials and customer data out of commits. `.env.example` contains
placeholders; the generated root `.env` is ignored by Git and excluded from
Docker build contexts.

## Changes and development records

- Keep each commit focused on a change that can be explained and reviewed.
- Describe the problem, resulting behavior and validation in pull requests.
- Document architectural decisions in `docs/ADR-*.md`.
- Add meaningful milestones and lessons to `docs/DEVLOG.md`.
- Run the container checks before submitting a pull request.

Contributions are licensed under the project's MIT License.

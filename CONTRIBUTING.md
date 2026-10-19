# Contributing to AgentOrbis

**Languages:** English | [简体中文](CONTRIBUTING.zh-CN.md)

Start with the README, [roadmap](docs/ROADMAP.md), and [code style](docs/CODE_STYLE.md). Keep changes focused and include the reasoning behind non-obvious behavior. New and modified Python comments and public docstrings should be in Chinese, with clear English identifiers.

Run the offline checks in Docker:

```bash
docker compose --profile test run --build --rm tests
```

Provider calls in the test suite use a mocked HTTP transport and do not need credentials. Keep `.env`, API keys, and real customer data out of commits. Add new model evaluation examples to a new frozen dataset version; do not edit old labels or run results.

Record meaningful decisions in the bilingual architecture or roadmap docs. Describe the changed behavior and validation in pull requests. Contributions are licensed under the MIT License.

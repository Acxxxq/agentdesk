# Contributing to AgentDesk

AgentDesk is under active development. Start with the README and
[roadmap](docs/ROADMAP.md). Open an issue describing the problem and expected
behavior before proposing a large architectural change.

## Local development

Use Python 3.12 or 3.13. From `backend/`:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
```

Domain tests run without MySQL or model credentials. To run the API, follow
the Docker Compose instructions in the README. Compose credentials are local
development examples; keep real credentials and customer data out of commits.

## Changes and development records

- Keep each commit focused on a change that can be explained and reviewed.
- Describe the problem, resulting behavior and validation in pull requests.
- Document architectural decisions in `docs/ADR-*.md`.
- Add meaningful milestones and lessons to `docs/DEVLOG.md`.
- Run the existing tests and lint checks before submitting a pull request.

Contributions are licensed under the project's MIT License.

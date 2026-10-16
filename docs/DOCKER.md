# AgentOrbis Docker environment

## Services and ports

Host ports bind to `127.0.0.1`. Container traffic uses service names and internal ports.

| Service | Role | Host port |
|---|---|---|
| api | Existing FastAPI conversation API | 18000 |
| mysql | Business state, MySQL 8.4 | 53306 |
| redis | Password-protected Redis 7.4 with AOF | 56379 |
| milvus | Milvus 2.6.24, embedded Woodpecker | 29530 / Web UI 29091 |
| etcd | Milvus metadata | Internal only |
| milvus-minio | Milvus internal objects and WAL | Internal only |
| document-minio | Application documents | S3 19000 / console 19001 |
| migrate | Alembic migration, exits on success | None |
| bucket-init | Creates private `agentdesk-documents` bucket, exits on success | None |
| tests | Offline tests and lint, `test` profile | None |
| attu | Optional Milvus administration, `admin` profile | 13000 |

Worker and frontend containers will be introduced with their implementations.

## Bootstrap

From the repository root, in PowerShell or a Linux/macOS shell:

```bash
docker run --rm --mount "type=bind,source=${PWD},target=/workspace" -w /workspace python:3.12-slim python scripts/generate_env.py
docker compose config --quiet
docker compose up -d --build --wait
docker compose ps -a
```

MySQL and MinIO initialize credentials on their first start. Keep `.env` with
the corresponding volumes. Changing a password in `.env` alone does not rotate
an existing MySQL account. The generator refuses to overwrite an existing file.
Root `.env` is the Compose configuration source; application settings are passed
through container environment variables. MySQL timestamps use UTC.
Generated passwords are URL-safe hex; manually chosen passwords need appropriate
URL encoding when constructing database and Redis connection URLs.

## Development and tests

```bash
docker compose -f compose.yaml -f compose.dev.yaml up -d --build --wait
docker compose logs -f api
docker compose --profile test build tests
docker compose --profile test run --rm --no-deps tests
```

The development API uses an editable install and mounts source into `/app/src`.
Polling enables reload on Windows Docker Desktop mounts. Dependency changes
require rebuilding images. The test image contains test files; rebuild after
test changes. The default runtime image uses a packaged install with no mounts.

With a running development stack, enable the real MySQL/API regression:

```bash
docker compose --profile test run --rm --no-deps -e AGENTORBIS_INTEGRATION_URL=http://api:8000 tests
```

This creates isolated demo conversations and checks turn writes, replay,
conflicting request IDs and ownership. It is skipped in the default offline run.
Use Docker Compose 2.20 or newer for optional initialization dependencies.

## Health and administration

- `/health` and `/health/live`: process responds; no dependency calls.
- `/health/ready`: MySQL is accessible; returns 503 on failure.
- `/health/dependencies`: concurrent bounded MySQL, Redis, Milvus and document
  bucket checks. Optional failures do not change core readiness.

Diagnostics return exception types, never credentials or connection strings.
RAG infrastructure readiness does not mean a RAG pipeline is implemented.
`migrate` and `bucket-init` showing `Exited (0)` is expected; nonzero means failure.

```bash
docker compose --profile admin up -d attu
```

Open Attu at `http://127.0.0.1:13000/login` and create the first administrator
through its setup flow. The preconfigured connection is `milvus:19530`. The document
MinIO console is `http://127.0.0.1:19001`; use `DOCUMENT_MINIO_USER` and
`DOCUMENT_MINIO_PASSWORD` from `.env`.

## Persistence and isolation

Named volumes belong to the `agentdesk` project. There are no fixed container
names, shared external networks or mounts of old Milvus data directories.
Existing EchoMind and Milvus services remain separate. Reusing an image does
not reuse another instance's data.

Woodpecker explicitly uses MinIO. The MinIO images are pinned to
`milvusdb/minio:RELEASE.2024-12-18T13-15-44Z`, matching the conditional-write
requirement in the [Milvus guide](https://milvus.io/docs/v2.6.x/use-woodpecker.md).
The two MinIO instances have independent credentials. Document credentials are
local administration credentials; use scoped service credentials in production.

```bash
docker compose stop
docker compose start
```

Stopping containers preserves data. Avoid `down -v` unless deliberately deleting
this project's data. Old Milvus data migration needs a separate backup/import
plan; copying one volume or changing MQ settings is not a migration procedure.

## Troubleshooting

```bash
docker compose ps -a
docker compose logs --tail=100 mysql migrate bucket-init api milvus
```

Change occupied host ports in root `.env` and recreate the affected service.
Review Docker Desktop memory allocation when running two Milvus instances.
The starter's `infra/compose.yaml` has moved to root `compose.yaml`.
This stack is for local development; the API still requires real authentication
and tenant authorization before Internet deployment.

## Rename compatibility

The project is now AgentOrbis. The Compose project name (`agentdesk`), existing storage buckets and local credentials retain their previous identifiers to preserve data access. The Python package is `agentorbis`; integration tests use `AGENTORBIS_INTEGRATION_URL`. The Git remote and workspace directory retain their existing paths until migrated separately.

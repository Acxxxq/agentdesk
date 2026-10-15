# Backend foundation

The API uses MySQL 8.4 migrations (`mysql+asyncmy`). Run development and tests
through the root Compose files; see [Docker guide](../docs/DOCKER.md).
Domain tests run without a database. `X-Demo-User` is a local-only development
identity substitute; all routes fail closed in production mode pending JWT/OIDC integration.

Do not deploy this scaffold publicly or use it to perform real refund operations.

"""Bounded dependency diagnostics; never return connection strings or credentials."""

import asyncio
from collections.abc import Awaitable, Callable
from uuid import uuid4

from sqlalchemy import text

from agentdesk.core.settings import get_settings
from agentdesk.infrastructure.db import engine


async def probe_mysql() -> None:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def probe_redis() -> None:
    from redis.asyncio import Redis

    client = Redis.from_url(
        get_settings().redis_url, socket_connect_timeout=2, socket_timeout=2,
    )
    try:
        if not await client.ping():
            raise RuntimeError("Redis ping failed")
    finally:
        await client.aclose()


def _milvus_check() -> None:
    from pymilvus import connections, utility

    alias = f"health-{uuid4()}"
    try:
        connections.connect(alias=alias, uri=get_settings().milvus_uri, timeout=3)
        utility.get_server_version(using=alias, timeout=3)
    finally:
        connections.disconnect(alias)


async def probe_milvus() -> None:
    await asyncio.to_thread(_milvus_check)


def _objectstore_check() -> None:
    from agentdesk.infrastructure.storage import storage_client

    client, transport = storage_client()
    try:
        if not client.bucket_exists(get_settings().objectstore_bucket):
            raise RuntimeError("Document bucket is missing")
    finally:
        transport.clear()


async def probe_objectstore() -> None:
    await asyncio.to_thread(_objectstore_check)


async def report(probes: dict[str, Callable[[], Awaitable[None]]]) -> dict:
    async def check(name: str, probe: Callable[[], Awaitable[None]]) -> tuple[str, str]:
        try:
            await asyncio.wait_for(probe(), timeout=4)
            return name, "ok"
        except Exception as exc:
            return name, f"error: {type(exc).__name__}"

    checks = dict(await asyncio.gather(*(check(name, probe) for name, probe in probes.items())))
    return {"status": "ok" if all(value == "ok" for value in checks.values()) else "degraded", "checks": checks}

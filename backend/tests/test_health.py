from fastapi.testclient import TestClient

from agentorbis.infrastructure import health
from agentorbis.main import app


async def ok():
    pass


async def unavailable():
    raise RuntimeError("sensitive connection details must not appear in responses")


def test_liveness_does_not_require_database():
    with TestClient(app) as client:
        assert client.get("/health/live").status_code == 200


def test_readiness_requires_mysql(monkeypatch):
    monkeypatch.setattr(health, "probe_mysql", unavailable)
    with TestClient(app) as client:
        response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["checks"] == {"mysql": "error: RuntimeError"}
    assert "sensitive" not in response.text


def test_optional_dependency_failure_does_not_block_conversation_readiness(monkeypatch):
    monkeypatch.setattr(health, "probe_mysql", ok)
    monkeypatch.setattr(health, "probe_redis", ok)
    monkeypatch.setattr(health, "probe_milvus", unavailable)
    monkeypatch.setattr(health, "probe_objectstore", ok)
    with TestClient(app) as client:
        assert client.get("/health/ready").status_code == 200
        response = client.get("/health/dependencies")
    assert response.status_code == 503
    assert response.json()["checks"]["milvus"] == "error: RuntimeError"

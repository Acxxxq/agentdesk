"""Opt-in regression against a running Docker API and its real MySQL instance."""

import os
from uuid import uuid4

import httpx
import pytest


@pytest.mark.skipif(
    not os.environ.get("AGENTDESK_INTEGRATION_URL"),
    reason="Set AGENTDESK_INTEGRATION_URL to run against a development stack",
)
def test_mysql_conversation_turns_replay_and_ownership():
    actor = f"integration-{uuid4()}"
    with httpx.Client(
        base_url=os.environ["AGENTDESK_INTEGRATION_URL"],
        headers={"X-Demo-User": actor}, timeout=10,
    ) as client:
        created = client.post("/api/v1/conversations", json={})
        assert created.status_code == 200, created.text
        path = f"/api/v1/conversations/{created.json()['id']}"
        started = client.post(f"{path}/turns", json={"request_id": "one", "message": "我要退款"})
        assert started.status_code == 200, started.text
        assert started.json()["action"] == "START_TASK"
        filled = client.post(f"{path}/turns", json={"request_id": "two", "message": "A1001"})
        assert filled.status_code == 200, filled.text
        assert filled.json()["action"] == "CONTINUE_TASK"
        replay = client.post(f"{path}/turns", json={"request_id": "two", "message": "A1001"})
        assert replay.status_code == 200, replay.text
        assert replay.json()["replayed"] is True
        conflict = client.post(f"{path}/turns", json={"request_id": "two", "message": "A2002"})
        assert conflict.status_code == 409
        stored = client.get(path).json()
        assert stored["version"] == 2
        assert stored["state"]["tasks"][stored["state"]["active_task_id"]]["slots"]["order_id"] == "A1001"
        assert client.get(path, headers={"X-Demo-User": f"other-{actor}"}).status_code == 404

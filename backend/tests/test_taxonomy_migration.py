"""校验数据迁移保留历史证据、用户消息和稳定任务类型。"""

import hashlib
import json
from pathlib import Path

DATASETS = Path(__file__).resolve().parents[2] / "evaluation" / "datasets"


def test_migration_manifest_and_request_context_are_preserved():
    manifest = json.loads((DATASETS / "taxonomy_v1_migration.json").read_text(encoding="utf-8"))
    assert manifest["taxonomy_version"] == "1.0"
    for entry in manifest["datasets"]:
        old = (DATASETS / entry["source"]).read_bytes()
        new = (DATASETS / entry["target"]).read_bytes()
        assert hashlib.sha256(old).hexdigest() == entry["source_sha256"]
        assert hashlib.sha256(new).hexdigest() == entry["target_sha256"]
        original = [json.loads(line) for line in old.decode("utf-8").splitlines() if line]
        migrated = [json.loads(line) for line in new.decode("utf-8").splitlines() if line]
        assert len(original) == len(migrated) == entry["cases"]
        for before, after in zip(original, migrated, strict=True):
            assert after["id"] == f"{before['id']}-taxonomy-v1"
            if "request" in before:
                for key in ("message", "task_summaries", "recent_messages"):
                    assert before["request"].get(key) == after["request"].get(key)
            if "turns" in before:
                for old_turn, new_turn in zip(before["turns"], after["turns"], strict=True):
                    assert old_turn["message"] == new_turn["message"]
                    if "expect" in old_turn:
                        assert old_turn["expect"] == new_turn["expect"]

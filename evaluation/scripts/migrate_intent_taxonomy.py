"""将旧业务标签迁移为正式 ID，生成新数据集并保存来源摘要，不覆盖历史数据。"""

import argparse
import hashlib
import json
from pathlib import Path

ALIASES = {"refund": "refund.apply", "logistics": "logistics.track", "policy_qa": "policy.consult"}
DATASETS = {
    "intent_v1.jsonl": "intent_taxonomy_v1.jsonl",
    "intent_edge_v1.jsonl": "intent_edge_taxonomy_v1.jsonl",
    "intent_random_v2.jsonl": "intent_random_taxonomy_v1.jsonl",
    "dialogue_policy_v1.jsonl": "dialogue_policy_taxonomy_v1.jsonl",
    "chat_e2e_v1.jsonl": "chat_e2e_taxonomy_v1.jsonl",
}


def migrate_value(value: object) -> object:
    """递归迁移语义字段；任务类型、用户原文、订单号和回复断言保持原样。"""
    if isinstance(value, list):
        return [migrate_value(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {}
    for key, item in value.items():
        if key in {"business_intent", "intent"} and isinstance(item, str):
            result[key] = ALIASES.get(item, item)
        elif key in {"intents", "exact_intents"} and isinstance(item, list) or key == "candidate_values" and value.get("kind") == "intent":
            result[key] = [ALIASES.get(label, label) for label in item]
        else:
            result[key] = migrate_value(item)
    return result


def migrate_datasets(root: Path) -> dict:
    """生成五份正式标签数据集及迁移清单；任何目标已存在时拒绝全部写入。"""
    manifest_path = root / "taxonomy_v1_migration.json"
    targets = [root / name for name in DATASETS.values()] + [manifest_path]
    if any(path.exists() for path in targets):
        raise ValueError("迁移目标已存在，请保留已有数据并使用新目录")
    sources = {name: (root / name).read_bytes() for name in DATASETS}
    outputs = {}
    manifest = {"taxonomy_version": "1.0", "aliases": ALIASES, "datasets": []}
    for source, target in DATASETS.items():
        rows = [json.loads(line) for line in sources[source].decode("utf-8").splitlines() if line.strip()]
        migrated = []
        for row in rows:
            item = migrate_value(row)
            item["id"] = f"{row['id']}-taxonomy-v1"
            item["taxonomy_version"] = "1.0"
            migrated.append(item)
        content = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in migrated).encode("utf-8")
        outputs[target] = content
        manifest["datasets"].append({
            "source": source, "target": target, "cases": len(rows),
            "source_sha256": hashlib.sha256(sources[source]).hexdigest(),
            "target_sha256": hashlib.sha256(content).hexdigest(),
        })
    for target, content in outputs.items():
        (root / target).write_bytes(content)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    """读取数据集目录，执行一次可审核的名称迁移。"""
    parser = argparse.ArgumentParser(description="迁移意图分类标签，保留旧数据集")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "datasets")
    args = parser.parse_args()
    print(json.dumps(migrate_datasets(args.root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

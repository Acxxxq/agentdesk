"""通过真实聊天 API 评测多轮语义理解、策略决策与状态变化。"""

import argparse
import hashlib
import json
import math
import subprocess
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from agentorbis.infrastructure.llm.message_interpreter import SYSTEM_PROMPT


def _contains_all(actual: list[Any], expected: list[Any]) -> bool:
    """判断实际列表是否包含所有标注项，保留额外但无害的结构化信息。"""
    remaining = list(actual)
    for item in expected:
        try:
            remaining.remove(item)
        except ValueError:
            return False
    return True


def score_turn(expected: dict[str, Any], response: dict[str, Any], status: int) -> dict[str, Any]:
    """检查单轮聊天响应中的理解、策略、事件、状态和回复约束。"""
    checks: dict[str, bool] = {"http_status": status == 200}
    if status != 200:
        return {"passed": False, "checks": checks, "failures": ["http_status"]}

    understanding = response.get("understanding") or {}
    acts = understanding.get("acts") or []
    intents = [act.get("business_intent") for act in acts]
    if "intents" in expected:
        checks["intents"] = _contains_all(intents, expected["intents"])
    if "exact_intents" in expected:
        checks["exact_intents"] = Counter(intents) == Counter(expected["exact_intents"])

    for index, wanted in enumerate(expected.get("acts", [])):
        matched = [act for act in acts if act.get("business_intent") == wanted["business_intent"]]
        if "dialogue_act" in wanted:
            allowed = wanted["dialogue_act"]
            matched = [act for act in matched if act.get("dialogue_act") in (
                allowed if isinstance(allowed, list) else [allowed]
            )]
        if "target_hint" in wanted:
            allowed = wanted["target_hint"]
            matched = [act for act in matched if act.get("target_hint") in (
                allowed if isinstance(allowed, list) else [allowed]
            )]
        if "entities" in wanted:
            matched = [act for act in matched if all(
                act.get("entities", {}).get(key) == value
                for key, value in wanted["entities"].items()
            )]
        checks[f"act_{index + 1}"] = bool(matched)

    ambiguity_kinds = [item.get("kind") for item in understanding.get("ambiguities", [])]
    if "ambiguities_required" in expected:
        checks["ambiguities_required"] = _contains_all(
            ambiguity_kinds, expected["ambiguities_required"]
        )
    if "ambiguities_forbidden" in expected:
        checks["ambiguities_forbidden"] = not any(
            kind in ambiguity_kinds for kind in expected["ambiguities_forbidden"]
        )

    decisions = (response.get("policy") or {}).get("decisions") or []
    decision_actions = [decision.get("action") for decision in decisions]
    if "decision_actions" in expected:
        checks["decision_actions"] = _contains_all(
            decision_actions, expected["decision_actions"]
        )

    events = response.get("events") or []
    event_types = [event.get("event_type") for event in events]
    if "event_types" in expected:
        checks["event_types"] = _contains_all(event_types, expected["event_types"])

    state = response.get("state") or {}
    if "task_statuses" in expected:
        actual: dict[str, list[str]] = defaultdict(list)
        for task in state.get("tasks", []):
            actual[task.get("type", "unknown")].append(task.get("status", "unknown"))
        actual = {key: sorted(value) for key, value in sorted(actual.items())}
        wanted = {key: sorted(value) for key, value in sorted(expected["task_statuses"].items())}
        checks["task_statuses"] = actual == wanted

    if "pending_question" in expected:
        pending = state.get("pending_question")
        wanted = expected["pending_question"]
        if wanted is None:
            checks["pending_question"] = pending is None
        elif pending is None:
            checks["pending_question"] = False
        else:
            task = next((item for item in state.get("tasks", [])
                         if item.get("task_id") == pending.get("task_id")), None)
            checks["pending_question"] = bool(
                task
                and task.get("type") == wanted.get("task_type")
                and pending.get("slot_name") == wanted.get("slot_name")
            )

    if "pending_clarification" in expected:
        pending = state.get("pending_clarification")
        checks["pending_clarification"] = (
            pending is None if expected["pending_clarification"] is None
            else bool(pending and pending.get("kind") == expected["pending_clarification"])
        )

    reply = response.get("reply", "")
    if "reply_contains" in expected:
        checks["reply_contains"] = all(part in reply for part in expected["reply_contains"])
    if "reply_forbidden" in expected:
        checks["reply_forbidden"] = not any(part in reply for part in expected["reply_forbidden"])

    failures = [name for name, passed in checks.items() if not passed]
    return {"passed": not failures, "checks": checks, "failures": failures}


def _post_chat(endpoint: str, body: dict[str, Any]) -> tuple[int, dict[str, Any], str | None]:
    """向聊天 API 发送一轮请求，返回 HTTP 状态、JSON 和传输错误。"""
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=75) as connection:
            raw = connection.read().decode("utf-8")
            status = connection.status
            error = None
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8", errors="replace")
        error = None
    except (OSError, TimeoutError) as exc:
        return 0, {}, type(exc).__name__
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {"raw": raw}
    return status, payload if isinstance(payload, dict) else {}, error


def _evaluate_scenario(scenario: dict[str, Any], endpoint: str) -> dict[str, Any]:
    """以独立会话顺序发送场景中的全部用户轮次，并逐轮评分。"""
    conversation_id = None
    turns = []
    for index, turn in enumerate(scenario["turns"], start=1):
        body: dict[str, Any] = {"message": turn["message"]}
        if conversation_id:
            body["conversation_id"] = conversation_id
        started = time.perf_counter()
        status, response, transport_error = _post_chat(endpoint, body)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        if status == 200:
            conversation_id = response.get("conversation_id", conversation_id)
        assessment = score_turn(turn.get("expected", {}), response, status)
        turns.append({
            "turn": index, "message": turn["message"], "expected": turn.get("expected", {}),
            "http_status": status, "response": response, "transport_error": transport_error,
            "elapsed_ms": elapsed_ms, "assessment": assessment,
        })
        print(
            f"{scenario['id']} {index}/{len(scenario['turns'])} "
            f"{'PASS' if assessment['passed'] else 'FAIL'}",
            flush=True,
        )
    return {
        "scenario_id": scenario["id"], "category": scenario["category"],
        "description": scenario["description"], "conversation_id": conversation_id,
        "passed": all(turn["assessment"]["passed"] for turn in turns), "turns": turns,
    }


def _summarize(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    """按场景和轮次汇总通过率、延迟与逐项断言。"""
    turns = [turn for scenario in scenarios for turn in scenario["turns"]]
    latencies = sorted(turn["elapsed_ms"] for turn in turns)
    checks: dict[str, list[bool]] = defaultdict(list)
    for turn in turns:
        for name, passed in turn["assessment"]["checks"].items():
            checks[name].append(bool(passed))
    return {
        "scenarios": len(scenarios),
        "scenarios_passed": sum(scenario["passed"] for scenario in scenarios),
        "turns": len(turns),
        "turns_passed": sum(turn["assessment"]["passed"] for turn in turns),
        "turn_pass_rate": sum(turn["assessment"]["passed"] for turn in turns) / len(turns) if turns else 0,
        "http_errors": sum(turn["http_status"] == 0 or turn["http_status"] >= 500 for turn in turns),
        "latency_ms": {
            "p50": latencies[math.ceil(len(latencies) * 0.5) - 1] if latencies else 0,
            "p95": latencies[math.ceil(len(latencies) * 0.95) - 1] if latencies else 0,
        },
        "checks": {
            name: {"passed": sum(values), "total": len(values),
                   "rate": sum(values) / len(values) if values else 0}
            for name, values in sorted(checks.items())
        },
    }


def run(dataset: Path, output: Path, endpoint: str, model: str, concurrency: int) -> dict[str, Any]:
    """调用真实聊天端点并保存冻结数据、逐轮响应、代码快照和报告。"""
    if output.exists():
        raise SystemExit("Output directory exists; use a new run ID")
    raw_dataset = dataset.read_bytes()
    scenarios = [json.loads(line) for line in raw_dataset.decode("utf-8").splitlines() if line.strip()]
    if len({item["id"] for item in scenarios}) != len(scenarios):
        raise SystemExit("Duplicate scenario IDs")
    output.mkdir(parents=True)
    repo = dataset.resolve().parents[2]
    metadata: dict[str, Any] = {
        "started_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "dataset": str(dataset), "dataset_sha256": hashlib.sha256(raw_dataset).hexdigest(),
        "endpoint": endpoint, "model": model, "concurrency": concurrency,
        "prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()),
        "status": "running", "source_hashes": {},
    }
    for relative in [
        "backend/src/agentorbis/api/chat.py",
        "backend/src/agentorbis/domain/understanding.py",
        "backend/src/agentorbis/domain/dialogue_policy.py",
        "backend/src/agentorbis/domain/state_reducer.py",
        "backend/src/agentorbis/infrastructure/llm/message_interpreter.py",
        "backend/src/agentorbis/evaluation/chat.py",
    ]:
        source = (repo / relative).read_bytes()
        metadata["source_hashes"][relative] = hashlib.sha256(source).hexdigest()
        snapshot = output / "source_snapshot" / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(source)
    (output / "dataset.jsonl").write_bytes(raw_dataset)
    (output / "prompt.txt").write_text(SYSTEM_PROMPT, encoding="utf-8")
    (output / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    records = []
    # 一个场景内仍串行；不同的独立会话并发，缩短等待并保留每场景边界。
    with (output / "results.jsonl").open("w", encoding="utf-8") as stream:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = [pool.submit(_evaluate_scenario, scenario, endpoint) for scenario in scenarios]
            for future in as_completed(futures):
                record = future.result()
                records.append(record)
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                stream.flush()
                print(
                    f"场景 {record['scenario_id']} "
                    f"{'PASS' if record['passed'] else 'FAIL'}",
                    flush=True,
                )
    (output / "results.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = _summarize(records)
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_category[record["category"]].append(record)
    report_data = {
        "metadata": metadata, "overall": summary,
        "by_category": {name: _summarize(items) for name, items in sorted(by_category.items())},
    }
    (output / "summary.json").write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")
    metadata.update(status="completed", finished_at=datetime.now(timezone(timedelta(hours=8))).isoformat())
    (output / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# AgentOrbis 多轮聊天端到端评测报告", "",
        f"时间：{metadata['started_at']}  ",
        f"数据集 SHA-256：`{metadata['dataset_sha256']}`  ",
        f"模型：`{model}`；提示词 SHA-256：`{metadata['prompt_sha256']}`", "",
        "## 评测范围", "",
        "通过真实 `/api/v1/chat` 接口连续发送每个场景的消息，检查模型理解、策略决策、领域事件、完整任务状态、待补参数和回复。每个场景使用新会话；轮次按顺序执行。",
        "数据为合成开发样例，非真实用户语料，未经独立人工复核；可能存在提示词回归偏差。服务端或传输错误保留在分母中，不重试。",
        "本评测不验证 MySQL 持久化、真实退款/物流执行、身份权限或并发请求。", "",
        "## 结果", "",
        f"- 场景：{summary['scenarios_passed']} / {summary['scenarios']} 全轮通过。",
        f"- 轮次：{summary['turns_passed']} / {summary['turns']} 通过（{summary['turn_pass_rate']:.1%}）。",
        f"- HTTP/网络错误：{summary['http_errors']}；延迟 P50/P95：{summary['latency_ms']['p50']:.0f}/{summary['latency_ms']['p95']:.0f} ms。", "",
        "## 分类结果", "", "| 分类 | 场景通过 / 总数 | 轮次通过 / 总数 |", "|---|---:|---:|",
    ]
    for category, result in report_data["by_category"].items():
        lines.append(f"| {category} | {result['scenarios_passed']} / {result['scenarios']} | {result['turns_passed']} / {result['turns']} |")
    lines += ["", "## 分项结果", "", "| 断言 | 通过 / 总数 | 比率 |", "|---|---:|---:|"]
    for name, result in summary["checks"].items():
        lines.append(f"| {name} | {result['passed']} / {result['total']} | {result['rate']:.1%} |")
    lines += ["", "## 失败轮次", ""]
    failures = [(scenario, turn) for scenario in records for turn in scenario["turns"]
                if not turn["assessment"]["passed"]]
    if failures:
        for scenario, turn in failures:
            lines += [f"### {scenario['scenario_id']} · 第 {turn['turn']} 轮", "",
                      f"输入：{turn['message']}", "",
                      f"未通过：{', '.join(turn['assessment']['failures'])}", "",
                      "```json", json.dumps({"expected": turn["expected"], "actual": turn["response"]},
                                             ensure_ascii=False, indent=2), "```", ""]
    else:
        lines.append("本轮无失败；结果仅适用于本数据集与本次模型配置。")
    (output / "report.zh-CN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return report_data


def main() -> None:
    """解析命令行参数并启动聊天端到端评测。"""
    parser = argparse.ArgumentParser(description="多轮聊天端到端评测")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:18000/api/v1/chat")
    parser.add_argument("--model", required=True, help="服务端配置的模型名，不含密钥")
    parser.add_argument("--concurrency", type=int, default=3, choices=range(1, 5))
    args = parser.parse_args()
    run(args.dataset, args.output, args.endpoint, args.model, args.concurrency)


if __name__ == "__main__":
    main()

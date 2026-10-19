"""批量评测现有 HTTP 意图接口，持久记录输入、输出、错误、耗时和版本信息。"""

import argparse
import hashlib
import itertools
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

from pydantic import ValidationError

from agentorbis.domain.understanding import MessageUnderstanding
from agentorbis.infrastructure.llm.message_interpreter import SYSTEM_PROMPT


def _allowed(actual, expected):
    """列表表示事先标注的可接受值集合，其他值进行精确比较。"""
    return actual in expected if isinstance(expected, list) else actual == expected


def _act_checks(expected, actual):
    """比较单个动作的指定字段；实体要求键和值完全匹配，避免串订单和幻觉参数。"""
    checks = {"intents": actual.get("business_intent") == expected["business_intent"]}
    for field, metric in [("dialogue_act", "dialogue_acts"), ("target_hint", "target_hints"),
                          ("referenced_task_id", "task_references")]:
        if field in expected:
            checks[metric] = _allowed(actual.get(field), expected[field])
    if "entities" in expected:
        checks["entity_binding"] = actual.get("entities", {}) == expected["entities"]
    return checks


def score_case(expected, response, status):
    """按固定语义约束评分并返回逐项结果；动作可重排，但实体和关系必须绑定正确。"""
    expected_status = expected.get("http_status", 200)
    checks = {"http_status": status == expected_status}
    if expected_status != 200:
        return {"passed": all(checks.values()), "checks": checks,
                "failures": [key for key, value in checks.items() if not value]}
    gold = expected.get("acts", [])
    metrics = {"intents", "act_count", "entity_binding", "ambiguities", "relations"}
    for item in gold:
        metrics.update(_act_checks(item, {}).keys())
    checks.update({metric: False for metric in metrics})
    if status != 200 or not isinstance(response.get("acts"), list):
        return {"passed": False, "checks": checks, "failures": [k for k, v in checks.items() if not v]}
    acts = response["acts"]
    checks["act_count"] = len(acts) == len(gold)
    checks["intents"] = Counter(a.get("business_intent") for a in acts) == Counter(g["business_intent"] for g in gold)
    # 最多 8 个动作；优先找使全部约束通过的匹配，不使用模型输出数组顺序作为标签。
    best_mapping = None
    best_checks = {}
    best_score = -1
    if checks["act_count"]:
        for mapping in itertools.permutations(range(len(acts))):
            if checks["intents"] and any(
                g["business_intent"] != acts[index].get("business_intent")
                for g, index in zip(gold, mapping, strict=True)
            ):
                continue
            pair_checks = [_act_checks(g, acts[index]) for g, index in zip(gold, mapping, strict=True)]
            candidate = {metric: all(p.get(metric, True) for p in pair_checks)
                         for metric in metrics - {"act_count", "ambiguities", "relations"}}
            ids = {index: acts[actual_index].get("act_id") for index, actual_index in enumerate(mapping)}
            gold_relations = Counter((ids[r["source_index"]], ids[r["target_index"]], r["kind"])
                                     for r in expected.get("relations", []))
            actual_relations = Counter((r.get("source_act_id"), r.get("target_act_id"), r.get("kind"))
                                       for r in response.get("relations", []))
            candidate["relations"] = gold_relations == actual_relations
            value = sum(candidate.values())
            if value > best_score:
                best_score, best_mapping, best_checks = value, mapping, candidate
        checks.update(best_checks)
    kinds = {a.get("kind") for a in response.get("ambiguities", [])}
    checks["ambiguities"] = (set(expected.get("ambiguity_required", [])) <= kinds
                              and not (set(expected.get("ambiguity_forbidden", [])) & kinds))
    return {"passed": all(checks.values()), "checks": checks,
            "failures": [key for key, value in checks.items() if not value],
            "matched_act_indices": list(best_mapping) if best_mapping is not None else None}


def summarize(records):
    """汇总全部请求，接口失败保留在分母中；分项指标只统计声明了该检查的样例。"""
    total = len(records)
    passed = sum(record["assessment"]["passed"] for record in records)
    latencies = sorted(record["elapsed_ms"] for record in records)
    metrics = defaultdict(lambda: {"passed": 0, "total": 0})
    for record in records:
        for name, value in record["assessment"]["checks"].items():
            metrics[name]["total"] += 1
            metrics[name]["passed"] += bool(value)
    for value in metrics.values():
        value["rate"] = value["passed"] / value["total"]
    return {
        "total": total, "passed": passed, "failed": total-passed, "pass_rate": passed/total if total else 0,
        "http_errors": sum(r["http_status"] == 0 or r["http_status"] >= 500 for r in records),
        "latency_ms": {"p50": latencies[math.ceil(total*.5)-1] if total else 0,
                       "p95": latencies[math.ceil(total*.95)-1] if total else 0},
        "metrics": dict(metrics),
    }


def evaluate_one(case, endpoint, repeat):
    """对一个合成样例发送一次 HTTP 请求，不重试；返回包含完整合成输入与输出的记录。"""
    started = time.perf_counter()
    body = json.dumps(case["request"], ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    status, response, transport_error = 0, {}, None
    try:
        with urllib.request.urlopen(request, timeout=65) as connection:
            status = connection.status
            raw = connection.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        status, raw = error.code, error.read().decode("utf-8", errors="replace")
    except (OSError, TimeoutError) as error:
        transport_error, raw = type(error).__name__, ""
    try:
        response = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        response = {"error": "non_json_response"}
    if not isinstance(response, dict):
        response = {"error": "non_object_response"}
    assessment = score_case(case["expected"], response, status)
    if status == 200:
        try:
            MessageUnderstanding.model_validate(response)
            assessment["checks"]["response_schema"] = True
        except ValidationError:
            assessment["checks"]["response_schema"] = False
            assessment["failures"].append("response_schema")
            assessment["passed"] = False
    return {
        "case_id": case["id"], "repeat": repeat, "category": case["category"], "origin": case["origin"],
        "request": case["request"], "expected": case["expected"], "http_status": status,
        "response": response, "raw_response": raw, "transport_error": transport_error,
        "elapsed_ms": round((time.perf_counter()-started)*1000, 2), "assessment": assessment,
    }


def write_report(output, metadata, records):
    """生成中文报告和机器可读汇总；列出所有失败，不剔除接口错误或调低标签要求。"""
    overall = summarize(records)
    groups = defaultdict(list)
    for record in records:
        groups[record["category"]].append(record)
    summary = {"metadata": metadata, "overall": overall,
               "by_category": {name: summarize(items) for name, items in sorted(groups.items())}}
    summary["semantic"] = summarize([r for r in records if r["expected"].get("http_status", 200) == 200])
    summary["input_validation"] = summarize([r for r in records if r["expected"].get("http_status", 200) != 200])
    origins = {r["origin"] for r in records}
    summary["by_origin"] = {origin: summarize([r for r in records if r["origin"] == origin]) for origin in sorted(origins)}
    (output/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# AgentOrbis 意图识别评测报告", "", f"时间：{metadata['started_at']}  ",
             f"数据集 SHA-256：`{metadata['dataset_sha256']}`  ",
             f"模型：`{metadata['model']}`；提示词 SHA-256：`{metadata['prompt_sha256']}`", "",
             "## 评测边界", "", "这是编码助手生成并预先标注的合成开发集，非真实用户数据，未经独立人工复核。",
             "包括已在提示词中出现的回归例子，单独按 origin 统计；不得作为独立泛化能力证明。",
             "上下文为固定快照；不评测自动任务创建、状态串写、持久化、真实退款或完整澄清闭环。",
             "精确评分只覆盖标签声明的字段，未标注的动作/目标字段不代表已正确。",
             "未使用 LLM 裁判；每次请求不重试，失败结果不丢弃。模型输出已通过 API 校验，非供应商原始响应。", "",
             "## 总体结果", "", f"- 请求数：{overall['total']}；通过：{overall['passed']}；失败：{overall['failed']}。",
             f"- 全约束通过率：{overall['pass_rate']:.1%}；服务端/网络错误：{overall['http_errors']}。",
             f"- 语义样例：{summary['semantic']['passed']} / {summary['semantic']['total']}；非法输入拦截：{summary['input_validation']['passed']} / {summary['input_validation']['total']}。",
             f"- HTTP 耗时 P50：{overall['latency_ms']['p50']:.0f} ms；P95：{overall['latency_ms']['p95']:.0f} ms（包含排队）。", "",
             "## 分类结果", "", "| 分类 | 通过 / 总数 | 全约束通过率 |", "|---|---:|---:|"]
    for name, stats in summary["by_category"].items():
        lines.append(f"| {name} | {stats['passed']} / {stats['total']} | {stats['pass_rate']:.1%} |")
    lines += ["", "## 分项结果", "", "| 检查 | 通过 / 有标签样例 | 比率 |", "|---|---:|---:|"]
    for name, metric in sorted(overall["metrics"].items()):
        lines.append(f"| {name} | {metric['passed']} / {metric['total']} | {metric['rate']:.1%} |")
    lines += ["", "## 失败明细", "", "详细请求、预期和完整响应见 `results.jsonl`。", ""]
    failures = [r for r in records if not r["assessment"]["passed"]]
    for record in failures:
        message = record["request"]["message"]
        lines += [f"### {record['case_id']} · {record['category']} · 第 {record['repeat']} 次", "",
                  f"输入：{message[:160]}{'…' if len(message)>160 else ''}", "",
                  f"HTTP：{record['http_status']}；未通过：{', '.join(record['assessment']['failures'])}", "",
                  "```json", json.dumps({"expected":record["expected"],"actual":record["response"]},ensure_ascii=False,indent=2), "```", ""]
    if not failures:
        lines.append("本轮无失败，不代表生产场景无误判。")
    (output/"report.zh-CN.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    return summary


def main():
    """读取冻结数据集，限并发调用现有服务，将每条结果立即落盘并保存最终报告。"""
    parser = argparse.ArgumentParser(description="意图识别固定标签 HTTP 评测")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:18000/api/v1/interpret")
    parser.add_argument("--model", required=True, help="从服务端配置核实的模型名称，不包含密钥")
    parser.add_argument("--concurrency", type=int, default=2, choices=range(1,5))
    parser.add_argument("--repeats", type=int, default=1, choices=range(1,4))
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Output directory exists; use a new run ID")
    dataset_bytes = args.dataset.read_bytes()
    cases = [json.loads(line) for line in dataset_bytes.decode("utf-8").splitlines() if line.strip()]
    if len({c["id"] for c in cases}) != len(cases):
        raise SystemExit("Duplicate case IDs")
    args.output.mkdir(parents=True)
    metadata = {
        "started_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "dataset": str(args.dataset), "dataset_sha256": hashlib.sha256(dataset_bytes).hexdigest(),
        "model": args.model, "endpoint": args.endpoint, "concurrency": args.concurrency,
        "repeats": args.repeats, "prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        "git_commit": subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "git_dirty": bool(subprocess.check_output(["git","status","--porcelain"],text=True).strip()),
        "source_hashes": {}, "status": "running",
    }
    repo = args.dataset.resolve().parents[3]
    # 冻结评分器和产品契约/提示词，避免未提交代码只靠 Git 提交号无法复现。
    for relative in ["backend/src/agentorbis/domain/understanding.py",
                     "backend/src/agentorbis/infrastructure/llm/message_interpreter.py",
                     "backend/src/agentorbis/evaluation/intent.py"]:
        data = (repo/relative).read_bytes()
        metadata["source_hashes"][relative] = hashlib.sha256(data).hexdigest()
        destination = args.output/"source_snapshot"/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(data)
    (args.output/"dataset.jsonl").write_bytes(dataset_bytes)
    (args.output/"prompt.txt").write_text(SYSTEM_PROMPT,encoding="utf-8")
    (args.output/"metadata.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
    records = []
    with (args.output/"results.jsonl").open("w",encoding="utf-8") as stream:
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures = [pool.submit(evaluate_one,c,args.endpoint,repeat)
                       for repeat in range(1,args.repeats+1) for c in cases]
            for future in as_completed(futures):
                record = future.result()
                stream.write(json.dumps(record,ensure_ascii=False)+"\n")
                stream.flush()
                records.append(record)
                print(f"{len(records)}/{len(futures)} {record['case_id']} {'PASS' if record['assessment']['passed'] else 'FAIL'}",flush=True)
    metadata.update(status="completed",finished_at=datetime.now(timezone(timedelta(hours=8))).isoformat())
    (args.output/"metadata.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
    result = write_report(args.output,metadata,records)
    print(json.dumps(result["overall"],ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()

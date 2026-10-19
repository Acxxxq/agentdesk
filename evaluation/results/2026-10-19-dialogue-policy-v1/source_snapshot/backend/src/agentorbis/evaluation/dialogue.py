"""运行固定语义输入上的多轮对话策略评测。"""

import argparse
import json
from pathlib import Path
from typing import Any

from agentorbis.api.chat import _build_reply
from agentorbis.domain.dialogue_policy import DialoguePolicy
from agentorbis.domain.state import ConversationState
from agentorbis.domain.state_reducer import reduce_state
from agentorbis.domain.understanding import MessageUnderstanding


def evaluate_dataset(dataset_path: Path) -> list[dict[str, Any]]:
    """按数据集中的固定语义结构重放会话并检查策略和状态结果。

    参数：
        dataset_path：JSONL 多轮对话数据集路径，每行包含场景、语义输入和预期结果。

    返回：
        list[dict[str, Any]]：逐场景记录每轮实际状态、事件、回复和断言结果。
    """
    results = []
    for line_number, line in enumerate(dataset_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        case = json.loads(line)
        state = ConversationState(conversation_id=f"evaluation:{case['id']}")
        turns = []
        for turn_index, turn in enumerate(case["turns"], 1):
            understanding = MessageUnderstanding.model_validate(turn["understanding"])
            policy = DialoguePolicy().decide(state, understanding, turn["message"])
            reduction = reduce_state(state, policy)
            reply = _build_reply(policy, reduction)
            actual = {
                "events": [event.event_type for event in reduction.events],
                "task_types": {task.type: task.status for task in reduction.state.tasks},
                "pending_clarification": (
                    reduction.state.pending_clarification.kind
                    if reduction.state.pending_clarification else None
                ),
                "pending_target_act": (
                    reduction.state.pending_clarification.target_act_id
                    if reduction.state.pending_clarification else None
                ),
                "pending_original_act_ids": (
                    [act.act_id for act in reduction.state.pending_clarification.original_acts]
                    if reduction.state.pending_clarification else []
                ),
                "pending_question_task_type": next((
                    task.type for task in reduction.state.tasks
                    if reduction.state.pending_question
                    and task.task_id == reduction.state.pending_question.task_id
                ), None),
                "pending_question_slot": (
                    reduction.state.pending_question.slot_name
                    if reduction.state.pending_question else None
                ),
                "reply": reply,
            }
            expected = turn["expect"]
            checks = {
                key: actual.get(key) == expected[key]
                for key in (
                    "events", "task_types", "pending_clarification", "pending_target_act",
                    "pending_original_act_ids", "pending_question_task_type", "pending_question_slot",
                )
                if key in expected
            }
            checks.update({
                f"reply_contains:{phrase}": phrase in reply
                for phrase in expected.get("reply_contains", [])
            })
            turns.append({
                "turn": turn_index,
                "message": turn["message"],
                "actual": actual,
                "expected": expected,
                "checks": checks,
                "passed": all(checks.values()),
            })
            state = reduction.state
        results.append({
            "id": case["id"],
            "description": case["description"],
            "source_line": line_number,
            "turns": turns,
            "passed": all(turn["passed"] for turn in turns),
        })
    return results


def write_evaluation(dataset_path: Path, output_dir: Path) -> dict[str, Any]:
    """运行评测并写入可复查的逐例结果、摘要和中文报告。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    results = evaluate_dataset(dataset_path)
    (output_dir / "dataset.jsonl").write_text(dataset_path.read_text(encoding="utf-8"), encoding="utf-8")
    (output_dir / "results.jsonl").write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in results),
        encoding="utf-8",
    )
    total_turns = sum(len(item["turns"]) for item in results)
    passed_turns = sum(turn["passed"] for item in results for turn in item["turns"])
    summary = {
        "dataset": dataset_path.name,
        "scenario_count": len(results),
        "passed_scenarios": sum(item["passed"] for item in results),
        "turn_count": total_turns,
        "passed_turns": passed_turns,
        "turn_pass_rate": round(passed_turns / total_turns, 4) if total_turns else 0,
        "evaluation_type": "deterministic dialogue policy and state reducer; fixed semantic inputs",
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    report = [
        "# 多轮对话策略评测",
        "",
        f"- 场景：{summary['scenario_count']}，通过：{summary['passed_scenarios']}",
        f"- 对话轮次：{total_turns}，通过：{passed_turns}，通过率：{summary['turn_pass_rate']:.0%}",
        "- 评测范围：使用固定语义结构输入，检查 DialoguePolicy、状态归约和用户回复；不调用 LLM。",
        "- 本轮修复：明确取消可与另一项缺参任务分开处理；澄清只保存未完成动作，补参时不会重放已完成动作。",
        "- [问题分析与评测边界](analysis.zh-CN.md)",
        "",
        "| 场景 | 结果 | 失败断言 |",
        "| --- | --- | --- |",
    ]
    for item in results:
        failures = [
            f"第{turn['turn']}轮 {key}"
            for turn in item["turns"]
            for key, passed in turn["checks"].items()
            if not passed
        ]
        report.append(f"| `{item['id']}` | {'通过' if item['passed'] else '失败'} | {'；'.join(failures) or '—'} |")
    (output_dir / "report.zh-CN.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    """解析命令行路径并执行策略评测。"""
    parser = argparse.ArgumentParser(description="评测 AgentOrbis 多轮对话策略")
    parser.add_argument("--dataset", type=Path, required=True, help="JSONL 对话数据集")
    parser.add_argument("--output", type=Path, required=True, help="结果目录")
    args = parser.parse_args()
    print(json.dumps(write_evaluation(args.dataset, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

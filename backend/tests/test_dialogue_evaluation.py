"""验证固定多轮数据集中的策略、状态事件和用户可见回复。"""

from pathlib import Path

from agentorbis.api.chat import ConversationSession, _make_interpretation_request
from agentorbis.domain.state import ConversationState, TaskState
from agentorbis.evaluation.dialogue import evaluate_dataset

DATASET = Path(__file__).resolve().parents[2] / "evaluation" / "datasets" / "dialogue_policy_taxonomy_v1.jsonl"


def test_dialogue_policy_dataset_passes():
    results = evaluate_dataset(DATASET)
    failures = [
        (case["id"], turn["turn"], turn["checks"])
        for case in results
        for turn in case["turns"]
        if not turn["passed"]
    ]
    assert not failures, failures


def test_cancel_and_clarification_are_both_applied_without_replaying_cancel():
    results = evaluate_dataset(DATASET)
    case = next(item for item in results if item["id"] == "cancel_refund_then_logistics-taxonomy-v1")

    assert case["turns"][1]["actual"]["events"] == [
        "task_cancelled", "clarification_requested",
    ]
    assert case["turns"][1]["actual"]["pending_original_act_ids"] == ["a2"]
    assert case["turns"][2]["actual"]["events"] == [
        "clarification_resolved", "task_created",
    ]


def test_legacy_and_canonical_policy_inputs_preserve_behavior():
    """同一批业务场景只迁移名称时，状态、事件和回复不得改变。"""
    legacy = evaluate_dataset(DATASET.with_name("dialogue_policy_v1.jsonl"))
    canonical = evaluate_dataset(DATASET)
    assert len(legacy) == len(canonical)
    for before, after in zip(legacy, canonical, strict=True):
        assert before["turns"] == after["turns"]


def test_interpreter_context_keeps_questions_for_all_collecting_tasks():
    state = ConversationState(
        conversation_id="conversation-multi-task",
        tasks=[
            TaskState(task_id="refund-1", type="refund", status="collecting"),
            TaskState(
                task_id="logistics-1", type="logistics", status="ready",
                slots={"order_id": "A100"},
            ),
        ],
        active_task_id="logistics-1",
        pending_question={
            "task_id": "refund-1", "slot_name": "order_id", "question": "请提供退款订单号。",
        },
    )
    request = _make_interpretation_request(
        ConversationSession(state=state), "那个退款的编号是B100",
    )

    assert [item.task_id for item in request.conversation.pending_questions] == ["refund-1"]
    assert request.conversation.pending_questions[0].slot_name == "order_id"

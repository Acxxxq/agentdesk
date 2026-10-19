import json
from pathlib import Path

from agentorbis.domain.dialogue_policy import DialoguePolicy
from agentorbis.domain.state import ConversationState, TaskState
from agentorbis.domain.understanding import Ambiguity, MessageUnderstanding
from agentorbis.evaluation.chat import score_turn

DATASET = Path(__file__).resolve().parents[2] / "evaluation" / "datasets" / "chat_e2e_v1.jsonl"


def test_chat_e2e_dataset_has_unique_scenarios_and_nonempty_turns():
    scenarios = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines()]

    assert len(scenarios) == 10
    assert len({scenario["id"] for scenario in scenarios}) == len(scenarios)
    assert all(scenario["turns"] for scenario in scenarios)
    assert all(turn["message"].strip() for scenario in scenarios for turn in scenario["turns"])


def test_chat_turn_scorer_checks_task_identity_for_pending_question():
    expected = {
        "intents": ["refund"],
        "acts": [{"business_intent": "refund", "entities": {"order_id": "R100"}}],
        "decision_actions": ["fill_slot"],
        "event_types": ["task_slot_filled"],
        "task_statuses": {"refund": ["collecting"]},
        "pending_question": {"task_type": "refund", "slot_name": "reason"},
        "reply_contains": ["已记录"],
    }
    response = {
        "understanding": {"acts": [{
            "business_intent": "refund", "dialogue_act": "answer_pending",
            "target_hint": "active_task", "entities": {"order_id": "R100"},
        }]},
        "policy": {"decisions": [{"action": "fill_slot"}]},
        "events": [{"event_type": "task_slot_filled"}],
        "state": {
            "tasks": [{"task_id": "refund-1", "type": "refund", "status": "collecting"}],
            "pending_question": {"task_id": "refund-1", "slot_name": "reason"},
            "pending_clarification": None,
        },
        "reply": "已记录你补充的信息。请说明申请退款的原因。",
    }

    assert score_turn(expected, response, 200)["passed"]

    response["state"]["pending_question"]["task_id"] = "logistics-1"
    assert "pending_question" in score_turn(expected, response, 200)["failures"]


def test_chat_turn_scorer_retains_http_failures_in_assessment():
    result = score_turn({"decision_actions": ["create_task"]}, {"error": "unavailable"}, 503)

    assert result == {"passed": False, "checks": {"http_status": False}, "failures": ["http_status"]}


def test_task_ambiguity_uses_business_labels_and_keeps_task_references():
    state = ConversationState(
        conversation_id="conversation-1",
        active_task_id="logistics-1",
        tasks=[
            TaskState(task_id="refund-1", type="refund"),
            TaskState(task_id="logistics-1", type="logistics"),
        ],
    )
    understanding = MessageUnderstanding(
        acts=[],
        ambiguities=[Ambiguity(
            kind="task", candidate_values=["refund-1", "logistics-1"],
            reason="两个任务都在等订单号，目标不明确",
        )],
        relations=[],
    )

    result = DialoguePolicy().decide(state, understanding, "那个呢")
    clarification = result.decisions[0].clarification

    assert clarification is not None
    assert clarification.candidate_task_ids == ["refund-1", "logistics-1"]
    assert "退款任务" in clarification.question
    assert "物流查询任务" in clarification.question
    assert "refund-1" not in clarification.question
    assert "logistics-1" not in clarification.question

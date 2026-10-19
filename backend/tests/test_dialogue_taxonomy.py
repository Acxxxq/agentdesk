"""验证正式意图名称下，新业务与旧澄清之间不会串写订单或丢失上下文。"""

import pytest

from agentorbis.domain.dialogue_policy import DialoguePolicy
from agentorbis.domain.state import ConversationState
from agentorbis.domain.state_reducer import reduce_state
from agentorbis.domain.understanding import MessageUnderstanding


def waiting_for_logistics_order() -> ConversationState:
    """构造正在追问物流订单号、尚未建立具体物流任务的会话。"""
    return ConversationState(
        conversation_id="switch-taxonomy", pending_clarification={
            "clarification_id": "old-logistics", "kind": "parameter",
            "question": "请提供要查询物流的订单号", "original_message": "查物流",
            "target_act_id": "old-act", "target_slot": "order_id",
            "target_ambiguity_index": 0,
            "original_acts": [{
                "act_id": "old-act", "business_intent": "logistics.track",
                "dialogue_act": "start_task", "target_hint": "new_task",
                "utterance_span": "查物流",
            }],
            "original_ambiguities": [{
                "kind": "parameter", "target_act_id": "old-act", "target_slot": "order_id",
            }],
        },
    )


@pytest.mark.parametrize("order_id", [None, "R100"])
def test_explicit_refund_does_not_answer_old_logistics_question(order_id):
    state = waiting_for_logistics_order()
    before = state.model_dump()
    understanding = MessageUnderstanding.model_validate({
        "acts": [{
            "act_id": "new-refund", "business_intent": "refund.apply",
            "dialogue_act": "start_task", "target_hint": "new_task",
            "utterance_span": "申请退款", "entities": {"order_id": order_id} if order_id else {},
        }],
        "ambiguities": [] if order_id else [{
            "kind": "parameter", "target_act_id": "new-refund", "target_slot": "order_id",
        }], "relations": [],
    })
    plan = DialoguePolicy().decide(state, understanding, "申请退款")
    after = reduce_state(state, plan).state
    assert state.model_dump() == before
    assert plan.decisions[0].action == "interrupt_clarification"
    assert after.suspended_clarifications[0].clarification_id == "old-logistics"
    assert not any(task.type == "logistics" for task in after.tasks)
    if order_id:
        assert after.tasks[0].type == "refund"
        assert after.tasks[0].slots["order_id"] == order_id
    else:
        assert after.pending_clarification.original_acts[0].business_intent == "refund.apply"
        assert "申请退款" in after.pending_clarification.question


def test_same_business_answer_resolves_original_clarification():
    state = waiting_for_logistics_order()
    understanding = MessageUnderstanding.model_validate({
        "acts": [{
            "act_id": "answer", "business_intent": "logistics.track",
            "dialogue_act": "start_task", "target_hint": "new_task",
            "entities": {"order_id": "L100"}, "utterance_span": "L100",
        }], "ambiguities": [], "relations": [],
    })
    after = reduce_state(state, DialoguePolicy().decide(state, understanding, "L100")).state
    assert not after.suspended_clarifications
    assert after.pending_clarification is None
    assert after.tasks[0].slots == {"order_id": "L100"}
    assert after.tasks[0].status == "ready"


def test_global_intent_ambiguity_does_not_interrupt_existing_clarification():
    state = waiting_for_logistics_order()
    understanding = MessageUnderstanding.model_validate({
        "acts": [{
            "act_id": "unclear", "business_intent": "refund.apply",
            "dialogue_act": "start_task", "target_hint": "new_task", "utterance_span": "处理一下",
        }], "ambiguities": [{"kind": "intent"}], "relations": [],
    })
    plan = DialoguePolicy().decide(state, understanding, "处理一下")
    assert [decision.action for decision in plan.decisions] == ["clarify"]
    assert plan.decisions[0].clarification.clarification_id == "old-logistics"


def test_different_business_slot_answer_cannot_fill_old_clarification():
    state = waiting_for_logistics_order()
    understanding = MessageUnderstanding.model_validate({
        "acts": [{
            "act_id": "refund-answer", "business_intent": "refund.apply",
            "dialogue_act": "answer_pending", "target_hint": "unspecified",
            "entities": {"order_id": "R100"}, "utterance_span": "退款订单 R100",
        }], "ambiguities": [], "relations": [],
    })
    plan = DialoguePolicy().decide(state, understanding, "退款订单 R100")
    after = reduce_state(state, plan).state
    assert not after.tasks
    assert after.pending_clarification.clarification_id == "old-logistics"

from agentorbis.domain.dialogue import DialogueManager
from agentorbis.domain.state import Action, ConversationState, TaskStatus


def turn(state, message):
    return DialogueManager().handle(state, message)


def test_initial_refund_creates_expected_slot():
    result = turn(ConversationState(), "我要退款")
    assert result.action == Action.START_TASK
    assert result.state.active_task().expected_input == "order_id"


def test_continue_task_without_reclassification():
    started = turn(ConversationState(), "我要退款")
    continued = turn(started.state, "A1001")
    assert continued.action == Action.CONTINUE_TASK
    assert continued.state.active_task().slots["order_id"] == "A1001"
    assert continued.state.active_task().status == TaskStatus.WAITING_TOOL
    assert "没有执行外部操作" in continued.response


def test_correction_invalidates_business_step():
    started = turn(ConversationState(), "我要退款")
    filled = turn(started.state, "A1001")
    fixed = turn(filled.state, "不对，订单号改成 A2002")
    assert fixed.action == Action.UPDATE_SLOT
    assert fixed.state.active_task().slots["order_id"] == "A2002"
    assert fixed.state.active_task().step == "check_eligibility"


def test_cancel_clears_active_task():
    started = turn(ConversationState(), "我要退款")
    cancelled = turn(started.state, "不退了")
    assert cancelled.action == Action.CANCEL_TASK
    assert cancelled.state.active_task_id is None
    assert next(iter(cancelled.state.tasks.values())).status == TaskStatus.CANCELLED


def test_switch_then_resume():
    started = turn(ConversationState(), "我要退款")
    switched = turn(started.state, "先查物流吧")
    assert switched.action == Action.SWITCH_TASK
    assert switched.state.active_task().type == "logistics"
    resumed = turn(switched.state, "还是退款吧")
    assert resumed.action == Action.RESUME_TASK
    assert resumed.state.active_task().type == "refund"


def test_irrelevant_order_without_task_is_not_implicitly_processed():
    result = turn(ConversationState(), "A1001")
    assert result.action == Action.CLARIFY


def test_informational_question_does_not_create_task():
    result = turn(ConversationState(), "退款多久到账？")
    assert result.action == Action.ANSWER_QUESTION
    assert result.state.active_task_id is None


def test_ambiguous_conversation_does_not_execute_tool():
    started = turn(ConversationState(), "我要退款")
    result = turn(started.state, "那还是那个吧")
    assert result.action == Action.CLARIFY


def test_new_refund_with_order_can_fill_in_same_turn():
    result = turn(ConversationState(), "我要退款，订单号 A1001")
    assert result.action == Action.START_TASK
    assert result.state.active_task().slots["order_id"] == "A1001"
    assert result.state.active_task().status == TaskStatus.WAITING_TOOL


def test_unref_task_cancel_does_not_cancel_different_task():
    start = turn(ConversationState(), "我要退款")
    switched = turn(start.state, "先查物流吧")
    result = turn(switched.state, "不退了")
    assert result.action == Action.CLARIFY
    assert result.state.active_task().type == "logistics"

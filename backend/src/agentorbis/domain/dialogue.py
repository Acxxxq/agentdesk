"""A deliberately SMALL deterministic FSM: no LLM, external tool or real refunds.

A phase-1 LLM interpreter can be injected for inputs this module marks CLARIFY.
Business side effects stay in audited task/tool handlers, never in this function.
"""
from __future__ import annotations

import re

from agentorbis.domain.state import (
    Action,
    ConversationState,
    DialogueResult,
    TaskState,
    TaskStatus,
)

ORDER_RE = re.compile(r"(?<![A-Za-z0-9])A\d{4,12}(?![A-Za-z0-9])", re.IGNORECASE)


class DialogueManager:
    def handle(self, old_state: ConversationState, message: str) -> DialogueResult:
        state = old_state.model_copy(deep=True)
        content = message.strip()
        if not content:
            return self._result(state, Action.CLARIFY, "请补充您需要办理的事项。")

        active = state.active_task()
        # Intentional narrow command grammar: ambiguous cases are NOT auto-executed.
        if active and ((active.type == "refund" and any(k in content for k in ("不退了", "取消退款"))) or "取消这个任务" in content):
            active.status = TaskStatus.CANCELLED
            state.active_task_id = None
            return self._result(state, Action.CANCEL_TASK, "已停止当前演示任务；没有发起退款。", active)

        # Correction has priority over filling a new slot.
        order_matches = ORDER_RE.findall(content.upper())
        correcting = any(k in content for k in ("不对", "改成", "应该是", "更正"))
        if active and correcting and order_matches:
            active.slots["order_id"] = order_matches[-1]
            active.step = "check_eligibility"
            active.status = TaskStatus.WAITING_TOOL
            active.expected_input = None
            return self._result(state, Action.UPDATE_SLOT, "订单号已更正；旧查询结果作废，等待接入真实资格校验工具。", active)

        if active and "先查物流" in content:
            active.status = TaskStatus.PAUSED
            new = self._new_task(state, "logistics")
            return self._result(state, Action.SWITCH_TASK, "已暂停原任务。请提供需要查询物流的订单号。", new)

        if "还是退款" in content or "继续退款" in content:
            candidate = next((t for t in reversed(list(state.tasks.values())) if t.type == "refund" and t.status == TaskStatus.PAUSED), None)
            if candidate:
                if active:
                    active.status = TaskStatus.PAUSED
                candidate.status = TaskStatus.WAITING_INPUT if candidate.expected_input else TaskStatus.WAITING_TOOL
                state.active_task_id = candidate.id
                return self._result(state, Action.RESUME_TASK, "已恢复之前的退款任务；会重新检查可能过期的资格信息。", candidate)

        # Explicit information-only question does not create a refund side-effect task.
        if any(k in content for k in ("退款多久到账", "退款一般多久", "退款规则")):
            return self._result(state, Action.ANSWER_QUESTION, "这是退款政策咨询，后续由知识库 Agent 提供有引用的回答。")

        if any(k in content for k in ("我要退款", "申请退款", "我想退款", "想要退款")):
            if active:
                active.status = TaskStatus.PAUSED
            new = self._new_task(state, "refund")
            if len(order_matches) == 1 and not any(k in content for k in ("不是", "不要查", "别查")):
                new.slots["order_id"] = order_matches[0]
                new.step = "check_eligibility"
                new.expected_input = None
                new.status = TaskStatus.WAITING_TOOL
                return self._result(state, Action.START_TASK, "已记录退款意向和订单号，尚未查询资格或执行退款。", new)
            return self._result(state, Action.START_TASK, "已创建退款咨询任务，请提供订单编号。", new)

        if active and active.expected_input == "order_id" and len(order_matches) == 1 and not any(k in content for k in ("不是", "不要查", "别查")):
            active.slots["order_id"] = order_matches[0]
            active.step = "check_eligibility"
            active.expected_input = None
            active.status = TaskStatus.WAITING_TOOL
            return self._result(state, Action.CONTINUE_TASK, "已记录订单号。需要接入真实业务工具校验退款/物流信息；当前没有执行外部操作。", active)

        if active:
            return self._result(state, Action.CLARIFY, "当前任务需要进一步理解您的意思。您要继续当前任务，还是发起其他咨询？", active)
        return self._result(state, Action.CLARIFY, "请描述您需要办理的业务，例如「我要退款」。")

    @staticmethod
    def _new_task(state: ConversationState, kind: str) -> TaskState:
        task = TaskState(type=kind, step="collect_order_id", slots={"order_id": None}, expected_input="order_id")
        state.tasks[task.id] = task
        state.active_task_id = task.id
        return task

    @staticmethod
    def _result(state: ConversationState, action: Action, response: str, task: TaskState | None = None) -> DialogueResult:
        return DialogueResult(action=action, response=response, state=state, intent=task.type if task else None, task_id=task.id if task else None)

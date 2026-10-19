"""纯状态归约器：校验策略决策并计算新状态与领域事件。"""

from typing import Any, Self

from pydantic import Field, model_validator

from agentorbis.domain.dialogue_policy import DialogueDecision, PolicyResult
from agentorbis.domain.state import (
    REQUIRED_SLOTS,
    ConversationState,
    CurrentFocus,
    TaskState,
)
from agentorbis.domain.understanding import Contract, PendingQuestion


class InvalidDecision(ValueError):
    """策略决策与当前状态冲突，整批归约应拒绝。"""


class DialogueEvent(Contract):
    """一次可审计的状态或策略事件，不含外部执行结果。"""

    event_id: str
    conversation_id: str
    version: int = Field(ge=0)
    event_type: str
    task_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ReductionResult(Contract):
    """归约产物，包含新状态及本轮生成的有序事件。"""

    state: ConversationState
    events: list[DialogueEvent] = Field(default_factory=list, max_length=48)

    @model_validator(mode="after")
    def validate_event_scope(self) -> Self:
        """确保本轮事件均属于同一个会话和状态版本。"""
        if any(
            event.conversation_id != self.state.conversation_id
            or event.version != self.state.version
            for event in self.events
        ):
            raise ValueError("Event does not match reduction state")
        return self


class StateReducer:
    """只依据旧状态和已校验决策生成新快照，不执行 I/O。"""

    def reduce(self, state: ConversationState, plan: PolicyResult) -> ReductionResult:
        """原子应用一组策略决策；任何非法动作都会拒绝整批变更。

        参数：
            state：归约前的不可变输入快照。
            plan：DialoguePolicy 生成的有序决策集合。

        返回：
            ReductionResult：新会话状态及对应领域事件。

        异常：
            InvalidDecision：决策目标缺失、状态转换非法或同批动作冲突。
        """
        # 所有修改都发生在深拷贝上；异常时调用方原状态保持不变。
        next_state = state.model_copy(deep=True)
        pending_events: list[tuple[str, str | None, dict[str, Any]]] = []
        changed = False
        seen_mutations: set[str] = set()

        for decision in plan.decisions:
            if decision.action in {
                "clarify", "resolve_clarification", "interrupt_clarification", "resume_clarification",
            }:
                if decision.action == "clarify":
                    if decision.clarification is None:
                        raise InvalidDecision("Clarification payload is missing")
                    if decision.clarification != next_state.pending_clarification:
                        next_state.pending_clarification = decision.clarification
                        pending_events.append(("clarification_requested", None, {
                            "clarification_id": decision.clarification.clarification_id,
                            "kind": decision.clarification.kind,
                            "question": decision.clarification.question,
                        }))
                        changed = True
                elif decision.action == "resume_clarification":
                    if next_state.pending_clarification is not None or not next_state.suspended_clarifications:
                        raise InvalidDecision("No suspended clarification can be resumed")
                    current = next_state.suspended_clarifications[-1]
                    if decision.clarification_id != current.clarification_id:
                        raise InvalidDecision("Clarification ID does not match suspended state")
                    next_state.suspended_clarifications.pop()
                    next_state.pending_clarification = current
                    pending_events.append(("clarification_resumed", None, {
                        "clarification_id": current.clarification_id,
                    }))
                    changed = True
                else:
                    current = next_state.pending_clarification
                    if current is None:
                        raise InvalidDecision("No pending clarification to resolve or interrupt")
                    if decision.clarification_id != current.clarification_id:
                        raise InvalidDecision("Clarification ID does not match current state")
                    if decision.action == "interrupt_clarification":
                        next_state.suspended_clarifications.append(current)
                    next_state.pending_clarification = None
                    event_type = (
                        "clarification_resolved"
                        if decision.action == "resolve_clarification"
                        else "clarification_interrupted"
                    )
                    pending_events.append((event_type, None, {
                        "clarification_id": current.clarification_id,
                    }))
                    changed = True
                continue

            if decision.action in {"answer_knowledge", "defer", "reject"}:
                if decision.action == "answer_knowledge":
                    next_state.current_focus = CurrentFocus(kind="policy_qa", intent="policy.consult")
                    changed = next_state.current_focus != state.current_focus or changed
                    pending_events.append(("knowledge_question_received", None, {
                        "act_id": decision.act_id,
                    }))
                else:
                    pending_events.append((
                        "conditional_action_deferred" if decision.action == "defer" else "action_rejected",
                        decision.task_id,
                        {"act_id": decision.act_id, "reason": decision.reason},
                    ))
                continue

            if decision.action not in {
                "create_task", "fill_slot", "correct_slot", "resume_task", "cancel_task",
            }:
                raise InvalidDecision("Unsupported decision action")
            target_key = decision.task_id or decision.act_id or ""
            if target_key in seen_mutations:
                raise InvalidDecision("A task may be mutated only once in one decision batch")
            seen_mutations.add(target_key)

            if decision.action == "create_task":
                if not decision.task_id or not decision.task_type:
                    raise InvalidDecision("Task creation needs an ID and type")
                if any(task.task_id == decision.task_id for task in next_state.tasks):
                    raise InvalidDecision("Task ID already exists")
                self._validate_entities(decision.entities, decision.task_type)
                task = TaskState(
                    task_id=decision.task_id,
                    type=decision.task_type,
                    status="collecting",
                    slots=decision.entities,
                )
                task.status = "ready" if not task.missing_slots else "collecting"
                next_state.tasks.append(task)
                next_state.active_task_id = task.task_id
                next_state.current_focus = CurrentFocus(kind="task", task_id=task.task_id)
                self._refresh_pending_question(next_state, task)
                pending_events.append(("task_created", task.task_id, {
                    "type": task.type, "slots": task.slots, "status": task.status,
                }))
                changed = True
                continue

            task = self._require_task(next_state, decision)
            if decision.action == "fill_slot":
                if task.status != "collecting":
                    raise InvalidDecision("Only a collecting task can receive missing slots")
                if len(decision.entities) != 1 or not set(decision.entities) <= set(task.missing_slots):
                    raise InvalidDecision("Slot answer must match a missing slot on the target task")
                self._validate_entities(decision.entities, task.type)
                task.slots.update(decision.entities)
                task.status = "ready" if not task.missing_slots else "collecting"
                self._refresh_pending_question(next_state, task)
                pending_events.append(("task_slot_filled", task.task_id, {
                    "slots": decision.entities, "status": task.status,
                }))
            elif decision.action == "correct_slot":
                if task.status not in {"collecting", "ready"}:
                    raise InvalidDecision("Task state does not allow slot correction")
                self._validate_entities(decision.entities, task.type)
                if not decision.entities or not set(decision.entities) <= set(task.slots):
                    raise InvalidDecision("Correction must replace an existing slot")
                task.slots.update(decision.entities)
                task.status = "ready" if not task.missing_slots else "collecting"
                self._refresh_pending_question(next_state, task)
                pending_events.append(("task_slot_corrected", task.task_id, {
                    "slots": decision.entities, "status": task.status,
                }))
            elif decision.action == "resume_task":
                if task.status not in {"collecting", "ready", "waiting_external"}:
                    raise InvalidDecision("Task state cannot be resumed")
                next_state.active_task_id = task.task_id
                next_state.current_focus = CurrentFocus(kind="task", task_id=task.task_id)
                self._refresh_pending_question(next_state, task)
                pending_events.append(("task_resumed", task.task_id, {"status": task.status}))
            else:
                if task.status in {"executing", "completed", "cancelled", "failed"}:
                    raise InvalidDecision("Task state cannot be cancelled")
                task.status = "cancelled"
                if next_state.active_task_id == task.task_id:
                    next_state.active_task_id = None
                if next_state.pending_question and next_state.pending_question.task_id == task.task_id:
                    next_state.pending_question = None
                self._refresh_pending_question(next_state)
                if next_state.current_focus.task_id == task.task_id:
                    next_state.current_focus = CurrentFocus()
                pending_events.append(("task_cancelled", task.task_id, {}))
            changed = True

        if changed:
            next_state.version = state.version + 1
        events = [
            DialogueEvent(
                event_id=f"{state.conversation_id}:{next_state.version}:{index}:{event_type}:{task_id or '-'}",
                conversation_id=state.conversation_id,
                version=next_state.version,
                event_type=event_type,
                task_id=task_id,
                payload=payload,
            )
            for index, (event_type, task_id, payload) in enumerate(pending_events, start=1)
        ]
        return ReductionResult(state=next_state, events=events)

    @staticmethod
    def _require_task(state: ConversationState, decision: DialogueDecision) -> TaskState:
        """查找决策目标并校验任务类型。"""
        task = next((item for item in state.tasks if item.task_id == decision.task_id), None)
        if task is None or (decision.task_type and task.type != decision.task_type):
            raise InvalidDecision("Decision target does not exist or has the wrong type")
        return task

    @staticmethod
    def _validate_entities(entities: dict[str, str], task_type: str) -> None:
        """限制槽位为对应业务类型支持的字段，并拒绝空值。"""
        allowed = set(REQUIRED_SLOTS[task_type])
        if any(slot not in allowed or not value.strip() for slot, value in entities.items()):
            raise InvalidDecision("Task contains an unsupported or empty slot")

    @staticmethod
    def _refresh_pending_question(state: ConversationState, task: TaskState | None = None) -> None:
        """更新当前提示问题，同时保留其他任务尚未填写的槽位问题。"""
        if task and task.status == "collecting" and task.missing_slots:
            selected = task
        else:
            current = next((
                item for item in state.tasks
                if state.pending_question and item.task_id == state.pending_question.task_id
            ), None)
            if (
                current and current.status == "collecting" and state.pending_question
                and state.pending_question.slot_name in current.missing_slots
            ):
                return
            selected = next((
                item for item in state.tasks if item.status == "collecting" and item.missing_slots
            ), None)
        if selected is None:
            state.pending_question = None
            return
        slot = selected.missing_slots[0]
        label = "订单号" if slot == "order_id" else "退款原因"
        state.pending_question = PendingQuestion(
            task_id=selected.task_id,
            slot_name=slot,
            question=f"请提供{label}。",
        )


def reduce_state(state: ConversationState, plan: PolicyResult) -> ReductionResult:
    """纯函数入口：依据会话状态和策略结果计算新状态与事件。

    参数：
        state：归约前会话快照。
        plan：策略层生成的决策批次。

    返回：
        ReductionResult：新快照及有序状态事件。
    """
    return StateReducer().reduce(state, plan)

"""确定性对话策略：把已校验的语义结果映射为待归约决策。"""

from collections import Counter
from typing import Literal, Self
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field, model_validator

from agentorbis.domain.state import ConversationState, TaskState
from agentorbis.domain.understanding import (
    Ambiguity,
    Contract,
    MessageAct,
    MessageUnderstanding,
    PendingClarificationContext,
)

TERMINAL_STATUSES = {"completed", "cancelled", "failed"}
class DialogueDecision(Contract):
    """策略层提出的一条状态或回复决策；本对象本身不会修改状态。"""

    action: Literal[
        "create_task", "fill_slot", "correct_slot", "resume_task", "cancel_task",
        "answer_knowledge", "clarify", "reject", "defer", "resolve_clarification",
        "interrupt_clarification", "resume_clarification",
    ]
    act_id: str | None = None
    task_id: str | None = None
    task_type: Literal["refund", "logistics"] | None = None
    entities: dict[str, str] = Field(default_factory=dict, max_length=10)
    question: str | None = None
    clarification: PendingClarificationContext | None = None
    clarification_id: str | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def validate_action_payload(self) -> Self:
        """校验决策动作所需的目标和载荷是否齐全。"""
        if self.action == "create_task" and (not self.task_id or not self.task_type):
            raise ValueError("Task creation needs an ID and type")
        if self.action in {"fill_slot", "correct_slot", "resume_task", "cancel_task"} and not self.task_id:
            raise ValueError("Task decision needs a task ID")
        if self.action == "clarify" and not self.clarification:
            raise ValueError("Clarification decision needs clarification state")
        if self.action in {"resolve_clarification", "interrupt_clarification", "resume_clarification"} and not self.clarification_id:
            raise ValueError("Clarification transition needs the current ID")
        return self


class PolicyResult(Contract):
    """一轮策略决策集合；Reducer 会将其中状态变化作为一个原子批次处理。"""

    decisions: list[DialogueDecision] = Field(default_factory=list, max_length=24)
    clarification_required: bool = False


class DialoguePolicy:
    """根据意图理解和当前状态选择任务目标，不执行 I/O 或业务副作用。"""

    def decide(
        self,
        state: ConversationState,
        understanding: MessageUnderstanding,
        message: str,
    ) -> PolicyResult:
        """为当前消息生成有序决策，并隔离不确定动作与可安全执行的动作。

        参数：
            state：当前会话快照，包含任务、焦点及待处理问题。
            understanding：Interpreter 返回并已通过结构校验的语义结果。
            message：触发本轮理解的原始消息，用于保存澄清来源。

        返回：
            PolicyResult：待归约的决策；其中不包含已执行的工具或数据库操作。
        """
        if state.pending_clarification:
            resumed = self._resolve_clarification(state, understanding, message)
            if resumed is not None:
                next_understanding, resolution = resumed
                base_state = state.model_copy(update={"pending_clarification": None})
                plan = self.decide(base_state, next_understanding, message)
                return PolicyResult(
                    decisions=[resolution, *plan.decisions],
                    clarification_required=plan.clarification_required,
                )
            interrupts_with_new_topic = any(
                (act.dialogue_act == "start_task" and act.target_hint == "new_task")
                or (act.business_intent == "policy_qa" and act.dialogue_act == "ask_question")
                for act in understanding.acts
            )
            if interrupts_with_new_topic and not understanding.ambiguities:
                plan = self._decide_without_pending(state, understanding, message)
                return PolicyResult(
                    decisions=[DialogueDecision(
                        action="interrupt_clarification",
                        clarification_id=state.pending_clarification.clarification_id,
                        reason="explicit_new_task_interrupts_pending_clarification",
                    ), *plan.decisions],
                    clarification_required=plan.clarification_required,
                )
            pending = state.pending_clarification
            return PolicyResult(decisions=[DialogueDecision(
                action="clarify", clarification=pending, question=pending.question,
            )], clarification_required=True)
        if state.suspended_clarifications and self._explicitly_resumes_clarification(message):
            pending = state.suspended_clarifications[-1]
            resumed_state = state.model_copy(deep=True)
            resumed_state.pending_clarification = pending
            resumed_state.suspended_clarifications.pop()
            resolved = self._resolve_clarification(resumed_state, understanding, message)
            if resolved is None:
                return PolicyResult(decisions=[
                    DialogueDecision(action="resume_clarification", clarification_id=pending.clarification_id),
                    DialogueDecision(action="clarify", clarification=pending, question=pending.question),
                ], clarification_required=True)
            next_understanding, resolution = resolved
            plan = self._decide_without_pending(resumed_state, next_understanding, message)
            return PolicyResult(
                decisions=[
                    DialogueDecision(action="resume_clarification", clarification_id=pending.clarification_id),
                    resolution,
                    *plan.decisions,
                ],
                clarification_required=plan.clarification_required,
            )
        return self._decide_without_pending(state, understanding, message)

    @staticmethod
    def _explicitly_resumes_clarification(message: str) -> bool:
        """只在用户明确指回先前确认时尝试恢复已暂存的澄清。"""
        has_reference = any(word in message for word in ("刚才", "上次", "之前", "前面"))
        has_resume = any(word in message for word in ("继续", "接着", "恢复", "那个问题", "那个确认"))
        return has_reference and has_resume

    def _decide_without_pending(
        self,
        state: ConversationState,
        understanding: MessageUnderstanding,
        message: str,
    ) -> PolicyResult:
        """完成无待澄清项时的预检查和决策构造。"""
        understanding = MessageUnderstanding(
            acts=understanding.acts,
            ambiguities=self._attribute_ambiguities(understanding),
            relations=understanding.relations,
        )
        targeted_ambiguities = [item for item in understanding.ambiguities if item.target_act_id]
        global_ambiguity = any(item.target_act_id is None for item in understanding.ambiguities)
        if global_ambiguity:
            ambiguity_index = next(
                index for index, item in enumerate(understanding.ambiguities)
                if item.target_act_id is None
            )
            clarification = self._make_clarification(
                state, understanding, message, ambiguity_index=ambiguity_index,
            )
            # 无法归属到单个动作的歧义可能改变整条消息的含义，因此继续阻止业务状态变化。
            decisions = [
                DialogueDecision(action="answer_knowledge", act_id=act.act_id, reason="policy_qa")
                for act in understanding.acts
                if act.business_intent == "policy_qa" and act.dialogue_act == "ask_question"
            ]
            decisions.append(DialogueDecision(
                action="clarify", clarification=clarification, question=clarification.question,
            ))
            return PolicyResult(decisions=decisions, clarification_required=True)

        conditional_ids = {
            relation.target_act_id
            for relation in understanding.relations
            if relation.kind == "condition"
        }
        decisions: list[DialogueDecision] = []
        clarifications: list[PendingClarificationContext] = []
        ambiguous_act_ids = {item.target_act_id for item in targeted_ambiguities}
        for act in understanding.acts:
            if act.act_id in ambiguous_act_ids:
                continue
            if act.act_id in conditional_ids:
                decisions.append(DialogueDecision(
                    action="defer", act_id=act.act_id,
                    reason="conditional_action_waits_for_external_result",
                ))
                continue
            if act.business_intent == "policy_qa" and act.dialogue_act == "ask_question":
                decisions.append(DialogueDecision(
                    action="answer_knowledge", act_id=act.act_id, reason="policy_qa",
                ))
                continue
            if act.business_intent == "unknown" or act.dialogue_act in {"reject", "other"}:
                decisions.append(DialogueDecision(
                    action="reject", act_id=act.act_id, reason="unsupported_or_non_actionable_intent",
                ))
                continue
            decision, target_error = self._decide_act(state, act)
            if decision is not None:
                decisions.append(decision)
            elif target_error:
                clarifications.append(self._task_clarification(state, understanding, message, act, target_error))

        if targeted_ambiguities:
            clarifications.insert(0, self._make_clarification(state, understanding, message))
        if clarifications:
            clarification = clarifications[0]
            decisions.append(DialogueDecision(
                action="clarify", clarification=clarification, question=clarification.question,
            ))
            return PolicyResult(decisions=decisions, clarification_required=True)
        return PolicyResult(decisions=decisions)

    @classmethod
    def _attribute_ambiguities(
        cls,
        understanding: MessageUnderstanding,
    ) -> list[Ambiguity]:
        """把可唯一归属的参数或任务歧义绑定到具体动作。

        参数：
            understanding：解释器产出的动作和歧义列表。

        返回：
            list[Ambiguity]：可确认目标动作的歧义已绑定 act_id，其余保持全局歧义。
        """
        attributed = []
        for ambiguity in understanding.ambiguities:
            if ambiguity.target_act_id is not None:
                attributed.append(ambiguity)
                continue
            target_act_id = None
            if ambiguity.kind == "parameter":
                slot = cls._infer_target_slot(ambiguity, understanding.acts)
                candidates = [
                    act for act in understanding.acts
                    if act.business_intent in {"refund", "logistics"}
                    and act.dialogue_act in {"start_task", "answer_pending", "correct"}
                    and slot is not None and slot not in act.entities
                ]
                if len(candidates) == 1:
                    target_act_id = candidates[0].act_id
            elif ambiguity.kind == "task":
                candidates = [
                    act for act in understanding.acts
                    if act.dialogue_act in {"resume", "correct", "cancel"}
                ]
                if len(candidates) == 1:
                    target_act_id = candidates[0].act_id
            attributed.append(
                ambiguity.model_copy(update={"target_act_id": target_act_id})
                if target_act_id else ambiguity
            )
        return attributed

    def _decide_act(
        self,
        state: ConversationState,
        act: MessageAct,
    ) -> tuple[DialogueDecision | None, str | None]:
        """为一个状态动作校验任务目标、动作类型和必需参数。"""
        if act.dialogue_act == "start_task":
            if act.business_intent not in {"refund", "logistics"}:
                return None, None
            if act.target_hint not in {"new_task", "unspecified"}:
                return None, "start_task_requires_new_target"
            task_id = str(uuid5(
                NAMESPACE_URL,
                f"agentorbis:{state.conversation_id}:{state.version}:{act.act_id}",
            ))
            return DialogueDecision(
                action="create_task", act_id=act.act_id, task_id=task_id,
                task_type=act.business_intent, entities=act.entities,
            ), None

        if act.dialogue_act == "answer_pending":
            slot_name = next((slot for slot in act.entities if slot in {"order_id", "reason"}), None)
            task = self._resolve_pending_task(state, act, slot_name)
            if task is None:
                return DialogueDecision(
                    action="reject", act_id=act.act_id, reason="no_pending_question",
                ), None
            if slot_name is None or slot_name not in task.missing_slots:
                return None, "pending_answer_missing_requested_slot"
            return DialogueDecision(
                action="fill_slot", act_id=act.act_id, task_id=task.task_id,
                task_type=task.type, entities={slot_name: act.entities[slot_name]},
            ), None

        if act.dialogue_act not in {"resume", "correct", "cancel"}:
            if act.dialogue_act == "ask_question" and act.business_intent == "policy_qa":
                return DialogueDecision(action="answer_knowledge", act_id=act.act_id), None
            return None, None

        task, error = self._resolve_task(state, act)
        if error:
            return None, error
        if task is None:
            return None, None
        action_by_act = {"resume": "resume_task", "correct": "correct_slot", "cancel": "cancel_task"}
        action = action_by_act[act.dialogue_act]
        if task.status in TERMINAL_STATUSES or task.status == "executing":
            return None, "task_state_does_not_allow_action"
        if action == "correct_slot" and not any(slot in task.slots for slot in act.entities):
            return None, "correction_does_not_identify_existing_slot"
        return DialogueDecision(
            action=action, act_id=act.act_id, task_id=task.task_id,
            task_type=task.type, entities=act.entities,
        ), None

    def _resolve_pending_task(
        self,
        state: ConversationState,
        act: MessageAct,
        slot_name: str | None,
    ) -> TaskState | None:
        """按显式任务、当前问题或唯一缺参任务定位 answer_pending 的目标。"""
        if slot_name is None:
            return None
        tasks = [
            task for task in state.tasks
            if task.type == act.business_intent and task.status == "collecting"
            and slot_name in task.missing_slots
        ]
        if act.referenced_task_id:
            return next((task for task in tasks if task.task_id == act.referenced_task_id), None)
        if act.target_hint == "active_task" and state.active_task_id:
            active = next((task for task in tasks if task.task_id == state.active_task_id), None)
            if active:
                return active
        pending = state.pending_question
        if pending and pending.slot_name == slot_name:
            selected = next((task for task in tasks if task.task_id == pending.task_id), None)
            if selected and selected.type == act.business_intent:
                return selected
        if len(tasks) == 1:
            return tasks[0]
        return None

    def _resolve_task(self, state: ConversationState, act: MessageAct) -> tuple[TaskState | None, str | None]:
        """按显式引用、明确提示和唯一上下文解析任务，不使用任意最近任务猜测。"""
        tasks = {task.task_id: task for task in state.tasks}
        if act.referenced_task_id:
            task = tasks.get(act.referenced_task_id)
            if task is None or task.type != act.business_intent:
                return None, "referenced_task_is_missing_or_wrong_type"
            return task, None
        if act.target_hint == "active_task" and state.active_task_id:
            task = tasks.get(state.active_task_id)
            if task and task.type == act.business_intent:
                return task, None
            return None, "active_task_type_mismatch"
        if act.target_hint == "explicit_task":
            return None, "explicit_task_id_missing"
        if act.target_hint == "previous_task":
            candidates = [
                task for task in state.tasks
                if task.type == act.business_intent and task.status not in TERMINAL_STATUSES
            ]
        else:
            candidates = [
                task for task in state.tasks
                if task.type == act.business_intent and task.status not in TERMINAL_STATUSES
            ]
        if len(candidates) == 1:
            return candidates[0], None
        if len(candidates) > 1:
            return None, "multiple_tasks_match"
        return None, "no_matching_task"

    @staticmethod
    def _task_by_id(state: ConversationState, task_id: str) -> TaskState | None:
        """按 ID 查找任务；未找到时返回 None。"""
        return next((task for task in state.tasks if task.task_id == task_id), None)

    def _make_clarification(
        self,
        state: ConversationState,
        understanding: MessageUnderstanding,
        message: str,
        *,
        ambiguity_index: int = 0,
    ) -> PendingClarificationContext:
        """把解释器报告的歧义冻结为下一轮可恢复的澄清上下文。"""
        ambiguity = understanding.ambiguities[ambiguity_index]
        candidate_task_ids = self._candidate_tasks(state, understanding.acts) if ambiguity.kind == "task" else []
        if ambiguity.kind == "task":
            # 模型有时会把任务 ID 放进 candidate_values；只接受当前 State 中存在的任务，
            # 并在用户可见的澄清文案中改用业务名称，避免泄露内部 ID。
            for candidate in ambiguity.candidate_values:
                task = self._task_by_id(state, candidate)
                if task and task.status not in TERMINAL_STATUSES and task.task_id not in candidate_task_ids:
                    candidate_task_ids.append(task.task_id)
            labels = [self._task_label(self._task_by_id(state, item)) for item in candidate_task_ids]
            label_counts = Counter(labels)
            label_indexes: Counter[str] = Counter()
            safe_labels = []
            for label in labels:
                label_indexes[label] += 1
                safe_labels.append(
                    f"第{label_indexes[label]}项{label}" if label_counts[label] > 1 else label
                )
            ambiguity = ambiguity.model_copy(update={"candidate_values": safe_labels})
            updated_ambiguities = list(understanding.ambiguities)
            updated_ambiguities[ambiguity_index] = ambiguity
            understanding = understanding.model_copy(update={"ambiguities": updated_ambiguities})
        target_slot = self._infer_target_slot(ambiguity, understanding.acts)
        target_act_id = ambiguity.target_act_id
        if target_act_id is None and ambiguity.kind == "parameter" and target_slot:
            candidates = [
                act for act in understanding.acts
                if act.business_intent in {"refund", "logistics"}
                and act.dialogue_act in {"start_task", "answer_pending", "correct"}
                and target_slot not in act.entities
            ]
            if len(candidates) == 1:
                target_act_id = candidates[0].act_id
        if target_act_id is None and ambiguity.kind == "task":
            candidates = [
                act for act in understanding.acts
                if act.dialogue_act in {"resume", "correct", "cancel"}
            ]
            if len(candidates) == 1:
                target_act_id = candidates[0].act_id
        if target_act_id is None and ambiguity.kind == "parameter":
            candidates = [
                act for act in understanding.acts
                if act.business_intent in {"refund", "logistics"}
                and act.dialogue_act in {"start_task", "answer_pending", "correct"}
                and target_slot and target_slot not in act.entities
            ]
            if len(candidates) == 1:
                target_act_id = candidates[0].act_id
        return self._clarification(
            state, understanding, message, ambiguity,
            candidate_task_ids=candidate_task_ids,
            target_ambiguity_index=ambiguity_index,
            target_act_id=target_act_id,
            target_slot=target_slot,
        )

    def _task_clarification(
        self,
        state: ConversationState,
        understanding: MessageUnderstanding,
        message: str,
        act: MessageAct,
        reason: str,
    ) -> PendingClarificationContext:
        """将任务目标或任务状态错误转成明确的澄清问题。"""
        candidates = self._candidate_tasks(state, [act])
        ambiguity = Ambiguity(
            kind="task" if reason == "multiple_tasks_match" else "other",
            candidate_values=[self._task_label(self._task_by_id(state, item)) for item in candidates],
            reason=reason,
        )
        return self._clarification(
            state, understanding, message, ambiguity, candidate_task_ids=candidates,
            target_act_id=act.act_id,
        )

    def _clarification(
        self,
        state: ConversationState,
        understanding: MessageUnderstanding,
        message: str,
        ambiguity: Ambiguity,
        *,
        candidate_task_ids: list[str] | None = None,
        target_act_id: str | None = None,
        target_ambiguity_index: int | None = None,
        target_slot: str | None = None,
    ) -> PendingClarificationContext:
        """创建确定性 ID 的澄清记录，并保留原消息动作和已确认实体。"""
        if target_act_id:
            targeted_ambiguities = [
                item for item in understanding.ambiguities if item.target_act_id
            ]
            if ambiguity.target_act_id:
                selected_ids = {item.target_act_id for item in targeted_ambiguities}
                selected_ambiguities = targeted_ambiguities
            else:
                selected_ids = {target_act_id}
                selected_ambiguities = [ambiguity]
            selected_acts = [act for act in understanding.acts if act.act_id in selected_ids]
            if selected_acts:
                selected_ambiguities = [
                    item.model_copy(update={"target_act_id": item.target_act_id or target_act_id})
                    for item in selected_ambiguities
                ]
                ambiguity = selected_ambiguities[0]
                selected_act_ids = {act.act_id for act in selected_acts}
                understanding = MessageUnderstanding(
                    acts=selected_acts,
                    ambiguities=selected_ambiguities,
                    relations=[
                        relation for relation in understanding.relations
                        if relation.source_act_id in selected_act_ids
                        and relation.target_act_id in selected_act_ids
                    ],
                )
                target_ambiguity_index = next(
                    index for index, item in enumerate(selected_ambiguities)
                    if item.target_act_id == target_act_id
                )
        entities: dict[str, str] = {}
        for act in understanding.acts:
            for name, value in act.entities.items():
                if name not in entities:
                    entities[name] = value
                elif entities[name] != value:
                    entities.pop(name, None)
        return PendingClarificationContext(
            clarification_id=str(uuid5(
                NAMESPACE_URL,
                f"agentorbis:clarification:{state.conversation_id}:{state.version}:{message}",
            )),
            kind=ambiguity.kind,
            question=self._clarification_question(ambiguity, understanding.acts, entities),
            original_message=message,
            candidate_values=ambiguity.candidate_values,
            candidate_task_ids=candidate_task_ids or [],
            target_act_id=target_act_id,
            target_ambiguity_index=target_ambiguity_index,
            target_slot=target_slot or ambiguity.target_slot,
            preserved_entities=entities,
            original_acts=understanding.acts,
            original_ambiguities=understanding.ambiguities,
            original_relations=understanding.relations,
        )

    @staticmethod
    def _clarification_question(
        ambiguity: Ambiguity,
        acts: list[MessageAct],
        preserved_entities: dict[str, str],
    ) -> str:
        """按歧义字段和业务动作生成可直接回答的澄清问题。"""
        if ambiguity.kind == "intent":
            return "你是想申请退款、查询物流，还是咨询退款政策？"
        if ambiguity.kind == "task":
            candidates = ambiguity.candidate_values
            options = "；".join(candidates)
            action = next((act.dialogue_act for act in acts if act.dialogue_act in {"resume", "correct", "cancel"}), None)
            verb = {"resume": "继续", "correct": "更正", "cancel": "取消"}.get(action, "处理")
            if options:
                return f"你想{verb}哪项任务？{options}"
            return f"我还不能确定要{verb}哪个任务，请提供对应的订单号或任务信息。"
        if ambiguity.kind == "parameter":
            slot = DialoguePolicy._infer_target_slot(ambiguity, acts, preserved_entities)
            intents = {act.business_intent for act in acts}
            candidates = ambiguity.candidate_values
            if slot == "order_id":
                if candidates:
                    return f"请确认要处理的订单号：{'、'.join(candidates)}。"
                task_name = "查询物流" if "logistics" in intents else "申请退款"
                return f"请提供要{task_name}的订单号。"
            if slot == "reason":
                if candidates:
                    return f"请确认退款原因：{'、'.join(candidates)}。"
                return "请说明申请退款的原因。"
            return "还缺少必要信息，请补充要处理的具体参数。"
        if ambiguity.kind == "other" and ambiguity.reason == "no_matching_task":
            return "我没有找到可继续处理的对应任务。你是想新建一项任务，还是补充订单号让我定位？"
        return "我还不能安全地确定要处理什么，请再具体说明一下。"

    @staticmethod
    def _infer_target_slot(
        ambiguity: Ambiguity,
        acts: list[MessageAct],
        preserved_entities: dict[str, str] | None = None,
    ) -> str | None:
        """从明确歧义字段、解释原因和待处理动作推断缺失参数名。"""
        if ambiguity.target_slot:
            return ambiguity.target_slot
        reason = ambiguity.reason.lower()
        if "订单号" in reason or "订单" in reason or "order_id" in reason:
            return "order_id"
        if "退款原因" in reason or "原因" in reason or "reason" in reason:
            return "reason"
        actionable = [
            act for act in acts
            if act.business_intent in {"refund", "logistics"}
            and act.dialogue_act in {"start_task", "answer_pending", "correct"}
        ]
        if any(act.business_intent == "logistics" for act in actionable):
            if not any(act.entities.get("order_id") for act in actionable if act.business_intent == "logistics"):
                return "order_id"
        refund_acts = [act for act in actionable if act.business_intent == "refund"]
        if refund_acts:
            has_order = any(act.entities.get("order_id") for act in refund_acts)
            has_reason = any(act.entities.get("reason") for act in refund_acts)
            if not has_order and not (preserved_entities or {}).get("order_id"):
                return "order_id"
            if not has_reason:
                return "reason"
        return None

    @staticmethod
    def _candidate_tasks(state: ConversationState, acts: list[MessageAct]) -> list[str]:
        """按歧义动作类型列出仍可继续的候选任务 ID。"""
        intents = {act.business_intent for act in acts if act.business_intent in {"refund", "logistics"}}
        return [
            task.task_id for task in state.tasks
            if task.type in intents and task.status not in TERMINAL_STATUSES
        ]

    @staticmethod
    def _task_label(task: TaskState | None) -> str:
        """生成不泄露内部状态的任务候选提示。"""
        if task is None:
            return "对应业务任务"
        order_id = task.slots.get("order_id")
        name = "退款任务" if task.type == "refund" else "物流查询任务"
        return f"{name}（订单 {order_id}）" if order_id else name

    def _resolve_clarification(
        self,
        state: ConversationState,
        answer: MessageUnderstanding,
        message: str,
    ) -> tuple[MessageUnderstanding, DialogueDecision] | None:
        """根据本轮明确回答恢复原始理解；无法唯一选择时返回 None。"""
        pending = state.pending_clarification
        if pending is None or answer.ambiguities or len(answer.acts) != 1:
            return None
        response_act = answer.acts[0]
        selected: MessageUnderstanding | None = None
        if pending.kind == "intent" and response_act.business_intent in {
            "refund", "logistics", "policy_qa",
        }:
            if len(pending.original_acts) > 1:
                return None
            if response_act.business_intent == "policy_qa":
                selected = MessageUnderstanding(acts=[response_act], ambiguities=[], relations=[])
            else:
                base = pending.original_acts[0] if pending.original_acts else response_act
                acts = [base.model_copy(update={
                    "business_intent": response_act.business_intent,
                    "dialogue_act": "start_task",
                    "target_hint": "new_task",
                    "referenced_task_id": None,
                    "entities": pending.preserved_entities or base.entities,
                })]
                selected = MessageUnderstanding(
                    acts=acts, ambiguities=self._remaining_ambiguities(pending),
                    relations=pending.original_relations,
                )
        elif pending.kind == "task":
            task_id = response_act.referenced_task_id
            if task_id is None and response_act.target_hint == "active_task":
                task_id = state.active_task_id
            if task_id is None:
                ordinal = self._selected_ordinal(message, len(pending.candidate_task_ids))
                if ordinal is not None:
                    task_id = pending.candidate_task_ids[ordinal]
            if task_id in pending.candidate_task_ids:
                original = pending.original_acts or [response_act]
                target_ids = {pending.target_act_id} if pending.target_act_id else {
                    original[0].act_id
                } if len(original) == 1 else set()
                if not target_ids:
                    return None
                acts = [act.model_copy(update={
                    "referenced_task_id": task_id, "target_hint": "explicit_task",
                }) if act.act_id in target_ids else act for act in original]
                selected = MessageUnderstanding(
                    acts=acts, ambiguities=self._remaining_ambiguities(pending),
                    relations=pending.original_relations,
                )
        elif pending.kind == "parameter":
            slot = pending.target_slot
            matches: list[tuple[str, str]] = []
            if slot and slot in response_act.entities:
                value = response_act.entities[slot]
                if not pending.candidate_values or value in pending.candidate_values:
                    matches.append((slot, value))
            if not matches:
                matches = [
                    (slot_name, value)
                    for slot_name, value in response_act.entities.items()
                    if value in pending.candidate_values
                    and (slot is None or slot_name == slot)
                ]
            # 用户可能用“第一个/第二个”选择候选；只在候选顺序明确时映射。
            ordinal = self._selected_ordinal(message, len(pending.candidate_values))
            if not matches and ordinal is not None:
                candidates = pending.candidate_values[ordinal]
                if slot:
                    matches = [(slot, candidates)]
            if len(matches) == 1:
                slot, value = matches[0]
                original = pending.original_acts or [response_act]
                target_act_id = pending.target_act_id
                if target_act_id is None and len(original) == 1:
                    target_act_id = original[0].act_id
                if target_act_id is None:
                    candidates = [
                        act for act in original
                        if act.business_intent in {"refund", "logistics"}
                        and act.dialogue_act in {"start_task", "answer_pending", "correct"}
                        and slot not in act.entities
                    ]
                    if len(candidates) == 1:
                        target_act_id = candidates[0].act_id
                if target_act_id is None:
                    return None
                acts = [act.model_copy(update={
                    "entities": {**act.entities, slot: value},
                }) if act.act_id == target_act_id else act for act in original]
                selected = MessageUnderstanding(
                    acts=acts, ambiguities=self._remaining_ambiguities(pending),
                    relations=pending.original_relations,
                )
        if selected is None:
            return None
        return selected, DialogueDecision(
            action="resolve_clarification", clarification_id=pending.clarification_id,
        )

    @staticmethod
    def _selected_ordinal(message: str, candidate_count: int) -> int | None:
        """将明确的中文序号答案转换成候选下标。"""
        if candidate_count < 2:
            return None
        text = message.strip().replace("第", "").replace("个", "").replace("项", "")
        ordinals = {"一": 0, "1": 0, "二": 1, "2": 1, "三": 2, "3": 2, "四": 3, "4": 3}
        value = ordinals.get(text)
        return value if value is not None and value < candidate_count else None

    @staticmethod
    def _remaining_ambiguities(
        pending: PendingClarificationContext,
    ) -> list[Ambiguity]:
        """返回尚未澄清的歧义，支持一轮只问一个最小问题。"""
        if pending.target_ambiguity_index is None:
            return pending.original_ambiguities
        return [
            item for index, item in enumerate(pending.original_ambiguities)
            if index != pending.target_ambiguity_index
        ]

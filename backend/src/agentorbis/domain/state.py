"""对话领域状态：任务、会话焦点、待补参数和待澄清项。"""

from typing import Literal, Self

from pydantic import Field, model_validator

from agentorbis.domain.understanding import (
    Contract,
    PendingClarificationContext,
    PendingQuestion,
)

TaskStatus = Literal[
    "collecting", "ready", "executing", "waiting_external", "completed", "cancelled", "failed",
]
TaskType = Literal["refund", "logistics"]

REQUIRED_SLOTS: dict[TaskType, tuple[str, ...]] = {
    "refund": ("order_id", "reason"),
    "logistics": ("order_id",),
}


class TaskState(Contract):
    """单个业务任务的权威领域状态。

    属性：
        task_id：任务唯一标识，由策略层按会话版本确定性生成。
        type：退款或物流任务类型。
        status：任务当前阶段；ready 只表示参数齐备，不代表操作已执行。
        slots：已由对话策略确认写入的业务参数。
    """

    task_id: str = Field(min_length=1, max_length=120)
    type: TaskType
    status: TaskStatus = "collecting"
    slots: dict[str, str | None] = Field(default_factory=dict, max_length=10)

    @model_validator(mode="after")
    def validate_task_slots(self) -> Self:
        """拒绝当前任务类型不支持的槽位和自相矛盾的 ready 状态。"""
        allowed = set(REQUIRED_SLOTS[self.type])
        if any(slot not in allowed for slot in self.slots):
            raise ValueError("Task has a slot unsupported by its type")
        if self.status == "ready" and self.missing_slots:
            raise ValueError("Ready task is missing required slots")
        return self

    @property
    def missing_slots(self) -> tuple[str, ...]:
        """按任务类型返回尚未填写的必需参数。

        参数：无。

        返回：
            tuple[str, ...]：缺失槽位名，按固定询问顺序排列。
        """
        return tuple(slot for slot in REQUIRED_SLOTS[self.type] if not self.slots.get(slot))


class CurrentFocus(Contract):
    """用户当前讨论焦点；与正在进行的业务任务指针分开保存。"""

    kind: Literal["none", "task", "policy_qa"] = "none"
    task_id: str | None = None
    intent: str | None = None

    @model_validator(mode="after")
    def validate_focus(self) -> Self:
        """确保任务焦点带任务 ID，非任务焦点不带任务 ID。"""
        if (self.kind == "task") != (self.task_id is not None):
            raise ValueError("Task focus must reference exactly one task")
        if self.kind == "policy_qa" and self.intent != "policy_qa":
            raise ValueError("Knowledge focus must identify policy_qa")
        return self


class ConversationState(Contract):
    """可独立测试的会话状态快照；不包含数据库或外部服务对象。"""

    conversation_id: str = Field(min_length=1, max_length=120)
    version: int = Field(default=0, ge=0)
    tasks: list[TaskState] = Field(default_factory=list, max_length=100)
    active_task_id: str | None = None
    current_focus: CurrentFocus = Field(default_factory=CurrentFocus)
    pending_question: PendingQuestion | None = None
    pending_clarification: PendingClarificationContext | None = None
    suspended_clarifications: list[PendingClarificationContext] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        """拒绝重复任务和指向不存在任务的会话状态。"""
        task_ids = {task.task_id for task in self.tasks}
        if len(task_ids) != len(self.tasks):
            raise ValueError("Duplicate task IDs")
        references = [self.active_task_id]
        if self.pending_question:
            references.append(self.pending_question.task_id)
        if self.current_focus.task_id:
            references.append(self.current_focus.task_id)
        if any(task_id is not None and task_id not in task_ids for task_id in references):
            raise ValueError("Conversation state references an unknown task")
        if self.pending_question:
            task = next(item for item in self.tasks if item.task_id == self.pending_question.task_id)
            if task.status != "collecting" or self.pending_question.slot_name not in task.missing_slots:
                raise ValueError("Pending question does not match a missing task slot")
        if self.pending_clarification and not set(self.pending_clarification.candidate_task_ids) <= task_ids:
            raise ValueError("Clarification references an unknown task")
        if any(
            not set(item.candidate_task_ids) <= task_ids
            for item in self.suspended_clarifications
        ):
            raise ValueError("Suspended clarification references an unknown task")
        return self

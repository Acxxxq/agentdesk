from __future__ import annotations

from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class Action(StrEnum):
    START_TASK = "START_TASK"
    CONTINUE_TASK = "CONTINUE_TASK"
    UPDATE_SLOT = "UPDATE_SLOT"
    SWITCH_TASK = "SWITCH_TASK"
    RESUME_TASK = "RESUME_TASK"
    CANCEL_TASK = "CANCEL_TASK"
    ANSWER_QUESTION = "ANSWER_QUESTION"
    CLARIFY = "CLARIFY"


class TaskStatus(StrEnum):
    WAITING_INPUT = "waiting_input"
    WAITING_TOOL = "waiting_tool"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class TaskState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    status: TaskStatus = TaskStatus.WAITING_INPUT
    step: str
    slots: dict[str, str | None] = Field(default_factory=dict)
    expected_input: str | None = None


class ConversationState(BaseModel):
    active_task_id: str | None = None
    tasks: dict[str, TaskState] = Field(default_factory=dict)

    def active_task(self) -> TaskState | None:
        return self.tasks.get(self.active_task_id) if self.active_task_id else None


class DialogueResult(BaseModel):
    action: Action
    response: str
    state: ConversationState
    intent: str | None = None
    task_id: str | None = None

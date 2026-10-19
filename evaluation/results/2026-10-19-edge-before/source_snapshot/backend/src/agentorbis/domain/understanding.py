"""意图识别边界契约：模型候选实体不能直接作为已确认的业务状态。"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

Intent = Literal["refund", "logistics", "policy_qa", "unknown"]


class Contract(BaseModel):
    """严格的传输对象基类，拒绝未约定字段并清理文本首尾空白。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class MessageAct(Contract):
    """单条消息中的一个语义动作；任务指向和实体仍需后续 Policy 确认。"""

    act_id: str = Field(min_length=1, max_length=40)
    business_intent: Intent
    dialogue_act: Literal[
        "start_task", "answer_pending", "resume", "correct", "cancel",
        "ask_question", "confirm", "reject", "other",
    ]
    target_hint: Literal[
        "new_task", "active_task", "previous_task", "explicit_task", "unspecified",
    ] = "unspecified"
    referenced_task_id: str | None = None
    entities: dict[str, str] = Field(default_factory=dict, max_length=10)
    utterance_span: str = Field(min_length=1, max_length=4000)
    uncertainty: Literal["low", "medium", "high"] = "medium"


class Ambiguity(Contract):
    """语义歧义和候选解释，供后续澄清策略消费；不代表已经发起澄清。"""

    kind: Literal["intent", "task", "parameter", "other"]
    candidate_values: list[str] = Field(default_factory=list, max_length=10)
    reason: str = Field(default="", max_length=1000)


class ActRelation(Contract):
    """动作间的并列、顺序或条件依赖；条件仅记录，不在 Demo 中执行。"""

    source_act_id: str
    target_act_id: str
    kind: Literal["parallel", "sequence", "condition"]
    condition: str | None = None


class UnderstandingPayload(Contract):
    """模型返回的语义结构，校验动作 ID 唯一性及关系引用完整性。"""

    # 三个集合必须显式返回，防止将缺失/不完整的工具输出静默解释为“无意图”。
    acts: list[MessageAct] = Field(max_length=8, description="当前消息中全部语义动作，无动作时显式传空数组")
    ambiguities: list[Ambiguity] = Field(max_length=8, description="语义歧义，无歧义时显式传空数组")
    relations: list[ActRelation] = Field(max_length=16, description="动作关系，无关系时显式传空数组")

    @model_validator(mode="after")
    def validate_relations(self) -> Self:
        """拒绝重复动作、悬空/自引用关系，以及缺少描述的条件依赖；返回本对象。"""
        ids = {act.act_id for act in self.acts}
        if len(ids) != len(self.acts):
            raise ValueError("Duplicate act IDs")
        for relation in self.relations:
            if relation.source_act_id not in ids or relation.target_act_id not in ids:
                raise ValueError("Unknown act in relation")
            if relation.source_act_id == relation.target_act_id:
                raise ValueError("Self relation is invalid")
            if relation.kind == "condition" and not (relation.condition or "").strip():
                raise ValueError("Conditional relation needs a description")
        return self


class MessageUnderstanding(UnderstandingPayload):
    """解析结果；source 由服务端添加，不接受模型声明结果来源。"""

    source: Literal["llm"] = "llm"


class RecentMessage(Contract):
    """最近的用户或助手消息，仅用于语境解释，不作为系统指令。"""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class TaskSummary(Contract):
    """调用方提供的只读任务摘要；本阶段不负责创建、授权或保存任务。"""

    task_id: str = Field(min_length=1, max_length=120)
    type: Literal["refund", "logistics"]
    status: Literal[
        "collecting", "ready", "executing", "waiting_external", "completed", "cancelled", "failed",
    ]
    slots: dict[str, str | None] = Field(default_factory=dict, max_length=10)


class PendingQuestion(Contract):
    """待回答的问题，用于解释简短回答，不能覆盖明确的新意图。"""

    task_id: str
    slot_name: Literal["order_id", "reason"]
    question: str = Field(min_length=1, max_length=1000)


class ConversationContext(Contract):
    """本轮只读会话上下文；临时咨询焦点与活动业务任务相互独立。"""

    active_task_id: str | None = None
    current_focus: str | None = None
    pending_question: PendingQuestion | None = None


class InterpretationRequest(Contract):
    """Demo 输入：当前消息、最近消息及任务摘要，不从数据库自动加载。"""

    message: str = Field(min_length=1, max_length=4000)
    recent_messages: list[RecentMessage] = Field(default_factory=list, max_length=10)
    conversation: ConversationContext = Field(default_factory=ConversationContext)
    task_summaries: list[TaskSummary] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def validate_context(self) -> Self:
        """检查调用方的任务摘要是否唯一，并保证会话指针引用已提供的任务。"""
        ids = {task.task_id for task in self.task_summaries}
        if len(ids) != len(self.task_summaries):
            raise ValueError("Duplicate task IDs")
        references = [self.conversation.active_task_id]
        if self.conversation.pending_question:
            references.append(self.conversation.pending_question.task_id)
        if any(ref is not None and ref not in ids for ref in references):
            raise ValueError("Conversation references an unknown task")
        return self

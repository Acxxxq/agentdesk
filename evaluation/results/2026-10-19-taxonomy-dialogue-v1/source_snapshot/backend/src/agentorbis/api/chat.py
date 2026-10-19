"""聊天工作流 API：串联意图理解、对话策略和纯状态归约。"""

import asyncio
from collections import OrderedDict
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import Field

from agentorbis.domain.dialogue_policy import DialoguePolicy, PolicyResult
from agentorbis.domain.state import ConversationState, TaskState
from agentorbis.domain.state_reducer import InvalidDecision, ReductionResult, reduce_state
from agentorbis.domain.understanding import (
    Contract,
    ConversationContext,
    InterpretationRequest,
    MessageUnderstanding,
    PendingQuestion,
    RecentMessage,
    TaskSummary,
)
from agentorbis.infrastructure.llm.message_interpreter import InterpretationError


class ChatRequest(Contract):
    """聊天请求；conversation_id 为空时创建一段全新会话。"""

    conversation_id: UUID | None = None
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(Contract):
    """聊天回复及本轮可检查的理解、策略和状态变化。"""

    conversation_id: UUID
    reply: str
    understanding: MessageUnderstanding
    policy: PolicyResult
    state: ConversationState
    events: list[dict[str, object]] = Field(default_factory=list)


class ConversationSnapshot(Contract):
    """页面重新打开时恢复的最近对话及权威会话状态。"""

    conversation_id: UUID
    recent_messages: list[RecentMessage]
    state: ConversationState


@dataclass
class ConversationSession:
    """开发环境中的单会话快照和串行锁。"""

    state: ConversationState
    recent_messages: list[RecentMessage] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class ConversationSessionStore:
    """进程内会话存储；后续由 MySQL 仓储替换。"""

    def __init__(self, max_sessions: int = 500) -> None:
        """初始化有上限的会话注册表，避免开发服务无限累积内存。"""
        self._sessions: OrderedDict[UUID, ConversationSession] = OrderedDict()
        self._registry_lock = asyncio.Lock()
        self._max_sessions = max_sessions

    async def get_or_create(self, conversation_id: UUID | None) -> tuple[UUID, ConversationSession]:
        """读取已有会话或创建新会话；未知 ID 不会被静默重置。"""
        async with self._registry_lock:
            if conversation_id is not None:
                session = self._sessions.get(conversation_id)
                if session is None:
                    raise LookupError("conversation_not_found")
                self._sessions.move_to_end(conversation_id)
                return conversation_id, session
            if len(self._sessions) >= self._max_sessions:
                self._sessions.popitem(last=False)
            new_id = uuid4()
            session = ConversationSession(
                state=ConversationState(conversation_id=str(new_id)),
            )
            self._sessions[new_id] = session
            return new_id, session


router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.get("/chat/{conversation_id}", response_model=ConversationSnapshot)
async def get_conversation(conversation_id: UUID, request: Request) -> ConversationSnapshot:
    """读取当前进程中的会话快照，供聊天页面刷新后恢复显示。"""
    from agentorbis.intent_demo import DemoSettings

    if DemoSettings().app_env != "development":
        raise HTTPException(503, detail="demo_disabled")
    store: ConversationSessionStore = request.app.state.conversation_store
    try:
        _, session = await store.get_or_create(conversation_id)
    except LookupError:
        raise HTTPException(404, detail="conversation_not_found") from None
    async with session.lock:
        return ConversationSnapshot(
            conversation_id=conversation_id,
            recent_messages=session.recent_messages,
            state=session.state,
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    """理解当前消息、制定策略并原子更新当前内存会话。"""
    from agentorbis.intent_demo import DemoSettings

    if DemoSettings().app_env != "development":
        raise HTTPException(503, detail="demo_disabled")
    interpreter = getattr(request.app.state, "interpreter", None)
    if interpreter is None:
        raise HTTPException(503, detail="missing_api_key")
    store: ConversationSessionStore = request.app.state.conversation_store
    try:
        conversation_id, session = await store.get_or_create(body.conversation_id)
    except LookupError:
        raise HTTPException(404, detail="conversation_not_found") from None

    async with session.lock:
        interpretation_request = _make_interpretation_request(session, body.message)
        try:
            understanding = await interpreter.interpret(interpretation_request)
        except InterpretationError as exc:
            status = 504 if str(exc) == "provider_timeout" else 502
            raise HTTPException(status, detail=str(exc)) from None

        policy = DialoguePolicy().decide(session.state, understanding, body.message)
        try:
            reduction = reduce_state(session.state, policy)
        except InvalidDecision:
            raise HTTPException(409, detail="state_conflict") from None

        reply = _build_reply(policy, reduction)
        session.state = reduction.state
        session.recent_messages.extend([
            RecentMessage(role="user", content=body.message),
            RecentMessage(role="assistant", content=reply),
        ])
        session.recent_messages = session.recent_messages[-10:]
        return ChatResponse(
            conversation_id=conversation_id,
            reply=reply,
            understanding=understanding,
            policy=policy,
            state=reduction.state,
            events=[event.model_dump() for event in reduction.events],
        )


def _make_interpretation_request(session: ConversationSession, message: str) -> InterpretationRequest:
    """从服务端权威会话构建解释器的只读上下文。"""
    state = session.state
    pending_question = None
    if state.pending_question:
        pending_question = PendingQuestion(
            task_id=state.pending_question.task_id,
            slot_name=state.pending_question.slot_name,
            question=state.pending_question.question,
        )
    context = ConversationContext(
        active_task_id=state.active_task_id,
        current_focus=(
            f"task:{state.current_focus.task_id}"
            if state.current_focus.kind == "task"
            else state.current_focus.kind
        ),
        pending_question=pending_question,
        pending_questions=[
            PendingQuestion(
                task_id=task.task_id,
                slot_name=task.missing_slots[0],
                question=(
                    "请提供退款订单号。" if task.type == "refund"
                    and task.missing_slots[0] == "order_id"
                    else "请说明申请退款的原因。" if task.type == "refund"
                    else "请提供物流查询订单号。"
                ),
            )
            for task in state.tasks
            if task.status == "collecting" and task.missing_slots
        ],
        pending_clarification=state.pending_clarification,
        suspended_clarifications=state.suspended_clarifications,
    )
    summaries = [TaskSummary(
        task_id=task.task_id,
        type=task.type,
        status=task.status,
        slots=task.slots,
    ) for task in state.tasks]
    return InterpretationRequest(
        message=message,
        recent_messages=session.recent_messages[-10:],
        conversation=context,
        task_summaries=summaries,
    )


def _build_reply(
    policy: PolicyResult,
    reduction: ReductionResult,
) -> str:
    """根据策略动作和归约后状态生成不虚构执行结果的中文回复。"""
    replies: list[str] = []
    for decision in policy.decisions:
        task = _find_task(reduction.state.tasks, decision.task_id)
        if decision.action == "create_task" and task:
            name = "退款" if task.type == "refund" else "物流查询"
            replies.append(f"已为你建立{name}任务。{_task_next_step(task)}")
        elif decision.action == "fill_slot" and task:
            replies.append(f"已记录你补充的信息。{_task_next_step(task)}")
        elif decision.action == "resume_task" and task:
            replies.append(f"已恢复这个任务。{_task_next_step(task)}")
        elif decision.action == "correct_slot" and task:
            replies.append(f"已更新任务信息。{_task_next_step(task)}")
        elif decision.action == "cancel_task":
            task_name = "退款申请" if task and task.type == "refund" else "任务"
            replies.append(f"已取消这项{task_name}。")
        elif decision.action == "clarify":
            replies.append(decision.question or "我需要再确认一下你要处理的内容。")
        elif decision.action == "answer_knowledge":
            replies.append("我识别到你在咨询退款政策。目前还没有接入政策知识库，所以不会编造政策答案。")
        elif decision.action == "defer":
            replies.append("这项操作依赖一个尚未确认的条件，我已暂缓处理。")
        elif decision.action == "reject":
            replies.append("我还不能安全地把这句话映射到支持的业务操作，请再说明一下要办理什么。")
    if not replies:
        return "你好，我可以帮你识别退款或物流请求。你也可以在一段对话里切换话题，或先咨询退款政策。"
    return "\n\n".join(dict.fromkeys(replies))


def _find_task(tasks: list[TaskState], task_id: str | None) -> TaskState | None:
    """按 ID 读取归约后的任务快照。"""
    if task_id is None:
        return None
    return next((task for task in tasks if task.task_id == task_id), None)


def _task_next_step(task: TaskState) -> str:
    """描述任务当前缺少的信息或尚未连接的真实服务。"""
    if task.missing_slots:
        slot = task.missing_slots[0]
        label = "订单号" if slot == "order_id" else "退款原因"
        return f"请提供{label}。"
    if task.type == "logistics":
        return "订单信息已齐备；当前还没有连接真实物流查询服务。"
    return "所需信息已齐备；当前还没有连接真实退款服务。"

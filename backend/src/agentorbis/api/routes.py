from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agentorbis.core.settings import get_settings
from agentorbis.domain.dialogue import DialogueManager
from agentorbis.domain.state import ConversationState
from agentorbis.infrastructure.db import get_session
from agentorbis.infrastructure.models import Conversation, Message, Turn

router = APIRouter(prefix="/api/v1")
SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Actor(BaseModel):
    tenant_id: str = "dev-tenant"
    user_id: str


def get_actor(x_demo_user: Annotated[str | None, Header()] = None) -> Actor:
    if get_settings().app_env != "development":
        raise HTTPException(503, "Demo authentication disabled. Configure real authentication before deployment.")
    if not x_demo_user or not x_demo_user.strip():
        raise HTTPException(401, "X-Demo-User required for LOCAL DEVELOPMENT only")
    return Actor(user_id=x_demo_user.strip())


ActorDep = Annotated[Actor, Depends(get_actor)]


class ConversationOut(BaseModel):
    id: str
    version: int
    state: ConversationState


class TurnIn(BaseModel):
    request_id: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=4000)


class TurnOut(BaseModel):
    request_id: str
    action: str
    response: str
    version: int
    state: ConversationState
    replayed: bool = False


async def get_authorized_conv(session: AsyncSession, actor: Actor, conv_id: str, lock: bool = False) -> Conversation:
    stmt = select(Conversation).where(
        Conversation.id == conv_id,
        Conversation.owner_id == actor.user_id,
        Conversation.tenant_id == actor.tenant_id,
    )
    if lock:
        stmt = stmt.with_for_update()
    conv = (await session.execute(stmt)).scalar_one_or_none()
    if conv is None:
        raise HTTPException(404, "Conversation not found")
    return conv


@router.post("/conversations", response_model=ConversationOut)
async def create_conversation(session: SessionDep, actor: ActorDep):
    conv = Conversation(
        id=str(uuid4()),
        owner_id=actor.user_id,
        tenant_id=actor.tenant_id,
        state=ConversationState().model_dump(mode="json"),
        version=0,
    )
    async with session.begin():
        session.add(conv)
    return ConversationOut(id=conv.id, state=ConversationState.model_validate(conv.state), version=conv.version)


@router.get("/conversations/{conv_id}", response_model=ConversationOut)
async def read_conversation(conv_id: str, session: SessionDep, actor: ActorDep):
    conv = await get_authorized_conv(session, actor, conv_id)
    return ConversationOut(id=conv.id, version=conv.version, state=ConversationState.model_validate(conv.state))


@router.post("/conversations/{conv_id}/turns", response_model=TurnOut)
async def create_turn(conv_id: str, body: TurnIn, session: SessionDep, actor: ActorDep):
    # This transaction is short and LOCAL deterministic only. Never await external LLM/tool work while holding this lock.
    async with session.begin():
        conv = await get_authorized_conv(session, actor, conv_id, lock=True)
        previous = (await session.execute(
            select(Turn).where(Turn.conversation_id == conv_id, Turn.request_id == body.request_id)
        )).scalar_one_or_none()
        if previous:
            if previous.input_message != body.message:
                raise HTTPException(409, "request_id reused with a different message")
            return TurnOut(request_id=previous.request_id, action=previous.action, response=previous.response,
                           version=conv.version, state=ConversationState.model_validate(conv.state), replayed=True)
        decision = DialogueManager().handle(ConversationState.model_validate(conv.state), body.message)
        turn = Turn(id=str(uuid4()), conversation_id=conv_id, request_id=body.request_id,
                    input_message=body.message, action=decision.action.value, response=decision.response)
        # No ORM relationships are configured, so establish the parent row before
        # inserting messages. Flush remains inside the same atomic transaction.
        session.add(turn)
        await session.flush()
        session.add_all([
            Message(conversation_id=conv_id, turn_id=turn.id, role="user", content=body.message),
            Message(conversation_id=conv_id, turn_id=turn.id, role="assistant", content=decision.response),
        ])
        conv.state = decision.state.model_dump(mode="json")
        conv.version += 1
    return TurnOut(request_id=body.request_id, action=decision.action.value, response=decision.response,
                   version=conv.version, state=decision.state)

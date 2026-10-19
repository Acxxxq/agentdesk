"""AgentOrbis FastAPI 应用入口：组装意图识别接口与本地聊天测试页。"""

from fastapi import FastAPI

from agentorbis.api.chat import ConversationSessionStore
from agentorbis.api.chat import router as chat_router
from agentorbis.api.demo import router as demo_router
from agentorbis.intent_demo import lifespan
from agentorbis.intent_demo import router as intent_router

app = FastAPI(title="AgentOrbis", version="0.2.0", lifespan=lifespan)
app.state.conversation_store = ConversationSessionStore()
app.include_router(intent_router)
app.include_router(chat_router)
app.include_router(demo_router)


@app.get("/health/live", tags=["health"])
def live() -> dict[str, str]:
    """返回进程存活状态，供容器健康检查使用。

    参数：无。

    返回：
        dict[str, str]：固定的运行状态。
    """
    return {"status": "ok"}

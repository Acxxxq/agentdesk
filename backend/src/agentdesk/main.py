from fastapi import FastAPI

from agentdesk.api.routes import router

app = FastAPI(title="AgentDesk (foundation)", version="0.1.0")
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "scope": "foundation_only"}

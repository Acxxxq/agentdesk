from fastapi import FastAPI
from fastapi.responses import JSONResponse

from agentdesk.api.routes import router
from agentdesk.infrastructure import health as dependency_health

app = FastAPI(title="AgentDesk (foundation)", version="0.1.0")
app.include_router(router)


@app.get("/health")
@app.get("/health/live")
def health():
    return {"status": "ok", "scope": "foundation_only"}


@app.get("/health/ready")
async def ready():
    result = await dependency_health.report({"mysql": dependency_health.probe_mysql})
    return JSONResponse(result, status_code=200 if result["status"] == "ok" else 503)


@app.get("/health/dependencies")
async def dependencies():
    result = await dependency_health.report({
        "mysql": dependency_health.probe_mysql,
        "redis": dependency_health.probe_redis,
        "milvus": dependency_health.probe_milvus,
        "objectstore": dependency_health.probe_objectstore,
    })
    return JSONResponse(result, status_code=200 if result["status"] == "ok" else 503)

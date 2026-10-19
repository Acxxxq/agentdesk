"""开发环境的聊天测试页；静态资源随 API 镜像发布。"""

from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from agentorbis.intent_demo import DemoSettings

WEB_ROOT = Path(__file__).resolve().parents[1] / "web"


def require_development() -> None:
    """仅允许开发环境读取聊天页及静态资源。

    参数：无；由 FastAPI 依赖注入执行。

    返回：
        None：开发环境通过；其他环境抛出 HTTP 404。
    """
    if DemoSettings().app_env != "development":
        raise HTTPException(404, detail="Not found")


router = APIRouter(include_in_schema=False, dependencies=[Depends(require_development)])


@router.get("/demo")
async def chat_demo() -> FileResponse:
    """返回中文聊天测试页。

    参数：无。

    返回：
        FileResponse：带禁用缓存响应头的静态 HTML 文件。
    """
    return FileResponse(WEB_ROOT / "chat.html", headers={"Cache-Control": "no-cache"})


@router.get("/demo/assets/{name}")
async def demo_asset(name: Literal["chat.css", "chat.js"]) -> FileResponse:
    """返回页面所需的 CSS 或 JavaScript 文件。

    参数：
        name：限定为 chat.css 或 chat.js，拒绝任意路径输入。

    返回：
        FileResponse：带禁用缓存响应头的静态资源文件。
    """
    return FileResponse(WEB_ROOT / name, headers={"Cache-Control": "no-cache"})

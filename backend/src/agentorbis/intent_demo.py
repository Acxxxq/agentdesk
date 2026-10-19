"""意图识别应用配置、FastAPI 路由与命令行入口；不修改业务状态。"""

import argparse
import asyncio
import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from anthropic import AsyncAnthropic
from fastapi import APIRouter, FastAPI, HTTPException, Request
from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from agentorbis.domain.understanding import InterpretationRequest, MessageUnderstanding
from agentorbis.infrastructure.llm.message_interpreter import (
    InterpretationError,
    MessageInterpreter,
)


class DemoSettings(BaseSettings):
    """读取模型服务和应用运行配置。

    属性：
        app_env：应用环境，仅 development 开放交互式意图识别接口。
        api_key：模型服务密钥，以 SecretStr 保存以避免对象打印时泄露。
        model：模型名称。
        base_url：Anthropic 兼容 API 地址。
        timeout_seconds：单次 SDK 请求超时，范围为 1～120 秒。
    """

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ANTHROPIC_", extra="ignore")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    api_key: SecretStr = Field(default=SecretStr(""))
    model: str = "deepseek-v4-pro"
    base_url: str = "https://api.deepseek.com/anthropic"
    timeout_seconds: float = Field(default=45, gt=0, le=120)


def create_client(settings: DemoSettings) -> AsyncAnthropic:
    """创建禁用 SDK 自动重试的客户端。

    参数：
        settings：经过校验的模型服务配置。

    返回：
        AsyncAnthropic：供解释器共享或调用的异步 SDK 客户端。

    异常：
        InterpretationError：密钥缺失时抛出稳定错误码。
    """
    if not settings.api_key.get_secret_value().strip():
        raise InterpretationError("missing_api_key")
    return AsyncAnthropic(
        api_key=settings.api_key.get_secret_value(), base_url=settings.base_url,
        timeout=settings.timeout_seconds, max_retries=0,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """管理 API 进程级 SDK 客户端的创建和关闭。

    参数：
        app：当前 FastAPI 应用实例。

    返回：
        AsyncIterator：应用运行期间持有客户端，关闭时释放其连接池。
    """
    settings = DemoSettings()
    client = create_client(settings) if settings.api_key.get_secret_value().strip() else None
    app.state.interpreter = MessageInterpreter(client, settings.model) if client else None
    try:
        yield
    finally:
        if client:
            await client.close()


router = APIRouter(prefix="/api/v1", tags=["intent-demo"])


@router.post("/interpret", response_model=MessageUnderstanding)
async def interpret(body: InterpretationRequest, request: Request) -> MessageUnderstanding:
    """解释一条消息并返回已校验的语义结构。

    参数：
        body：当前消息及可选的只读历史和任务摘要。
        request：FastAPI 请求对象，用于取得进程级解释器。

    返回：
        MessageUnderstanding：结构化动作、歧义、关系及服务端结果来源。

    说明：
        非开发环境或缺少密钥时返回 503；输入校验错误由 FastAPI 返回 422；
        模型超时返回 504，其他模型边界错误返回脱敏的 502。
    """
    if DemoSettings().app_env != "development":
        raise HTTPException(503, detail="demo_disabled")
    interpreter = getattr(request.app.state, "interpreter", None)
    if interpreter is None:
        raise HTTPException(503, detail="missing_api_key")
    try:
        return await interpreter.interpret(body)
    except InterpretationError as exc:
        raise HTTPException(504 if str(exc) == "provider_timeout" else 502, detail=str(exc)) from None


async def run_request(request: InterpretationRequest) -> MessageUnderstanding:
    """为命令行创建短生命周期客户端并解析一条请求。

    参数：
        request：待解释的消息与可选上下文。

    返回：
        MessageUnderstanding：通过结构和证据校验的语义结果。
    """
    settings = DemoSettings()
    async with create_client(settings) as client:
        return await MessageInterpreter(client, settings.model).interpret(request)


def main() -> None:
    """读取命令行消息或 JSON 请求文件并打印结果。

    参数：无；参数由 argparse 从进程命令行解析。

    返回：
        None：成功时向标准输出打印 JSON；输入或模型错误时以非零状态退出。
    """
    parser = argparse.ArgumentParser(description="AgentOrbis 意图识别 Demo")
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--message", help="仅识别一条消息，不提供任务上下文")
    inputs.add_argument("--request", type=Path, help="包含上下文的 JSON 请求文件")
    args = parser.parse_args()
    try:
        request = (
            InterpretationRequest.model_validate_json(args.request.read_text(encoding="utf-8"))
            if args.request else InterpretationRequest(message=args.message)
        )
        result = asyncio.run(run_request(request))
    except (ValidationError, ValueError, OSError):
        # 校验异常包含输入片段，不能直接打印异常正文。
        print(json.dumps({"error": "invalid_request_or_config"}), file=sys.stderr)
        raise SystemExit(2) from None
    except InterpretationError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(1) from None
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

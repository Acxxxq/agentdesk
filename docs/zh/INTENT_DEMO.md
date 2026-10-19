# 意图识别模块

**语言：**[English](../INTENT_DEMO.md) | 简体中文

意图识别是 AgentOrbis 第一个正式实现的模块。`/demo` 工作台现调用 `POST /api/v1/chat`，将语义解析与确定性对话策略、内存状态归约器串联起来。只想查看结构化解析且不改变任务状态时，可调用 `POST /api/v1/interpret`。两个接口都不会执行外部业务工具。

## 启动

从模板创建 `.env`，填写 `ANTHROPIC_API_KEY`，然后在 Docker 中启动 API：

```bash
docker run --rm --mount "type=bind,source=${PWD},target=/workspace" -w /workspace python:3.12-slim python scripts/generate_env.py
docker compose up -d --build --wait api
```

打开 [Agent 工作台](http://127.0.0.1:18000/demo)，或在[API 文档](http://127.0.0.1:18000/docs)中调用 `POST /api/v1/chat` 或 `POST /api/v1/interpret`：

```json
{"message": "先查 A1001 物流，再申请 A2002 退款"}
```

带上下文的请求样例保存在 `backend/examples/intent/`。在容器中可这样提交：

```bash
docker compose exec api python -m agentorbis.intent_demo --request examples/intent/topic_switch.json
```

本地聊天路由仅在 `APP_ENV=development` 时开放。会话暂存在 API 进程内存，服务重启后清空。独立解释接口的上下文由调用方提供；聊天流程则从自身会话状态构建上下文。

## 输入、输出与限制

输入包含当前消息、最多十条最近消息、会话指针和最多二十个任务摘要。输出含零个或多个动作、歧义及动作关系，版本为 `taxonomy_version: "1.0"`。业务意图为 `refund.apply`、`logistics.track`、`policy.consult` 和兼容兜底 `unknown`。旧语义输入别名可恢复，但响应统一使用正式 ID；任务摘要的 type 继续使用 `refund`、`logistics`。详见[分类体系](INTENT_TAXONOMY.md)。候选实体仅包括 `order_id`、`reason`，且必须能在当前消息中逐字找到。结构校验通过不等于语义一定正确。

模型适配器使用 `anthropic.AsyncAnthropic` 和仅用于传输数据的命名工具结构，不会执行工具。SDK 自动重试已关闭。结构化输出不合法时最多再请求一次纠正；超时和供应商错误不重试。API 错误响应经过脱敏。

## 评测和测试

冻结数据集、评分实现、全部运行记录和对照报告集中保存在[`evaluation/`](../../evaluation/README.md)。当前原始合成集为 80/80，边界集为 24/24；模型结构不合法时最多进行一次纠正。这些结果仅是开发回归结果，不代表生产准确率。

在 Docker 中运行模拟模型服务的单元测试和代码检查，无需模型密钥：

```bash
docker compose --profile test run --build --rm tests
```

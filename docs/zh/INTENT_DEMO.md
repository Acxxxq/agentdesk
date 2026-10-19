# 意图识别模块

**语言：**[English](../INTENT_DEMO.md) | 简体中文

这是 AgentOrbis 第一个正式实现的模块。它读取当前消息和调用方可选提供的上下文，返回结构化业务动作、候选实体、动作关系及歧义；它没有任务状态写权限，也不会执行任何业务工具。

## 启动

从模板创建 `.env`，填写 `ANTHROPIC_API_KEY`，然后在 Docker 中启动 API：

```bash
docker run --rm --mount "type=bind,source=${PWD},target=/workspace" -w /workspace python:3.12-slim python scripts/generate_env.py
docker compose up -d --build --wait api
```

打开[聊天测试页](http://127.0.0.1:18000/demo)，或在[API 文档](http://127.0.0.1:18000/docs)中调用 `POST /api/v1/interpret`：

```json
{"message": "先查 A1001 物流，再申请 A2002 退款"}
```

带上下文的请求样例保存在 `backend/examples/intent/`。在容器中可这样提交：

```bash
docker compose exec api python -m agentorbis.intent_demo --request examples/intent/topic_switch.json
```

本地测试路由仅在 `APP_ENV=development` 时开放。上下文由调用方提供，解释器不会读取或授权真实任务。

## 输入、输出与限制

输入包含当前消息、最多十条最近消息、会话指针和最多二十个任务摘要。输出含零个或多个动作、歧义及动作关系。支持的意图为 `refund`、`logistics`、`policy_qa` 和 `unknown`。候选实体仅包括 `order_id`、`reason`，且必须能在当前消息中逐字找到。结构校验通过不等于语义一定正确。

模型适配器使用 `anthropic.AsyncAnthropic` 和仅用于传输数据的命名工具结构，不会执行工具。SDK 自动重试已关闭。结构化输出不合法时最多再请求一次纠正；超时和供应商错误不重试。API 错误响应经过脱敏。

## 评测和测试

冻结数据集、评分实现、全部运行记录和对照报告集中保存在[`evaluation/`](../../evaluation/README.md)。当前原始合成集为 80/80，边界集为 24/24；模型结构不合法时最多进行一次纠正。这些结果仅是开发回归结果，不代表生产准确率。

在 Docker 中运行模拟模型服务的单元测试和代码检查，无需模型密钥：

```bash
docker compose --profile test run --build --rm tests
```

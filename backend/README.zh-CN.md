# 意图识别服务

**语言：**[English](README.md) | 简体中文

后端提供 `POST /api/v1/interpret`，并在 `/demo` 提供中文聊天测试页。服务使用严格的 Pydantic 契约和 Anthropic Python SDK，结合当前消息及可选只读上下文输出语义结构；不会持久化或执行业务任务。

通过仓库根目录的 Docker Compose 配置运行。使用说明见[意图识别指南](../docs/zh/INTENT_DEMO.md)，评测证据见[评测记录](../evaluation/README.md)。

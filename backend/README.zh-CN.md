# 意图识别服务

**语言：**[English](README.md) | 简体中文

后端提供 `POST /api/v1/interpret` 意图解析接口，以及 `POST /api/v1/chat` 完整聊天工作流。`/demo` 是 AgentOrbis 的正式前端工作台，串联意图解析、对话策略和纯状态归约，并可查看会话任务与状态事件。会话当前只保存在 API 进程内存中，服务重启后清空；尚未连接 MySQL，也不会执行真实退款、物流查询或政策问答。

通过仓库根目录的 Docker Compose 配置运行。使用说明见[意图识别指南](../docs/zh/INTENT_DEMO.md)，评测证据见[评测记录](../evaluation/README.md)。

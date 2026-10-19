# AgentOrbis

**企业级 AI Agent 平台**

为真实业务流程构建可靠的 Agent。

**语言：**[English](README.md) | 简体中文

AgentOrbis 从一个范围清晰、可以评测的意图识别模块开始。它结合当前消息和只读会话上下文识别业务动作、提取有原文依据的实体并报告歧义。现在 `/demo` 已接入确定性对话策略与纯状态归约器，可在内存会话中真实演练任务状态变化。

## 第一个模块：意图识别

- FastAPI 接口：`POST /api/v1/interpret`
- 使用 Anthropic Python SDK，可连接 DeepSeek 等兼容接口
- 使用严格的 Pydantic 输出契约和证据校验
- 处理话题与意图切换、多动作、任务指向和歧义
- `/demo` 提供中文聊天测试页
- 固定合成数据集和可复现评测记录集中保存在 [`evaluation/`](evaluation/README.md)

## 正在开发：对话策略与状态归约

- 确定性选择创建、补充、恢复、更正或取消任务
- 在意图、目标任务或参数不明确时保存澄清上下文
- 纯内存状态归约器输出新状态和领域事件，不调用数据库或外部工具
- 聊天页面和 API 已接入；会话暂存于服务进程内存，MySQL 尚未接入

当前评测集是项目作者编写的开发集。分数用于指导迭代，不代表生产准确率，也不是盲测基准。

## 使用 Docker 启动

安装 Git 和 Docker Desktop 或 Docker Engine，然后执行：

```bash
git clone https://github.com/Acxxxq/agentdesk.git agentorbis
cd agentorbis
docker run --rm --mount "type=bind,source=${PWD},target=/workspace" -w /workspace python:3.12-slim python scripts/generate_env.py
```

在被 Git 忽略的 `.env` 中填写模型服务密钥，然后启动 API：

```bash
docker compose up -d --build --wait api
```

打开 [Agent 工作台](http://127.0.0.1:18000/demo)或 [API 文档](http://127.0.0.1:18000/docs)。工作台现已接入意图解析、对话策略和内存状态归约；默认端口为 `18000`，可在 `.env` 中修改 `API_PORT`。

在容器中运行离线测试和代码检查：

```bash
docker compose --profile test run --build --rm tests
```

详情见 [Docker 指南](docs/zh/DOCKER.md)和[意图识别指南](docs/zh/INTENT_DEMO.md)。

## 项目方向

意图理解器是 AgentOrbis 的第一个正式模块。当前进入对话策略与状态归约阶段，完成状态规则后再接入持久化和工具执行。更完整的目标架构记录在[平台规划](docs/zh/PLATFORM_PLAN.md)。

## 文档

- [系统架构](docs/zh/ARCHITECTURE.md)
- [意图分类体系 v1](docs/zh/INTENT_TAXONOMY.md)
- [开发路线图](docs/zh/ROADMAP.md)
- [开发日志](docs/zh/DEVLOG.md)
- [代码规范与中文注释](docs/zh/CODE_STYLE.md)
- [评测数据与结果](evaluation/README.md)
- [参与贡献](CONTRIBUTING.zh-CN.md)

## 许可证

[MIT](LICENSE) © 2026 Acxxxq。

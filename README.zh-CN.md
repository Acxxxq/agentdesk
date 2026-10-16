# AgentOrbis

**企业级 AI Agent 平台**

为真实业务流程构建可靠的 Agent。

**语言：**[English](README.md) | 简体中文

AgentOrbis 是一个面向企业客服场景的开源 Agent 平台，逐步实现多轮对话、Agent 编排、工具调用和 RAG，并从可运行的基础版本开始演进。

**当前范围：**项目目前包含基于规则的对话与任务演示、MySQL 会话状态、请求去重、隔离的 Docker 开发环境和依赖诊断。真实 LLM 路由、订单/退款工具、RAG 流程、身份认证、长期记忆、异步 Worker 和前端仍在规划中。

## 快速开始

安装 Git 和支持 Linux 容器的 Docker（Windows 用户可使用 Docker Desktop + WSL 2）。Python、MySQL、Redis 和 Milvus 均通过容器运行。在 PowerShell、Linux 或 macOS 终端执行：

```bash
git clone https://github.com/Acxxxq/agentdesk.git agentorbis
cd agentorbis
docker run --rm --mount "type=bind,source=${PWD},target=/workspace" -w /workspace python:3.12-slim python scripts/generate_env.py
docker compose config --quiet
docker compose up -d --build --wait
```

环境生成脚本会创建被 Git 忽略的 `.env`，并为不同服务生成独立随机密码；如果文件已存在，脚本会拒绝覆盖，此时跳过生成命令。启动与排错细节见 [Docker 指南](docs/DOCKER.md)。

打开 [API 文档](http://127.0.0.1:18000/docs)，或检查服务状态：

```bash
curl http://127.0.0.1:18000/health/ready
curl http://127.0.0.1:18000/health/dependencies
```

Windows PowerShell 中若 `curl` 被解析为 PowerShell 别名，请使用 `curl.exe`。

## 开发与测试

开发后端时使用源代码挂载和自动重载：

```bash
docker compose -f compose.yaml -f compose.dev.yaml up -d --build --wait
docker compose logs -f api
```

无需启动基础设施即可运行离线测试：

```bash
docker compose --profile test build tests
docker compose --profile test run --rm --no-deps tests
```

GitHub Actions 使用相同的容器命令。测试覆盖确定性的对话状态转换和就绪检查；依赖真实基础设施的验证单独执行。

## 对话演示

通过本地开发身份请求头创建会话，再发送 `我要退款` 和 `A1001`，每次请求使用不同的请求 ID。API 文档包含请求结构和交互示例。

```bash
curl http://127.0.0.1:18000/api/v1/conversations -H 'X-Demo-User: user_001' -H 'Content-Type: application/json' -d '{}'
```

重复提交相同请求 ID 可以避免重复处理该消息，但这不代表外部业务工具具有幂等性。当前演示不会实际提交退款。

## 架构与部署

- Python 3.12、FastAPI、Pydantic v2、SQLAlchemy 异步接口和 Alembic。
- MySQL 8.4 保存权威业务状态；Redis 提供缓存和队列基础设施。
- Milvus 2.6.24 使用独立的 etcd 和 MinIO；另一套 MinIO 保存应用文档。
- 当前采用模块化单体架构，包含确定性的任务状态转换，并为后续模型和工具适配器预留扩展点。
- 独立的一次性容器负责数据库迁移和初始化私有文档 Bucket。
- 可选的 Attu 管理界面：`docker compose --profile admin up -d attu`。

所有服务使用隔离的 `agentdesk` 网络和命名数据卷，宿主机端口仅绑定到本机。现有 EchoMind 和 Milvus 实例继续使用各自的数据和端口。开发 API 使用演示身份请求头；部署到互联网前必须接入真实身份认证和租户授权。

## 项目文档

- [系统架构](docs/zh/ARCHITECTURE.md)
- [技术选型决策](docs/zh/ADR-001-stack.md)
- [开发路线图](docs/zh/ROADMAP.md)
- [开发日志](docs/zh/DEVLOG.md)
- [代码规范](docs/zh/CODE_STYLE.md)
- [参与贡献](CONTRIBUTING.zh-CN.md)
- [中文文档索引](docs/zh/README.md)

## 许可证

[MIT](LICENSE) © 2026 Acxxxq。

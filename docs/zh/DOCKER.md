# AgentOrbis Docker 开发环境

**语言：**[English](../DOCKER.md) | 简体中文

## 服务与端口

宿主机端口仅绑定到 `127.0.0.1`。容器通过服务名和内部端口通信。

| 服务 | 用途 | 宿主机端口 |
|---|---|---|
| `api` | FastAPI 对话 API | 18000 |
| `mysql` | 业务状态，MySQL 8.4 | 53306 |
| `redis` | 带密码和 AOF 的 Redis 7.4 | 56379 |
| `milvus` | Milvus 2.6.24，内嵌 Woodpecker | 29530 / Web UI 29091 |
| `etcd` | Milvus 元数据 | 仅内部访问 |
| `milvus-minio` | Milvus 内部对象和 WAL | 仅内部访问 |
| `document-minio` | 应用文档对象存储 | S3 19000 / 控制台 19001 |
| `migrate` | 执行 Alembic 迁移后退出 | 无 |
| `bucket-init` | 创建私有 `agentdesk-documents` Bucket 后退出 | 无 |
| `tests` | 离线测试和代码检查，`test` Profile | 无 |
| `attu` | 可选的 Milvus 管理界面，`admin` Profile | 13000 |

Worker 和前端容器会在对应功能实现后加入。

## 首次启动

在仓库根目录运行：

```bash
docker run --rm --mount "type=bind,source=${PWD},target=/workspace" -w /workspace python:3.12-slim python scripts/generate_env.py
docker compose config --quiet
docker compose up -d --build --wait
docker compose ps -a
```

MySQL 和 MinIO 会在首次启动时初始化账号。请保留 `.env` 及其数据卷；只改 `.env` 中的密码不会轮换已创建的 MySQL 账号。生成脚本不会覆盖已有 `.env`。根目录 `.env` 是 Compose 配置来源，应用配置通过容器环境变量传入。MySQL 时间戳使用 UTC。生成的密码使用 URL 安全字符；手动设置密码后拼入连接 URL 前需要进行 URL 编码。

## 开发与测试

```bash
docker compose -f compose.yaml -f compose.dev.yaml up -d --build --wait
docker compose logs -f api
docker compose --profile test build tests
docker compose --profile test run --rm --no-deps tests
```

开发 API 使用可编辑安装，并将源码挂载到 `/app/src`。为兼容 Windows Docker Desktop，自动重载使用轮询方式。依赖变更后需重建镜像；测试文件变更后也需重建测试镜像。默认运行镜像使用打包安装，不挂载源码。

需要验证真实 MySQL 和运行中 API 时，先启动开发环境，再执行：

```bash
docker compose --profile test run --rm --no-deps -e AGENTORBIS_INTEGRATION_URL=http://api:8000 tests
```

该验证会创建隔离的演示会话，并检查轮次写入、请求重放、冲突请求 ID 和会话归属。默认离线测试会跳过此项。可选初始化依赖需要 Docker Compose 2.20 或更新版本。

## 健康检查与管理

- `/health` 和 `/health/live`：检查进程是否响应，不调用依赖服务。
- `/health/ready`：检查 MySQL 是否可用；失败时返回 503。
- `/health/dependencies`：并发检查 MySQL、Redis、Milvus 和文档 Bucket，带有超时限制；可选依赖失败不会影响核心就绪状态。

诊断响应只返回异常类型，不暴露凭据或连接字符串。RAG 基础设施可用不代表 RAG 流程已经实现。`migrate` 和 `bucket-init` 显示 `Exited (0)` 属于预期；非零退出表示执行失败。

启动 Attu 管理界面：

```bash
docker compose --profile admin up -d attu
```

打开 `http://127.0.0.1:13000/login`，按页面流程创建首个管理员。预配置 Milvus 地址为 `milvus:19530`。文档 MinIO 控制台地址是 `http://127.0.0.1:19001`，凭据来自 `.env` 中的 `DOCUMENT_MINIO_USER` 和 `DOCUMENT_MINIO_PASSWORD`。

## 数据持久化与环境隔离

命名数据卷属于 `agentdesk` Compose 项目。配置不使用固定容器名、共享外部网络，也不挂载旧 Milvus 数据目录。现有 EchoMind 和 Milvus 服务保持独立；复用镜像不会复用其他实例的数据。

Woodpecker 明确使用 MinIO。MinIO 镜像固定为 `milvusdb/minio:RELEASE.2024-12-18T13-15-44Z`，以满足 [Milvus Woodpecker 配置要求](https://milvus.io/docs/v2.6.x/use-woodpecker.md)。两套 MinIO 使用独立凭据。文档存储凭据用于本地管理，生产环境应改用权限受限的服务账号。

停止后重新启动容器不会删除数据：

```bash
docker compose stop
docker compose start
```

除非确认要删除本项目数据，否则不要运行 `docker compose down -v`。旧 Milvus 数据迁移需要单独制定备份和导入方案；复制单个数据卷或修改消息队列配置都不构成迁移。

## 排错

```bash
docker compose ps -a
docker compose logs --tail=100 mysql migrate bucket-init api milvus
```

若宿主机端口被占用，请在根目录 `.env` 中调整端口并重建对应服务。若同时运行两个 Milvus，请检查 Docker Desktop 分配的内存。基础设施配置已从 `infra/compose.yaml` 移至根目录 `compose.yaml`。此环境面向本地开发；API 部署到互联网前仍需接入真实身份认证和租户授权。

## 改名兼容说明

项目现名为 AgentOrbis。为保持现有数据访问，Compose 项目名（`agentdesk`）、存储 Bucket 和本地凭据沿用原标识。Python 包名已改为 `agentorbis`，集成测试使用 `AGENTORBIS_INTEGRATION_URL`。Git 远程地址和工作目录保留现有路径，后续单独迁移。

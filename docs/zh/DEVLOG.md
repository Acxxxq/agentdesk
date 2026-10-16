# AgentOrbis 开发日志

**语言：**[English](../DEVLOG.md) | 简体中文

本日志记录重要里程碑和工程决策。详细代码变更由 Git 提交记录；计划工作由 Issue 跟踪。

## 2026-10-14 — AgentOrbis 初始基础版本

- 确定项目名称为 AgentDesk（2026-10-16 更名为 AgentOrbis），采用 MIT 许可证。
- 将 Python 包名和应用配置统一为 `agentorbis`。
- 选择 MySQL 8.4、SQLAlchemy 异步接口、asyncmy 和 Alembic 保存业务状态。
- 初始版本包含对话 API、JSON 会话状态、请求去重和确定性的对话/任务演示。
- 在 `docs/` 下整理架构决策和交付路线图。
- 验证：10 个对话测试通过；Ruff、Compose 配置检查和离线 MySQL 迁移 SQL 生成检查通过。

基础版本尚未实现真实 LLM 路由、产生业务副作用的工具、认证适配器、RAG 和前端。MySQL 仍需进行连接真实服务的集成验证。

## 日志格式

每个有意义的里程碑记录日期、问题、变更、验证结果和下一步；如有对应 Issue 或 Pull Request，请附上链接。

## 2026-10-14 — 统一 Docker 开发环境

- 将提供的基础设施 Starter 整合进现有 AgentOrbis API。
- 将 Compose 文件移至仓库根目录；增加源码热重载和容器化测试。
- 为 Milvus 配置独立的 etcd 和内部 MinIO，应用文档使用另一套 MinIO。
- 明确选择内嵌 Woodpecker，并使用兼容的 MinIO 镜像。
- 增加本地随机凭据、一次性数据库迁移和文档 Bucket 初始化。
- 区分进程存活检查、MySQL 就绪检查和可选依赖诊断。
- CI 和贡献指南统一使用容器测试流程。
- 真实 MySQL 验证发现写入消息时父轮次尚未插入；现在在同一事务中显式 flush 轮次。
- 增加可选的运行中服务 API 回归检查，与离线测试分开执行。

### 2026-10-15 — Docker 环境验证

- 运行时、迁移、Bucket 初始化、开发和测试镜像均构建成功。
- 开启真实 MySQL/API 回归验证后，14 个测试全部通过；Ruff 和离线迁移 SQL 生成检查通过。
- MySQL、Redis、Milvus 和文档 Bucket 连通性检查均返回 `ok`。
- 重建 MySQL 和 API 容器后，对话状态仍然保留。
- 补充可编辑安装所需的构建依赖，并记录在 `/login` 创建 Attu 本地管理员的步骤。
- 测试客户端会产生一条上游 HTTPX 弃用警告；测试结果通过。

## 2026-10-16 — 项目更名为 AgentOrbis

- 将品牌和 Python 包统一更名为 AgentOrbis / `agentorbis`。
- 同步更新包引用、容器启动入口和中英文文档。
- 保留现有 Compose/存储标识和 Git 远程地址，保持兼容。

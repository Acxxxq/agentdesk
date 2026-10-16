# 后端基础

**语言：**[English](README.md) | 简体中文

API 使用 MySQL 8.4 和 Alembic 管理数据库迁移，异步连接方言为 `mysql+asyncmy`。请通过仓库根目录的 Compose 配置运行开发环境和测试，详见 [Docker 指南](../docs/zh/DOCKER.md)。领域测试不依赖数据库。

`X-Demo-User` 仅用于本地开发，不能代替正式身份认证。JWT/OIDC 尚未接入；生产模式下相关路由会拒绝未认证请求。

此基础项目尚不能公开部署，也不能用于执行真实退款操作。

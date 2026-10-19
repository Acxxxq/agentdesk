# Docker 开发环境

**语言：**[English](../DOCKER.md) | 简体中文

意图识别阶段只需要一个应用容器。MySQL、Redis 和 Milvus 会在后续模块真正需要时加入。

## 首次配置

只需创建一次本地环境文件：

```bash
docker run --rm --mount "type=bind,source=${PWD},target=/workspace" -w /workspace python:3.12-slim python scripts/generate_env.py
```

在 `.env` 中填写 `ANTHROPIC_API_KEY`。模板默认连接 DeepSeek 的 Anthropic 兼容接口，也可以在文件中修改模型名和服务地址。

## 启动与查看

```bash
docker compose config --quiet
docker compose up -d --build --wait api
docker compose ps
docker compose logs -f api
```

打开 `http://127.0.0.1:18000/demo` 使用聊天测试页，或访问 `http://127.0.0.1:18000/docs` 查看 API。默认只绑定本机地址。

## 离线检查

测试配置通过模拟模型服务运行单元测试，无需 API 密钥：

```bash
docker compose --profile test run --build --rm tests
```

当前阶段不挂载基础设施数据卷。旧版环境若曾创建 MySQL、Redis 或 Milvus 数据卷，本 Compose 配置不会引用或删除它们。

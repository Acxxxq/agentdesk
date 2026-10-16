# 参与 AgentOrbis 开发

**语言：**[English](CONTRIBUTING.md) | 简体中文

开始之前，请阅读 [项目介绍](README.zh-CN.md)、[路线图](docs/zh/ROADMAP.md) 和[代码规范](docs/zh/CODE_STYLE.md)。如果准备进行较大的架构调整，请先提交 Issue，说明要解决的问题和预期行为，便于讨论方案。

## 开发环境

项目使用 Git 和 Docker。按照 README 生成仓库根目录的 `.env` 后，启动开发环境并运行检查：

```bash
docker compose -f compose.yaml -f compose.dev.yaml up -d --build --wait
docker compose --profile test build tests
docker compose --profile test run --rm --no-deps tests
```

`backend/src/` 下的代码会自动重载。依赖变更后需要重新构建镜像；修改测试后也要重建测试镜像。测试命令会运行 pytest、Ruff 和离线 MySQL 迁移 SQL 生成检查，不要求模型凭据或启动数据库。

## 代码与文档要求

- 优先提交范围清晰、容易理解和评审的改动；保持命名具体，函数职责单一，避免不必要的抽象。
- 新增或修改的项目说明使用中文；代码中的注释和文档字符串使用中文，重点解释业务意图、约束和不明显的设计原因，不要逐行复述代码。
- Python 代码保持英文标识符，并使用类型标注；遵循项目 Ruff 配置。详细约定见[代码规范](docs/CODE_STYLE.md)。
- 行为变更应补充有意义的测试，并在 Pull Request 中说明验证结果和未覆盖之处。
- 架构决策记录在 `docs/ADR-*.md`；有意义的开发里程碑和经验记录在 `docs/DEVLOG.md`。
- 提交前运行上面的容器检查。不要把真实凭据、客户数据或生成的 `.env` 提交到仓库。

## Pull Request

请在描述中写清楚问题、变更后的行为、验证方式，以及仍存在的限制；有对应 Issue 时请附上链接。提交可以使用清晰的 Conventional Commits 标题，例如 `feat: 添加会话查询`、`docs: 完善中文开发指南`。

所有贡献均遵循项目的 MIT 许可证。

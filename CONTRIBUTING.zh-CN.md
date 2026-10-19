# 参与 AgentOrbis 开发

**语言：**[English](CONTRIBUTING.md) | 简体中文

开始前请阅读项目介绍、[路线图](docs/zh/ROADMAP.md)和[代码规范](docs/zh/CODE_STYLE.md)。提交范围清晰的改动，并说明不明显行为背后的原因。新增或修改的 Python 注释和公开文档字符串使用中文，代码标识符使用易读的英文。

在 Docker 中运行离线检查：

```bash
docker compose --profile test run --build --rm tests
```

测试通过模拟 HTTP 调用，不需要模型密钥。不要提交 `.env`、真实 API Key 或客户数据。新增模型评测样例时创建新的冻结数据集版本，不要修改旧标签或评测结果。

重要决策记录在中英文架构或路线图文档中。Pull Request 说明行为变化和验证结果。所有贡献遵循 MIT 许可证。

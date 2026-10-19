# AgentOrbis 评测归档

**语言：**[English](README.md) | 简体中文

此目录集中保存按版本冻结的合成数据集和不可变 HTTP 评测记录。评测证据独立于应用包，便于和代码变更一起审阅。

## 当前数据集

- [`datasets/intent_v1.jsonl`](datasets/intent_v1.jsonl)：80 条固定样例，覆盖单意图、政策咨询、话题切换、待回答问题、多动作、否定、更正、取消/恢复、歧义、历史上下文、无关输入、数据中的提示注入和请求校验。
- [`datasets/intent_edge_v1.jsonl`](datasets/intent_edge_v1.jsonl)：24 条冻结边界样例，覆盖描述不足、订单号互斥候选、并行查询、唯一待回答上下文、明确切换话题和否定提及。

两组数据均为开发用途，由项目作者编写，未经独立人工复核。部分样例曾用于完善提示词，因此属于回归数据，不是盲测泛化基准。

## 已记录结果

[优化对照报告](results/optimization-comparison.zh-CN.md)汇总所有运行。每次运行分别保存数据集副本、逐条请求与响应、汇总指标、报告、模型和源码摘要，以及解释该版本所需的源码快照。

| 运行 | 通过数 | 用途 |
|---|---:|---|
| [基线 v1](results/2026-10-19-baseline-v1/report.zh-CN.md) | 74/80 | 初始测量 |
| [优化前边界集](results/2026-10-19-edge-before/report.zh-CN.md) | 20/24 | 修改提示词前冻结的挑战集 |
| [优化 v2](results/2026-10-19-optimized-v2/report.zh-CN.md) | 79/80 | 语义提示优化 |
| [v2 边界复测](results/2026-10-19-edge-after-v2/report.zh-CN.md) | 24/24 | 优化后的挑战集回归 |
| [优化 v3](results/2026-10-19-optimized-v3/report.zh-CN.md) | 80/80 | 对无效结构化输出最多纠正一次 |
| [v3 边界复测](results/2026-10-19-edge-after-v3/report.zh-CN.md) | 24/24 | 最终挑战集回归 |

最终成绩覆盖包含最多一次结构纠正的完整解释器，不是首次模型调用准确率、生产准确率，也不保证新用户消息一定正确。

## 在 Docker 中复现

在被 Git 忽略的根目录 `.env` 中填写模型密钥并启动 API。再运行评测配置；它会挂载整个仓库，将新证据写回此目录：

```bash
docker compose up -d --build --wait api
docker compose --profile evaluation run --build --rm evaluator --dataset evaluation/datasets/intent_v1.jsonl --output evaluation/results/new-run-id --model deepseek-v4-pro --endpoint http://api:8000/api/v1/interpret --concurrency 2
```

每次运行使用新的输出目录；若目录已存在，评测器会拒绝覆盖。评测器每条样例只发起一次 HTTP 请求，不重试；解释器内部仍可能针对无效模型结构执行一次纠正调用。`model` 标签用于记录，API 实际使用运行容器中的模型配置，因此两者需要保持一致。

## 增加新数据

生成脚本仅在目标文件不存在时创建初始数据。需要调整标签或增加挑战样例时，创建新的版本化数据集，保留旧数据和分数。除非已获准并完成脱敏，不要使用真实客户对话。

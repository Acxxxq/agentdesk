# AgentOrbis 评测归档

**语言：**[English](README.md) | 简体中文

此目录集中保存按版本冻结的合成数据集和不可变 HTTP 评测记录。评测证据独立于应用包，便于和代码变更一起审阅。

## 当前数据集

当前服务采用正式意图 ID（`refund.apply`、`logistics.track`、`policy.consult`），解释结果版本为 `1.0`。当前回归应使用以下五份正式标签数据：

- [`intent_taxonomy_v1.jsonl`](datasets/intent_taxonomy_v1.jsonl)：80 条基础样例。
- [`intent_edge_taxonomy_v1.jsonl`](datasets/intent_edge_taxonomy_v1.jsonl)：24 条边界样例。
- [`intent_random_taxonomy_v1.jsonl`](datasets/intent_random_taxonomy_v1.jsonl)：110 条随机表达样例。
- [`dialogue_policy_taxonomy_v1.jsonl`](datasets/dialogue_policy_taxonomy_v1.jsonl)：7 个固定语义多轮场景。
- [`chat_e2e_taxonomy_v1.jsonl`](datasets/chat_e2e_taxonomy_v1.jsonl)：10 个聊天端到端场景。

[`taxonomy_v1_migration.json`](datasets/taxonomy_v1_migration.json) 保存来源及目标摘要，迁移脚本为 [`migrate_intent_taxonomy.py`](scripts/migrate_intent_taxonomy.py)。此次只迁移语义标签，保留用户原文、订单参数、任务类型及评分规则。下面的旧数据和历史成绩继续归档，不能直接用旧标签与当前 API 的正式 ID 做字符串评分。随机生成脚本 `generate_random_intent_dataset.py` 保留用于复现历史 v2 数据，输出仍是旧标签。

- [`datasets/intent_v1.jsonl`](datasets/intent_v1.jsonl)：80 条固定样例，覆盖单意图、政策咨询、话题切换、待回答问题、多动作、否定、更正、取消/恢复、歧义、历史上下文、无关输入、数据中的提示注入和请求校验。
- [`datasets/intent_edge_v1.jsonl`](datasets/intent_edge_v1.jsonl)：24 条冻结边界样例，覆盖描述不足、订单号互斥候选、并行查询、唯一待回答上下文、明确切换话题和否定提及。
- [`datasets/intent_random_v2.jsonl`](datasets/intent_random_v2.jsonl)：110 条固定种子生成的表达变体，覆盖退款、物流、政策问答、未说明业务用途的订单、互斥订单和范围外输入；订单号和样例顺序随机化。
- [`datasets/intent_random_v1.jsonl`](datasets/intent_random_v1.jsonl)：随机扩展集的首轮标签版本，保留用于核对评分口径变化。
- [`datasets/dialogue_policy_v1.jsonl`](datasets/dialogue_policy_v1.jsonl)：7 个多轮策略场景，检查取消与新任务并发、跨话题补充旧任务参数、澄清隔离和恢复、全局歧义、条件动作及任务目标缺失。
- [`datasets/chat_e2e_v1.jsonl`](datasets/chat_e2e_v1.jsonl)：10 个真实聊天 API 多轮端到端场景，检查模型理解、策略决策、领域事件、任务状态、待补参数与回复。

这些数据均为开发用途，由项目作者编写，未经独立人工复核。部分样例曾用于完善提示词，因此属于回归数据，不是盲测泛化基准。

## 已记录结果

最新正式 ID 迁移结果见[迁移复测报告](results/taxonomy-migration.zh-CN.md)：基础 80/80、边界 24/24、随机 110/110、固定语义 14/14 轮、聊天端到端 24/25 轮。剩余范围外处理差异、四轮完整结果及源码摘要均已保留，未修改原标签消除失败。

[优化对照报告](results/optimization-comparison.zh-CN.md)汇总所有运行。每次运行分别保存数据集副本、逐条请求与响应、汇总指标、报告、模型和源码摘要，以及解释该版本所需的源码快照。

| 运行 | 通过数 | 用途 |
|---|---:|---|
| [基线 v1](results/2026-10-19-baseline-v1/report.zh-CN.md) | 74/80 | 初始测量 |
| [优化前边界集](results/2026-10-19-edge-before/report.zh-CN.md) | 20/24 | 修改提示词前冻结的挑战集 |
| [优化 v2](results/2026-10-19-optimized-v2/report.zh-CN.md) | 79/80 | 语义提示优化 |
| [v2 边界复测](results/2026-10-19-edge-after-v2/report.zh-CN.md) | 24/24 | 优化后的挑战集回归 |
| [优化 v3](results/2026-10-19-optimized-v3/report.zh-CN.md) | 80/80 | 对无效结构化输出最多纠正一次 |
| [v3 边界复测](results/2026-10-19-edge-after-v3/report.zh-CN.md) | 24/24 | 最终挑战集回归 |
| [多轮策略 v1](results/2026-10-19-dialogue-policy-v1/report.zh-CN.md) | 14/14 轮次 | 固定语义输入下的策略、归约与回复回归 |
| [聊天端到端 v4](results/2026-10-19-chat-e2e-v4/report.zh-CN.md) | 25/25 轮次 | 真实聊天 API、模型理解与状态变化闭环 |
| [随机扩展集 v1](results/2026-10-19-intent-random-v1-run2/report.zh-CN.md) | 91/110 | 首轮随机表达评测；暴露缺参歧义与退款原因标签口径问题 |
| [随机扩展集 v2](results/2026-10-19-intent-random-v2/report.zh-CN.md) | 110/110 | 复核标签口径后的随机表达回归 |

最终成绩覆盖包含最多一次结构纠正的完整解释器，不是首次模型调用准确率、生产准确率，也不保证新用户消息一定正确。

随机扩展集由 [`scripts/generate_random_intent_dataset.py`](scripts/generate_random_intent_dataset.py) 生成，默认种子为 `20261019`。v1 首轮后复核了评分口径：明确退款原因应计入实体标签；缺少订单号时允许输出 `parameter` 歧义，因为后续策略会向用户补问。v2 按修订后的口径重建数据并重新评测；这属于开发回归，不是盲测，也没有调整提示词或模型。两轮均只有一次模型采样，不能据此声称泛化准确率。

多轮策略评测固定了解释器输出的语义结构，不调用模型；它验证的是任务选择、澄清保存、事件顺序及状态变化。自然语言到语义结构的识别能力继续由上面的意图数据集评测。

聊天端到端评测则对每个场景顺序调用 `/api/v1/chat`，同一场景沿用一个会话 ID，每个场景之间新建会话。它检查从自然语言理解到状态变化的完整路径。模型输出存在随机性，因此应保留逐轮记录；失败轮次不重试，也不会从分母剔除。当前数据集属于合成开发回归集，未经独立人工复核，不能据此推断生产准确率。

在本地虚拟环境运行：

```powershell
cd backend
$env:PYTHONPATH = "src"
..\.venv-intent\Scripts\python.exe -m agentorbis.evaluation.dialogue --dataset ..\evaluation\datasets\dialogue_policy_taxonomy_v1.jsonl --output ..\evaluation\results\new-dialogue-run
```

## 在 Docker 中复现

在被 Git 忽略的根目录 `.env` 中填写模型密钥并启动 API。再运行评测配置；它会挂载整个仓库，将新证据写回此目录：

```bash
docker compose up -d --build --wait api
docker compose --profile evaluation run --build --rm evaluator --dataset evaluation/datasets/intent_taxonomy_v1.jsonl --output evaluation/results/new-run-id --model deepseek-v4-pro --endpoint http://api:8000/api/v1/interpret --concurrency 2

# 多轮聊天端到端评测；会连续调用模型，按实际轮数产生 API 用量
docker compose --profile evaluation run --build --rm chat-evaluator --dataset evaluation/datasets/chat_e2e_taxonomy_v1.jsonl --output evaluation/results/new-chat-e2e-run --model deepseek-v4-pro --endpoint http://api:8000/api/v1/chat
```

本次记录的端到端运行命令为：

```powershell
# 在仓库根目录的第一个终端启动 API；它从根目录 .env 读取模型配置
$env:PYTHONPATH = "backend/src"
.\.venv-intent\Scripts\python.exe -m uvicorn agentorbis.main:app --host 127.0.0.1 --port 18001
```

在第二个终端运行评测：

```powershell
$env:PYTHONPATH = "backend/src"
.\.venv-intent\Scripts\python.exe -m agentorbis.evaluation.chat --dataset evaluation/datasets/chat_e2e_taxonomy_v1.jsonl --output evaluation/results/2026-10-19-chat-e2e-v4 --model deepseek-v4-pro --endpoint http://127.0.0.1:18001/api/v1/chat --concurrency 3
```

每次运行使用新的输出目录；若目录已存在，评测器会拒绝覆盖。评测器每条样例只发起一次 HTTP 请求，不重试；解释器内部仍可能针对无效模型结构执行一次纠正调用。`model` 标签用于记录，API 实际使用运行容器中的模型配置，因此两者需要保持一致。

## 增加新数据

生成脚本仅在目标文件不存在时创建初始数据。需要调整标签或增加挑战样例时，创建新的版本化数据集，保留旧数据和分数。除非已获准并完成脱敏，不要使用真实客户对话。

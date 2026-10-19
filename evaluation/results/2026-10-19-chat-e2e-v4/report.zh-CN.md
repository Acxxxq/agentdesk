# AgentOrbis 多轮聊天端到端评测报告

时间：2026-10-19T17:45:19.297209+08:00  
数据集 SHA-256：`f537e865269ce7a6eee2ed05e00f0f6db43cb42844a388d6d02f1f1900c5c0d3`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`776c9571ee5325fe249338dc742b7499341d89e505010247be6a13d0c8aa708e`

## 评测范围

通过真实 `/api/v1/chat` 接口连续发送每个场景的消息，检查模型理解、策略决策、领域事件、完整任务状态、待补参数和回复。每个场景使用新会话；轮次按顺序执行。
数据为合成开发样例，非真实用户语料，未经独立人工复核；可能存在提示词回归偏差。服务端或传输错误保留在分母中，不重试。
本评测不验证 MySQL 持久化、真实退款/物流执行、身份权限或并发请求。

## 结果

- 场景：10 / 10 全轮通过。
- 轮次：25 / 25 通过（100.0%）。
- HTTP/网络错误：0；延迟 P50/P95：2166/3223 ms。

## 分类结果

| 分类 | 场景通过 / 总数 | 轮次通过 / 总数 |
|---|---:|---:|
| ambiguity_safety | 1 / 1 | 1 / 1 |
| clarification | 1 / 1 | 2 / 2 |
| multi_action | 1 / 1 | 2 / 2 |
| out_of_scope | 1 / 1 | 1 / 1 |
| slot_collection | 1 / 1 | 3 / 3 |
| task_reference | 2 / 2 | 8 / 8 |
| task_targeting | 1 / 1 | 3 / 3 |
| topic_switch | 2 / 2 | 5 / 5 |

## 分项结果

| 断言 | 通过 / 总数 | 比率 |
|---|---:|---:|
| act_1 | 11 / 11 | 100.0% |
| act_2 | 2 / 2 | 100.0% |
| ambiguities_required | 2 / 2 | 100.0% |
| decision_actions | 24 / 24 | 100.0% |
| event_types | 13 / 13 | 100.0% |
| http_status | 25 / 25 | 100.0% |
| intents | 22 / 22 | 100.0% |
| internal_task_ids_hidden | 22 / 22 | 100.0% |
| pending_clarification | 11 / 11 | 100.0% |
| pending_clarification_candidate_task_types | 1 / 1 | 100.0% |
| pending_question | 11 / 11 | 100.0% |
| reply_contains | 12 / 12 | 100.0% |
| task_statuses | 25 / 25 | 100.0% |

## 失败轮次

本轮无失败；结果仅适用于本数据集与本次模型配置。

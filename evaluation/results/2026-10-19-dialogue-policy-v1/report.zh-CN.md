# 多轮对话策略评测

- 场景：7，通过：7
- 对话轮次：14，通过：14，通过率：100%
- 评测范围：使用固定语义结构输入，检查 DialoguePolicy、状态归约和用户回复；不调用 LLM。
- 本轮修复：明确取消可与另一项缺参任务分开处理；澄清只保存未完成动作，补参时不会重放已完成动作。
- [问题分析与评测边界](analysis.zh-CN.md)

| 场景 | 结果 | 失败断言 |
| --- | --- | --- |
| `cancel_refund_then_logistics` | 通过 | — |
| `create_complete_refund_and_clarify_logistics` | 通过 | — |
| `only_missing_logistics_parameter` | 通过 | — |
| `global_ambiguity_blocks_mutation` | 通过 | — |
| `conditional_action_is_deferred` | 通过 | — |
| `cancel_target_unresolved` | 通过 | — |
| `answer_older_task_after_topic_switch` | 通过 | — |

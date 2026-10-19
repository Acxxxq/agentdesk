# 多轮对话策略评测

- 场景：7，通过：7
- 对话轮次：14，通过：14，通过率：100%
- 评测范围：使用固定语义结构输入，检查 DialoguePolicy、状态归约和用户回复；不调用 LLM。
- 本报告仅验证合成数据中的固定语义输入，不验证自然语言识别或外部业务执行。

| 场景 | 结果 | 失败断言 |
| --- | --- | --- |
| `cancel_refund_then_logistics-taxonomy-v1` | 通过 | — |
| `create_complete_refund_and_clarify_logistics-taxonomy-v1` | 通过 | — |
| `only_missing_logistics_parameter-taxonomy-v1` | 通过 | — |
| `global_ambiguity_blocks_mutation-taxonomy-v1` | 通过 | — |
| `conditional_action_is_deferred-taxonomy-v1` | 通过 | — |
| `cancel_target_unresolved-taxonomy-v1` | 通过 | — |
| `answer_older_task_after_topic_switch-taxonomy-v1` | 通过 | — |

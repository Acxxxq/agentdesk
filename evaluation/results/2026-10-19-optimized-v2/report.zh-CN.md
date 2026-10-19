# AgentOrbis 意图识别评测报告

时间：2026-10-19T16:02:38.025571+08:00  
数据集 SHA-256：`a46c3cdc197bbdede34e96c373f645b719a4dcd0b052d023ec84f01797d7c67a`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`bfa15d29683c75b47242c1806ccffbc9df42eafbbae78bc7a4da4f76e573706a`

## 评测边界

这是编码助手生成并预先标注的合成开发集，非真实用户数据，未经独立人工复核。
包括已在提示词中出现的回归例子，单独按 origin 统计；不得作为独立泛化能力证明。
上下文为固定快照；不评测自动任务创建、状态串写、持久化、真实退款或完整澄清闭环。
精确评分只覆盖标签声明的字段，未标注的动作/目标字段不代表已正确。
未使用 LLM 裁判；每次请求不重试，失败结果不丢弃。模型输出已通过 API 校验，非供应商原始响应。

## 总体结果

- 请求数：80；通过：79；失败：1。
- 全约束通过率：98.8%；服务端/网络错误：1。
- 语义样例：73 / 74；非法输入拦截：6 / 6。
- HTTP 耗时 P50：2084 ms；P95：3014 ms（包含排队）。

## 分类结果

| 分类 | 通过 / 总数 | 全约束通过率 |
|---|---:|---:|
| ambiguity | 6 / 6 | 100.0% |
| cancel_resume | 6 / 6 | 100.0% |
| correction | 6 / 6 | 100.0% |
| history_context | 6 / 6 | 100.0% |
| input_validation | 6 / 6 | 100.0% |
| instruction_in_data | 4 / 4 | 100.0% |
| multiple_intents | 5 / 6 | 83.3% |
| negation | 6 / 6 | 100.0% |
| out_of_scope | 6 / 6 | 100.0% |
| pending_answer | 6 / 6 | 100.0% |
| policy_question | 6 / 6 | 100.0% |
| single_intent | 8 / 8 | 100.0% |
| topic_switch | 8 / 8 | 100.0% |

## 分项结果

| 检查 | 通过 / 有标签样例 | 比率 |
|---|---:|---:|
| act_count | 73 / 74 | 98.6% |
| ambiguities | 73 / 74 | 98.6% |
| dialogue_acts | 43 / 43 | 100.0% |
| entity_binding | 73 / 74 | 98.6% |
| http_status | 79 / 80 | 98.8% |
| intents | 73 / 74 | 98.6% |
| relations | 73 / 74 | 98.6% |
| response_schema | 73 / 73 | 100.0% |
| target_hints | 20 / 20 | 100.0% |
| task_references | 12 / 12 | 100.0% |

## 失败明细

详细请求、预期和完整响应见 `results.jsonl`。

### intent-v1-031 · multiple_intents · 第 1 次

输入：先跟踪 C6103 的快递，然后退 A6104

HTTP：502；未通过：http_status, relations, intents, entity_binding, act_count, ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {
          "order_id": "C6103"
        }
      },
      {
        "business_intent": "refund",
        "entities": {
          "order_id": "A6104"
        }
      }
    ],
    "ambiguity_required": [],
    "ambiguity_forbidden": [
      "intent",
      "task",
      "parameter",
      "other"
    ],
    "relations": [
      {
        "source_index": 0,
        "target_index": 1,
        "kind": "sequence"
      }
    ]
  },
  "actual": {
    "detail": "invalid_output"
  }
}
```


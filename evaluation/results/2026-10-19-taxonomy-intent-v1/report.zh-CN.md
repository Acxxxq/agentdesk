# AgentOrbis 意图识别评测报告

时间：2026-10-19T23:36:11.822510+08:00  
数据集 SHA-256：`d02b4aadf2dcb8a1bf117f2f44dae7b715aa64d29c07131a900bbcbc5832e9f0`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`bed929f82125c85799f8c2f3dbe99351ecbe3994f600ddb3ad0476286b2ec4e4`

## 评测边界

这是编码助手生成并预先标注的合成开发集，非真实用户数据，未经独立人工复核。
包括已在提示词中出现的回归例子，单独按 origin 统计；不得作为独立泛化能力证明。
上下文为固定快照；不评测自动任务创建、状态串写、持久化、真实退款或完整澄清闭环。
精确评分只覆盖标签声明的字段，未标注的动作/目标字段不代表已正确。
未使用 LLM 裁判；每次请求不重试，失败结果不丢弃。模型输出已通过 API 校验，非供应商原始响应。

## 总体结果

- 请求数：80；通过：76；失败：4。
- 全约束通过率：95.0%；服务端/网络错误：0。
- 语义样例：70 / 74；非法输入拦截：6 / 6。
- HTTP 耗时 P50：1753 ms；P95：2427 ms（包含排队）。

## 分类结果

| 分类 | 通过 / 总数 | 全约束通过率 |
|---|---:|---:|
| ambiguity | 3 / 6 | 50.0% |
| cancel_resume | 6 / 6 | 100.0% |
| correction | 6 / 6 | 100.0% |
| history_context | 6 / 6 | 100.0% |
| input_validation | 6 / 6 | 100.0% |
| instruction_in_data | 4 / 4 | 100.0% |
| multiple_intents | 6 / 6 | 100.0% |
| negation | 5 / 6 | 83.3% |
| out_of_scope | 6 / 6 | 100.0% |
| pending_answer | 6 / 6 | 100.0% |
| policy_question | 6 / 6 | 100.0% |
| single_intent | 8 / 8 | 100.0% |
| topic_switch | 8 / 8 | 100.0% |

## 分项结果

| 检查 | 通过 / 有标签样例 | 比率 |
|---|---:|---:|
| act_count | 70 / 74 | 94.6% |
| ambiguities | 73 / 74 | 98.6% |
| dialogue_acts | 41 / 43 | 95.3% |
| entity_binding | 70 / 74 | 94.6% |
| http_status | 80 / 80 | 100.0% |
| intents | 70 / 74 | 94.6% |
| relations | 70 / 74 | 94.6% |
| response_schema | 74 / 74 | 100.0% |
| target_hints | 20 / 20 | 100.0% |
| task_references | 10 / 12 | 83.3% |

## 失败明细

详细请求、预期和完整响应见 `results.jsonl`。

### intent-v1-038-taxonomy-v1 · negation · 第 1 次

输入：A7105 不用退，申请 B7106 退款

HTTP：200；未通过：entity_binding, intents, act_count, relations

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "refund.apply",
        "entities": {
          "order_id": "B7106"
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
    "relations": []
  },
  "actual": {
    "acts": [
      {
        "act_id": "a1",
        "business_intent": "refund.apply",
        "dialogue_act": "reject",
        "target_hint": "unspecified",
        "referenced_task_id": null,
        "entities": {
          "order_id": "A7105"
        },
        "utterance_span": "A7105 不用退",
        "uncertainty": "low"
      },
      {
        "act_id": "a2",
        "business_intent": "refund.apply",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "order_id": "B7106"
        },
        "utterance_span": "申请 B7106 退款",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [],
    "relations": [],
    "source": "llm",
    "taxonomy_version": "1.0"
  }
}
```

### intent-v1-053-taxonomy-v1 · ambiguity · 第 1 次

输入：帮我查一下 A9201

HTTP：200；未通过：ambiguities, entity_binding, intents, act_count, relations

```json
{
  "expected": {
    "http_status": 200,
    "acts": [],
    "ambiguity_required": [
      "intent"
    ],
    "ambiguity_forbidden": [],
    "relations": []
  },
  "actual": {
    "acts": [
      {
        "act_id": "a1",
        "business_intent": "logistics.track",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "order_id": "A9201"
        },
        "utterance_span": "帮我查一下 A9201",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [],
    "relations": [],
    "source": "llm",
    "taxonomy_version": "1.0"
  }
}
```

### intent-v1-055-taxonomy-v1 · ambiguity · 第 1 次

输入：继续那个退款

HTTP：200；未通过：entity_binding, dialogue_acts, intents, task_references, act_count, relations

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "refund.apply",
        "entities": {},
        "dialogue_act": [
          "resume"
        ],
        "referenced_task_id": null
      }
    ],
    "ambiguity_required": [
      "task"
    ],
    "ambiguity_forbidden": [],
    "relations": []
  },
  "actual": {
    "acts": [],
    "ambiguities": [
      {
        "kind": "task",
        "candidate_values": [
          "refund_001",
          "refund_002"
        ],
        "target_slot": null,
        "target_act_id": null,
        "reason": "用户说“继续那个退款”，但存在两个退款任务 refund_001 和 refund_002，无法确定指哪一个"
      }
    ],
    "relations": [],
    "source": "llm",
    "taxonomy_version": "1.0"
  }
}
```

### intent-v1-056-taxonomy-v1 · ambiguity · 第 1 次

输入：取消那个退款

HTTP：200；未通过：entity_binding, dialogue_acts, intents, task_references, act_count, relations

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "refund.apply",
        "entities": {},
        "dialogue_act": [
          "cancel"
        ],
        "referenced_task_id": null
      }
    ],
    "ambiguity_required": [
      "task"
    ],
    "ambiguity_forbidden": [],
    "relations": []
  },
  "actual": {
    "acts": [],
    "ambiguities": [
      {
        "kind": "task",
        "candidate_values": [
          "refund_001",
          "refund_002"
        ],
        "target_slot": null,
        "target_act_id": null,
        "reason": "用户说“取消那个退款”，但存在两个退款任务 refund_001 和 refund_002，无法确定要取消哪一个。"
      }
    ],
    "relations": [],
    "source": "llm",
    "taxonomy_version": "1.0"
  }
}
```


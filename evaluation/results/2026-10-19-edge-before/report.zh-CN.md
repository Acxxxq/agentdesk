# AgentOrbis 意图识别评测报告

时间：2026-10-19T15:59:55.099962+08:00  
数据集 SHA-256：`ef502e7ea6ab42ff231d4a9ed3ede13e6872a561093e218d65ab06a9ea31b275`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`5a742db10773ed8a96e593c786cec6075964b238a7f27f0cbc833e09db6f2fa0`

## 评测边界

这是编码助手生成并预先标注的合成开发集，非真实用户数据，未经独立人工复核。
包括已在提示词中出现的回归例子，单独按 origin 统计；不得作为独立泛化能力证明。
上下文为固定快照；不评测自动任务创建、状态串写、持久化、真实退款或完整澄清闭环。
精确评分只覆盖标签声明的字段，未标注的动作/目标字段不代表已正确。
未使用 LLM 裁判；每次请求不重试，失败结果不丢弃。模型输出已通过 API 校验，非供应商原始响应。

## 总体结果

- 请求数：24；通过：20；失败：4。
- 全约束通过率：83.3%；服务端/网络错误：0。
- 语义样例：20 / 24；非法输入拦截：0 / 0。
- HTTP 耗时 P50：2153 ms；P95：3104 ms（包含排队）。

## 分类结果

| 分类 | 通过 / 总数 | 全约束通过率 |
|---|---:|---:|
| alternative_orders | 4 / 4 | 100.0% |
| explicit_new_topic | 4 / 4 | 100.0% |
| negated_mention | 4 / 4 | 100.0% |
| parallel_orders | 4 / 4 | 100.0% |
| underspecified_query | 0 / 4 | 0.0% |
| unique_pending_context | 4 / 4 | 100.0% |

## 分项结果

| 检查 | 通过 / 有标签样例 | 比率 |
|---|---:|---:|
| act_count | 20 / 24 | 83.3% |
| ambiguities | 21 / 24 | 87.5% |
| dialogue_acts | 8 / 8 | 100.0% |
| entity_binding | 20 / 24 | 83.3% |
| http_status | 24 / 24 | 100.0% |
| intents | 20 / 24 | 83.3% |
| relations | 20 / 24 | 83.3% |
| response_schema | 24 / 24 | 100.0% |
| target_hints | 4 / 4 | 100.0% |
| task_references | 4 / 4 | 100.0% |

## 失败明细

详细请求、预期和完整响应见 `results.jsonl`。

### intent-edge-v1-002 · underspecified_query · 第 1 次

输入：E10102 这个单帮我瞧瞧

HTTP：200；未通过：intents, relations, entity_binding, act_count, ambiguities

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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "order_id": "E10102"
        },
        "utterance_span": "E10102 这个单帮我瞧瞧",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [],
    "relations": [],
    "source": "llm"
  }
}
```

### intent-edge-v1-001 · underspecified_query · 第 1 次

输入：麻烦看一下 D10101

HTTP：200；未通过：intents, relations, entity_binding, act_count

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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "order_id": "D10101"
        },
        "utterance_span": "麻烦看一下 D10101",
        "uncertainty": "medium"
      }
    ],
    "ambiguities": [
      {
        "kind": "intent",
        "candidate_values": [
          "logistics",
          "refund"
        ],
        "reason": "用户只说“看一下 D10101”，未明确是查物流还是退款进度，倾向物流但存在歧义"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### intent-edge-v1-003 · underspecified_query · 第 1 次

输入：F10103 查查吧

HTTP：200；未通过：intents, relations, entity_binding, act_count, ambiguities

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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "order_id": "F10103"
        },
        "utterance_span": "F10103 查查吧",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [],
    "relations": [],
    "source": "llm"
  }
}
```

### intent-edge-v1-004 · underspecified_query · 第 1 次

输入：查一下 G10104 的情况

HTTP：200；未通过：intents, relations, entity_binding, act_count, ambiguities

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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "order_id": "G10104"
        },
        "utterance_span": "查一下 G10104 的情况",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [],
    "relations": [],
    "source": "llm"
  }
}
```


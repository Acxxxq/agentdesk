# AgentOrbis 意图识别评测报告

时间：2026-10-19T19:34:39.790678+08:00  
数据集 SHA-256：`e9e1bbd3d8f28f36a2e947cc3e111a0b2c2efa13bf72ced2a231225097610534`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`776c9571ee5325fe249338dc742b7499341d89e505010247be6a13d0c8aa708e`

## 评测边界

这是编码助手生成并预先标注的合成开发集，非真实用户数据，未经独立人工复核。
包括已在提示词中出现的回归例子，单独按 origin 统计；不得作为独立泛化能力证明。
上下文为固定快照；不评测自动任务创建、状态串写、持久化、真实退款或完整澄清闭环。
精确评分只覆盖标签声明的字段，未标注的动作/目标字段不代表已正确。
未使用 LLM 裁判；每次请求不重试，失败结果不丢弃。模型输出已通过 API 校验，非供应商原始响应。

## 总体结果

- 请求数：110；通过：91；失败：19。
- 全约束通过率：82.7%；服务端/网络错误：0。
- 语义样例：91 / 110；非法输入拦截：0 / 0。
- HTTP 耗时 P50：2025 ms；P95：2753 ms（包含排队）。

## 分类结果

| 分类 | 通过 / 总数 | 全约束通过率 |
|---|---:|---:|
| random_alternative_orders | 10 / 10 | 100.0% |
| random_logistics | 18 / 30 | 60.0% |
| random_out_of_scope | 10 / 10 | 100.0% |
| random_policy_question | 20 / 20 | 100.0% |
| random_refund | 23 / 30 | 76.7% |
| random_underspecified | 10 / 10 | 100.0% |

## 分项结果

| 检查 | 通过 / 有标签样例 | 比率 |
|---|---:|---:|
| act_count | 110 / 110 | 100.0% |
| ambiguities | 97 / 110 | 88.2% |
| dialogue_acts | 80 / 80 | 100.0% |
| entity_binding | 104 / 110 | 94.5% |
| http_status | 110 / 110 | 100.0% |
| intents | 110 / 110 | 100.0% |
| relations | 110 / 110 | 100.0% |
| response_schema | 110 / 110 | 100.0% |
| target_hints | 60 / 60 | 100.0% |
| task_references | 60 / 60 | 100.0% |

## 失败明细

详细请求、预期和完整响应见 `results.jsonl`。

### random-v1-047 · random_logistics · 第 1 次

输入：帮我查一下物流

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "帮我查一下物流",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户要查物流但未提供订单号"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-050 · random_logistics · 第 1 次

输入：这个订单什么时候送到

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "这个订单什么时候送到",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户询问物流送达时间，但未提供订单号，无法确定具体订单"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-023 · random_refund · 第 1 次

输入：订单 T49787 买错了，帮我申请退款

HTTP：200；未通过：entity_binding

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "refund",
        "entities": {
          "order_id": "T49787"
        },
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "refund",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "order_id": "T49787",
          "reason": "买错了"
        },
        "utterance_span": "订单 T49787 买错了，帮我申请退款",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-058 · random_logistics · 第 1 次

输入：我的快递到哪儿了

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "我的快递到哪儿了",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户想查物流，但未提供订单号，无法确定查询哪个快递"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-025 · random_refund · 第 1 次

输入：订单 V24118 买错了，帮我申请退款

HTTP：200；未通过：entity_binding

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "refund",
        "entities": {
          "order_id": "V24118"
        },
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "refund",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "order_id": "V24118",
          "reason": "买错了"
        },
        "utterance_span": "订单 V24118 买错了，帮我申请退款",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-049 · random_logistics · 第 1 次

输入：帮我查一下物流

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "帮我查一下物流",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户要查物流但未提供订单号"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-009 · random_refund · 第 1 次

输入：订单 T51394 买错了，帮我申请退款

HTTP：200；未通过：entity_binding

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "refund",
        "entities": {
          "order_id": "T51394"
        },
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "refund",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "order_id": "T51394",
          "reason": "买错了"
        },
        "utterance_span": "订单 T51394 买错了，帮我申请退款",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-055 · random_logistics · 第 1 次

输入：我想知道商品的物流进度

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "我想知道商品的物流进度",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户想查物流但未提供订单号，无法确定查询对象"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-038 · random_logistics · 第 1 次

输入：能帮我追踪一下包裹吗

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "能帮我追踪一下包裹吗",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户想追踪包裹，但未提供订单号或运单号"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-051 · random_logistics · 第 1 次

输入：我买的东西寄出来了吗

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "我买的东西寄出来了吗",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户询问物流但未提供订单号，无法确定查询哪个订单"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-028 · random_refund · 第 1 次

输入：买错东西了，我要退掉

HTTP：200；未通过：entity_binding

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "refund",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "refund",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "reason": "买错东西了"
        },
        "utterance_span": "买错东西了，我要退掉",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-016 · random_refund · 第 1 次

输入：订单 F85197 买错了，帮我申请退款

HTTP：200；未通过：entity_binding

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "refund",
        "entities": {
          "order_id": "F85197"
        },
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "refund",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "order_id": "F85197",
          "reason": "买错了"
        },
        "utterance_span": "订单 F85197 买错了，帮我申请退款",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-034 · random_logistics · 第 1 次

输入：能帮我追踪一下包裹吗

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "能帮我追踪一下包裹吗",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户想追踪包裹，但未提供订单号或运单号"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-011 · random_refund · 第 1 次

输入：订单 H69198 买错了，帮我申请退款

HTTP：200；未通过：entity_binding

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "refund",
        "entities": {
          "order_id": "H69198"
        },
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "refund",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {
          "order_id": "H69198",
          "reason": "买错了"
        },
        "utterance_span": "订单 H69198 买错了，帮我申请退款",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-043 · random_logistics · 第 1 次

输入：帮我查一下物流

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "帮我查一下物流",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户要查物流但未提供订单号"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-045 · random_logistics · 第 1 次

输入：想看看包裹现在的配送进度

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "想看看包裹现在的配送进度",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户想查物流进度，但未提供订单号或包裹标识"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-021 · random_refund · 第 1 次

输入：我要把刚买的东西退了

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "refund",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "refund",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "我要把刚买的东西退了",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户要退款但未提供订单号，无法确定具体订单"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-040 · random_logistics · 第 1 次

输入：查询一下快递状态

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "查询一下快递状态",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户要查询物流，但未提供订单号"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```

### random-v1-035 · random_logistics · 第 1 次

输入：想看看包裹现在的配送进度

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics",
        "entities": {},
        "dialogue_act": [
          "start_task"
        ],
        "target_hint": [
          "new_task"
        ],
        "referenced_task_id": null
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
        "business_intent": "logistics",
        "dialogue_act": "start_task",
        "target_hint": "new_task",
        "referenced_task_id": null,
        "entities": {},
        "utterance_span": "想看看包裹现在的配送进度",
        "uncertainty": "low"
      }
    ],
    "ambiguities": [
      {
        "kind": "parameter",
        "candidate_values": [],
        "target_slot": "order_id",
        "target_act_id": "a1",
        "reason": "用户想查物流进度，但未提供订单号或包裹标识"
      }
    ],
    "relations": [],
    "source": "llm"
  }
}
```


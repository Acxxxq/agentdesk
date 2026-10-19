# AgentOrbis 意图识别评测报告

时间：2026-10-19T23:46:37.818020+08:00  
数据集 SHA-256：`15b540f3bbb0178a7bb2a278bc774df649b9549f314cf3ecfcea94c52de2ac0e`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`5d4ba34c718c9a2cf81c6b552634f5112cc1abc489e636dc98596efcdb0254c6`

## 评测边界

这是编码助手生成并预先标注的合成开发集，非真实用户数据，未经独立人工复核。
包括已在提示词中出现的回归例子，单独按 origin 统计；不得作为独立泛化能力证明。
上下文为固定快照；不评测自动任务创建、状态串写、持久化、真实退款或完整澄清闭环。
精确评分只覆盖标签声明的字段，未标注的动作/目标字段不代表已正确。
未使用 LLM 裁判；每次请求不重试，失败结果不丢弃。模型输出已通过 API 校验，非供应商原始响应。

## 总体结果

- 请求数：24；通过：20；失败：4。
- 全约束通过率：83.3%；服务端/网络错误：4。
- 语义样例：20 / 24；非法输入拦截：0 / 0。
- HTTP 耗时 P50：1936 ms；P95：4393 ms（包含排队）。

## 分类结果

| 分类 | 通过 / 总数 | 全约束通过率 |
|---|---:|---:|
| alternative_orders | 4 / 4 | 100.0% |
| explicit_new_topic | 4 / 4 | 100.0% |
| negated_mention | 4 / 4 | 100.0% |
| parallel_orders | 0 / 4 | 0.0% |
| underspecified_query | 4 / 4 | 100.0% |
| unique_pending_context | 4 / 4 | 100.0% |

## 分项结果

| 检查 | 通过 / 有标签样例 | 比率 |
|---|---:|---:|
| act_count | 20 / 24 | 83.3% |
| ambiguities | 20 / 24 | 83.3% |
| dialogue_acts | 8 / 8 | 100.0% |
| entity_binding | 20 / 24 | 83.3% |
| http_status | 20 / 24 | 83.3% |
| intents | 20 / 24 | 83.3% |
| relations | 20 / 24 | 83.3% |
| response_schema | 20 / 20 | 100.0% |
| target_hints | 4 / 4 | 100.0% |
| task_references | 4 / 4 | 100.0% |

## 失败明细

详细请求、预期和完整响应见 `results.jsonl`。

### intent-edge-v1-009-taxonomy-v1 · parallel_orders · 第 1 次

输入：查 D10301 和 E10302 的物流，两单都查

HTTP：502；未通过：http_status, act_count, intents, entity_binding, relations, ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics.track",
        "entities": {
          "order_id": "D10301"
        }
      },
      {
        "business_intent": "logistics.track",
        "entities": {
          "order_id": "E10302"
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
        "kind": "parallel"
      }
    ]
  },
  "actual": {
    "detail": "invalid_output"
  }
}
```

### intent-edge-v1-010-taxonomy-v1 · parallel_orders · 第 1 次

输入：查 F10303 和 G10304 的物流，两单都查

HTTP：502；未通过：http_status, act_count, intents, entity_binding, relations, ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics.track",
        "entities": {
          "order_id": "F10303"
        }
      },
      {
        "business_intent": "logistics.track",
        "entities": {
          "order_id": "G10304"
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
        "kind": "parallel"
      }
    ]
  },
  "actual": {
    "detail": "invalid_output"
  }
}
```

### intent-edge-v1-011-taxonomy-v1 · parallel_orders · 第 1 次

输入：查 H10305 和 J10306 的物流，两单都查

HTTP：502；未通过：http_status, act_count, intents, entity_binding, relations, ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics.track",
        "entities": {
          "order_id": "H10305"
        }
      },
      {
        "business_intent": "logistics.track",
        "entities": {
          "order_id": "J10306"
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
        "kind": "parallel"
      }
    ]
  },
  "actual": {
    "detail": "invalid_output"
  }
}
```

### intent-edge-v1-012-taxonomy-v1 · parallel_orders · 第 1 次

输入：查 K10307 和 L10308 的物流，两单都查

HTTP：502；未通过：http_status, act_count, intents, entity_binding, relations, ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics.track",
        "entities": {
          "order_id": "K10307"
        }
      },
      {
        "business_intent": "logistics.track",
        "entities": {
          "order_id": "L10308"
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
        "kind": "parallel"
      }
    ]
  },
  "actual": {
    "detail": "invalid_output"
  }
}
```


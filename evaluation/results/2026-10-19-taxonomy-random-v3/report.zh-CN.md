# AgentOrbis 意图识别评测报告

时间：2026-10-19T23:47:06.933067+08:00  
数据集 SHA-256：`44e119331601597c9dc9d13414ca45a7b9f20accde052f2d06b0dd21f05a1fcd`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`5d4ba34c718c9a2cf81c6b552634f5112cc1abc489e636dc98596efcdb0254c6`

## 评测边界

这是编码助手生成并预先标注的合成开发集，非真实用户数据，未经独立人工复核。
包括已在提示词中出现的回归例子，单独按 origin 统计；不得作为独立泛化能力证明。
上下文为固定快照；不评测自动任务创建、状态串写、持久化、真实退款或完整澄清闭环。
精确评分只覆盖标签声明的字段，未标注的动作/目标字段不代表已正确。
未使用 LLM 裁判；每次请求不重试，失败结果不丢弃。模型输出已通过 API 校验，非供应商原始响应。

## 总体结果

- 请求数：110；通过：107；失败：3。
- 全约束通过率：97.3%；服务端/网络错误：0。
- 语义样例：107 / 110；非法输入拦截：0 / 0。
- HTTP 耗时 P50：1776 ms；P95：2381 ms（包含排队）。

## 分类结果

| 分类 | 通过 / 总数 | 全约束通过率 |
|---|---:|---:|
| random_alternative_orders | 10 / 10 | 100.0% |
| random_logistics | 30 / 30 | 100.0% |
| random_out_of_scope | 7 / 10 | 70.0% |
| random_policy_question | 20 / 20 | 100.0% |
| random_refund | 30 / 30 | 100.0% |
| random_underspecified | 10 / 10 | 100.0% |

## 分项结果

| 检查 | 通过 / 有标签样例 | 比率 |
|---|---:|---:|
| act_count | 110 / 110 | 100.0% |
| ambiguities | 107 / 110 | 97.3% |
| dialogue_acts | 80 / 80 | 100.0% |
| entity_binding | 110 / 110 | 100.0% |
| http_status | 110 / 110 | 100.0% |
| intents | 110 / 110 | 100.0% |
| relations | 110 / 110 | 100.0% |
| response_schema | 110 / 110 | 100.0% |
| target_hints | 60 / 60 | 100.0% |
| task_references | 60 / 60 | 100.0% |

## 失败明细

详细请求、预期和完整响应见 `results.jsonl`。

### random-v2-104-taxonomy-v1 · random_out_of_scope · 第 1 次

输入：推荐几本适合周末看的书

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [],
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
    "acts": [],
    "ambiguities": [
      {
        "kind": "intent",
        "candidate_values": [],
        "target_slot": null,
        "target_act_id": null,
        "reason": "用户请求推荐书籍，与退款、物流、售后政策等受支持业务无关，业务用途未知"
      }
    ],
    "relations": [],
    "source": "llm",
    "taxonomy_version": "1.0"
  }
}
```

### random-v2-106-taxonomy-v1 · random_out_of_scope · 第 1 次

输入：给我介绍一下杭州的景点

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [],
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
    "acts": [],
    "ambiguities": [
      {
        "kind": "intent",
        "candidate_values": [],
        "target_slot": null,
        "target_act_id": null,
        "reason": "用户询问杭州景点介绍，与退款、物流、售后政策等受支持业务无关，业务用途未知"
      }
    ],
    "relations": [],
    "source": "llm",
    "taxonomy_version": "1.0"
  }
}
```

### random-v2-110-taxonomy-v1 · random_out_of_scope · 第 1 次

输入：帮我做一道数学题

HTTP：200；未通过：ambiguities

```json
{
  "expected": {
    "http_status": 200,
    "acts": [],
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
    "acts": [],
    "ambiguities": [
      {
        "kind": "intent",
        "candidate_values": [],
        "target_slot": null,
        "target_act_id": null,
        "reason": "用户请求做数学题，与退款、物流、售后政策等受支持业务无关，业务用途未知"
      }
    ],
    "relations": [],
    "source": "llm",
    "taxonomy_version": "1.0"
  }
}
```


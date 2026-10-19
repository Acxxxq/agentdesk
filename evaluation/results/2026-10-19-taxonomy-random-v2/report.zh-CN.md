# AgentOrbis 意图识别评测报告

时间：2026-10-19T23:42:24.982397+08:00  
数据集 SHA-256：`44e119331601597c9dc9d13414ca45a7b9f20accde052f2d06b0dd21f05a1fcd`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`ce4d15bebef592fcc0947c30436bc870f32f842ca711326024db3ab133fe1458`

## 评测边界

这是编码助手生成并预先标注的合成开发集，非真实用户数据，未经独立人工复核。
包括已在提示词中出现的回归例子，单独按 origin 统计；不得作为独立泛化能力证明。
上下文为固定快照；不评测自动任务创建、状态串写、持久化、真实退款或完整澄清闭环。
精确评分只覆盖标签声明的字段，未标注的动作/目标字段不代表已正确。
未使用 LLM 裁判；每次请求不重试，失败结果不丢弃。模型输出已通过 API 校验，非供应商原始响应。

## 总体结果

- 请求数：110；通过：109；失败：1。
- 全约束通过率：99.1%；服务端/网络错误：0。
- 语义样例：109 / 110；非法输入拦截：0 / 0。
- HTTP 耗时 P50：1777 ms；P95：2367 ms（包含排队）。

## 分类结果

| 分类 | 通过 / 总数 | 全约束通过率 |
|---|---:|---:|
| random_alternative_orders | 10 / 10 | 100.0% |
| random_logistics | 29 / 30 | 96.7% |
| random_out_of_scope | 10 / 10 | 100.0% |
| random_policy_question | 20 / 20 | 100.0% |
| random_refund | 30 / 30 | 100.0% |
| random_underspecified | 10 / 10 | 100.0% |

## 分项结果

| 检查 | 通过 / 有标签样例 | 比率 |
|---|---:|---:|
| act_count | 109 / 110 | 99.1% |
| ambiguities | 109 / 110 | 99.1% |
| dialogue_acts | 79 / 80 | 98.8% |
| entity_binding | 109 / 110 | 99.1% |
| http_status | 110 / 110 | 100.0% |
| intents | 109 / 110 | 99.1% |
| relations | 109 / 110 | 99.1% |
| response_schema | 110 / 110 | 100.0% |
| target_hints | 59 / 60 | 98.3% |
| task_references | 59 / 60 | 98.3% |

## 失败明细

详细请求、预期和完整响应见 `results.jsonl`。

### random-v2-050-taxonomy-v1 · random_logistics · 第 1 次

输入：这个订单什么时候送到

HTTP：200；未通过：dialogue_acts, ambiguities, act_count, relations, entity_binding, target_hints, intents, task_references

```json
{
  "expected": {
    "http_status": 200,
    "acts": [
      {
        "business_intent": "logistics.track",
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
      "other"
    ],
    "relations": []
  },
  "actual": {
    "acts": [],
    "ambiguities": [
      {
        "kind": "intent",
        "candidate_values": [
          "logistics.track"
        ],
        "target_slot": null,
        "target_act_id": null,
        "reason": "用户询问订单送达时间，但未说明订单号，且未明确是查物流还是其他业务；无上下文可确认业务用途"
      }
    ],
    "relations": [],
    "source": "llm",
    "taxonomy_version": "1.0"
  }
}
```


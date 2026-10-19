# AgentOrbis 多轮聊天端到端评测报告

时间：2026-10-19T23:50:04.916771+08:00  
数据集 SHA-256：`35aa5d3cd214ccd26c28f03d144d994b5d66b3efcd5075230669da04d4dcaa3a`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`b1509783040cd5acc171f98befd63392c6d964c1d8c16d97536936a3882b5503`

## 评测范围

通过真实 `/api/v1/chat` 接口连续发送每个场景的消息，检查模型理解、策略决策、领域事件、完整任务状态、待补参数和回复。每个场景使用新会话；轮次按顺序执行。
数据为合成开发样例，非真实用户语料，未经独立人工复核；可能存在提示词回归偏差。服务端或传输错误保留在分母中，不重试。
本评测不验证 MySQL 持久化、真实退款/物流执行、身份权限或并发请求。

## 结果

- 场景：9 / 10 全轮通过。
- 轮次：24 / 25 通过（96.0%）。
- HTTP/网络错误：0；延迟 P50/P95：1749/2505 ms。

## 分类结果

| 分类 | 场景通过 / 总数 | 轮次通过 / 总数 |
|---|---:|---:|
| ambiguity_safety | 1 / 1 | 1 / 1 |
| clarification | 1 / 1 | 2 / 2 |
| multi_action | 1 / 1 | 2 / 2 |
| out_of_scope | 0 / 1 | 0 / 1 |
| slot_collection | 1 / 1 | 3 / 3 |
| task_reference | 2 / 2 | 8 / 8 |
| task_targeting | 1 / 1 | 3 / 3 |
| topic_switch | 2 / 2 | 5 / 5 |

## 分项结果

| 断言 | 通过 / 总数 | 比率 |
|---|---:|---:|
| act_1 | 11 / 11 | 100.0% |
| act_2 | 2 / 2 | 100.0% |
| ambiguities_required | 1 / 2 | 50.0% |
| decision_actions | 23 / 24 | 95.8% |
| event_types | 13 / 13 | 100.0% |
| http_status | 25 / 25 | 100.0% |
| intents | 22 / 22 | 100.0% |
| internal_task_ids_hidden | 22 / 22 | 100.0% |
| pending_clarification | 10 / 11 | 90.9% |
| pending_clarification_candidate_task_types | 1 / 1 | 100.0% |
| pending_question | 11 / 11 | 100.0% |
| reply_contains | 11 / 12 | 91.7% |
| task_statuses | 25 / 25 | 100.0% |

## 失败轮次

### unsupported_request_is_not_misrouted-taxonomy-v1 · 第 1 轮

输入：帮我订一张明天去上海的火车票

未通过：ambiguities_required, decision_actions, pending_clarification, reply_contains

```json
{
  "expected": {
    "ambiguities_required": [
      "intent"
    ],
    "decision_actions": [
      "clarify"
    ],
    "task_statuses": {},
    "pending_clarification": "intent",
    "reply_contains": [
      "申请退款",
      "查询物流"
    ]
  },
  "actual": {
    "conversation_id": "06e50574-c866-4d5a-bd97-d7b2324dc44a",
    "reply": "你好，我可以帮你识别退款或物流请求。你也可以在一段对话里切换话题，或先咨询退款政策。",
    "understanding": {
      "acts": [],
      "ambiguities": [],
      "relations": [],
      "source": "llm",
      "taxonomy_version": "1.0"
    },
    "policy": {
      "decisions": [],
      "clarification_required": false
    },
    "state": {
      "conversation_id": "06e50574-c866-4d5a-bd97-d7b2324dc44a",
      "version": 0,
      "tasks": [],
      "active_task_id": null,
      "current_focus": {
        "kind": "none",
        "task_id": null,
        "intent": null
      },
      "pending_question": null,
      "pending_clarification": null,
      "suspended_clarifications": []
    },
    "events": []
  }
}
```


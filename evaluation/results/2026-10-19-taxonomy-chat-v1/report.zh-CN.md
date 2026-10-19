# AgentOrbis 多轮聊天端到端评测报告

时间：2026-10-19T23:36:12.467464+08:00  
数据集 SHA-256：`35aa5d3cd214ccd26c28f03d144d994b5d66b3efcd5075230669da04d4dcaa3a`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`bed929f82125c85799f8c2f3dbe99351ecbe3994f600ddb3ad0476286b2ec4e4`

## 评测范围

通过真实 `/api/v1/chat` 接口连续发送每个场景的消息，检查模型理解、策略决策、领域事件、完整任务状态、待补参数和回复。每个场景使用新会话；轮次按顺序执行。
数据为合成开发样例，非真实用户语料，未经独立人工复核；可能存在提示词回归偏差。服务端或传输错误保留在分母中，不重试。
本评测不验证 MySQL 持久化、真实退款/物流执行、身份权限或并发请求。

## 结果

- 场景：9 / 10 全轮通过。
- 轮次：24 / 25 通过（96.0%）。
- HTTP/网络错误：0；延迟 P50/P95：1860/2950 ms。

## 分类结果

| 分类 | 场景通过 / 总数 | 轮次通过 / 总数 |
|---|---:|---:|
| ambiguity_safety | 1 / 1 | 1 / 1 |
| clarification | 1 / 1 | 2 / 2 |
| multi_action | 1 / 1 | 2 / 2 |
| out_of_scope | 1 / 1 | 1 / 1 |
| slot_collection | 1 / 1 | 3 / 3 |
| task_reference | 1 / 2 | 7 / 8 |
| task_targeting | 1 / 1 | 3 / 3 |
| topic_switch | 2 / 2 | 5 / 5 |

## 分项结果

| 断言 | 通过 / 总数 | 比率 |
|---|---:|---:|
| act_1 | 11 / 11 | 100.0% |
| act_2 | 2 / 2 | 100.0% |
| ambiguities_required | 2 / 2 | 100.0% |
| decision_actions | 24 / 24 | 100.0% |
| event_types | 13 / 13 | 100.0% |
| http_status | 25 / 25 | 100.0% |
| intents | 22 / 22 | 100.0% |
| internal_task_ids_hidden | 22 / 22 | 100.0% |
| pending_clarification | 10 / 11 | 90.9% |
| pending_clarification_candidate_task_types | 0 / 1 | 0.0% |
| pending_question | 11 / 11 | 100.0% |
| reply_contains | 11 / 12 | 91.7% |
| task_statuses | 25 / 25 | 100.0% |

## 失败轮次

### ambiguous_old_task_reference-taxonomy-v1 · 第 3 轮

输入：那个呢

未通过：pending_clarification, pending_clarification_candidate_task_types, reply_contains

```json
{
  "expected": {
    "decision_actions": [
      "clarify"
    ],
    "task_statuses": {
      "refund": [
        "collecting"
      ],
      "logistics": [
        "collecting"
      ]
    },
    "pending_clarification": "task",
    "reply_contains": [
      "退款任务",
      "物流查询任务"
    ],
    "pending_clarification_candidate_task_types": [
      "refund",
      "logistics"
    ]
  },
  "actual": {
    "conversation_id": "a13ddaa2-6f71-4d2f-97e7-49570d0a3d5d",
    "reply": "你是想申请退款、查询物流，还是咨询退款政策？",
    "understanding": {
      "acts": [],
      "ambiguities": [
        {
          "kind": "intent",
          "candidate_values": [],
          "target_slot": null,
          "target_act_id": null,
          "reason": "用户说“那个呢”，没有提供任何参数或明确业务，无法判断是在回答哪个待补问题或提出新请求"
        }
      ],
      "relations": [],
      "source": "llm",
      "taxonomy_version": "1.0"
    },
    "policy": {
      "decisions": [
        {
          "action": "clarify",
          "act_id": null,
          "task_id": null,
          "task_type": null,
          "entities": {},
          "question": "你是想申请退款、查询物流，还是咨询退款政策？",
          "clarification": {
            "clarification_id": "64577bee-57f6-5214-b8cf-b2b5a8f4b32b",
            "kind": "intent",
            "question": "你是想申请退款、查询物流，还是咨询退款政策？",
            "original_message": "那个呢",
            "candidate_values": [],
            "candidate_task_ids": [],
            "target_act_id": null,
            "target_ambiguity_index": 0,
            "target_slot": null,
            "preserved_entities": {},
            "original_acts": [],
            "original_ambiguities": [
              {
                "kind": "intent",
                "candidate_values": [],
                "target_slot": null,
                "target_act_id": null,
                "reason": "用户说“那个呢”，没有提供任何参数或明确业务，无法判断是在回答哪个待补问题或提出新请求"
              }
            ],
            "original_relations": []
          },
          "clarification_id": null,
          "reason": null
        }
      ],
      "clarification_required": true
    },
    "state": {
      "conversation_id": "a13ddaa2-6f71-4d2f-97e7-49570d0a3d5d",
      "version": 3,
      "tasks": [
        {
          "task_id": "a14a9446-5c4e-5df2-b4fe-d52ef0d5e716",
          "type": "refund",
          "status": "collecting",
          "slots": {}
        },
        {
          "task_id": "6865cc4f-0706-52b0-a6e8-e4f540eeee2d",
          "type": "logistics",
          "status": "collecting",
          "slots": {}
        }
      ],
      "active_task_id": "6865cc4f-0706-52b0-a6e8-e4f540eeee2d",
      "current_focus": {
        "kind": "task",
        "task_id": "6865cc4f-0706-52b0-a6e8-e4f540eeee2d",
        "intent": null
      },
      "pending_question": {
        "task_id": "6865cc4f-0706-52b0-a6e8-e4f540eeee2d",
        "slot_name": "order_id",
        "question": "请提供订单号。"
      },
      "pending_clarification": {
        "clarification_id": "64577bee-57f6-5214-b8cf-b2b5a8f4b32b",
        "kind": "intent",
        "question": "你是想申请退款、查询物流，还是咨询退款政策？",
        "original_message": "那个呢",
        "candidate_values": [],
        "candidate_task_ids": [],
        "target_act_id": null,
        "target_ambiguity_index": 0,
        "target_slot": null,
        "preserved_entities": {},
        "original_acts": [],
        "original_ambiguities": [
          {
            "kind": "intent",
            "candidate_values": [],
            "target_slot": null,
            "target_act_id": null,
            "reason": "用户说“那个呢”，没有提供任何参数或明确业务，无法判断是在回答哪个待补问题或提出新请求"
          }
        ],
        "original_relations": []
      },
      "suspended_clarifications": []
    },
    "events": [
      {
        "event_id": "a13ddaa2-6f71-4d2f-97e7-49570d0a3d5d:3:1:clarification_requested:-",
        "conversation_id": "a13ddaa2-6f71-4d2f-97e7-49570d0a3d5d",
        "version": 3,
        "event_type": "clarification_requested",
        "task_id": null,
        "payload": {
          "clarification_id": "64577bee-57f6-5214-b8cf-b2b5a8f4b32b",
          "kind": "intent",
          "question": "你是想申请退款、查询物流，还是咨询退款政策？"
        }
      }
    ]
  }
}
```


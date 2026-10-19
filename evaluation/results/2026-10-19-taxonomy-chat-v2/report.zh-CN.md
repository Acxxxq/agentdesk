# AgentOrbis 多轮聊天端到端评测报告

时间：2026-10-19T23:40:41.913199+08:00  
数据集 SHA-256：`35aa5d3cd214ccd26c28f03d144d994b5d66b3efcd5075230669da04d4dcaa3a`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`ce4d15bebef592fcc0947c30436bc870f32f842ca711326024db3ab133fe1458`

## 评测范围

通过真实 `/api/v1/chat` 接口连续发送每个场景的消息，检查模型理解、策略决策、领域事件、完整任务状态、待补参数和回复。每个场景使用新会话；轮次按顺序执行。
数据为合成开发样例，非真实用户语料，未经独立人工复核；可能存在提示词回归偏差。服务端或传输错误保留在分母中，不重试。
本评测不验证 MySQL 持久化、真实退款/物流执行、身份权限或并发请求。

## 结果

- 场景：8 / 10 全轮通过。
- 轮次：22 / 25 通过（88.0%）。
- HTTP/网络错误：0；延迟 P50/P95：1893/3068 ms。

## 分类结果

| 分类 | 场景通过 / 总数 | 轮次通过 / 总数 |
|---|---:|---:|
| ambiguity_safety | 1 / 1 | 1 / 1 |
| clarification | 0 / 1 | 1 / 2 |
| multi_action | 1 / 1 | 2 / 2 |
| out_of_scope | 1 / 1 | 1 / 1 |
| slot_collection | 1 / 1 | 3 / 3 |
| task_reference | 1 / 2 | 6 / 8 |
| task_targeting | 1 / 1 | 3 / 3 |
| topic_switch | 2 / 2 | 5 / 5 |

## 分项结果

| 断言 | 通过 / 总数 | 比率 |
|---|---:|---:|
| act_1 | 11 / 11 | 100.0% |
| act_2 | 2 / 2 | 100.0% |
| ambiguities_required | 2 / 2 | 100.0% |
| decision_actions | 22 / 24 | 91.7% |
| event_types | 11 / 13 | 84.6% |
| http_status | 25 / 25 | 100.0% |
| intents | 22 / 22 | 100.0% |
| internal_task_ids_hidden | 21 / 21 | 100.0% |
| pending_clarification | 8 / 11 | 72.7% |
| pending_clarification_candidate_task_types | 0 / 1 | 0.0% |
| pending_question | 9 / 11 | 81.8% |
| reply_contains | 11 / 12 | 91.7% |
| task_statuses | 22 / 25 | 88.0% |

## 失败轮次

### new_topic_interrupts_clarification-taxonomy-v1 · 第 2 轮

输入：我想改成申请退款

未通过：decision_actions, event_types, task_statuses, pending_question, pending_clarification

```json
{
  "expected": {
    "intents": [
      "refund.apply"
    ],
    "decision_actions": [
      "interrupt_clarification",
      "create_task"
    ],
    "event_types": [
      "clarification_interrupted",
      "task_created"
    ],
    "task_statuses": {
      "refund": [
        "collecting"
      ]
    },
    "pending_clarification": null,
    "pending_question": {
      "task_type": "refund",
      "slot_name": "order_id"
    }
  },
  "actual": {
    "conversation_id": "4d67fa48-cd6e-4bb3-a202-48b95a7dad01",
    "reply": "请提供要查询物流的订单号。",
    "understanding": {
      "acts": [
        {
          "act_id": "a1",
          "business_intent": "refund.apply",
          "dialogue_act": "start_task",
          "target_hint": "new_task",
          "referenced_task_id": null,
          "entities": {},
          "utterance_span": "我想改成申请退款",
          "uncertainty": "low"
        }
      ],
      "ambiguities": [
        {
          "kind": "parameter",
          "candidate_values": [],
          "target_slot": "order_id",
          "target_act_id": "a1",
          "reason": "用户改为申请退款，但未提供订单号"
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
          "question": "请提供要查询物流的订单号。",
          "clarification": {
            "clarification_id": "0119cdf8-786d-5781-81f1-ca68ba671bf6",
            "kind": "parameter",
            "question": "请提供要查询物流的订单号。",
            "original_message": "帮我查一下物流",
            "candidate_values": [],
            "candidate_task_ids": [],
            "target_act_id": "a1",
            "target_ambiguity_index": 0,
            "target_slot": "order_id",
            "preserved_entities": {},
            "original_acts": [
              {
                "act_id": "a1",
                "business_intent": "logistics.track",
                "dialogue_act": "start_task",
                "target_hint": "new_task",
                "referenced_task_id": null,
                "entities": {},
                "utterance_span": "帮我查一下物流",
                "uncertainty": "low"
              }
            ],
            "original_ambiguities": [
              {
                "kind": "parameter",
                "candidate_values": [],
                "target_slot": "order_id",
                "target_act_id": "a1",
                "reason": "用户要求查物流，但未提供订单号"
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
      "conversation_id": "4d67fa48-cd6e-4bb3-a202-48b95a7dad01",
      "version": 1,
      "tasks": [],
      "active_task_id": null,
      "current_focus": {
        "kind": "none",
        "task_id": null,
        "intent": null
      },
      "pending_question": null,
      "pending_clarification": {
        "clarification_id": "0119cdf8-786d-5781-81f1-ca68ba671bf6",
        "kind": "parameter",
        "question": "请提供要查询物流的订单号。",
        "original_message": "帮我查一下物流",
        "candidate_values": [],
        "candidate_task_ids": [],
        "target_act_id": "a1",
        "target_ambiguity_index": 0,
        "target_slot": "order_id",
        "preserved_entities": {},
        "original_acts": [
          {
            "act_id": "a1",
            "business_intent": "logistics.track",
            "dialogue_act": "start_task",
            "target_hint": "new_task",
            "referenced_task_id": null,
            "entities": {},
            "utterance_span": "帮我查一下物流",
            "uncertainty": "low"
          }
        ],
        "original_ambiguities": [
          {
            "kind": "parameter",
            "candidate_values": [],
            "target_slot": "order_id",
            "target_act_id": "a1",
            "reason": "用户要求查物流，但未提供订单号"
          }
        ],
        "original_relations": []
      },
      "suspended_clarifications": []
    },
    "events": []
  }
}
```

### ambiguous_old_task_reference-taxonomy-v1 · 第 2 轮

输入：再帮我查一下物流

未通过：decision_actions, event_types, task_statuses, pending_question, pending_clarification

```json
{
  "expected": {
    "intents": [
      "logistics.track"
    ],
    "decision_actions": [
      "create_task"
    ],
    "task_statuses": {
      "refund": [
        "collecting"
      ],
      "logistics": [
        "collecting"
      ]
    },
    "pending_clarification": null,
    "event_types": [
      "task_created"
    ],
    "pending_question": {
      "task_type": "logistics",
      "slot_name": "order_id"
    }
  },
  "actual": {
    "conversation_id": "bd799a1b-7f58-4410-832a-e13f562a535b",
    "reply": "请提供要查询物流的订单号。",
    "understanding": {
      "acts": [
        {
          "act_id": "a1",
          "business_intent": "logistics.track",
          "dialogue_act": "start_task",
          "target_hint": "new_task",
          "referenced_task_id": null,
          "entities": {},
          "utterance_span": "再帮我查一下物流",
          "uncertainty": "low"
        }
      ],
      "ambiguities": [
        {
          "kind": "parameter",
          "candidate_values": [],
          "target_slot": "order_id",
          "target_act_id": "a1",
          "reason": "用户提出查询物流，但未提供订单号，无法确定要查询哪个订单。"
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
          "question": "请提供要查询物流的订单号。",
          "clarification": {
            "clarification_id": "951bf4da-23c9-57b2-9caf-6b4b795eafc4",
            "kind": "parameter",
            "question": "请提供要查询物流的订单号。",
            "original_message": "再帮我查一下物流",
            "candidate_values": [],
            "candidate_task_ids": [],
            "target_act_id": "a1",
            "target_ambiguity_index": 0,
            "target_slot": "order_id",
            "preserved_entities": {},
            "original_acts": [
              {
                "act_id": "a1",
                "business_intent": "logistics.track",
                "dialogue_act": "start_task",
                "target_hint": "new_task",
                "referenced_task_id": null,
                "entities": {},
                "utterance_span": "再帮我查一下物流",
                "uncertainty": "low"
              }
            ],
            "original_ambiguities": [
              {
                "kind": "parameter",
                "candidate_values": [],
                "target_slot": "order_id",
                "target_act_id": "a1",
                "reason": "用户提出查询物流，但未提供订单号，无法确定要查询哪个订单。"
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
      "conversation_id": "bd799a1b-7f58-4410-832a-e13f562a535b",
      "version": 2,
      "tasks": [
        {
          "task_id": "22cc3693-73c6-5b09-9940-604d5769c287",
          "type": "refund",
          "status": "collecting",
          "slots": {}
        }
      ],
      "active_task_id": "22cc3693-73c6-5b09-9940-604d5769c287",
      "current_focus": {
        "kind": "task",
        "task_id": "22cc3693-73c6-5b09-9940-604d5769c287",
        "intent": null
      },
      "pending_question": {
        "task_id": "22cc3693-73c6-5b09-9940-604d5769c287",
        "slot_name": "order_id",
        "question": "请提供订单号。"
      },
      "pending_clarification": {
        "clarification_id": "951bf4da-23c9-57b2-9caf-6b4b795eafc4",
        "kind": "parameter",
        "question": "请提供要查询物流的订单号。",
        "original_message": "再帮我查一下物流",
        "candidate_values": [],
        "candidate_task_ids": [],
        "target_act_id": "a1",
        "target_ambiguity_index": 0,
        "target_slot": "order_id",
        "preserved_entities": {},
        "original_acts": [
          {
            "act_id": "a1",
            "business_intent": "logistics.track",
            "dialogue_act": "start_task",
            "target_hint": "new_task",
            "referenced_task_id": null,
            "entities": {},
            "utterance_span": "再帮我查一下物流",
            "uncertainty": "low"
          }
        ],
        "original_ambiguities": [
          {
            "kind": "parameter",
            "candidate_values": [],
            "target_slot": "order_id",
            "target_act_id": "a1",
            "reason": "用户提出查询物流，但未提供订单号，无法确定要查询哪个订单。"
          }
        ],
        "original_relations": []
      },
      "suspended_clarifications": []
    },
    "events": [
      {
        "event_id": "bd799a1b-7f58-4410-832a-e13f562a535b:2:1:clarification_requested:-",
        "conversation_id": "bd799a1b-7f58-4410-832a-e13f562a535b",
        "version": 2,
        "event_type": "clarification_requested",
        "task_id": null,
        "payload": {
          "clarification_id": "951bf4da-23c9-57b2-9caf-6b4b795eafc4",
          "kind": "parameter",
          "question": "请提供要查询物流的订单号。"
        }
      }
    ]
  }
}
```

### ambiguous_old_task_reference-taxonomy-v1 · 第 3 轮

输入：那个呢

未通过：task_statuses, pending_clarification, pending_clarification_candidate_task_types, reply_contains

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
    "conversation_id": "bd799a1b-7f58-4410-832a-e13f562a535b",
    "reply": "请提供要查询物流的订单号。",
    "understanding": {
      "acts": [],
      "ambiguities": [
        {
          "kind": "intent",
          "candidate_values": [],
          "target_slot": null,
          "target_act_id": null,
          "reason": "用户说“那个呢”，没有明确业务用途，无法判断是在回答退款订单号、物流订单号还是其他内容。"
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
          "question": "请提供要查询物流的订单号。",
          "clarification": {
            "clarification_id": "951bf4da-23c9-57b2-9caf-6b4b795eafc4",
            "kind": "parameter",
            "question": "请提供要查询物流的订单号。",
            "original_message": "再帮我查一下物流",
            "candidate_values": [],
            "candidate_task_ids": [],
            "target_act_id": "a1",
            "target_ambiguity_index": 0,
            "target_slot": "order_id",
            "preserved_entities": {},
            "original_acts": [
              {
                "act_id": "a1",
                "business_intent": "logistics.track",
                "dialogue_act": "start_task",
                "target_hint": "new_task",
                "referenced_task_id": null,
                "entities": {},
                "utterance_span": "再帮我查一下物流",
                "uncertainty": "low"
              }
            ],
            "original_ambiguities": [
              {
                "kind": "parameter",
                "candidate_values": [],
                "target_slot": "order_id",
                "target_act_id": "a1",
                "reason": "用户提出查询物流，但未提供订单号，无法确定要查询哪个订单。"
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
      "conversation_id": "bd799a1b-7f58-4410-832a-e13f562a535b",
      "version": 2,
      "tasks": [
        {
          "task_id": "22cc3693-73c6-5b09-9940-604d5769c287",
          "type": "refund",
          "status": "collecting",
          "slots": {}
        }
      ],
      "active_task_id": "22cc3693-73c6-5b09-9940-604d5769c287",
      "current_focus": {
        "kind": "task",
        "task_id": "22cc3693-73c6-5b09-9940-604d5769c287",
        "intent": null
      },
      "pending_question": {
        "task_id": "22cc3693-73c6-5b09-9940-604d5769c287",
        "slot_name": "order_id",
        "question": "请提供订单号。"
      },
      "pending_clarification": {
        "clarification_id": "951bf4da-23c9-57b2-9caf-6b4b795eafc4",
        "kind": "parameter",
        "question": "请提供要查询物流的订单号。",
        "original_message": "再帮我查一下物流",
        "candidate_values": [],
        "candidate_task_ids": [],
        "target_act_id": "a1",
        "target_ambiguity_index": 0,
        "target_slot": "order_id",
        "preserved_entities": {},
        "original_acts": [
          {
            "act_id": "a1",
            "business_intent": "logistics.track",
            "dialogue_act": "start_task",
            "target_hint": "new_task",
            "referenced_task_id": null,
            "entities": {},
            "utterance_span": "再帮我查一下物流",
            "uncertainty": "low"
          }
        ],
        "original_ambiguities": [
          {
            "kind": "parameter",
            "candidate_values": [],
            "target_slot": "order_id",
            "target_act_id": "a1",
            "reason": "用户提出查询物流，但未提供订单号，无法确定要查询哪个订单。"
          }
        ],
        "original_relations": []
      },
      "suspended_clarifications": []
    },
    "events": []
  }
}
```


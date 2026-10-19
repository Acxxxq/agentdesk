# AgentOrbis 多轮聊天端到端评测报告

时间：2026-10-19T17:40:19.731091+08:00  
数据集 SHA-256：`17be6c79c14d009fc195bf4df9a27eb9b89e00da2dd3d020a3fb5424bf97655f`  
模型：`deepseek-v4-pro`；提示词 SHA-256：`776c9571ee5325fe249338dc742b7499341d89e505010247be6a13d0c8aa708e`

## 评测范围

通过真实 `/api/v1/chat` 接口连续发送每个场景的消息，检查模型理解、策略决策、领域事件、完整任务状态、待补参数和回复。每个场景使用新会话；轮次按顺序执行。
数据为合成开发样例，非真实用户语料，未经独立人工复核；可能存在提示词回归偏差。服务端或传输错误保留在分母中，不重试。
本评测不验证 MySQL 持久化、真实退款/物流执行、身份权限或并发请求。

## 结果

- 场景：8 / 10 全轮通过。
- 轮次：22 / 25 通过（88.0%）。
- HTTP/网络错误：0；延迟 P50/P95：1884/3035 ms。

## 分类结果

| 分类 | 场景通过 / 总数 | 轮次通过 / 总数 |
|---|---:|---:|
| ambiguity_safety | 1 / 1 | 1 / 1 |
| clarification | 1 / 1 | 2 / 2 |
| multi_action | 1 / 1 | 2 / 2 |
| out_of_scope | 0 / 1 | 0 / 1 |
| slot_collection | 1 / 1 | 3 / 3 |
| task_reference | 1 / 2 | 6 / 8 |
| task_targeting | 1 / 1 | 3 / 3 |
| topic_switch | 2 / 2 | 5 / 5 |

## 分项结果

| 断言 | 通过 / 总数 | 比率 |
|---|---:|---:|
| act_1 | 11 / 11 | 100.0% |
| act_2 | 2 / 2 | 100.0% |
| ambiguities_required | 1 / 1 | 100.0% |
| decision_actions | 22 / 24 | 91.7% |
| event_types | 12 / 12 | 100.0% |
| exact_intents | 0 / 1 | 0.0% |
| http_status | 25 / 25 | 100.0% |
| intents | 22 / 22 | 100.0% |
| pending_clarification | 8 / 11 | 72.7% |
| pending_question | 11 / 11 | 100.0% |
| reply_contains | 10 / 12 | 83.3% |
| task_statuses | 23 / 25 | 92.0% |

## 失败轮次

### unsupported_request_is_not_misrouted · 第 1 轮

输入：帮我订一张明天去上海的火车票

未通过：exact_intents, decision_actions, pending_clarification, reply_contains

```json
{
  "expected": {
    "exact_intents": [
      "unknown"
    ],
    "decision_actions": [
      "reject"
    ],
    "task_statuses": {},
    "pending_question": null,
    "pending_clarification": null,
    "reply_contains": [
      "还不能安全地把这句话映射"
    ]
  },
  "actual": {
    "conversation_id": "39bdb5b4-45b5-47d9-8d57-640d284f74bc",
    "reply": "你是想申请退款、查询物流，还是咨询退款政策？",
    "understanding": {
      "acts": [],
      "ambiguities": [
        {
          "kind": "intent",
          "candidate_values": [],
          "target_slot": null,
          "target_act_id": null,
          "reason": "用户请求订火车票，不属于退款、物流、退款政策咨询等受支持业务范围"
        }
      ],
      "relations": [],
      "source": "llm"
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
            "clarification_id": "e39fb4e5-4ffb-5089-bf13-a3b848235457",
            "kind": "intent",
            "question": "你是想申请退款、查询物流，还是咨询退款政策？",
            "original_message": "帮我订一张明天去上海的火车票",
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
                "reason": "用户请求订火车票，不属于退款、物流、退款政策咨询等受支持业务范围"
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
      "conversation_id": "39bdb5b4-45b5-47d9-8d57-640d284f74bc",
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
        "clarification_id": "e39fb4e5-4ffb-5089-bf13-a3b848235457",
        "kind": "intent",
        "question": "你是想申请退款、查询物流，还是咨询退款政策？",
        "original_message": "帮我订一张明天去上海的火车票",
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
            "reason": "用户请求订火车票，不属于退款、物流、退款政策咨询等受支持业务范围"
          }
        ],
        "original_relations": []
      },
      "suspended_clarifications": []
    },
    "events": [
      {
        "event_id": "39bdb5b4-45b5-47d9-8d57-640d284f74bc:1:1:clarification_requested:-",
        "conversation_id": "39bdb5b4-45b5-47d9-8d57-640d284f74bc",
        "version": 1,
        "event_type": "clarification_requested",
        "task_id": null,
        "payload": {
          "clarification_id": "e39fb4e5-4ffb-5089-bf13-a3b848235457",
          "kind": "intent",
          "question": "你是想申请退款、查询物流，还是咨询退款政策？"
        }
      }
    ]
  }
}
```

### ambiguous_old_task_reference · 第 2 轮

输入：再帮我查一下物流

未通过：decision_actions, task_statuses, pending_clarification

```json
{
  "expected": {
    "intents": [
      "logistics"
    ],
    "decision_actions": [
      "clarify"
    ],
    "task_statuses": {
      "refund": [
        "collecting"
      ]
    },
    "pending_clarification": "parameter"
  },
  "actual": {
    "conversation_id": "0981ccd0-0109-4c20-87cf-86b552301403",
    "reply": "已为你建立物流查询任务。请提供订单号。",
    "understanding": {
      "acts": [
        {
          "act_id": "a1",
          "business_intent": "logistics",
          "dialogue_act": "start_task",
          "target_hint": "new_task",
          "referenced_task_id": null,
          "entities": {},
          "utterance_span": "再帮我查一下物流",
          "uncertainty": "low"
        }
      ],
      "ambiguities": [],
      "relations": [],
      "source": "llm"
    },
    "policy": {
      "decisions": [
        {
          "action": "create_task",
          "act_id": "a1",
          "task_id": "17a0a452-fd94-5443-8a1b-77048acf0af9",
          "task_type": "logistics",
          "entities": {},
          "question": null,
          "clarification": null,
          "clarification_id": null,
          "reason": null
        }
      ],
      "clarification_required": false
    },
    "state": {
      "conversation_id": "0981ccd0-0109-4c20-87cf-86b552301403",
      "version": 2,
      "tasks": [
        {
          "task_id": "1313f2a8-d0d5-582b-8af5-ce69a9152910",
          "type": "refund",
          "status": "collecting",
          "slots": {}
        },
        {
          "task_id": "17a0a452-fd94-5443-8a1b-77048acf0af9",
          "type": "logistics",
          "status": "collecting",
          "slots": {}
        }
      ],
      "active_task_id": "17a0a452-fd94-5443-8a1b-77048acf0af9",
      "current_focus": {
        "kind": "task",
        "task_id": "17a0a452-fd94-5443-8a1b-77048acf0af9",
        "intent": null
      },
      "pending_question": {
        "task_id": "17a0a452-fd94-5443-8a1b-77048acf0af9",
        "slot_name": "order_id",
        "question": "请提供订单号。"
      },
      "pending_clarification": null,
      "suspended_clarifications": []
    },
    "events": [
      {
        "event_id": "0981ccd0-0109-4c20-87cf-86b552301403:2:1:task_created:17a0a452-fd94-5443-8a1b-77048acf0af9",
        "conversation_id": "0981ccd0-0109-4c20-87cf-86b552301403",
        "version": 2,
        "event_type": "task_created",
        "task_id": "17a0a452-fd94-5443-8a1b-77048acf0af9",
        "payload": {
          "type": "logistics",
          "slots": {},
          "status": "collecting"
        }
      }
    ]
  }
}
```

### ambiguous_old_task_reference · 第 3 轮

输入：那个呢

未通过：task_statuses, pending_clarification, reply_contains

```json
{
  "expected": {
    "decision_actions": [
      "clarify"
    ],
    "task_statuses": {
      "refund": [
        "collecting"
      ]
    },
    "pending_clarification": "parameter",
    "reply_contains": [
      "订单号"
    ]
  },
  "actual": {
    "conversation_id": "0981ccd0-0109-4c20-87cf-86b552301403",
    "reply": "你想处理哪项任务？1313f2a8-d0d5-582b-8af5-ce69a9152910；17a0a452-fd94-5443-8a1b-77048acf0af9",
    "understanding": {
      "acts": [],
      "ambiguities": [
        {
          "kind": "task",
          "candidate_values": [
            "1313f2a8-d0d5-582b-8af5-ce69a9152910",
            "17a0a452-fd94-5443-8a1b-77048acf0af9"
          ],
          "target_slot": null,
          "target_act_id": null,
          "reason": "用户说“那个呢”，没有明确指向退款任务还是物流查询任务，两个任务都在等待订单号，无法唯一确定回答对象。"
        }
      ],
      "relations": [],
      "source": "llm"
    },
    "policy": {
      "decisions": [
        {
          "action": "clarify",
          "act_id": null,
          "task_id": null,
          "task_type": null,
          "entities": {},
          "question": "你想处理哪项任务？1313f2a8-d0d5-582b-8af5-ce69a9152910；17a0a452-fd94-5443-8a1b-77048acf0af9",
          "clarification": {
            "clarification_id": "2aa2cfff-fbbd-5b27-9d9b-9240f8cae445",
            "kind": "task",
            "question": "你想处理哪项任务？1313f2a8-d0d5-582b-8af5-ce69a9152910；17a0a452-fd94-5443-8a1b-77048acf0af9",
            "original_message": "那个呢",
            "candidate_values": [
              "1313f2a8-d0d5-582b-8af5-ce69a9152910",
              "17a0a452-fd94-5443-8a1b-77048acf0af9"
            ],
            "candidate_task_ids": [],
            "target_act_id": null,
            "target_ambiguity_index": 0,
            "target_slot": "order_id",
            "preserved_entities": {},
            "original_acts": [],
            "original_ambiguities": [
              {
                "kind": "task",
                "candidate_values": [
                  "1313f2a8-d0d5-582b-8af5-ce69a9152910",
                  "17a0a452-fd94-5443-8a1b-77048acf0af9"
                ],
                "target_slot": null,
                "target_act_id": null,
                "reason": "用户说“那个呢”，没有明确指向退款任务还是物流查询任务，两个任务都在等待订单号，无法唯一确定回答对象。"
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
      "conversation_id": "0981ccd0-0109-4c20-87cf-86b552301403",
      "version": 3,
      "tasks": [
        {
          "task_id": "1313f2a8-d0d5-582b-8af5-ce69a9152910",
          "type": "refund",
          "status": "collecting",
          "slots": {}
        },
        {
          "task_id": "17a0a452-fd94-5443-8a1b-77048acf0af9",
          "type": "logistics",
          "status": "collecting",
          "slots": {}
        }
      ],
      "active_task_id": "17a0a452-fd94-5443-8a1b-77048acf0af9",
      "current_focus": {
        "kind": "task",
        "task_id": "17a0a452-fd94-5443-8a1b-77048acf0af9",
        "intent": null
      },
      "pending_question": {
        "task_id": "17a0a452-fd94-5443-8a1b-77048acf0af9",
        "slot_name": "order_id",
        "question": "请提供订单号。"
      },
      "pending_clarification": {
        "clarification_id": "2aa2cfff-fbbd-5b27-9d9b-9240f8cae445",
        "kind": "task",
        "question": "你想处理哪项任务？1313f2a8-d0d5-582b-8af5-ce69a9152910；17a0a452-fd94-5443-8a1b-77048acf0af9",
        "original_message": "那个呢",
        "candidate_values": [
          "1313f2a8-d0d5-582b-8af5-ce69a9152910",
          "17a0a452-fd94-5443-8a1b-77048acf0af9"
        ],
        "candidate_task_ids": [],
        "target_act_id": null,
        "target_ambiguity_index": 0,
        "target_slot": "order_id",
        "preserved_entities": {},
        "original_acts": [],
        "original_ambiguities": [
          {
            "kind": "task",
            "candidate_values": [
              "1313f2a8-d0d5-582b-8af5-ce69a9152910",
              "17a0a452-fd94-5443-8a1b-77048acf0af9"
            ],
            "target_slot": null,
            "target_act_id": null,
            "reason": "用户说“那个呢”，没有明确指向退款任务还是物流查询任务，两个任务都在等待订单号，无法唯一确定回答对象。"
          }
        ],
        "original_relations": []
      },
      "suspended_clarifications": []
    },
    "events": [
      {
        "event_id": "0981ccd0-0109-4c20-87cf-86b552301403:3:1:clarification_requested:-",
        "conversation_id": "0981ccd0-0109-4c20-87cf-86b552301403",
        "version": 3,
        "event_type": "clarification_requested",
        "task_id": null,
        "payload": {
          "clarification_id": "2aa2cfff-fbbd-5b27-9d9b-9240f8cae445",
          "kind": "task",
          "question": "你想处理哪项任务？1313f2a8-d0d5-582b-8af5-ce69a9152910；17a0a452-fd94-5443-8a1b-77048acf0af9"
        }
      }
    ]
  }
}
```


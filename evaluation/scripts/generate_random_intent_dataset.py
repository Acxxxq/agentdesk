"""用固定随机种子生成意图识别合成扩展集。

标签由明确的模板定义，不依赖模型自评。此数据用于开发回归，不代表真实用户分布，
也不替代人工标注或盲测集。
"""

import argparse
import json
import random
from pathlib import Path

REFUND_WITH_ORDER = [
    "帮我把订单 {order} 退了",
    "订单号 {order}，我想申请退款",
    "麻烦处理一下 {order} 这笔订单的退款",
    "我想退掉编号为 {order} 的订单",
    "请问能帮我给 {order} 办理退款吗",
    "{order} 这单我不想要了，想退款",
    "帮忙退一下 {order} 订单",
    "我要退货退款，订单是 {order}",
    "订单 {order} 买错了，帮我申请退款",
    "麻烦把 {order} 的钱退回来",
]
REFUND_WITHOUT_ORDER = [
    "我想申请退款",
    "麻烦帮我办理退款",
    "买错东西了，我要退掉",
    "我不想要这个商品了，想退款",
    "帮我发起一个退款申请",
    "我要把刚买的东西退了",
    "可以帮我处理退货退款吗",
    "这件商品我想退掉并退款",
    "我需要申请退钱",
    "请帮忙走一下退款流程",
]
LOGISTICS_WITH_ORDER = [
    "帮我查一下订单 {order} 到哪儿了",
    "订单号 {order} 的物流现在是什么状态",
    "麻烦查查 {order} 这个包裹到哪了",
    "快递单对应的订单是 {order}，帮我看看进度",
    "{order} 什么时候能送到",
    "请查询一下 {order} 的配送情况",
    "我想知道订单 {order} 发货了没有",
    "帮忙追踪一下编号 {order} 的包裹",
    "看看 {order} 现在运输到哪里了",
    "请帮我查订单 {order} 的快递信息",
]
LOGISTICS_WITHOUT_ORDER = [
    "帮我查一下物流",
    "我的快递到哪儿了",
    "想看看包裹现在的配送进度",
    "麻烦查下发货情况",
    "我买的东西寄出来了吗",
    "查询一下快递状态",
    "能帮我追踪一下包裹吗",
    "这个订单什么时候送到",
    "我想知道商品的物流进度",
    "看看我的货发到哪里了",
]
POLICY_QUESTIONS = [
    "退款一般需要多久才能到账",
    "申请退款要符合什么条件",
    "退货退款的流程是什么",
    "退款会退回到原来的支付账户吗",
    "哪些商品不支持退款",
    "提交退款后通常几天处理完成",
    "退款规则是怎样的",
    "如果商品已经发货还可以申请退款吗",
    "退款成功后钱会退到哪里",
    "退货需要我自己承担运费吗",
    "什么情况下可以办理退款",
    "退款审核一般要等多长时间",
    "平台的退货政策是什么",
    "申请退款之后还能撤销吗",
    "退款到账时间有规定吗",
    "商品拆封后还能退吗",
    "退款需要提供哪些材料",
    "退货运费由谁来出",
    "退款申请提交后怎么处理",
    "我想了解一下退款政策",
]
AMBIGUOUS_ORDER = [
    "帮我看下订单 {order}",
    "麻烦查一下编号 {order} 的情况",
    "订单 {order} 现在怎么样了",
    "帮忙看看 {order} 这个单子",
    "我想了解一下订单 {order}",
]
AMBIGUOUS_ALTERNATIVES = [
    "查下物流，订单可能是 {first}，也可能是 {second}，我不确定",
    "帮我追踪一下包裹，单号在 {first} 和 {second} 里面，但记不清哪个了",
    "查物流订单 {first} 或 {second}，我想不起来具体是哪一个",
    "看看快递进度，我有 {first}、{second} 两个订单，不确定要查哪个",
    "请查下 {first} 或者 {second} 的物流，我不确定是哪笔",
]
OUT_OF_SCOPE = [
    "今天外面天气怎么样",
    "帮我写一首关于春天的诗",
    "你能讲个笑话吗",
    "推荐几本适合周末看的书",
    "解释一下什么是人工智能",
    "给我介绍一下杭州的景点",
    "现在几点了",
    "谢谢你",
    "你好呀",
    "帮我做一道数学题",
]


def _case(case_id: str, category: str, message: str, expected: dict, seed: int) -> dict:
    """构造一个带来源说明的样例，标明其为程序生成而非人工盲测。"""
    return {
        "id": case_id,
        "category": category,
        "origin": "seeded_random_template_generation",
        "generation_seed": seed,
        "request": {"message": message},
        "expected": expected,
        "annotation_note": "模板语义预先定义并由脚本生成；未经独立人工复核，不是盲测样例。",
    }


def generate(seed: int = 20261019) -> list[dict]:
    """按固定种子生成 110 条随机化表达和订单号样例。"""
    rng = random.Random(seed)
    result = []
    index = 1

    def order_id() -> str:
        """生成便于识别的随机订单号。"""
        return f"{rng.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{rng.randint(10000, 99999)}"

    def append_intent(category: str, messages: list[str], intent: str, slot: bool) -> None:
        """将模板表达绑定到预期意图与可选订单号实体。"""
        nonlocal index
        for _ in range(30 if intent in {"refund", "logistics"} else 20):
            template = rng.choice(messages)
            has_order = "{order}" in template
            value = order_id() if has_order else None
            message = template.format(order=value) if has_order else template
            entities = {"order_id": value} if has_order and slot else {}
            # 退款原因是消息中明确提供时的可提取实体，独立于订单号生成。
            if intent == "refund" and "买错了" in template:
                entities["reason"] = "买错了"
            elif intent == "refund" and "买错东西了" in template:
                entities["reason"] = "买错东西了"
            elif intent == "refund" and "不想要这个商品了" in template:
                entities["reason"] = "不想要这个商品了"
            elif intent == "refund" and "这单我不想要了" in template:
                entities["reason"] = "不想要了"
            expected = {
                "http_status": 200,
                "acts": [{
                    "business_intent": intent,
                    "entities": entities,
                    "dialogue_act": ["ask_question"] if intent == "policy_qa" else ["start_task"],
                    **({"target_hint": ["new_task"], "referenced_task_id": None}
                       if intent in {"refund", "logistics"} else {}),
                }],
                "ambiguity_required": [],
                # 缺订单号时，允许语义层标出待确认参数；策略层也可独立收集缺失字段。
                "ambiguity_forbidden": (["intent", "task", "other"]
                                         if intent in {"refund", "logistics"} and not has_order
                                         else ["intent", "task", "parameter", "other"]),
                "relations": [],
            }
            result.append(_case(f"random-v2-{index:03d}", category, message, expected, seed))
            index += 1

    append_intent("random_refund", REFUND_WITH_ORDER + REFUND_WITHOUT_ORDER, "refund", True)
    append_intent("random_logistics", LOGISTICS_WITH_ORDER + LOGISTICS_WITHOUT_ORDER, "logistics", True)
    append_intent("random_policy_question", POLICY_QUESTIONS, "policy_qa", False)

    for _ in range(10):
        message = rng.choice(AMBIGUOUS_ORDER).format(order=order_id())
        expected = {
            "http_status": 200, "acts": [], "ambiguity_required": ["intent"],
            "ambiguity_forbidden": [], "relations": [],
        }
        result.append(_case(f"random-v2-{index:03d}", "random_underspecified", message, expected, seed))
        index += 1

    for _ in range(10):
        first, second = order_id(), order_id()
        message = rng.choice(AMBIGUOUS_ALTERNATIVES).format(first=first, second=second)
        expected = {
            "http_status": 200,
            "acts": [{"business_intent": "logistics", "entities": {}}],
            "ambiguity_required": ["parameter"], "ambiguity_forbidden": [], "relations": [],
        }
        result.append(_case(f"random-v2-{index:03d}", "random_alternative_orders", message, expected, seed))
        index += 1

    for message in OUT_OF_SCOPE:
        expected = {
            "http_status": 200, "acts": [], "ambiguity_required": [],
            "ambiguity_forbidden": ["intent", "task", "parameter", "other"], "relations": [],
        }
        result.append(_case(f"random-v2-{index:03d}", "random_out_of_scope", message, expected, seed))
        index += 1
    rng.shuffle(result)
    return result


def main() -> None:
    """写出新的 JSONL 数据集，不覆盖已存在的数据。"""
    parser = argparse.ArgumentParser(description="生成可复现的随机意图识别扩展数据集")
    parser.add_argument("--seed", type=int, default=20261019)
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parents[1] / "datasets" / "intent_random_v2.jsonl",
    )
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"目标文件已存在，拒绝覆盖：{args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cases = generate(args.seed)
    args.output.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in cases),
        encoding="utf-8",
    )
    print(json.dumps({"output": str(args.output), "seed": args.seed, "cases": len(cases)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

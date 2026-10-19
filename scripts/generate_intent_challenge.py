"""生成本轮优化前冻结的 24 条边界集；不复制 v1 失败句子，不修改已存在版本。"""

import json
from pathlib import Path

from generate_intent_eval import CASES, act, add, context

ROOT = Path(__file__).resolve().parents[1]


def main():
    """冻结边界样例，覆盖意图/参数歧义、订单关系、上下文、话题切换和否定。

    参数：无。

    返回：
        None：将新版本数据集写入 evaluation/datasets；目标存在时拒绝覆盖。
    """
    CASES.clear()
    for message in ["麻烦看一下 D10101", "E10102 这个单帮我瞧瞧", "F10103 查查吧", "查一下 G10104 的情况"]:
        add("underspecified_query", message, [], ambiguities=["intent"])
    for message in [
        "查下物流，订单 D10201 或 E10202，我记不清了",
        "我想查快递，是 F10203 还是 G10204 来着",
        "包裹查询：可能 H10205，也可能 J10206",
        "查物流，K10207 和 L10208 二选一，先别猜",
    ]:
        add("alternative_orders", message, [act("logistics")], ambiguities=["parameter"])
    for first, second in [("D10301","E10302"),("F10303","G10304"),("H10305","J10306"),("K10307","L10308")]:
        add("parallel_orders", f"查 {first} 和 {second} 的物流，两单都查",
            [act("logistics",{"order_id":first}),act("logistics",{"order_id":second})],
            relations=[{"source_index":0,"target_index":1,"kind":"parallel"}])
    for message, order in [("D10401","D10401"),("订单是 E10402","E10402"),
                           ("编号 F10403","F10403"),("要查的单号 G10404","G10404")]:
        add("unique_pending_context",message,[act("logistics",{"order_id":order},"answer_pending")],ctx=context("logistics"))
    for order in ["D10501","E10502","F10503","G10504"]:
        add("explicit_new_topic",f"现在换个事情，追踪 {order} 的包裹",
            [act("logistics",{"order_id":order},"start_task","new_task",None)],ctx=context())
    for old,new in [("D10601","E10602"),("F10603","G10604"),("H10605","J10606"),("K10607","L10608")]:
        add("negated_mention",f"不是查 {old}，是查 {new} 的物流",[act("logistics",{"order_id":new})])
    for index, case in enumerate(CASES,1):
        case["id"]=f"intent-edge-v1-{index:03d}"
        case["origin"]="assistant_authored_frozen_edge_cases"
    path=ROOT/"evaluation/datasets/intent_edge_v1.jsonl"
    if path.exists():
        raise SystemExit("Frozen edge set exists; use a new version")
    path.write_text("".join(json.dumps(c,ensure_ascii=False)+"\n" for c in CASES),encoding="utf-8")
    print(f"Generated {len(CASES)} edge cases")


if __name__=="__main__":
    main()

"""意图分类目录 v1：维护用户目标、参数和能力声明，不执行路由或业务操作。"""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

TAXONOMY_VERSION = "1.0"


@dataclass(frozen=True)
class IntentDefinition:
    """一个已支持业务目标的不可变定义。

    属性：intent_id 为正式名称；legacy_id 为兼容输入别名；required_slots 为参数询问顺序；
    capabilities 是未来编排使用的能力需求，不代表已经实现工具或绑定某个 Agent。
    """

    intent_id: str
    legacy_id: str
    description: str
    mode: Literal["task", "knowledge"]
    task_type: Literal["refund", "logistics"] | None
    required_slots: tuple[str, ...]
    capabilities: tuple[str, ...]
    examples: tuple[str, ...]
    exclusions: tuple[str, ...]


INTENTS = MappingProxyType({
    "refund.apply": IntentDefinition(
        intent_id="refund.apply", legacy_id="refund", description="收集退款申请所需资料",
        mode="task", task_type="refund", required_slots=("order_id", "reason"),
        capabilities=("refund.application",),
        examples=("我要申请退款", "订单 A100 买错了，帮我退款"),
        exclusions=("退款进度查询", "撤销已提交退款", "退款规则咨询"),
    ),
    "logistics.track": IntentDefinition(
        intent_id="logistics.track", legacy_id="logistics", description="查询指定订单的物流情况",
        mode="task", task_type="logistics", required_slots=("order_id",),
        capabilities=("logistics.tracking",),
        examples=("查一下 A100 的物流", "我的包裹到哪里了"),
        exclusions=("修改收货地址", "物流催单", "只说看看订单但未说明用途"),
    ),
    "policy.consult": IntentDefinition(
        intent_id="policy.consult", legacy_id="policy_qa", description="咨询电商售后政策或规则",
        mode="knowledge", task_type=None, required_slots=(), capabilities=("policy.retrieval",),
        examples=("退款一般多久到账", "退货运费谁承担"),
        exclusions=("特定订单的实际退款进度", "直接办理退款", "一般百科问题"),
    ),
})


@dataclass(frozen=True)
class DialogueActDefinition:
    """对话动作定义；解释用户如何推进对话，不能直接授权外部操作。"""

    description: str
    target_required: bool
    boundary: str


DIALOGUE_ACTS = MappingProxyType({
    "start_task": DialogueActDefinition("提出新的业务目标", False, "明确新业务优先于旧待回答问题"),
    "answer_pending": DialogueActDefinition("回答待补信息或澄清问题", True, "歧义候选必须由用户唯一选定"),
    "correct": DialogueActDefinition("更正已提供的信息", True, "只写入当前消息中明确的新值"),
    "resume": DialogueActDefinition("恢复之前的任务或澄清", True, "多个候选任务时先澄清"),
    "cancel": DialogueActDefinition("请求放弃当前办理流程", True, "不能等同于撤销已提交的真实业务"),
    "ask_question": DialogueActDefinition("提出政策或规则问题", False, "咨询不覆盖正在办理的任务"),
    "confirm": DialogueActDefinition("确认明确的待确认对象", True, "没有待确认对象时不推导执行授权"),
    "reject": DialogueActDefinition("否定明确的候选或提议", True, "否定提及不自动取消已有任务"),
    "other": DialogueActDefinition("尚无明确动作归类", False, "不能作为执行外部业务的依据"),
})

# 候选目录与已支持目录分开：调用方不能把产品规划当作已实现能力。
PLANNED_INTENTS = (
    "refund.status", "refund.withdraw", "order.detail", "order.cancel",
    "order.change_address", "after_sales.exchange", "after_sales.repair",
    "support.complaint", "support.handoff",
)


def resolve_intent(intent_id: str) -> IntentDefinition:
    """按正式名称或当前 API 别名查找已支持意图。

    参数：intent_id 为正式 ID（如 refund.apply）或旧 ID（如 refund）。
    返回：不可变的业务意图定义。
    异常：KeyError 表示未知、未实现或兜底标签；调用方需要澄清或说明能力边界。
    """
    if intent_id in INTENTS:
        return INTENTS[intent_id]
    for definition in INTENTS.values():
        if definition.legacy_id == intent_id:
            return definition
    raise KeyError(f"Unsupported business intent: {intent_id}")

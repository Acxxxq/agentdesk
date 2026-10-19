"""检查分类目录与现有任务契约兼容，防止扩展时发生规则漂移。"""

from typing import get_args

import pytest

from agentorbis.domain.intent_registry import DIALOGUE_ACTS, INTENTS, resolve_intent
from agentorbis.domain.state import REQUIRED_SLOTS, CurrentFocus
from agentorbis.domain.understanding import Intent, MessageAct, MessageUnderstanding


def test_registered_task_slots_match_runtime_contract():
    for definition in INTENTS.values():
        if definition.task_type:
            assert definition.required_slots == REQUIRED_SLOTS[definition.task_type]


def test_all_business_labels_and_dialogue_acts_have_definitions():
    assert set(INTENTS) == set(get_args(Intent)) - {"unknown"}
    annotation = MessageAct.model_fields["dialogue_act"].annotation
    assert set(DIALOGUE_ACTS) == set(get_args(annotation))


@pytest.mark.parametrize("canonical,alias", [
    ("refund.apply", "refund"), ("logistics.track", "logistics"), ("policy.consult", "policy_qa"),
])
def test_alias_and_canonical_id_resolve_to_same_definition(canonical, alias):
    assert resolve_intent(canonical) is resolve_intent(alias)


@pytest.mark.parametrize("canonical,alias", [
    ("refund.apply", "refund"), ("logistics.track", "logistics"), ("policy.consult", "policy_qa"),
])
def test_legacy_actions_serialize_canonical_ids(canonical, alias):
    action = MessageAct(
        act_id="a1", business_intent=alias, dialogue_act="start_task", utterance_span="测试",
    )
    assert action.model_dump()["business_intent"] == canonical
    assert action.task_type == resolve_intent(canonical).task_type


def test_model_schema_only_advertises_canonical_intents():
    schema = MessageAct.model_json_schema()["properties"]["business_intent"]
    assert set(schema["enum"]) == set(INTENTS) | {"unknown"}
    result = MessageUnderstanding(acts=[], ambiguities=[], relations=[])
    assert result.model_dump()["taxonomy_version"] == "1.0"


def test_legacy_knowledge_focus_restores_canonical_intent():
    focus = CurrentFocus(kind="policy_qa", intent="policy_qa")
    assert focus.intent == "policy.consult"


@pytest.mark.parametrize("intent_id", ["unknown", "refund.withdraw", "order.cancel", "not_registered"])
def test_fallback_and_planned_intents_are_not_executable(intent_id):
    with pytest.raises(KeyError):
        resolve_intent(intent_id)

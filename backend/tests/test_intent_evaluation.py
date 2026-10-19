"""评测器自身的回归：错误绑定、多动作漏识别和接口错误不能被算成通过。"""

from agentorbis.evaluation.intent import score_case, summarize


def actual(acts):
    return {"acts": acts, "ambiguities": [], "relations": [], "source": "llm"}


def test_swapped_order_bindings_fail_even_when_intents_match():
    expected = {"acts": [
        {"business_intent": "logistics", "entities": {"order_id": "A1001"}},
        {"business_intent": "refund", "entities": {"order_id": "A2002"}},
    ]}
    result = actual([
        {"act_id": "a1", "business_intent": "logistics", "entities": {"order_id": "A2002"}},
        {"act_id": "a2", "business_intent": "refund", "entities": {"order_id": "A1001"}},
    ])
    assert not score_case(expected, result, 200)["passed"]


def test_missing_act_and_false_positive_are_not_ignored():
    expected = {"acts": [{"business_intent": "refund", "entities": {}}]}
    assert not score_case(expected, actual([]), 200)["passed"]
    assert not score_case({"acts": []}, actual([{"business_intent": "refund"}]), 200)["passed"]


def test_act_order_can_differ_but_relation_must_reference_correct_acts():
    expected = {"acts": [
        {"business_intent": "logistics", "entities": {"order_id": "A1001"}},
        {"business_intent": "refund", "entities": {"order_id": "A2002"}},
    ], "relations": [{"source_index": 0, "target_index": 1, "kind": "sequence"}]}
    result = actual([
        {"act_id": "b", "business_intent": "refund", "entities": {"order_id": "A2002"}},
        {"act_id": "a", "business_intent": "logistics", "entities": {"order_id": "A1001"}},
    ])
    result["relations"] = [{"source_act_id": "a", "target_act_id": "b", "kind": "sequence"}]
    assert score_case(expected, result, 200)["passed"]
    result["relations"][0]["source_act_id"] = "b"
    assert not score_case(expected, result, 200)["passed"]


def test_expected_422_passes_but_502_is_a_failure():
    assert score_case({"http_status": 422}, {"detail": []}, 422)["passed"]
    assert not score_case({"acts": []}, {"detail": "invalid_output"}, 502)["passed"]


def test_http_failures_remain_in_total_denominator():
    records = [
        {"category": "single", "elapsed_ms": 10, "http_status": 200,
         "assessment": {"passed": True, "checks": {"http_status": True, "intents": True}}},
        {"category": "single", "elapsed_ms": 20, "http_status": 502,
         "assessment": {"passed": False, "checks": {"http_status": False}}},
    ]
    summary = summarize(records)
    assert summary["total"] == 2
    assert summary["passed"] == 1
    assert summary["pass_rate"] == 0.5
    assert summary["http_errors"] == 1

"""意图识别 Demo 的离线测试；模拟 HTTP 响应，不调用真实模型。"""

import asyncio
import json

import httpx
import pytest
from pydantic import ValidationError

from agentorbis.domain.understanding import InterpretationRequest, MessageUnderstanding
from agentorbis.infrastructure.llm.message_interpreter import (
    InterpretationError,
    MessageInterpreter,
)


def act(**changes):
    """构造默认物流语义动作，可覆盖字段以验证边界。"""
    return {
        "act_id": "a1", "business_intent": "logistics.track", "dialogue_act": "start_task",
        "target_hint": "new_task", "referenced_task_id": None,
        "entities": {"order_id": "A1001"}, "utterance_span": "查 A1001 物流",
        "uncertainty": "low", **changes,
    }


def understanding(acts=None, **changes):
    """构造模型候选输出，source 由服务端补充。"""
    return {"acts": [act()] if acts is None else acts, "ambiguities": [], "relations": [], **changes}


def execute(payload, request=None, *, stop_reason="tool_use", status=200, next_payload=None):
    """经真实 Anthropic SDK 和模拟 HTTP 传输执行一次解析，并返回结果与出站请求。"""
    from anthropic import AsyncAnthropic

    captured = []

    def respond(outbound):
        captured.append(json.loads(outbound.content))
        tool_payload = next_payload if len(captured) > 1 and next_payload is not None else payload
        if status == 0:
            raise httpx.ReadTimeout("private timeout", request=outbound)
        if status != 200:
            return httpx.Response(status, json={"error": {"type": "api_error", "message": "private"}})
        return httpx.Response(200, json={
            "id": "msg_test", "type": "message", "role": "assistant", "model": "demo",
            "content": [{"type": "tool_use", "id": "tool_1", "name": "record_understanding", "input": tool_payload}],
            "stop_reason": stop_reason, "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 20},
        })

    async def run():
        async with AsyncAnthropic(
            api_key="test-key", base_url="https://example.test/anthropic",
            max_retries=0, http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
        ) as client:
            interpreter = MessageInterpreter(client, model="deepseek-v4-pro")
            return await interpreter.interpret(request or InterpretationRequest(message="查 A1001 物流"))

    return asyncio.run(run()), captured


def test_topic_switch_is_understood_without_mutating_context():
    request = InterpretationRequest.model_validate({
        "message": "查 A1001 物流",
        "conversation": {"active_task_id": "refund_1", "pending_question": {
            "task_id": "refund_1", "slot_name": "order_id", "question": "请提供退款订单号",
        }},
        "task_summaries": [{"task_id": "refund_1", "type": "refund", "status": "collecting"}],
    })
    before = request.model_dump()
    result, captured = execute(understanding(), request)
    assert result.acts[0].business_intent == "logistics.track"
    assert result.acts[0].target_hint == "new_task"
    assert result.source == "llm"
    assert request.model_dump() == before
    assert captured[0]["model"] == "deepseek-v4-pro"
    assert captured[0]["tool_choice"]["name"] == "record_understanding"
    assert "不能" in captured[0]["system"]


def test_preserves_multiple_acts_and_order():
    second = act(act_id="a2", business_intent="refund.apply", utterance_span="申请 A2002 退款",
                 entities={"order_id": "A2002"})
    result, _ = execute(understanding([act(), second], relations=[{
        "source_act_id": "a1", "target_act_id": "a2", "kind": "sequence", "condition": None,
    }]), InterpretationRequest(message="查 A1001 物流，再申请 A2002 退款"))
    assert [a.business_intent for a in result.acts] == ["logistics.track", "refund.apply"]
    assert result.relations[0].kind == "sequence"


def test_legacy_provider_label_is_normalized_at_sdk_boundary():
    result, _ = execute(understanding([act(business_intent="logistics")]))
    assert result.acts[0].business_intent == "logistics.track"
    assert result.model_dump()["taxonomy_version"] == "1.0"


def test_unknown_task_reference_is_rejected():
    with pytest.raises(InterpretationError, match="invalid_output"):
        execute(understanding([act(referenced_task_id="invented", target_hint="explicit_task")]))


def test_payload_wrapper_preserves_logistics_intent_and_ambiguity():
    request = InterpretationRequest(message="我昨天那个快递到哪了 帮我看看")
    payload = understanding([act(entities={}, utterance_span=request.message, uncertainty="medium")],
                            ambiguities=[{"kind": "parameter", "candidate_values": [], "reason": "请确认订单号"}])
    result, _ = execute({"payload": payload}, request)
    assert result.acts[0].business_intent == "logistics.track"
    assert result.acts[0].entities == {}
    assert result.ambiguities[0].kind == "parameter"


@pytest.mark.parametrize("payload", [
    {"payload": {}},
    {"payload": understanding(), "execute": True},
    {"payload": {"payload": understanding()}},
    {"payload": understanding([act(referenced_task_id="invented", target_hint="explicit_task")])},
    {"payload": understanding([act(entities={"order_id": "A9999"})])},
])
def test_payload_wrapper_does_not_bypass_validation(payload):
    with pytest.raises(InterpretationError, match="invalid_output"):
        execute(payload)


@pytest.mark.parametrize("payload", [
    {},
    understanding([act(), act()]),
    understanding(relations=[{"source_act_id": "a1", "target_act_id": "missing", "kind": "parallel"}]),
    understanding(relations=[{"source_act_id": "a1", "target_act_id": "a1", "kind": "sequence"}]),
    understanding([act(business_intent="execute_payment")]),
    understanding([act(utterance_span="用户没有说过的内容")]),
    understanding([act(entities={"order_id": "A9999"})]),
])
def test_invalid_model_output_is_rejected(payload):
    with pytest.raises(InterpretationError, match="invalid_output"):
        execute(payload)


def test_ambiguity_and_no_act_are_supported():
    result, _ = execute(understanding([], ambiguities=[{
        "kind": "intent", "candidate_values": ["logistics", "refund"], "reason": "查询对象不明确",
    }]), InterpretationRequest(message="帮我查一下 A1001"))
    assert not result.acts
    assert result.ambiguities[0].kind == "intent"


def test_truncated_output_is_rejected():
    with pytest.raises(InterpretationError, match="incomplete_output"):
        execute(understanding(), stop_reason="max_tokens")


def test_provider_error_is_sanitized():
    with pytest.raises(InterpretationError, match="provider_error") as error:
        execute({}, status=500)
    assert "private" not in str(error.value)


def test_invalid_output_gets_one_bounded_repair():
    result, requests = execute({}, next_payload=understanding())
    assert result.acts[0].business_intent == "logistics.track"
    assert len(requests) == 2
    assert "前一次工具参数" in requests[1]["system"]


def test_repair_receives_only_fixed_evidence_issue_not_raw_provider_output():
    invalid = understanding([act(utterance_span="不存在的改写片段")])
    result, requests = execute(invalid, next_payload=understanding())
    assert result.acts[0].business_intent == "logistics.track"
    assert len(requests) == 2
    assert "不是输入的连续原文" in requests[1]["system"]
    assert "不存在的改写片段" not in requests[1]["system"]


def test_parallel_acts_may_share_the_same_verbatim_message():
    message = "查 A1001 和 B2002 两个订单的物流"
    payload = understanding([
        act(utterance_span=message),
        act(act_id="a2", entities={"order_id": "B2002"}, utterance_span=message),
    ], relations=[{"source_act_id": "a1", "target_act_id": "a2", "kind": "parallel"}])
    result, requests = execute(payload, InterpretationRequest(message=message))
    assert len(result.acts) == 2
    assert len(requests) == 1


def test_request_rejects_whitespace_and_unknown_context_task():
    with pytest.raises(ValidationError):
        InterpretationRequest(message="   ")
    with pytest.raises(ValidationError):
        InterpretationRequest(message="继续", conversation={"active_task_id": "missing"})


def test_schema_does_not_allow_extra_fields():
    with pytest.raises(ValidationError):
        MessageUnderstanding.model_validate({**understanding(), "source": "llm", "execute": True})


def test_provider_timeout_is_sanitized():
    with pytest.raises(InterpretationError, match="provider_timeout"):
        execute({}, status=0)


def test_api_missing_key_and_production_gate(monkeypatch):
    from fastapi.testclient import TestClient

    from agentorbis.main import app

    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("APP_ENV", "development")
    with TestClient(app) as client:
        response = client.post("/api/v1/interpret", json={"message": "我要退款"})
        assert response.status_code == 503
        assert response.json()["detail"] == "missing_api_key"
        monkeypatch.setenv("APP_ENV", "production")
        response = client.post("/api/v1/interpret", json={"message": "我要退款"})
        assert response.status_code == 503
        assert response.json()["detail"] == "demo_disabled"


def test_api_returns_interpretation_and_sanitized_failure(monkeypatch):
    from fastapi.testclient import TestClient

    from agentorbis.main import app

    class StubInterpreter:
        """仅替换模型边界，验证实际路由与响应模型。"""

        async def interpret(self, request):
            if request.message == "超时":
                raise InterpretationError("provider_timeout")
            return MessageUnderstanding.model_validate(understanding())

    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("APP_ENV", "development")
    with TestClient(app) as client:
        app.state.interpreter = StubInterpreter()
        response = client.post("/api/v1/interpret", json={"message": "查 A1001 物流"}).json()
        assert response["source"] == "llm"
        assert response["taxonomy_version"] == "1.0"
        assert response["acts"][0]["business_intent"] == "logistics.track"
        assert client.post("/api/v1/interpret", json={"message": "超时"}).status_code == 504
        assert client.post("/api/v1/interpret", json={"message": " "}).status_code == 422

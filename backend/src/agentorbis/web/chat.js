"use strict";

// 浏览器只保存当前页面的聊天语境；模拟任务不随模型输出自动改变。
const elements = Object.fromEntries([
  "messages", "welcome", "scenario", "context-preview", "request-status",
  "composer", "message", "send", "clear",
].map(id => [id, document.getElementById(id)]));
const history = [];
let busy = false;

const labels = {
  intents: { refund: "申请退款", logistics: "查询物流", policy_qa: "退款政策咨询", unknown: "暂不明确" },
  acts: {
    start_task: "发起新任务", answer_pending: "补充待回答信息", resume: "继续已有任务",
    correct: "更正信息", cancel: "取消任务", ask_question: "知识咨询", confirm: "确认",
    reject: "否定", other: "其他表达",
  },
  targets: {
    new_task: "新任务", active_task: "当前任务", previous_task: "之前的任务",
    explicit_task: "指定任务", unspecified: "尚未指定",
  },
  uncertainty: { low: "低", medium: "中", high: "高" },
  entities: { order_id: "订单号", reason: "退款原因" },
  ambiguities: { intent: "意图", task: "目标任务", parameter: "参数", other: "其他" },
  relations: { parallel: "并列", sequence: "先后顺序", condition: "条件依赖" },
};

/** 返回所选场景的全新上下文对象；不把模型候选结果写入预设。 */
function scenarioContext() {
  if (elements.scenario.value === "refund") {
    return {
      conversation: {
        active_task_id: "refund_001",
        pending_question: { task_id: "refund_001", slot_name: "order_id", question: "请提供退款订单号" },
      },
      task_summaries: [{ task_id: "refund_001", type: "refund", status: "collecting", slots: { order_id: null } }],
    };
  }
  if (elements.scenario.value === "ambiguous") {
    return {
      conversation: {},
      task_summaries: [
        { task_id: "refund_001", type: "refund", status: "collecting", slots: { order_id: "A1001" } },
        { task_id: "refund_002", type: "refund", status: "collecting", slots: { order_id: "A2002" } },
      ],
    };
  }
  return { conversation: {}, task_summaries: [] };
}

/** 创建文本节点；用户输入、模型文本和 JSON 均通过 textContent 展示，避免注入 HTML。 */
function node(tag, className = "", text = "") {
  const item = document.createElement(tag);
  item.className = className;
  item.textContent = text;
  return item;
}

/** 新增一条消息壳，返回可填充内容的 bubble；不改变发给模型的历史。 */
function messageBubble(role) {
  elements.welcome.hidden = true;
  const message = node("article", `message ${role}`);
  const label = node("div", "message-label");
  if (role === "assistant") label.append(node("span", "mini-orbit", "◎"));
  label.append(document.createTextNode(role === "user" ? "你" : "AgentOrbis · 语义解析"));
  const bubble = node("div", "bubble");
  message.append(label, bubble);
  elements.messages.append(message);
  return bubble;
}

function scrollToBottom() {
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

/** 同步表单忙状态；请求期间禁止新消息与上下文变更，避免响应串线。 */
function setBusy(value) {
  busy = value;
  for (const element of [elements.message, elements.send, elements.clear, elements.scenario]) {
    element.disabled = value;
  }
  document.querySelectorAll(".suggestion").forEach(button => { button.disabled = value; });
  elements.composer.setAttribute("aria-busy", String(value));
  elements.send.firstChild.textContent = value ? "识别中 " : "发送 ";
}

/** 更新预设摘要和本轮会携带的历史条数。 */
function refreshContext() {
  const context = scenarioContext();
  const preview = elements["context-preview"];
  preview.replaceChildren();
  if (!context.task_summaries.length) {
    preview.append(node("div", "", "当前没有已有任务。先试一句业务请求，或选择退款场景测试话题切换。"));
  } else {
    preview.append(node("div", "", elements.scenario.value === "refund" ? "正在等待：退款订单号" : "需要区分：两个退款任务"));
    context.task_summaries.forEach(task => {
      preview.append(node("span", "task-chip", `${task.task_id} · ${task.slots.order_id || "订单号未填写"}`));
    });
  }
  elements["request-status"].textContent = `当前：${elements.scenario.selectedOptions[0].textContent} · 携带最近 ${Math.min(history.length, 10)} 条消息`;
}

/** 清空页面内存中的聊天记录；保留当前预设，并恢复欢迎页。 */
function resetChat() {
  if (busy) return;
  history.length = 0;
  elements.messages.querySelectorAll(".message").forEach(message => message.remove());
  elements.welcome.hidden = false;
  elements.message.value = "";
  elements.message.style.height = "auto";
  refreshContext();
  elements.message.focus();
}

/** 展示结构化 JSON，方便核对原始输出或本轮提交的上下文。 */
function appendDetails(parent, title, data) {
  const details = node("details", "raw-details");
  details.append(node("summary", "", title), node("pre", "", JSON.stringify(data, null, 2)));
  parent.append(details);
}

/** 渲染模型结果，并返回有明确“仅识别”标记的摘要，供后续消息消歧使用。 */
function renderResult(bubble, result, request) {
  bubble.replaceChildren();
  const summaries = [];
  bubble.append(node("p", "result-intro", result.acts.length ? `这句话包含 ${result.acts.length} 个语义动作：` : "当前没有识别到可确定的业务动作。"));
  result.acts.forEach((act, index) => {
    const intent = labels.intents[act.business_intent] || act.business_intent;
    const action = labels.acts[act.dialogue_act] || act.dialogue_act;
    const card = node("section", "act-card");
    const head = node("div", "act-head");
    head.append(node("span", "intent-badge", intent), node("span", "act-type", `${index + 1}. ${action}`));
    card.append(head);
    let target = labels.targets[act.target_hint] || act.target_hint;
    if (act.referenced_task_id) target += `（${act.referenced_task_id}）`;
    card.append(node("p", "act-meta", `目标：${target}　·　不确定程度：${labels.uncertainty[act.uncertainty] || act.uncertainty}`));
    const entityRow = node("div", "entity-row");
    Object.entries(act.entities).forEach(([key, value]) => entityRow.append(node("span", "entity-tag", `${labels.entities[key] || key}：${value}`)));
    if (entityRow.childNodes.length) card.append(entityRow);
    card.append(node("p", "evidence", `原文依据：「${act.utterance_span}」`));
    bubble.append(card);
    summaries.push(`${intent} / ${action} / ${target} / 候选实体 ${JSON.stringify(act.entities)}`);
  });
  result.ambiguities.forEach(ambiguity => {
    const text = `${labels.ambiguities[ambiguity.kind] || ambiguity.kind}存在歧义：${ambiguity.reason}`;
    bubble.append(node("div", "ambiguity", text));
    summaries.push(text);
  });
  result.relations.forEach(relation => {
    bubble.append(node("div", "relation", `${relation.source_act_id} → ${relation.target_act_id} · ${labels.relations[relation.kind] || relation.kind}${relation.condition ? `：${relation.condition}` : ""}`));
  });
  bubble.append(node("p", "result-note", "以上仅为语义识别结果，任务和槽位均未改变。"));
  appendDetails(bubble, "查看结构化结果", result);
  appendDetails(bubble, "查看本轮输入上下文", request);
  return `[意图识别摘要，非实际客服回复；未执行任何动作] ${summaries.join("；") || "无确定的业务动作"}`.slice(0, 4000);
}

/** 将脱敏 API 错误映射为中文提示；原始响应正文不直接显示。 */
function errorMessage(code) {
  return {
    missing_api_key: "尚未配置模型密钥，请检查服务端 .env 后重新启动 API。",
    provider_timeout: "模型响应超时，未产生任务变更，可以稍后重试。",
    provider_error: "模型服务暂时不可用，请稍后重试。",
    invalid_output: "模型输出未通过结构校验，已拒绝该结果，请重试。",
    incomplete_output: "模型输出不完整，已拒绝该结果，请重试。",
    demo_disabled: "此测试接口只在开发环境开放。",
    invalid_request: "输入或上下文不符合格式要求，请重新选择测试场景。",
    network_error: "无法连接 API，请确认现有服务正在运行。",
  }[code] || "暂时无法完成识别，请稍后重试。";
}

/** 提交当前消息和最近 10 条成功消息；失败结果不加入模型历史。 */
async function sendMessage(text) {
  const message = text.trim();
  if (busy || !message) return;
  const request = { message, recent_messages: history.slice(-10), ...scenarioContext() };
  messageBubble("user").textContent = message;
  const bubble = messageBubble("assistant");
  const loading = node("div", "loading");
  loading.append(node("span", "spinner"), document.createTextNode("正在理解这条消息…"));
  bubble.append(loading);
  elements.message.value = "";
  elements.message.style.height = "auto";
  setBusy(true);
  scrollToBottom();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 65000);
  try {
    const response = await fetch("/api/v1/interpret", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request), signal: controller.signal,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(response.status === 422 ? "invalid_request" : data.detail);
    const summary = renderResult(bubble, data, request);
    history.push({ role: "user", content: message }, { role: "assistant", content: summary });
    // 内存同样只保留最近 5 轮，清空或刷新页面后不会恢复聊天内容。
    if (history.length > 10) history.splice(0, history.length - 10);
  } catch (error) {
    const code = error.name === "AbortError" ? "provider_timeout" : error.message;
    const panel = node("div", "error", errorMessage(code === "Failed to fetch" ? "network_error" : code));
    const retry = node("button", "", "将消息放回输入框");
    retry.type = "button";
    retry.addEventListener("click", () => {
      if (!busy) { elements.message.value = message; elements.message.focus(); }
    });
    panel.append(retry);
    bubble.replaceChildren(panel);
  } finally {
    clearTimeout(timer);
    setBusy(false);
    refreshContext();
    scrollToBottom();
    elements.message.focus();
  }
}

elements.composer.addEventListener("submit", event => {
  event.preventDefault();
  sendMessage(elements.message.value);
});
elements.message.addEventListener("keydown", event => {
  // 中文输入法确认候选词时不发送，Shift + Enter 保留换行。
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing && event.keyCode !== 229) {
    event.preventDefault();
    elements.composer.requestSubmit();
  }
});
elements.message.addEventListener("input", () => {
  elements.message.style.height = "auto";
  elements.message.style.height = `${Math.min(elements.message.scrollHeight, 144)}px`;
});
elements.clear.addEventListener("click", resetChat);
elements.scenario.addEventListener("change", resetChat);
document.querySelectorAll(".suggestion").forEach(button => {
  button.addEventListener("click", () => {
    if (busy) return;
    if (button.dataset.scenario) { elements.scenario.value = button.dataset.scenario; resetChat(); }
    sendMessage(button.dataset.message);
  });
});
refreshContext();

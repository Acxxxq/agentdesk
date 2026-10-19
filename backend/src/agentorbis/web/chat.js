"use strict";

// 浏览器只保存会话 ID；任务状态由聊天 API 的会话存储管理。
const elements = Object.fromEntries([
  "messages", "welcome", "context-preview", "request-status",
  "composer", "message", "send", "clear",
].map(id => [id, document.getElementById(id)]));
let conversationId = sessionStorage.getItem("agentorbis.conversation_id");
let busy = false;

const labels = {
  intents: {
    "refund.apply": "申请退款", "logistics.track": "查询物流", "policy.consult": "售后政策咨询",
    // 历史消息仍可显示旧名称；新接口统一返回正式意图 ID。
    refund: "申请退款", logistics: "查询物流", policy_qa: "售后政策咨询", unknown: "暂不明确",
  },
  acts: {
    start_task: "发起新任务", answer_pending: "补充待回答信息", resume: "继续已有任务",
    correct: "更正信息", cancel: "取消任务", ask_question: "知识咨询", confirm: "确认",
    reject: "否定", other: "其他表达",
  },
  targets: {
    new_task: "新任务", active_task: "当前任务", previous_task: "之前的任务",
    explicit_task: "指定任务", unspecified: "尚未指定",
  },
  statuses: {
    collecting: "等待补充", ready: "信息齐备", executing: "处理中",
    waiting_external: "等待外部服务", completed: "已完成", cancelled: "已取消", failed: "失败",
  },
  entities: { order_id: "订单号", reason: "退款原因" },
  ambiguities: { intent: "业务意图", task: "目标任务", parameter: "参数", other: "其他" },
  relations: { parallel: "并列", sequence: "先后顺序", condition: "条件依赖" },
};

function node(tag, className = "", text = "") {
  const item = document.createElement(tag);
  item.className = className;
  item.textContent = text;
  return item;
}

function scrollToBottom() {
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

function setBusy(value) {
  busy = value;
  for (const element of [elements.message, elements.send, elements.clear]) element.disabled = value;
  elements.composer.setAttribute("aria-busy", String(value));
  elements.send.firstChild.textContent = value ? "处理中 " : "发送 ";
}

function messageBubble(role) {
  elements.welcome.hidden = true;
  const message = node("article", `message ${role}`);
  const label = node("div", "message-label");
  if (role === "assistant") label.append(node("span", "mini-orbit", "◎"));
  label.append(document.createTextNode(role === "user" ? "你" : "AgentOrbis · 对话助手"));
  const bubble = node("div", "bubble");
  message.append(label, bubble);
  elements.messages.append(message);
  return bubble;
}

function appendPlainMessage(role, text) {
  const bubble = messageBubble(role);
  bubble.append(node("p", role === "assistant" ? "assistant-reply" : "", text));
  return bubble;
}

function appendDetails(parent, title, data) {
  const details = node("details", "raw-details");
  details.append(node("summary", "", title), node("pre", "", JSON.stringify(data, null, 2)));
  parent.append(details);
}

function renderUnderstanding(parent, result) {
  const section = node("section", "diagnostic-section");
  section.append(node("p", "diagnostic-title", result.acts.length
    ? `识别到 ${result.acts.length} 个语义动作`
    : "没有识别到明确的业务动作"));
  result.acts.forEach((act, index) => {
    const card = node("div", "act-card");
    const intent = labels.intents[act.business_intent] || act.business_intent;
    const action = labels.acts[act.dialogue_act] || act.dialogue_act;
    card.append(node("strong", "", `${index + 1}. ${intent} · ${action}`));
    const target = labels.targets[act.target_hint] || act.target_hint;
    card.append(node("p", "act-meta", `目标：${target}${act.referenced_task_id ? `（${act.referenced_task_id}）` : ""}`));
    Object.entries(act.entities).forEach(([key, value]) => {
      card.append(node("span", "entity-tag", `${labels.entities[key] || key}：${value}`));
    });
    card.append(node("p", "evidence", `原文依据：「${act.utterance_span}」`));
    section.append(card);
  });
  result.ambiguities.forEach(item => {
    section.append(node("div", "ambiguity", `${labels.ambiguities[item.kind] || item.kind}需要确认：${item.reason || "信息不足"}`));
  });
  result.relations.forEach(item => {
    section.append(node("div", "relation", `${item.source_act_id} → ${item.target_act_id} · ${labels.relations[item.kind] || item.kind}${item.condition ? `：${item.condition}` : ""}`));
  });
  appendDetails(section, "查看原始语义结构", result);
  parent.append(section);
}

function renderResponse(data) {
  const bubble = messageBubble("assistant");
  bubble.append(node("p", "assistant-reply", data.reply));
  if (data.events.length) {
    const changed = data.events.map(event => event.event_type).join("、");
    bubble.append(node("p", "result-note", `本轮状态变化：${changed}`));
  }
  renderUnderstanding(bubble, data.understanding);
  appendDetails(bubble, "查看策略决策与状态事件", {
    decisions: data.policy.decisions,
    events: data.events,
    state_version: data.state.version,
  });
  refreshContext(data.state);
  return bubble;
}

function refreshContext(state = null) {
  const preview = elements["context-preview"];
  preview.replaceChildren();
  if (!state) {
    preview.append(node("div", "", "发送一条消息后，这里会显示当前任务和待处理事项。"));
    elements["request-status"].textContent = conversationId
      ? `会话 ${conversationId.slice(0, 8)} · 正在恢复`
      : "新会话 · 状态保存在当前开发服务中";
    return;
  }
  const tasks = state.tasks || [];
  if (!tasks.length) preview.append(node("div", "", "当前没有业务任务。"));
  tasks.forEach(task => {
    const title = task.type === "refund" ? "退款" : "物流查询";
    const card = node("div", "session-task");
    card.append(node("strong", "", title), node("span", "task-status", labels.statuses[task.status] || task.status));
    const orderId = task.slots.order_id;
    if (orderId) card.append(node("div", "task-chip", `订单 ${orderId}`));
    if (task.slots.reason) card.append(node("div", "task-chip", `原因：${task.slots.reason}`));
    preview.append(card);
  });
  if (state.pending_question) preview.append(node("div", "pending-chip", `待补充：${state.pending_question.question}`));
  if (state.pending_clarification) preview.append(node("div", "pending-chip", `待澄清：${state.pending_clarification.question}`));
  if (state.suspended_clarifications?.length) {
    preview.append(node("div", "paused-chip", `已暂存 ${state.suspended_clarifications.length} 个待澄清请求`));
  }
  elements["request-status"].textContent = `会话 ${conversationId.slice(0, 8)} · 状态版本 ${state.version} · ${tasks.length} 个任务`;
}

function clearMessages() {
  elements.messages.querySelectorAll(".message").forEach(item => item.remove());
  elements.welcome.hidden = false;
}

function resetChat() {
  if (busy) return;
  conversationId = null;
  sessionStorage.removeItem("agentorbis.conversation_id");
  clearMessages();
  elements.message.value = "";
  elements.message.style.height = "auto";
  refreshContext();
  elements.message.focus();
}

function errorMessage(code) {
  return {
    missing_api_key: "服务端尚未配置模型密钥，请检查 .env。",
    provider_timeout: "模型响应超时，本轮没有更新任务状态，可以重试。",
    provider_error: "模型服务暂时不可用，请稍后重试。",
    invalid_output: "模型输出未通过校验，本轮没有更新任务状态。",
    incomplete_output: "模型输出不完整，本轮没有更新任务状态。",
    demo_disabled: "聊天工作台只在开发环境开放。",
    invalid_request: "消息格式不正确，请修改后重试。",
    state_conflict: "任务状态发生冲突，本轮没有保存，请重新发送。",
    network_error: "无法连接 AgentOrbis API，请确认服务正在运行。",
    conversation_capacity_reached: "开发会话容量已满，请新建会话后重试。",
  }[code] || "暂时无法处理这条消息，请稍后重试。";
}

async function postChat(message, id) {
  return fetch("/api/v1/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id: id, message }),
  });
}

async function sendMessage(text) {
  const message = text.trim();
  if (busy || !message) return;
  appendPlainMessage("user", message);
  const bubble = messageBubble("assistant");
  const loading = node("div", "loading");
  loading.append(node("span", "spinner"), document.createTextNode("正在理解并更新会话状态…"));
  bubble.append(loading);
  elements.message.value = "";
  elements.message.style.height = "auto";
  setBusy(true);
  scrollToBottom();
  try {
    let response = await postChat(message, conversationId);
    let data = await response.json();
    if (response.status === 404 && data.detail === "conversation_not_found") {
      // 开发服务重启会清空内存会话；将当前消息作为新会话的第一条继续处理。
      conversationId = null;
      sessionStorage.removeItem("agentorbis.conversation_id");
      response = await postChat(message, null);
      data = await response.json();
    }
    if (!response.ok) throw new Error(response.status === 422 ? "invalid_request" : data.detail);
    conversationId = data.conversation_id;
    sessionStorage.setItem("agentorbis.conversation_id", conversationId);
    bubble.replaceChildren();
    renderResponse(data);
  } catch (error) {
    const code = error.message === "Failed to fetch" ? "network_error" : error.message;
    const panel = node("div", "error");
    panel.append(node("p", "", errorMessage(code)));
    const retry = node("button", "", "重新发送");
    retry.type = "button";
    retry.addEventListener("click", () => { if (!busy) sendMessage(message); });
    panel.append(retry);
    bubble.replaceChildren(panel);
  } finally {
    setBusy(false);
    scrollToBottom();
    elements.message.focus();
  }
}

async function restoreConversation() {
  if (!conversationId) {
    refreshContext();
    return;
  }
  try {
    const response = await fetch(`/api/v1/chat/${encodeURIComponent(conversationId)}`);
    if (response.status === 404) {
      conversationId = null;
      sessionStorage.removeItem("agentorbis.conversation_id");
      refreshContext();
      return;
    }
    if (!response.ok) throw new Error("restore_failed");
    const snapshot = await response.json();
    snapshot.recent_messages.forEach(message => appendPlainMessage(message.role, message.content));
    refreshContext(snapshot.state);
    scrollToBottom();
  } catch {
    refreshContext();
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
document.querySelectorAll(".suggestion").forEach(button => {
  button.addEventListener("click", () => { if (!busy) sendMessage(button.dataset.message); });
});
restoreConversation();

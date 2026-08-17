/**
 * SCNA Assistant widget.
 */
(function () {
  "use strict";

  const root = document.getElementById("scna-assistant");
  if (!root) return;

  const toggleBtn = document.getElementById("assistant-toggle");
  const closeBtn = document.getElementById("assistant-close");
  const panel = document.getElementById("assistant-panel");
  const messagesEl = document.getElementById("assistant-messages");
  const suggestionsEl = document.getElementById("assistant-suggestions");
  const form = document.getElementById("assistant-form");
  const input = document.getElementById("assistant-input");
  const sendBtn = document.getElementById("assistant-send");

  const history = [];
  let sending = false;

  function setOpen(open) {
    root.dataset.open = open ? "true" : "false";
    toggleBtn.setAttribute("aria-label", open ? "Close SCNA Assistant" : "Open SCNA Assistant");
    if (open) {
      window.setTimeout(() => input.focus(), 150);
    }
  }

  toggleBtn.addEventListener("click", () => setOpen(root.dataset.open !== "true"));
  closeBtn.addEventListener("click", () => setOpen(false));

  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      setOpen(true);
    } else if (e.key === "Escape" && root.dataset.open === "true") {
      setOpen(false);
    }
  });

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addMessage(role, text) {
    const wrap = document.createElement("div");
    wrap.className = "assistant-msg " + (role === "user" ? "assistant-msg-user" : "assistant-msg-bot");
    const bubble = document.createElement("div");
    bubble.className = "assistant-bubble-text";
    bubble.textContent = text;
    wrap.appendChild(bubble);
    messagesEl.appendChild(wrap);
    scrollToBottom();
  }

  function addResults(results) {
    if (!results || !results.length) return;
    const wrap = document.createElement("div");
    wrap.className = "assistant-results";
    results.forEach((r) => {
      const link = document.createElement("a");
      link.className = "assistant-result-card";
      link.href = r.url;
      const title = document.createElement("div");
      title.className = "assistant-result-title";
      title.textContent = r.title;
      link.appendChild(title);
      if (r.subtitle) {
        const sub = document.createElement("div");
        sub.className = "assistant-result-subtitle";
        sub.textContent = r.subtitle;
        link.appendChild(sub);
      }
      const arrow = document.createElement("span");
      arrow.className = "assistant-result-arrow";
      arrow.textContent = "→";
      link.appendChild(arrow);
      wrap.appendChild(link);
    });
    messagesEl.appendChild(wrap);
    scrollToBottom();
  }

  function addTyping() {
    const wrap = document.createElement("div");
    wrap.className = "assistant-msg assistant-msg-bot assistant-typing";
    wrap.id = "assistant-typing-indicator";
    const dots = document.createElement("div");
    dots.className = "assistant-typing-dots";
    dots.innerHTML = "<span></span><span></span><span></span>";
    wrap.appendChild(dots);
    messagesEl.appendChild(wrap);
    scrollToBottom();
  }

  function removeTyping() {
    const el = document.getElementById("assistant-typing-indicator");
    if (el) el.remove();
  }

  async function sendMessage(text) {
    if (sending || !text.trim()) return;
    sending = true;
    sendBtn.disabled = true;
    if (suggestionsEl) suggestionsEl.remove();

    addMessage("user", text);
    history.push({ role: "user", text });
    addTyping();

    try {
      const resp = await fetch("/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history: history.slice(-12) }),
      });

      removeTyping();
      if (resp.status === 401) {
        addMessage("bot", "Your session expired -- please log in again.");
        sending = false;
        sendBtn.disabled = false;
        return;
      }

      const data = await resp.json();
      const reply = data.reply || "Sorry, I didn't get a response for that.";
      addMessage("bot", reply);
      history.push({ role: "assistant", text: reply });
      addResults(data.results);
    } catch (err) {
      removeTyping();
      addMessage("bot", "I couldn't reach the server -- please check your connection and try again.");
    } finally {
      sending = false;
      sendBtn.disabled = false;
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = input.value;
    input.value = "";
    input.style.height = "auto";
    sendMessage(text);
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 120) + "px";
  });

  if (suggestionsEl) {
    suggestionsEl.querySelectorAll(".assistant-chip").forEach((chip) => {
      chip.addEventListener("click", () => sendMessage(chip.dataset.q));
    });
  }
})();

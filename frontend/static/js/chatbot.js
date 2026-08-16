/**
 * AI chatbot widget. Conversation history lives in sessionStorage (per
 * browser tab, survives navigating between pages, cleared on tab close) so
 * the assistant can be asked a follow-up after clicking through to a
 * different page. The server never stores this history itself -- the full
 * conversation is resent on every message (see /chatbot/message).
 */
(function () {
    const HISTORY_KEY = 'scna_chatbot_history';
    const MAX_STORED_MESSAGES = 30;

    const scriptTag = document.currentScript;
    const endpoint = scriptTag ? scriptTag.getAttribute('data-endpoint') : '/chatbot/message';

    const panel = document.getElementById('chatbotPanel');
    const toggleBtn = document.getElementById('chatbotToggle');
    const messagesEl = document.getElementById('chatbotMessages');
    const suggestionsEl = document.getElementById('chatbotSuggestions');
    const inputEl = document.getElementById('chatbotInput');
    const formEl = document.getElementById('chatbotForm');

    if (!panel || !toggleBtn || !messagesEl || !inputEl || !formEl) {
        // Widget markup isn't on this page (e.g. logged-out auth pages) --
        // nothing to wire up.
        return;
    }

    let sending = false;

    function loadHistory() {
        try {
            const raw = sessionStorage.getItem(HISTORY_KEY);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            return [];
        }
    }

    function saveHistory(history) {
        try {
            sessionStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(-MAX_STORED_MESSAGES)));
        } catch (e) {
            // Storage full or unavailable -- conversation just won't
            // persist across a page navigation, which is a fine fallback.
        }
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // Very small, safe subset of markdown: bold, and bare URLs / relative
    // paths become links. No raw HTML from the model is ever injected.
    function renderMessageHtml(text) {
        let safe = escapeHtml(text);
        safe = safe.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        safe = safe.replace(/(^|[\s(])(\/[a-zA-Z0-9\-_\/]+)/g, '$1<a href="$2">$2</a>');
        safe = safe.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        safe = safe.replace(/\n/g, '<br>');
        return safe;
    }

    function appendMessage(role, text, opts) {
        opts = opts || {};
        const row = document.createElement('div');
        row.className = 'chatbot-msg ' + (role === 'user' ? 'chatbot-msg-user' : 'chatbot-msg-bot');
        if (opts.isError) row.classList.add('chatbot-msg-error');
        const p = document.createElement('p');
        p.innerHTML = renderMessageHtml(text);
        row.appendChild(p);
        messagesEl.appendChild(row);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        return row;
    }

    function showTyping() {
        const row = document.createElement('div');
        row.className = 'chatbot-msg chatbot-msg-bot chatbot-typing';
        row.id = 'chatbotTypingRow';
        row.innerHTML = '<span class="chatbot-typing-dot"></span><span class="chatbot-typing-dot"></span><span class="chatbot-typing-dot"></span>';
        messagesEl.appendChild(row);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function hideTyping() {
        const row = document.getElementById('chatbotTypingRow');
        if (row) row.remove();
    }

    function setSending(isSending) {
        sending = isSending;
        inputEl.disabled = isSending;
        const btn = formEl.querySelector('.chatbot-send-btn');
        if (btn) btn.disabled = isSending;
    }

    async function sendToServer(history) {
        const resp = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: history }),
        });
        const data = await resp.json().catch(function () { return {}; });
        if (!resp.ok) {
            throw new Error(data.error || 'The assistant is unavailable right now. Please try again shortly.');
        }
        return data.reply;
    }

    async function ask(text) {
        text = (text || '').trim();
        if (!text || sending) return;

        if (suggestionsEl) suggestionsEl.style.display = 'none';
        appendMessage('user', text);

        const history = loadHistory();
        history.push({ role: 'user', content: text });
        saveHistory(history);

        inputEl.value = '';
        setSending(true);
        showTyping();

        try {
            const reply = await sendToServer(history);
            hideTyping();
            appendMessage('assistant', reply);
            history.push({ role: 'assistant', content: reply });
            saveHistory(history);
        } catch (err) {
            hideTyping();
            appendMessage('assistant', err.message, { isError: true });
        } finally {
            setSending(false);
            inputEl.focus();
        }
    }

    function submit(evt) {
        evt.preventDefault();
        ask(inputEl.value);
        return false;
    }

    function toggle() {
        const isOpen = panel.classList.toggle('open');
        toggleBtn.classList.toggle('open', isOpen);
        toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        panel.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
        if (isOpen) inputEl.focus();
    }

    function clearConversation() {
        sessionStorage.removeItem(HISTORY_KEY);
        messagesEl.querySelectorAll('.chatbot-msg').forEach(function (el, i) {
            if (i > 0) el.remove(); // keep the initial greeting
        });
        if (suggestionsEl) suggestionsEl.style.display = '';
    }

    // Replay any history saved from a previous page in this tab.
    (function restore() {
        const history = loadHistory();
        if (!history.length) return;
        if (suggestionsEl) suggestionsEl.style.display = 'none';
        history.forEach(function (m) {
            appendMessage(m.role === 'user' ? 'user' : 'assistant', m.content);
        });
    })();

    window.Chatbot = { toggle: toggle, submit: submit, ask: ask, clear: clearConversation };
})();

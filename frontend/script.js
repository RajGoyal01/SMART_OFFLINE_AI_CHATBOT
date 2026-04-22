/* ============================================================
   R4 Rescue — Offline Intelligence Frontend Logic
   ============================================================ */

(() => {
    "use strict";

    // ─── DOM refs ────────────────────────────────────────────
    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebar-toggle");

    // Nav buttons
    const navChat = document.getElementById("nav-chat");
    const navMap = document.getElementById("nav-map");
    const navWalkyTalky = document.getElementById("nav-walky-talky");
    const navRadio = document.getElementById("nav-radio");
    const navEmergencySos = document.getElementById("nav-emergency-sos");
    const navChatHistory = document.getElementById("nav-chat-history");
    const navSettings = document.getElementById("nav-settings");

    // View panels
    const viewChat = document.getElementById("view-chat");
    const viewMap = document.getElementById("view-map");
    const viewWalkyTalky = document.getElementById("view-walky-talky");
    const viewRadio = document.getElementById("view-radio");
    const viewEmergencySos = document.getElementById("view-emergency-sos");
    const viewChatHistory = document.getElementById("view-chat-history");
    const viewSettings = document.getElementById("view-settings");

    // Chat elements
    const welcomeScreen = document.getElementById("welcome-screen");
    const chatMessages = document.getElementById("chat-messages");
    const chatInputArea = document.getElementById("chat-input-area");

    // Welcome screen input
    const messageInput = document.getElementById("message-input");
    const sendBtn = document.getElementById("send-btn");

    // Chat mode input
    const messageInputChat = document.getElementById("message-input-chat");
    const sendBtnChat = document.getElementById("send-btn-chat");

    // Mic buttons
    const micBtn = document.getElementById("mic-btn");
    const micBtnChat = document.getElementById("mic-btn-chat");

    // Settings modal (legacy)
    const settingsBtn = document.getElementById("settings-btn");
    const settingsModal = document.getElementById("settings-modal");
    const closeSettings = document.getElementById("close-settings");
    const tempSlider = document.getElementById("temperature-slider");
    const tempValue = document.getElementById("temperature-value");
    const clearDataBtn = document.getElementById("clear-data-btn");

    // Settings view (inline)
    const tempSliderInline = document.getElementById("temperature-slider-inline");
    const tempValueInline = document.getElementById("temperature-value-inline");
    const clearDataBtnInline = document.getElementById("clear-data-btn-inline");

    // ─── Simulated AI responses ──────────────────────────────
    const aiResponses = [
        "R4 Rescue here. Let me analyze that for you.\n\nBased on field data, there are several critical factors:\n\n1. **Assess the situation** — Determine immediate threats\n2. **Secure communication** — Establish relay if possible\n3. **Follow protocol** — Standard operating procedures apply\n\nNeed me to elaborate on any of these?",
        "Copy that. Here's my assessment:\n\nThe key principle in this scenario is to prioritize safety above all else. Rushing without proper evaluation increases risk.\n\n> \"Preparation eliminates hesitation.\" — Field Manual\n\nWant me to run a deeper analysis?",
        "Acknowledged. Breaking this down:\n\n**Situation Report:**\n- Current conditions favor cautious approach\n- Resources should be allocated efficiently\n- Communication channels must remain open\n\nI can provide more detailed guidance. What's your priority?",
        "Good query. Here's what the data shows:\n\nThe short answer: it depends on your operational context. General guidance:\n\n• **Level 1:** Immediate response — stabilize the situation\n• **Level 2:** Assessment — gather intel and resources\n• **Level 3:** Long-term — establish sustainable operations\n\nWhat operational level are you working at?",
        "R4 processing... Analysis complete.\n\nBased on available offline data, here are the recommended steps:\n\n1. **Secure the perimeter** — Safety first\n2. **Establish comms** — Even low-bandwidth helps\n3. **Deploy resources** — Prioritize critical needs\n4. **Document everything** — For after-action review\n\nShall I detail any specific step?"
    ];

    // ─── Nav / View mapping ──────────────────────────────────
    const navMap_ = {
        "chat": { nav: navChat, view: viewChat },
        "map": { nav: navMap, view: viewMap },
        "walky-talky": { nav: navWalkyTalky, view: viewWalkyTalky },
        "radio": { nav: navRadio, view: viewRadio },
        "emergency-sos": { nav: navEmergencySos, view: viewEmergencySos },
        "chat-history": { nav: navChatHistory, view: viewChatHistory },
        "settings": { nav: navSettings, view: viewSettings },
    };

    // ─── State ───────────────────────────────────────────────
    let messages = [];
    let isTyping = false;

    // ─── Helpers ─────────────────────────────────────────────
    function scrollToBottom() {
        requestAnimationFrame(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    }

    function autoResize(input) {
        input.style.height = "auto";
        input.style.height = Math.min(input.scrollHeight, 140) + "px";
    }

    function toggleSendBtn() {
        sendBtn.disabled = !messageInput.value.trim();
    }

    function toggleSendBtnChat() {
        sendBtnChat.disabled = !messageInputChat.value.trim();
    }

    function switchToChat() {
        welcomeScreen.classList.add("hidden");
        chatMessages.classList.remove("hidden");
        chatInputArea.classList.remove("hidden");
        // Focus the chat input
        messageInputChat.focus();
    }

    function switchToWelcome() {
        welcomeScreen.classList.remove("hidden");
        chatMessages.classList.add("hidden");
        chatInputArea.classList.add("hidden");
    }

    // ─── View switching ──────────────────────────────────────
    function activateView(viewName) {
        // Toggle nav active state
        document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
        document.querySelectorAll(".view-panel").forEach(v => v.classList.remove("active-view"));

        const entry = navMap_[viewName];
        if (entry) {
            entry.nav.classList.add("active");
            entry.view.classList.add("active-view");
        }

        // Populate chat history when navigating to it
        if (viewName === "chat-history") populateChatHistory();

        // Close sidebar on mobile
        if (window.innerWidth <= 768) sidebar.classList.remove("open");
    }

    // ─── Chat History ────────────────────────────────────────
    function populateChatHistory() {
        const historyList = document.getElementById("history-list");
        const historyEmpty = document.getElementById("history-empty");
        if (!historyList) return;

        // Clear previous items (keep the empty placeholder)
        historyList.querySelectorAll(".history-item").forEach(el => el.remove());

        // Build conversation entries from user messages
        const userMsgs = messages.filter(m => m.role === "user");

        if (userMsgs.length === 0) {
            if (historyEmpty) historyEmpty.classList.remove("hidden");
            return;
        }
        if (historyEmpty) historyEmpty.classList.add("hidden");

        userMsgs.forEach((msg, idx) => {
            const item = document.createElement("div");
            item.className = "history-item";

            const icon = document.createElement("div");
            icon.className = "history-item-icon";
            icon.textContent = "💬";

            const body = document.createElement("div");
            body.className = "history-item-body";

            const title = document.createElement("div");
            title.className = "history-item-title";
            title.textContent = msg.text.length > 80 ? msg.text.slice(0, 80) + "…" : msg.text;

            const time = document.createElement("div");
            time.className = "history-item-time";
            time.textContent = msg.timestamp || "This session";

            body.appendChild(title);
            body.appendChild(time);
            item.appendChild(icon);
            item.appendChild(body);

            // Click to jump to chat and scroll to that message
            item.addEventListener("click", () => {
                activateView("chat");
                if (chatMessages.children[idx * 2]) {
                    chatMessages.children[idx * 2].scrollIntoView({ behavior: "smooth" });
                }
            });

            historyList.appendChild(item);
        });
    }

    // Attach click handlers to all nav items
    Object.keys(navMap_).forEach(viewName => {
        const entry = navMap_[viewName];
        if (entry && entry.nav) {
            entry.nav.addEventListener("click", () => activateView(viewName));
        }
    });

    // ─── Render a message ────────────────────────────────────
    function renderMessage(role, text) {
        const row = document.createElement("div");
        row.className = `message-row ${role}`;

        if (role === "ai") {
            const avatar = document.createElement("div");
            avatar.className = "avatar ai-avatar";
            avatar.textContent = "AI";
            row.appendChild(avatar);
        }

        const bubbleWrap = document.createElement("div");

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.innerHTML = formatText(text);
        bubbleWrap.appendChild(bubble);

        // Action buttons
        const actions = document.createElement("div");
        actions.className = "message-actions";
        if (role === "ai") {
            actions.innerHTML = `
        <button class="action-btn copy-btn" title="Copy">COPY</button>
        <button class="action-btn" title="Regenerate">RETRY</button>
      `;
        } else {
            actions.innerHTML = `
        <button class="action-btn copy-btn" title="Copy">COPY</button>
        <button class="action-btn" title="Edit">EDIT</button>
      `;
        }
        bubbleWrap.appendChild(actions);
        row.appendChild(bubbleWrap);

        if (role === "user") {
            const avatar = document.createElement("div");
            avatar.className = "avatar user-avatar";
            avatar.textContent = "USR";
            row.appendChild(avatar);
        }

        chatMessages.appendChild(row);
        scrollToBottom();

        // Copy handler
        const copyBtn = actions.querySelector(".copy-btn");
        copyBtn.addEventListener("click", () => {
            navigator.clipboard.writeText(text).then(() => {
                copyBtn.textContent = "COPIED";
                setTimeout(() => (copyBtn.textContent = "COPY"), 1500);
            });
        });
    }

    // ─── Simple markdown-like formatting ─────────────────────
    function formatText(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
            .replace(/`(.+?)`/g, '<code style="background:rgba(0,229,160,.1);padding:2px 6px;border-radius:3px;font-size:12px;color:#00e5a0">$1</code>')
            .replace(/^&gt; (.+)$/gm, '<blockquote style="border-left:2px solid #00e5a0;padding-left:10px;color:#7faa9a;margin:6px 0">$1</blockquote>')
            .replace(/^(\d+)\. (.+)$/gm, '<div style="margin:3px 0;padding-left:6px">$1. $2</div>')
            .replace(/^[•\-] (.+)$/gm, '<div style="margin:3px 0;padding-left:6px">• $1</div>')
            .replace(/\n/g, "<br>");
    }

    // ─── Typing indicator ───────────────────────────────────
    function showTypingIndicator() {
        const row = document.createElement("div");
        row.className = "message-row ai";
        row.id = "typing-row";

        const avatar = document.createElement("div");
        avatar.className = "avatar ai-avatar";
        avatar.textContent = "AI";
        row.appendChild(avatar);

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
        row.appendChild(bubble);

        chatMessages.appendChild(row);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const el = document.getElementById("typing-row");
        if (el) el.remove();
    }

    // ─── Send message ───────────────────────────────────────
    function sendMessage(text) {
        if (!text.trim() || isTyping) return;

        switchToChat();
        messages.push({ role: "user", text });
        renderMessage("user", text);

        // Clear both inputs
        messageInput.value = "";
        messageInputChat.value = "";
        autoResize(messageInput);
        autoResize(messageInputChat);
        toggleSendBtn();
        toggleSendBtnChat();

        // Simulate AI response
        isTyping = true;
        showTypingIndicator();

        const delay = 1000 + Math.random() * 1500;
        setTimeout(() => {
            removeTypingIndicator();
            const response = aiResponses[Math.floor(Math.random() * aiResponses.length)];
            messages.push({ role: "ai", text: response });
            renderMessage("ai", response);
            isTyping = false;
        }, delay);
    }

    // ─── Event listeners ────────────────────────────────────

    // Welcome screen send
    sendBtn.addEventListener("click", () => sendMessage(messageInput.value));
    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage(messageInput.value);
        }
    });
    messageInput.addEventListener("input", () => {
        autoResize(messageInput);
        toggleSendBtn();
    });

    // Chat mode send
    sendBtnChat.addEventListener("click", () => sendMessage(messageInputChat.value));
    messageInputChat.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage(messageInputChat.value);
        }
    });
    messageInputChat.addEventListener("input", () => {
        autoResize(messageInputChat);
        toggleSendBtnChat();
    });

    // Suggestion cards
    document.querySelectorAll(".suggestion-card").forEach((card) => {
        card.addEventListener("click", () => {
            const prompt = card.getAttribute("data-prompt");
            messageInput.value = prompt;
            toggleSendBtn();
            sendMessage(prompt);
        });
    });

    // Sidebar toggle (mobile)
    sidebarToggle.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });

    // Settings modal (legacy — still works from sidebar footer gear icon)
    settingsBtn.addEventListener("click", () => settingsModal.classList.remove("hidden"));
    closeSettings.addEventListener("click", () => settingsModal.classList.add("hidden"));
    settingsModal.addEventListener("click", (e) => {
        if (e.target === settingsModal) settingsModal.classList.add("hidden");
    });

    // Temperature slider — modal
    tempSlider.addEventListener("input", () => {
        tempValue.textContent = (tempSlider.value / 100).toFixed(1);
    });

    // Temperature slider — inline settings view
    if (tempSliderInline) {
        tempSliderInline.addEventListener("input", () => {
            tempValueInline.textContent = (tempSliderInline.value / 100).toFixed(1);
        });
    }

    // Clear data — modal
    clearDataBtn.addEventListener("click", () => {
        if (confirm("Are you sure you want to delete all conversations?")) {
            messages = [];
            chatMessages.innerHTML = "";
            switchToWelcome();
            settingsModal.classList.add("hidden");
        }
    });

    // Clear data — inline settings view
    if (clearDataBtnInline) {
        clearDataBtnInline.addEventListener("click", () => {
            if (confirm("Are you sure you want to delete all conversations?")) {
                messages = [];
                chatMessages.innerHTML = "";
                switchToWelcome();
                activateView("chat");
            }
        });
    }

    // ─── Voice input (Web Speech API) ─────────────────────
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    function setupMic(btn, inputEl, toggleFn) {
        if (!SpeechRecognition || !btn) return;

        let recognition = null;
        let isRecording = false;

        btn.addEventListener("click", () => {
            if (isRecording && recognition) {
                recognition.stop();
                return;
            }

            recognition = new SpeechRecognition();
            recognition.lang = "en-US";
            recognition.interimResults = true;
            recognition.continuous = false;

            recognition.onstart = () => {
                isRecording = true;
                btn.classList.add("recording");
                btn.title = "Stop recording";
            };

            recognition.onresult = (event) => {
                let transcript = "";
                for (let i = 0; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                inputEl.value = transcript;
                autoResize(inputEl);
                if (toggleFn) toggleFn();
            };

            recognition.onend = () => {
                isRecording = false;
                btn.classList.remove("recording");
                btn.title = "Voice input";
            };

            recognition.onerror = (event) => {
                console.warn("Speech recognition error:", event.error);
                isRecording = false;
                btn.classList.remove("recording");
                btn.title = "Voice input";
            };

            recognition.start();
        });
    }

    setupMic(micBtn, messageInput, toggleSendBtn);
    setupMic(micBtnChat, messageInputChat, toggleSendBtnChat);

    // Focus input on load
    messageInput.focus();
})();
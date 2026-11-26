// =========================================
// ASK BUDDY - FRONTEND APPLICATION
// =========================================

const API_URL = "";

// DOM ELEMENTS
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const messagesContainer = document.getElementById("messagesContainer");
const conversationList = document.getElementById("conversationList");
const welcomeScreen = document.getElementById("welcomeScreen");

const newChatBtn = document.getElementById("newChatBtn");
const menuButton = document.getElementById("menuButton");
const closeSidebar = document.getElementById("closeSidebar");
const sidebar = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");


// APPLICATION STATE
let conversationId = null;
let messages = [];
let isGenerating = false;


// =========================================
// SAFE MARKDOWN RENDERING
// =========================================

function escapeHTML(text) {
    return text.replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function renderMarkdown(text) {

    let safe = escapeHTML(text);

    // Code blocks
    const codeBlocks = [];

    safe = safe.replace(/```([\w-]*)\n?([\s\S]*?)```/g, (_, lang, code) => {
        const index = codeBlocks.length;

        codeBlocks.push(
            `<pre><code>${code.trim()}</code></pre>`
        );

        return `%%CODEBLOCK${index}%%`;
    });

    // Inline code
    safe = safe.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Links
    safe = safe.replace(
        /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
        (_, label, url) => {
            return `<a href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`;
        }
    );

    // Bold
    safe = safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Italics
    safe = safe.replace(/\*(.*?)\*/g, "<em>$1</em>");

    // Headings
    safe = safe.replace(/^### (.+)$/gm, "<strong>$1</strong>");
    safe = safe.replace(/^## (.+)$/gm, "<strong>$1</strong>");
    safe = safe.replace(/^# (.+)$/gm, "<strong>$1</strong>");

    // Lists
    safe = safe.replace(/^\s*[-*] (.+)$/gm, "• $1");

    // Plain URLs
    safe = safe.replace(
        /(^|[\s(])(https?:\/\/[^\s<]+)/g,
        (match, prefix, url) => {
            return `${prefix}<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
        }
    );

    // Line breaks
    safe = safe.replace(/\n/g, "<br>");

    // Restore code blocks
    safe = safe.replace(
        /%%CODEBLOCK(\d+)%%/g,
        (_, index) => codeBlocks[Number(index)]
    );

    return safe;
}


// =========================================
// SCROLL TO BOTTOM
// =========================================

function scrollToBottom() {
    const chatArea = document.getElementById("chatArea");

    chatArea.scrollTo({
        top: chatArea.scrollHeight,
        behavior: "smooth"
    });
}


// =========================================
// UPDATE WELCOME SCREEN
// =========================================

function updateWelcomeScreen() {

    welcomeScreen.style.display =
        messages.length === 0 ? "block" : "none";
}


// =========================================
// DISPLAY MESSAGE
// =========================================

function addMessage(role, content, streaming = false) {

    const row = document.createElement("div");

    row.className = `message-row ${role}`;

    const avatar = document.createElement("div");

    avatar.className = "message-avatar";

    avatar.textContent = role === "user" ? "Y" : "✦";

    const contentBox = document.createElement("div");

    contentBox.className = "message-content";

    contentBox.innerHTML = renderMarkdown(content);

    row.appendChild(avatar);
    row.appendChild(contentBox);

    messagesContainer.appendChild(row);

    if (role === "assistant" && !streaming) {

        const actions = document.createElement("div");

        actions.className = "message-actions";

        const copyButton = document.createElement("button");

        copyButton.className = "copy-button";
        copyButton.textContent = "Copy";

        copyButton.addEventListener("click", async () => {

            try {
                await navigator.clipboard.writeText(content);
                copyButton.textContent = "Copied!";
                setTimeout(() => {
                    copyButton.textContent = "Copy";
                }, 1500);
            } catch {
                copyButton.textContent = "Copy unavailable";
            }

        });

        actions.appendChild(copyButton);
        contentBox.appendChild(actions);
    }

    updateWelcomeScreen();
    scrollToBottom();

    return {
        row,
        contentBox
    };
}


// =========================================
// RENDER CONVERSATION
// =========================================

function renderConversation() {

    messagesContainer.innerHTML = "";

    messages.forEach(message => {

        addMessage(
            message.role,
            message.content
        );

    });

    updateWelcomeScreen();
}


// =========================================
// LOAD CONVERSATION HISTORY
// =========================================

async function loadConversations() {

    try {

        const response = await fetch(
            `${API_URL}/conversations/`
        );

        if (!response.ok) {
            throw new Error("Could not fetch conversations.");
        }

        const conversations = await response.json();

        conversationList.innerHTML = "";

        if (conversations.length === 0) {

            conversationList.innerHTML =
                '<div class="history-empty">No conversations yet.</div>';

            return;
        }

        conversations.forEach(conversation => {

            const item = document.createElement("div");

            item.className = "conversation-item";

            const selectButton = document.createElement("button");

            selectButton.className = "conversation-select";

            if (conversation.id === conversationId) {
                selectButton.classList.add("active");
            }

            selectButton.textContent =
                conversation.title || "New Conversation";

            selectButton.title =
                conversation.title || "New Conversation";

            selectButton.addEventListener("click", () => {
                openConversation(conversation.id);
            });

            const deleteButton = document.createElement("button");

            deleteButton.className = "delete-button";
            deleteButton.textContent = "×";
            deleteButton.title = "Delete conversation";
            deleteButton.setAttribute("aria-label", "Delete conversation");

            deleteButton.addEventListener("click", () => {
                deleteConversation(conversation.id);
            });

            item.appendChild(selectButton);
            item.appendChild(deleteButton);

            conversationList.appendChild(item);

        });

    } catch (error) {

        conversationList.innerHTML =
            '<div class="history-empty">Unable to load conversations.</div>';

        console.error(error);
    }
}


// =========================================
// CREATE NEW CONVERSATION
// =========================================

async function createConversation() {

    if (isGenerating) return;

    try {

        const response = await fetch(
            `${API_URL}/conversations/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    title: "Ask Buddy Chat"
                })
            }
        );

        if (!response.ok) {
            throw new Error("Could not create conversation.");
        }

        const data = await response.json();

        conversationId = data.id;
        messages = [];

        messagesContainer.innerHTML = "";

        updateWelcomeScreen();

        history.replaceState(
            {},
            "",
            `/?cid=${conversationId}`
        );

        await loadConversations();

        closeMobileSidebar();

        messageInput.focus();

    } catch (error) {

        alert(error.message);
    }
}


// =========================================
// OPEN EXISTING CONVERSATION
// =========================================

async function openConversation(id) {

    if (isGenerating) return;

    try {

        const response = await fetch(
            `${API_URL}/conversations/${id}`
        );

        if (!response.ok) {
            throw new Error("Could not load conversation.");
        }

        const data = await response.json();

        conversationId = data.id;

        messages = data.messages.map(message => ({
            role: message.role,
            content: message.content
        }));

        history.replaceState(
            {},
            "",
            `/?cid=${conversationId}`
        );

        renderConversation();

        await loadConversations();

        closeMobileSidebar();

    } catch (error) {

        alert(error.message);
    }
}


// =========================================
// DELETE CONVERSATION
// =========================================

async function deleteConversation(id) {

    if (isGenerating) return;

    if (!confirm("Delete this conversation permanently?")) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/conversations/${id}`,
            {
                method: "DELETE"
            }
        );

        if (!response.ok) {
            throw new Error("Could not delete conversation.");
        }

        if (conversationId === id) {

            conversationId = null;
            messages = [];

            messagesContainer.innerHTML = "";

            history.replaceState({}, "", "/");

            updateWelcomeScreen();
        }

        await loadConversations();

    } catch (error) {

        alert(error.message);
    }
}


// =========================================
// STREAM AI RESPONSE
// =========================================

async function sendMessage() {

    const query = messageInput.value.trim();

    if (!query || isGenerating) return;

    // Create a conversation automatically
    if (conversationId === null) {

        await createConversation();

        if (conversationId === null) return;
    }

    isGenerating = true;

    sendButton.disabled = true;
    messageInput.disabled = true;

    // Hide welcome screen
    welcomeScreen.style.display = "none";

    // Display user message
    addMessage("user", query);

    messages.push({
        role: "user",
        content: query
    });

    messageInput.value = "";
    messageInput.style.height = "auto";

    // Display assistant placeholder
    const assistant = addMessage(
        "assistant",
        "Thinking...",
        true
    );

    assistant.contentBox.innerHTML =
        '<span class="typing-indicator">● ● ●</span>';

    let aiResponse = "";

    try {

        const response = await fetch(
            `${API_URL}/chat/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    conversation_id: conversationId,
                    message: query
                })
            }
        );

        if (!response.ok) {

            const errorText = await response.text();

            throw new Error(errorText || "AI request failed.");
        }

        if (!response.body) {
            throw new Error("Streaming is not supported by this response.");
        }

        const reader = response.body.getReader();

        const decoder = new TextDecoder();

        while (true) {

            const { value, done } = await reader.read();

            if (done) break;

            aiResponse += decoder.decode(
                value,
                { stream: true }
            );

            assistant.contentBox.innerHTML =
                renderMarkdown(aiResponse);

            scrollToBottom();
        }

        aiResponse += decoder.decode();

        assistant.contentBox.innerHTML =
            renderMarkdown(aiResponse);

        // Add copy button
        const actions = document.createElement("div");

        actions.className = "message-actions";

        const copyButton = document.createElement("button");

        copyButton.className = "copy-button";
        copyButton.textContent = "Copy";

        copyButton.addEventListener("click", async () => {

            try {
                await navigator.clipboard.writeText(aiResponse);
                copyButton.textContent = "Copied!";

                setTimeout(() => {
                    copyButton.textContent = "Copy";
                }, 1500);

            } catch {
                copyButton.textContent = "Copy unavailable";
            }

        });

        actions.appendChild(copyButton);
        assistant.contentBox.appendChild(actions);

        messages.push({
            role: "assistant",
            content: aiResponse
        });

        await loadConversations();

    } catch (error) {

        assistant.contentBox.textContent =
            `Something went wrong: ${error.message}`;

        console.error(error);

    } finally {

        isGenerating = false;

        sendButton.disabled = false;
        messageInput.disabled = false;

        messageInput.focus();
        scrollToBottom();
    }
}


// =========================================
// MOBILE SIDEBAR
// =========================================

function openMobileSidebar() {

    sidebar.classList.add("open");
    sidebarOverlay.classList.add("active");
}

function closeMobileSidebar() {

    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("active");
}

// Desktop: collapse / expand sidebar
// Mobile: open / close sidebar


menuButton.addEventListener("click", () => {

    if (window.innerWidth <= 850) {

        openMobileSidebar();

    } else {

        document.body.classList.toggle("sidebar-collapsed");

        const collapsed =
            document.body.classList.contains("sidebar-collapsed");

        menuButton.title = collapsed
            ? "Expand sidebar"
            : "Collapse sidebar";

    }

});


if (closeSidebar) {
    closeSidebar.addEventListener("click", closeMobileSidebar);
}


sidebarOverlay.addEventListener(
    "click",
    closeMobileSidebar
);


// =========================================
// EVENT LISTENERS
// =========================================

newChatBtn.addEventListener(
    "click",
    createConversation
);

sendButton.addEventListener(
    "click",
    sendMessage
);

messageInput.addEventListener("keydown", event => {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        sendMessage();
    }

});

messageInput.addEventListener("input", () => {

    messageInput.style.height = "auto";

    messageInput.style.height =
        `${Math.min(messageInput.scrollHeight, 150)}px`;

});


// Suggestion cards
document.querySelectorAll(".suggestion-card").forEach(card => {

    card.addEventListener("click", () => {

        messageInput.value = card.dataset.prompt;

        messageInput.focus();

        sendMessage();
    });

});


// =========================================
// RESTORE CONVERSATION FROM URL
// =========================================

async function initializeApp() {

    await loadConversations();

    const params = new URLSearchParams(
        window.location.search
    );

    const savedId = params.get("cid");

    if (savedId && /^\d+$/.test(savedId)) {

        await openConversation(Number(savedId));

    } else {

        updateWelcomeScreen();
    }
}


// START APPLICATION
initializeApp();

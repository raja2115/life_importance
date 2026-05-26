/* ═══════════════════════════════════════════════════════════════
   ExamTrack AI — Chatbot Module
   ═══════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function() {
    const fab = document.getElementById('chatbotFab');
    const window_ = document.getElementById('chatbotWindow');
    const closeBtn = document.getElementById('chatbotClose');
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSend');
    const messages = document.getElementById('chatMessages');

    // Toggle chatbot window
    if (fab) {
        fab.addEventListener('click', () => {
            window_.classList.toggle('active');
            if (window_.classList.contains('active')) {
                // Show welcome message if first time
                if (messages.children.length === 0) {
                    addBotMessage("👋 Hi! I'm your **ExamTrack AI Assistant**.\n\nI can help you:\n📝 Add exams\n🔍 Search exams\n📅 Show upcoming\n📊 View stats\n\nType **help** for all commands!");
                }
                input.focus();
            }
        });
    }

    // Close chatbot
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            window_.classList.remove('active');
        });
    }

    // Send message on Enter
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                sendMessage(input.value.trim());
            }
        });
    }

    // Send button click
    if (sendBtn) {
        sendBtn.addEventListener('click', () => {
            if (input && input.value.trim()) {
                sendMessage(input.value.trim());
            }
        });
    }

    // Quick reply buttons
    document.querySelectorAll('.quick-reply-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            sendMessage(btn.dataset.msg);
        });
    });
});


/**
 * Send a message to the chatbot API.
 */
async function sendMessage(text) {
    const input = document.getElementById('chatInput');
    const messages = document.getElementById('chatMessages');

    // Add user message
    addUserMessage(text);
    input.value = '';

    // Show typing indicator
    const typing = showTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator(typing);

        // Add bot response
        addBotMessage(data.response, data.type);

        // If exam was added, refresh page data
        if (data.type === 'success' && data.data) {
            showToast('Exam updated via chat!', 'success');
        }

    } catch(e) {
        removeTypingIndicator(typing);
        addBotMessage('❌ Sorry, something went wrong. Please try again.', 'error');
    }
}


/**
 * Add a user message bubble.
 */
function addUserMessage(text) {
    const messages = document.getElementById('chatMessages');
    const bubble = document.createElement('div');
    bubble.className = 'chat-message user';
    bubble.textContent = text;
    messages.appendChild(bubble);
    scrollToBottom();
}


/**
 * Add a bot message bubble with markdown-like formatting.
 */
function addBotMessage(text, type = 'info') {
    const messages = document.getElementById('chatMessages');
    const bubble = document.createElement('div');
    bubble.className = 'chat-message bot';

    // Simple markdown-like formatting
    let html = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/• /g, '&nbsp;&nbsp;• ');

    bubble.innerHTML = html;
    messages.appendChild(bubble);
    scrollToBottom();
}


/**
 * Show typing indicator dots.
 */
function showTypingIndicator() {
    const messages = document.getElementById('chatMessages');
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    messages.appendChild(indicator);
    scrollToBottom();
    return indicator;
}


/**
 * Remove typing indicator.
 */
function removeTypingIndicator(indicator) {
    if (indicator && indicator.parentNode) {
        indicator.parentNode.removeChild(indicator);
    }
}


/**
 * Scroll chat to bottom.
 */
function scrollToBottom() {
    const messages = document.getElementById('chatMessages');
    if (messages) {
        messages.scrollTop = messages.scrollHeight;
    }
}

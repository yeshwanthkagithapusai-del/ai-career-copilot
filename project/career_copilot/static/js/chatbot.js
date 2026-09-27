/* ===== AI Career Assistant Chatbot ===== */

function getCSRFToken() {
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    if (match) {
        return decodeURIComponent(match[1]);
    }

    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) {
        return meta.getAttribute('content');
    }

    const hidden = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return hidden ? hidden.value : '';
}

document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('chatbot-toggle');
    const panel = document.getElementById('chatbot-panel');
    const close = document.getElementById('chatbot-close');
    const send = document.getElementById('chatbot-send');
    const input = document.getElementById('chatbot-input');
    const messages = document.getElementById('chatbot-messages');
    
    if (toggle && panel) {
        toggle.addEventListener('click', function() {
            panel.classList.toggle('open');
            if (panel.classList.contains('open') && input) input.focus();
        });
    }
    
    if (close) {
        close.addEventListener('click', function() {
            panel.classList.remove('open');
        });
    }
    
    if (send && input) {
        send.addEventListener('click', sendMessage);
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    }
    
    function sendMessage() {
        const message = input.value.trim();
        if (!message) return;
        
        // Add user message
        const userMsg = document.createElement('div');
        userMsg.className = 'chat-message user';
        userMsg.textContent = message;
        messages.appendChild(userMsg);
        
        input.value = '';
        input.disabled = true;
        send.disabled = true;
        
        // Add typing indicator
        const typingMsg = document.createElement('div');
        typingMsg.className = 'chat-message bot';
        typingMsg.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Thinking...';
        typingMsg.id = 'typing-indicator';
        messages.appendChild(typingMsg);
        
        messages.scrollTop = messages.scrollHeight;
        
        // Send to backend
        fetch('/api/ai/chat/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ message: message }),
        })
        .then(async response => {
            const text = await response.text();
            let data = {};

            if (text) {
                try {
                    data = JSON.parse(text);
                } catch (e) {
                    data = { error: text };
                }
            }

            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }

            return data;
        })
        .then(data => {
            const indicator = document.getElementById('typing-indicator');
            if (indicator) indicator.remove();
            
            const botMsg = document.createElement('div');
            botMsg.className = 'chat-message bot';
            if (data.error) {
                botMsg.textContent = 'Sorry, I could not process your request. Please try again.';
            } else {
                botMsg.textContent = data.response || 'I did not understand that. Could you rephrase?';
            }
            messages.appendChild(botMsg);
            messages.scrollTop = messages.scrollHeight;
        })
        .catch(function(err) {
            const indicator = document.getElementById('typing-indicator');
            if (indicator) indicator.remove();
            
            const botMsg = document.createElement('div');
            botMsg.className = 'chat-message bot';
            botMsg.textContent = err.message || 'Network error. Please try again.';
            messages.appendChild(botMsg);
            messages.scrollTop = messages.scrollHeight;
        })
        .finally(function() {
            input.disabled = false;
            send.disabled = false;
            input.focus();
        });
    }
});

/**
 * AI Chatbot Widget
 * 
 * Floating chatbot widget for the Student Welfare Management System.
 * Provides AI-powered assistance for students and administrators.
 */

class WelfareChatbot {
    constructor() {
        this.isOpen = false;
        this.conversationHistory = [];
        this.apiEndpoint = '/api/chatbot/';
        this.csrfToken = this.getCSRFToken();

        // Load conversation history from localStorage
        this.loadHistory();

        // Initialize UI
        this.render();
        this.attachEventListeners();
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    render() {
        const chatbotHTML = `
            <!-- Chatbot Container -->
            <div id="welfare-chatbot" class="fixed bottom-6 left-6 z-50">
                <!-- Floating Button (Minimized State) -->
                <button id="chatbot-toggle" 
                        class="group relative w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-full shadow-2xl hover:shadow-indigo-500/50 transition-all duration-300 hover:scale-110 flex items-center justify-center"
                        aria-label="Open AI Assistant">
                    <svg class="w-8 h-8 text-white animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
                    </svg>
                    <!-- Notification Badge -->
                    <span id="chatbot-badge" 
                          class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center hidden">
                        1
                    </span>
                </button>
                
                <!-- Chat Window (Expanded State) -->
                <div id="chatbot-window" 
                     class="hidden absolute bottom-20 left-0 w-96 h-[600px] bg-white dark:bg-slate-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-slate-200 dark:border-slate-700 transition-all duration-300">
                    
                    <!-- Header -->
                    <div class="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
                                </svg>
                            </div>
                            <div>
                                <h3 class="text-white font-bold text-lg">AI Campus Assistant</h3>
                                <div class="flex items-center gap-1.5">
                                    <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                                    <p class="text-white/80 text-xs">Online • 24/7 Support</p>
                                </div>
                            </div>
                        </div>
                        <button id="chatbot-close" 
                                class="text-white/80 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-lg"
                                aria-label="Close chat">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Messages Container -->
                    <div id="chatbot-messages" 
                         class="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50 dark:bg-slate-900/50">
                        <!-- Welcome Message -->
                        <div class="flex gap-3">
                            <div class="w-8 h-8 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-full flex-shrink-0 flex items-center justify-center">
                                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
                                </svg>
                            </div>
                            <div class="bg-white dark:bg-slate-800 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm max-w-[85%]">
                                <p class="text-slate-700 dark:text-slate-200 text-sm">
                                    <strong>Hi! I'm your AI Campus Assistant.</strong><br>
                                    I can help you with anything about Campus Care!<br><br>
                                    💡 Try asking:<br>
                                    • "How to apply for deferment?"<br>
                                    • "Check my fee balance"<br>
                                    • "Who is the owner?"<br>
                                    • "Book health appointment"<br>
                                    • "Report maintenance issue"<br>
                                    • "Borrow library book"<br>
                                    • "Reset my password"
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Quick Replies -->
                    <div id="chatbot-quick-replies" class="px-4 py-2">
                        <div class="flex flex-wrap gap-2">
                            <button onclick="document.getElementById('chatbot-input').value='How to apply for deferment?'; document.getElementById('chatbot-send').click();" class="text-xs bg-indigo-50 hover:bg-indigo-100 text-indigo-700 px-3 py-1.5 rounded-full border border-indigo-200 transition-colors">📝 Apply for Deferment</button>
                            <button onclick="document.getElementById('chatbot-input').value='Check my fee balance'; document.getElementById('chatbot-send').click();" class="text-xs bg-indigo-50 hover:bg-indigo-100 text-indigo-700 px-3 py-1.5 rounded-full border border-indigo-200 transition-colors">💰 Fee Balance</button>
                            <button onclick="document.getElementById('chatbot-input').value='Who is the owner?'; document.getElementById('chatbot-send').click();" class="text-xs bg-indigo-50 hover:bg-indigo-100 text-indigo-700 px-3 py-1.5 rounded-full border border-indigo-200 transition-colors">👨‍💻 Owner Info</button>
                        </div>
                    </div>
                    
                    <!-- Input Area -->
                    <div class="bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 p-4">
                        <div class="flex gap-2">
                            <input type="text" 
                                   id="chatbot-input" 
                                   placeholder="Type your message..."
                                   class="flex-1 px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-700 dark:text-white text-sm"
                                   autocomplete="off">
                            <button id="chatbot-send" 
                                    class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-5 py-3 rounded-xl hover:shadow-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                          d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                                </svg>
                            </button>
                        </div>
                        <!-- Typing Indicator -->
                        <div id="chatbot-typing" class="hidden mt-2 text-xs text-slate-500 flex items-center gap-2">
                            <div class="flex gap-1">
                                <span class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                                <span class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                                <span class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
                            </div>
                            <span>Assistant is typing...</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Mobile Styles -->
            <style>
                @media (max-width: 640px) {
                    #chatbot-window {
                        position: fixed !important;
                        bottom: 0 !important;
                        right: 0 !important;
                        left: 0 !important;
                        width: 100% !important;
                        height: 100% !important;
                        border-radius: 0 !important;
                    }
                }
            </style>
        `;

        // Inject into page
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    }

    attachEventListeners() {
        const toggleBtn = document.getElementById('chatbot-toggle');
        const closeBtn = document.getElementById('chatbot-close');
        const sendBtn = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');

        toggleBtn.addEventListener('click', () => this.toggleChat());
        closeBtn.addEventListener('click', () => this.toggleChat());
        sendBtn.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');

        if (this.isOpen) {
            window.classList.remove('hidden');
            toggle.classList.add('hidden');
            document.getElementById('chatbot-input').focus();
        } else {
            window.classList.add('hidden');
            toggle.classList.remove('hidden');
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();

        if (!message) return;

        // Clear input
        input.value = '';

        // Add user message to UI
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTyping(true);

        // Disable send button
        document.getElementById('chatbot-send').disabled = true;

        try {
            // Send to API
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    message: message,
                    history: this.conversationHistory
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data = await response.json();

            // Add assistant response to UI
            this.addMessage(data.response, 'assistant');

            // Update conversation history
            this.conversationHistory.push({ role: 'user', content: message });
            this.conversationHistory.push({ role: 'assistant', content: data.response });

            // Save to localStorage
            this.saveHistory();

        } catch (error) {
            console.error('Chatbot error:', error);
            this.addMessage(
                "I'm having trouble connecting right now. Please try again in a moment.",
                'assistant',
                true
            );
        } finally {
            // Hide typing indicator
            this.showTyping(false);

            // Re-enable send button
            document.getElementById('chatbot-send').disabled = false;

            // Focus input
            input.focus();
        }
    }

    addMessage(content, role, isError = false) {
        const messagesContainer = document.getElementById('chatbot-messages');

        const messageHTML = role === 'user' ? `
            <div class="flex gap-3 justify-end">
                <div class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-2xl rounded-tr-none px-4 py-3 shadow-sm max-w-[80%]">
                    <p class="text-sm">${this.escapeHTML(content)}</p>
                </div>
            </div>
        ` : `
            <div class="flex gap-3">
                <div class="w-8 h-8 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-full flex-shrink-0 flex items-center justify-center">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
                    </svg>
                </div>
                <div class="bg-white dark:bg-slate-800 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm max-w-[80%] ${isError ? 'border-2 border-red-300' : ''}">
                    <p class="text-slate-700 dark:text-slate-200 text-sm">${this.escapeHTML(content)}</p>
                </div>
            </div>
        `;

        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTyping(show) {
        const typingIndicator = document.getElementById('chatbot-typing');
        if (show) {
            typingIndicator.classList.remove('hidden');
        } else {
            typingIndicator.classList.add('hidden');
        }
    }

    escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    saveHistory() {
        localStorage.setItem('welfare_chatbot_history', JSON.stringify(this.conversationHistory));
    }

    loadHistory() {
        const saved = localStorage.getItem('welfare_chatbot_history');
        if (saved) {
            try {
                this.conversationHistory = JSON.parse(saved);
            } catch (e) {
                this.conversationHistory = [];
            }
        }
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new WelfareChatbot();
});

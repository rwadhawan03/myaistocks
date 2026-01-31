class Chat {
    static conversationHistory = [];
    static currentSymbol = null;
    
    static init() {
        this.render();
        this.setupEventListeners();
    }
    
    static render() {
        const container = document.getElementById('chat-page');
        container.innerHTML = `
            <div class="row">
                <div class="col-12">
                    <h2 class="mb-3"><i class="bi bi-chat-dots me-2"></i>AI Stock Analyst</h2>
                    <p class="text-muted">Ask questions about stocks, ETFs, market trends, and get AI-powered recommendations</p>
                </div>
            </div>
            
            <div class="row">
                <div class="col-lg-9">
                    <div class="card chat-container">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span>
                                <i class="bi bi-robot me-2"></i>Chat with AI Analyst
                                <span id="currentSymbolBadge" class="symbol-badge d-none ms-2"></span>
                            </span>
                            <button class="btn btn-sm btn-light" id="clearChatBtn">
                                <i class="bi bi-trash me-1"></i>Clear
                            </button>
                        </div>
                        <div class="chat-messages" id="chatMessages">
                            <div class="message assistant">
                                <p>Hello! I'm your AI Stock Analyst. I can help you with:</p>
                                <ul>
                                    <li>Stock analysis and recommendations (e.g., "Analyze AAPL")</li>
                                    <li>Market trends and insights</li>
                                    <li>Technical and fundamental analysis</li>
                                    <li>Comparing stocks and ETFs</li>
                                    <li>Understanding financial metrics</li>
                                </ul>
                                <p>What would you like to know?</p>
                            </div>
                        </div>
                        <div class="chat-input-container">
                            <div class="input-group mb-2">
                                <span class="input-group-text">
                                    <i class="bi bi-tag"></i>
                                </span>
                                <input type="text" class="form-control" id="symbolInput" 
                                    placeholder="Symbol (optional, e.g., AAPL)" maxlength="10">
                                <button class="btn btn-outline-secondary" type="button" id="clearSymbolBtn">
                                    <i class="bi bi-x"></i>
                                </button>
                            </div>
                            <div class="input-group">
                                <input type="text" class="form-control" id="chatInput" 
                                    placeholder="Ask about stocks, market trends, or request analysis...">
                                <button class="btn btn-primary" type="button" id="sendChatBtn">
                                    <i class="bi bi-send"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3">
                    <div class="card mb-3">
                        <div class="card-header">
                            <i class="bi bi-lightbulb me-2"></i>Quick Prompts
                        </div>
                        <div class="card-body p-0">
                            <div class="list-group list-group-flush" id="quickPrompts">
                                <button class="list-group-item list-group-item-action" data-prompt="What are the top performing stocks today?">
                                    Top performers today
                                </button>
                                <button class="list-group-item list-group-item-action" data-prompt="Give me a market overview and sentiment analysis">
                                    Market overview
                                </button>
                                <button class="list-group-item list-group-item-action" data-prompt="What are the best ETFs to invest in right now?">
                                    Best ETFs to invest
                                </button>
                                <button class="list-group-item list-group-item-action" data-prompt="Analyze the tech sector outlook">
                                    Tech sector outlook
                                </button>
                                <button class="list-group-item list-group-item-action" data-prompt="What stocks should I buy for long-term growth?">
                                    Long-term growth picks
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <i class="bi bi-clock-history me-2"></i>Popular Symbols
                        </div>
                        <div class="card-body">
                            <div class="d-flex flex-wrap gap-2" id="popularSymbols">
                                <button class="btn btn-outline-primary btn-sm" data-symbol="AAPL">AAPL</button>
                                <button class="btn btn-outline-primary btn-sm" data-symbol="MSFT">MSFT</button>
                                <button class="btn btn-outline-primary btn-sm" data-symbol="GOOGL">GOOGL</button>
                                <button class="btn btn-outline-primary btn-sm" data-symbol="AMZN">AMZN</button>
                                <button class="btn btn-outline-primary btn-sm" data-symbol="NVDA">NVDA</button>
                                <button class="btn btn-outline-primary btn-sm" data-symbol="TSLA">TSLA</button>
                                <button class="btn btn-outline-primary btn-sm" data-symbol="META">META</button>
                                <button class="btn btn-outline-primary btn-sm" data-symbol="SPY">SPY</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    static setupEventListeners() {
        document.getElementById('sendChatBtn').addEventListener('click', () => this.sendMessage());
        
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        document.getElementById('clearChatBtn').addEventListener('click', () => this.clearChat());
        
        document.getElementById('clearSymbolBtn').addEventListener('click', () => {
            document.getElementById('symbolInput').value = '';
            this.currentSymbol = null;
            document.getElementById('currentSymbolBadge').classList.add('d-none');
        });
        
        document.getElementById('symbolInput').addEventListener('change', (e) => {
            const symbol = e.target.value.toUpperCase().trim();
            this.currentSymbol = symbol || null;
            const badge = document.getElementById('currentSymbolBadge');
            if (symbol) {
                badge.textContent = symbol;
                badge.classList.remove('d-none');
            } else {
                badge.classList.add('d-none');
            }
        });
        
        document.querySelectorAll('#quickPrompts button').forEach(btn => {
            btn.addEventListener('click', () => {
                document.getElementById('chatInput').value = btn.dataset.prompt;
                this.sendMessage();
            });
        });
        
        document.querySelectorAll('#popularSymbols button').forEach(btn => {
            btn.addEventListener('click', () => {
                const symbol = btn.dataset.symbol;
                document.getElementById('symbolInput').value = symbol;
                document.getElementById('symbolInput').dispatchEvent(new Event('change'));
                document.getElementById('chatInput').value = `Give me a comprehensive analysis of ${symbol}`;
                this.sendMessage();
            });
        });
    }
    
    static async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        const symbol = document.getElementById('symbolInput').value.toUpperCase().trim() || null;
        
        this.addMessage('user', message);
        input.value = '';
        
        this.showTypingIndicator();
        
        try {
            const response = await API.chat.send(message, symbol, this.conversationHistory);
            
            this.hideTypingIndicator();
            
            this.conversationHistory.push({ role: 'user', content: message });
            this.conversationHistory.push({ role: 'assistant', content: response.response });
            
            this.addMessage('assistant', response.response);
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('assistant', `Sorry, I encountered an error: ${error.message}. Please make sure the backend is running and the OpenAI API key is configured.`);
        }
    }
    
    static addMessage(role, content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        if (role === 'assistant') {
            messageDiv.innerHTML = `<div class="markdown-content">${this.formatMarkdown(content)}</div>`;
        } else {
            messageDiv.textContent = content;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    static showTypingIndicator() {
        const messagesContainer = document.getElementById('chatMessages');
        const indicator = document.createElement('div');
        indicator.className = 'message assistant';
        indicator.id = 'typingIndicator';
        indicator.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        messagesContainer.appendChild(indicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    static hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) indicator.remove();
    }
    
    static clearChat() {
        this.conversationHistory = [];
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.innerHTML = `
            <div class="message assistant">
                <p>Chat cleared. How can I help you with stock analysis?</p>
            </div>
        `;
    }
    
    static formatMarkdown(text) {
        if (!text) return '';
        
        let formatted = text
            .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^### (.*$)/gm, '<h5 class="mt-3 mb-2">$1</h5>')
            .replace(/^## (.*$)/gm, '<h4 class="mt-3 mb-2">$1</h4>')
            .replace(/^# (.*$)/gm, '<h3 class="mt-3 mb-2">$1</h3>')
            .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
            .replace(/^\- (.*$)/gm, '<li>$1</li>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        
        formatted = formatted.replace(/(<li>.*?<\/li>)+/gs, (match) => {
            return `<ul class="mb-2">${match}</ul>`;
        });
        
        return `<p>${formatted}</p>`;
    }
}

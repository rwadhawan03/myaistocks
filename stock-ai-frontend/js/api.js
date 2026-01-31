class API {
    static async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        
        const defaultHeaders = {
            'Content-Type': 'application/json'
        };
        
        if (CONFIG.API_AUTH) {
            defaultHeaders['Authorization'] = CONFIG.API_AUTH;
        }
        
        const defaultOptions = {
            headers: defaultHeaders
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Request failed' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    static async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    static async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    static async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    static async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
    
    static auth = {
        login: (email, password) => API.post(CONFIG.ENDPOINTS.AUTH.LOGIN, { email, password }),
        register: (name, email, password) => API.post(CONFIG.ENDPOINTS.AUTH.REGISTER, { name, email, password })
    };
    
    static chat = {
        send: (message, symbol = null, conversationHistory = []) => 
            API.post(CONFIG.ENDPOINTS.CHAT, { 
                message, 
                symbol, 
                conversation_history: conversationHistory 
            })
    };
    
    static market = {
        getSummary: () => API.get(CONFIG.ENDPOINTS.MARKET.SUMMARY),
        getAISummary: () => API.get(CONFIG.ENDPOINTS.MARKET.AI_SUMMARY),
        getIndices: () => API.get(CONFIG.ENDPOINTS.MARKET.INDICES),
        getMovers: (marketType = 'stocks', limit = 10) => 
            API.get(`${CONFIG.ENDPOINTS.MARKET.MOVERS}?market_type=${marketType}&limit=${limit}`)
    };
    
    static stocks = {
        getInfo: (symbol) => API.get(CONFIG.ENDPOINTS.STOCKS.INFO(symbol)),
        getHistory: (symbol, period = '1mo', interval = '1d') => 
            API.get(`${CONFIG.ENDPOINTS.STOCKS.HISTORY(symbol)}?period=${period}&interval=${interval}`),
        getNews: (symbol) => API.get(CONFIG.ENDPOINTS.STOCKS.NEWS(symbol)),
        getTechnicals: (symbol) => API.get(CONFIG.ENDPOINTS.STOCKS.TECHNICALS(symbol)),
        getFinancials: (symbol) => API.get(CONFIG.ENDPOINTS.STOCKS.FINANCIALS(symbol)),
        getRecommendations: (symbol) => API.get(CONFIG.ENDPOINTS.STOCKS.RECOMMENDATIONS(symbol)),
        getAIAnalysis: (symbol) => API.get(CONFIG.ENDPOINTS.STOCKS.AI_ANALYSIS(symbol))
    };
    
    static search = {
        stocks: (query, limit = 10) => API.get(`${CONFIG.ENDPOINTS.SEARCH}?query=${encodeURIComponent(query)}&limit=${limit}`)
    };
    
    static scheduler = {
        create: (data) => API.post(CONFIG.ENDPOINTS.SCHEDULER.CREATE, data),
        getUserSchedulers: (userId) => API.get(CONFIG.ENDPOINTS.SCHEDULER.USER(userId)),
        get: (id) => API.get(CONFIG.ENDPOINTS.SCHEDULER.GET(id)),
        update: (id, data) => API.put(CONFIG.ENDPOINTS.SCHEDULER.UPDATE(id), data),
        delete: (id) => API.delete(CONFIG.ENDPOINTS.SCHEDULER.DELETE(id)),
        test: (id) => API.post(CONFIG.ENDPOINTS.SCHEDULER.TEST(id), {}),
        getNextRuns: () => API.get(CONFIG.ENDPOINTS.SCHEDULER.NEXT_RUNS)
    };
}

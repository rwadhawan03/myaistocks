const CONFIG = {
    API_BASE_URL: 'https://stock-ai-backend-irfcgkkf.fly.dev',
    
    ENDPOINTS: {
        AUTH: {
            LOGIN: '/api/auth/login',
            REGISTER: '/api/auth/register'
        },
        CHAT: '/api/chat',
        MARKET: {
            SUMMARY: '/api/market/summary',
            AI_SUMMARY: '/api/market/ai-summary',
            INDICES: '/api/market/indices',
            MOVERS: '/api/market/movers'
        },
        STOCKS: {
            INFO: (symbol) => `/api/stocks/${symbol}`,
            HISTORY: (symbol) => `/api/stocks/${symbol}/history`,
            NEWS: (symbol) => `/api/stocks/${symbol}/news`,
            TECHNICALS: (symbol) => `/api/stocks/${symbol}/technicals`,
            FINANCIALS: (symbol) => `/api/stocks/${symbol}/financials`,
            RECOMMENDATIONS: (symbol) => `/api/stocks/${symbol}/recommendations`,
            AI_ANALYSIS: (symbol) => `/api/stocks/${symbol}/ai-analysis`
        },
        SEARCH: '/api/search',
        SCHEDULER: {
            CREATE: '/api/scheduler',
            USER: (userId) => `/api/scheduler/user/${userId}`,
            GET: (id) => `/api/scheduler/${id}`,
            UPDATE: (id) => `/api/scheduler/${id}`,
            DELETE: (id) => `/api/scheduler/${id}`,
            TEST: (id) => `/api/scheduler/${id}/test`,
            NEXT_RUNS: '/api/scheduler/next-runs'
        }
    },
    
    STORAGE_KEYS: {
        USER: 'stock_ai_user',
        THEME: 'stock_ai_theme'
    },
    
    REFRESH_INTERVALS: {
        MARKET_SUMMARY: 60000,
        STOCK_PRICE: 30000
    }
};

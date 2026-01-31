# Stock AI Analyst

AI-powered stock analysis application using OpenAI GPT-4 and yfinance for real-time financial data.

## Features

- **Dashboard** - Real-time market indices, top gainers/losers, AI-powered market summary
- **AI Analyst** - Chat interface for stock analysis with buy/sell/hold recommendations
- **Market Explorer** - Search and analyze stocks, ETFs, and funds with charts
- **Scheduler** - Configure automated morning and evening alerts

## Tech Stack

### Backend (FastAPI + Python)
- OpenAI GPT-4o integration for AI-powered analysis
- MCP-based tools using yfinance for real-time financial data
- User registration/authentication
- Email service for scheduled alerts
- APScheduler for morning (8:30 AM) and evening (5:00 PM) alerts

### Frontend (HTML/JavaScript)
- Responsive web interface
- Real-time market data display
- Interactive charts and technical indicators

## Setup

### Backend

1. Navigate to the backend directory:
   ```bash
   cd stock-ai-backend
   ```

2. Copy the environment file and add your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   uvicorn app.main:app --port 8000
   ```

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd stock-ai-frontend
   ```

2. Update `js/config.js` with your backend URL

3. Serve the frontend:
   ```bash
   python3 -m http.server 3000
   ```

4. Open http://localhost:3000 in your browser

## API Endpoints

- `GET /api/market/summary` - Market overview with indices and movers
- `GET /api/market/ai-summary` - AI-generated market analysis
- `POST /api/chat` - Chat with AI analyst
- `GET /api/stocks/{symbol}` - Stock information
- `GET /api/stocks/{symbol}/technicals` - Technical indicators
- `GET /api/stocks/{symbol}/ai-analysis` - AI-powered stock analysis
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/scheduler` - Create scheduled alerts

## License

MIT

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime
import os

from .models import (
    UserCreate, UserResponse, UserLogin, ChatRequest, ChatResponse,
    StockQuery, MarketQuery, SchedulerCreate, SchedulerResponse,
    StockRecommendation, MarketSummary, TriggerTime
)
from .database import (
    create_user, authenticate_user, get_user_by_id,
    create_scheduler, get_user_schedulers, get_scheduler_by_id,
    update_scheduler, delete_scheduler
)
from .mcp_tools import mcp_tools
from .ai_service import ai_analyst
from .email_service import email_service
from .scheduler_service import scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler_service.start()
    yield
    scheduler_service.stop()


app = FastAPI(
    title="Stock AI Analyst API",
    description="AI-powered stock analysis with MCP tools, OpenAI, and yfinance",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Stock AI Analyst API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "chat": "/api/chat",
            "market": "/api/market",
            "stocks": "/api/stocks",
            "scheduler": "/api/scheduler"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, background_tasks: BackgroundTasks):
    result = create_user(user.email, user.name, user.password)
    if not result:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    background_tasks.add_task(email_service.send_welcome_email, user.email, user.name)
    
    return UserResponse(
        id=result["id"],
        email=result["email"],
        name=result["name"],
        created_at=datetime.fromisoformat(result["created_at"])
    )


@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    user = authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"]
        },
        "message": "Login successful"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in (request.conversation_history or [])
    ]
    
    result = await ai_analyst.chat(
        message=request.message,
        symbol=request.symbol,
        conversation_history=conversation_history
    )
    
    return ChatResponse(
        response=result["response"],
        symbol=result.get("symbol"),
        data=result.get("data")
    )


@app.get("/api/market/summary")
async def get_market_summary():
    try:
        indices = mcp_tools.get_market_indices()
        movers = mcp_tools.get_top_movers("stocks", 5)
        
        return {
            "market_status": "open" if datetime.now().hour >= 9 and datetime.now().hour < 16 else "closed",
            "major_indices": indices,
            "top_gainers": movers.get("gainers", []),
            "top_losers": movers.get("losers", []),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/ai-summary")
async def get_ai_market_summary():
    try:
        result = await ai_analyst.generate_market_summary()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/indices")
async def get_indices():
    try:
        indices = mcp_tools.get_market_indices()
        return {"indices": indices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/movers")
async def get_movers(market_type: str = "stocks", limit: int = 10):
    try:
        movers = mcp_tools.get_top_movers(market_type, limit)
        return movers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{symbol}")
async def get_stock_info(symbol: str):
    try:
        info = mcp_tools.get_stock_info(symbol)
        if "error" in info:
            raise HTTPException(status_code=404, detail=info["error"])
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{symbol}/history")
async def get_stock_history(symbol: str, period: str = "1mo", interval: str = "1d"):
    try:
        history = mcp_tools.get_historical_data(symbol, period, interval)
        if "error" in history:
            raise HTTPException(status_code=404, detail=history["error"])
        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{symbol}/news")
async def get_stock_news(symbol: str):
    try:
        news = mcp_tools.get_stock_news(symbol)
        return {"symbol": symbol, "news": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{symbol}/technicals")
async def get_stock_technicals(symbol: str):
    try:
        technicals = mcp_tools.analyze_stock_technicals(symbol)
        if "error" in technicals:
            raise HTTPException(status_code=404, detail=technicals["error"])
        return technicals
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{symbol}/financials")
async def get_stock_financials(symbol: str):
    try:
        financials = mcp_tools.get_financials(symbol)
        if "error" in financials:
            raise HTTPException(status_code=404, detail=financials["error"])
        return financials
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{symbol}/recommendations")
async def get_stock_recommendations(symbol: str):
    try:
        recommendations = mcp_tools.get_recommendations(symbol)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{symbol}/ai-analysis")
async def get_ai_stock_analysis(symbol: str):
    try:
        result = await ai_analyst.generate_stock_recommendation(symbol)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search")
async def search_stocks(query: str, limit: int = 10):
    try:
        results = mcp_tools.search_stocks(query, limit)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scheduler")
async def create_scheduler_endpoint(scheduler: SchedulerCreate):
    user = get_user_by_id(scheduler.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = create_scheduler(
        user_id=scheduler.user_id,
        prompt=scheduler.prompt,
        trigger_time=scheduler.trigger_time.value,
        symbols=scheduler.symbols or [],
        is_active=scheduler.is_active
    )
    
    next_runs = scheduler_service.get_next_run_times()
    
    return {
        **result,
        "next_run": next_runs.get(scheduler.trigger_time.value)
    }


@app.get("/api/scheduler/user/{user_id}")
async def get_user_schedulers_endpoint(user_id: str):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    schedulers = get_user_schedulers(user_id)
    next_runs = scheduler_service.get_next_run_times()
    
    for s in schedulers:
        s["next_run"] = next_runs.get(s["trigger_time"])
    
    return {"schedulers": schedulers}


@app.get("/api/scheduler/{scheduler_id}")
async def get_scheduler_endpoint(scheduler_id: str):
    scheduler = get_scheduler_by_id(scheduler_id)
    if not scheduler:
        raise HTTPException(status_code=404, detail="Scheduler not found")
    
    next_runs = scheduler_service.get_next_run_times()
    scheduler["next_run"] = next_runs.get(scheduler["trigger_time"])
    
    return scheduler


@app.put("/api/scheduler/{scheduler_id}")
async def update_scheduler_endpoint(scheduler_id: str, updates: dict):
    result = update_scheduler(scheduler_id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="Scheduler not found")
    return result


@app.delete("/api/scheduler/{scheduler_id}")
async def delete_scheduler_endpoint(scheduler_id: str):
    success = delete_scheduler(scheduler_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scheduler not found")
    return {"message": "Scheduler deleted successfully"}


@app.post("/api/scheduler/{scheduler_id}/test")
async def test_scheduler_endpoint(scheduler_id: str):
    result = await scheduler_service.run_manual_alert(scheduler_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/api/scheduler/next-runs")
async def get_next_runs():
    return scheduler_service.get_next_run_times()


# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "stock-ai-frontend")
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR)

@app.get("/app")
async def serve_app():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/app/{path:path}")
async def serve_frontend(path: str):
    file_path = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Mount static directories
if os.path.exists(os.path.join(FRONTEND_DIR, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
if os.path.exists(os.path.join(FRONTEND_DIR, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")

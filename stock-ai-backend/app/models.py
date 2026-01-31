from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TriggerTime(str, Enum):
    MORNING = "morning"
    EVENING = "evening"


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    symbol: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    symbol: Optional[str] = None
    data: Optional[dict] = None


class StockQuery(BaseModel):
    symbol: str
    period: Optional[str] = "1mo"


class MarketQuery(BaseModel):
    market_type: str = "stocks"
    limit: int = 10


class SchedulerCreate(BaseModel):
    user_id: str
    prompt: str
    trigger_time: TriggerTime
    symbols: Optional[List[str]] = []
    is_active: bool = True


class SchedulerResponse(BaseModel):
    id: str
    user_id: str
    prompt: str
    trigger_time: TriggerTime
    symbols: List[str]
    is_active: bool
    created_at: datetime
    next_run: Optional[datetime] = None


class StockRecommendation(BaseModel):
    symbol: str
    name: str
    current_price: float
    recommendation: str
    confidence: float
    reasoning: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None


class MarketSummary(BaseModel):
    market_status: str
    major_indices: List[dict]
    top_gainers: List[dict]
    top_losers: List[dict]
    market_news: List[dict]
    last_updated: datetime

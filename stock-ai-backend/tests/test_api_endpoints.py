"""
Unit tests for main.py - FastAPI API endpoints.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with patch('app.main.scheduler_service'):
        from app.main import app
        return TestClient(app)


class TestRootEndpoints:
    """Tests for root and health endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Stock AI Analyst API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestAuthEndpoints:
    """Tests for authentication endpoints."""
    
    def test_register_success(self, client, temp_data_dir):
        """Test successful user registration."""
        with patch('app.main.create_user') as mock_create, \
             patch('app.main.email_service'):
            mock_create.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "name": "Test User",
                "created_at": "2024-01-01T00:00:00"
            }
            
            response = client.post("/api/auth/register", json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "password123"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            assert data["name"] == "Test User"
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        with patch('app.main.create_user', return_value=None):
            response = client.post("/api/auth/register", json={
                "email": "existing@example.com",
                "name": "Test User",
                "password": "password123"
            })
            
            assert response.status_code == 400
            assert "already registered" in response.json()["detail"].lower()
    
    def test_login_success(self, client):
        """Test successful login."""
        with patch('app.main.authenticate_user') as mock_auth:
            mock_auth.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "name": "Test User"
            }
            
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "password123"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Login successful"
            assert data["user"]["email"] == "test@example.com"
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        with patch('app.main.authenticate_user', return_value=None):
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "wrongpassword"
            })
            
            assert response.status_code == 401
            assert "invalid" in response.json()["detail"].lower()


class TestChatEndpoint:
    """Tests for chat endpoint."""
    
    def test_chat_success(self, client):
        """Test successful chat request."""
        with patch('app.main.ai_analyst') as mock_ai:
            mock_ai.chat = AsyncMock(return_value={
                "response": "AAPL is a strong buy.",
                "symbol": "AAPL",
                "data": None
            })
            
            response = client.post("/api/chat", json={
                "message": "Analyze AAPL",
                "symbol": "AAPL"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert data["symbol"] == "AAPL"
    
    def test_chat_without_symbol(self, client):
        """Test chat request without specific symbol."""
        with patch('app.main.ai_analyst') as mock_ai:
            mock_ai.chat = AsyncMock(return_value={
                "response": "The market is bullish today.",
                "symbol": None,
                "data": None
            })
            
            response = client.post("/api/chat", json={
                "message": "How is the market today?"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data


class TestMarketEndpoints:
    """Tests for market data endpoints."""
    
    def test_get_market_summary(self, client):
        """Test market summary endpoint."""
        with patch('app.main.mcp_tools') as mock_mcp:
            mock_mcp.get_market_indices.return_value = [
                {"symbol": "^GSPC", "name": "S&P 500", "price": 5000}
            ]
            mock_mcp.get_top_movers.return_value = {
                "gainers": [{"symbol": "AAPL", "change_percent": 5.0}],
                "losers": [{"symbol": "MSFT", "change_percent": -3.0}]
            }
            
            response = client.get("/api/market/summary")
            
            assert response.status_code == 200
            data = response.json()
            assert "market_status" in data
            assert "major_indices" in data
            assert "top_gainers" in data
            assert "top_losers" in data
    
    def test_get_ai_market_summary(self, client):
        """Test AI market summary endpoint."""
        with patch('app.main.ai_analyst') as mock_ai:
            mock_ai.generate_market_summary = AsyncMock(return_value={
                "summary": "Market is bullish",
                "indices": [],
                "movers": {}
            })
            
            response = client.get("/api/market/ai-summary")
            
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
    
    def test_get_indices(self, client):
        """Test market indices endpoint."""
        with patch('app.main.mcp_tools') as mock_mcp:
            mock_mcp.get_market_indices.return_value = [
                {"symbol": "^GSPC", "name": "S&P 500", "price": 5000}
            ]
            
            response = client.get("/api/market/indices")
            
            assert response.status_code == 200
            data = response.json()
            assert "indices" in data
    
    def test_get_movers(self, client):
        """Test market movers endpoint."""
        with patch('app.main.mcp_tools') as mock_mcp:
            mock_mcp.get_top_movers.return_value = {
                "gainers": [],
                "losers": []
            }
            
            response = client.get("/api/market/movers")
            
            assert response.status_code == 200
            data = response.json()
            assert "gainers" in data
            assert "losers" in data


class TestStockEndpoints:
    """Tests for stock data endpoints."""
    
    def test_get_stock_info(self, client):
        """Test stock info endpoint."""
        with patch('app.main.mcp_tools') as mock_mcp:
            mock_mcp.get_stock_info.return_value = {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "current_price": 150.0
            }
            
            response = client.get("/api/stocks/AAPL")
            
            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "AAPL"
    
    def test_get_stock_info_not_found(self, client):
        """Test stock info endpoint with invalid symbol."""
        with patch('app.main.mcp_tools') as mock_mcp:
            mock_mcp.get_stock_info.return_value = {"error": "Stock not found"}
            
            response = client.get("/api/stocks/INVALID")
            
            assert response.status_code == 404
    
    def test_get_stock_history(self, client):
        """Test stock history endpoint."""
        with patch('app.main.mcp_tools') as mock_mcp:
            mock_mcp.get_historical_data.return_value = {
                "symbol": "AAPL",
                "data": [{"date": "2024-01-01", "close": 150.0}]
            }
            
            response = client.get("/api/stocks/AAPL/history")
            
            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "AAPL"
            assert "data" in data
    
    def test_get_stock_news(self, client):
        """Test stock news endpoint."""
        with patch('app.main.mcp_tools') as mock_mcp:
            mock_mcp.get_stock_news.return_value = [
                {"title": "Apple news", "publisher": "Reuters"}
            ]
            
            response = client.get("/api/stocks/AAPL/news")
            
            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "AAPL"
            assert "news" in data
    
    def test_get_stock_technicals(self, client):
        """Test stock technicals endpoint."""
        with patch('app.main.mcp_tools') as mock_mcp:
            mock_mcp.analyze_stock_technicals.return_value = {
                "symbol": "AAPL",
                "rsi": 55.0,
                "macd": 2.5
            }
            
            response = client.get("/api/stocks/AAPL/technicals")
            
            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "AAPL"
            assert "rsi" in data
    
    def test_get_stock_financials(self, client):
        """Test stock financials endpoint."""
        with patch('app.main.mcp_tools') as mock_mcp:
            mock_mcp.get_financials.return_value = {
                "symbol": "AAPL",
                "income_statement": {},
                "balance_sheet": {}
            }
            
            response = client.get("/api/stocks/AAPL/financials")
            
            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "AAPL"
    
    def test_get_stock_recommendations(self, client):
        """Test stock recommendations endpoint."""
        with patch('app.main.mcp_tools') as mock_mcp:
            mock_mcp.get_recommendations.return_value = {
                "symbol": "AAPL",
                "recommendations": []
            }
            
            response = client.get("/api/stocks/AAPL/recommendations")
            
            assert response.status_code == 200
            data = response.json()
            assert "recommendations" in data
    
    def test_get_ai_stock_analysis(self, client):
        """Test AI stock analysis endpoint."""
        with patch('app.main.ai_analyst') as mock_ai:
            mock_ai.generate_stock_recommendation = AsyncMock(return_value={
                "symbol": "AAPL",
                "analysis": "BUY recommendation"
            })
            
            response = client.get("/api/stocks/AAPL/ai-analysis")
            
            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "AAPL"
            assert "analysis" in data
    
    def test_search_stocks(self, client):
        """Test stock search endpoint."""
        with patch('app.main.mcp_tools') as mock_mcp:
            mock_mcp.search_stocks.return_value = [
                {"symbol": "AAPL", "name": "Apple Inc."}
            ]
            
            response = client.get("/api/search?query=Apple")
            
            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "Apple"
            assert "results" in data


class TestSchedulerEndpoints:
    """Tests for scheduler endpoints."""
    
    def test_create_scheduler(self, client):
        """Test scheduler creation endpoint."""
        with patch('app.main.get_user_by_id') as mock_get_user, \
             patch('app.main.create_scheduler') as mock_create, \
             patch('app.main.scheduler_service') as mock_service:
            
            mock_get_user.return_value = {"id": "user-123", "email": "test@example.com"}
            mock_create.return_value = {
                "id": "scheduler-123",
                "user_id": "user-123",
                "prompt": "Analyze AAPL",
                "trigger_time": "morning",
                "symbols": ["AAPL"],
                "is_active": True,
                "created_at": "2024-01-01T00:00:00"
            }
            mock_service.get_next_run_times.return_value = {
                "morning": "2024-01-02T08:30:00",
                "evening": "2024-01-01T17:00:00"
            }
            
            response = client.post("/api/scheduler", json={
                "user_id": "user-123",
                "prompt": "Analyze AAPL",
                "trigger_time": "morning",
                "symbols": ["AAPL"],
                "is_active": True
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "user-123"
            assert data["prompt"] == "Analyze AAPL"
    
    def test_create_scheduler_user_not_found(self, client):
        """Test scheduler creation with non-existent user."""
        with patch('app.main.get_user_by_id', return_value=None):
            response = client.post("/api/scheduler", json={
                "user_id": "nonexistent",
                "prompt": "Test",
                "trigger_time": "morning",
                "symbols": [],
                "is_active": True
            })
            
            assert response.status_code == 404
    
    def test_get_user_schedulers(self, client):
        """Test getting user's schedulers."""
        with patch('app.main.get_user_by_id') as mock_get_user, \
             patch('app.main.get_user_schedulers') as mock_get_schedulers, \
             patch('app.main.scheduler_service') as mock_service:
            
            mock_get_user.return_value = {"id": "user-123"}
            mock_get_schedulers.return_value = [
                {"id": "scheduler-1", "trigger_time": "morning"},
                {"id": "scheduler-2", "trigger_time": "evening"}
            ]
            mock_service.get_next_run_times.return_value = {
                "morning": "2024-01-02T08:30:00",
                "evening": "2024-01-01T17:00:00"
            }
            
            response = client.get("/api/scheduler/user/user-123")
            
            assert response.status_code == 200
            data = response.json()
            assert "schedulers" in data
            assert len(data["schedulers"]) == 2
    
    def test_get_scheduler_by_id(self, client):
        """Test getting scheduler by ID."""
        with patch('app.main.get_scheduler_by_id') as mock_get, \
             patch('app.main.scheduler_service') as mock_service:
            
            mock_get.return_value = {
                "id": "scheduler-123",
                "trigger_time": "morning"
            }
            mock_service.get_next_run_times.return_value = {
                "morning": "2024-01-02T08:30:00"
            }
            
            response = client.get("/api/scheduler/scheduler-123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "scheduler-123"
    
    def test_update_scheduler(self, client):
        """Test updating a scheduler."""
        with patch('app.main.update_scheduler') as mock_update:
            mock_update.return_value = {
                "id": "scheduler-123",
                "prompt": "Updated prompt",
                "is_active": False
            }
            
            response = client.put("/api/scheduler/scheduler-123", json={
                "prompt": "Updated prompt",
                "is_active": False
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["prompt"] == "Updated prompt"
    
    def test_delete_scheduler(self, client):
        """Test deleting a scheduler."""
        with patch('app.main.delete_scheduler', return_value=True):
            response = client.delete("/api/scheduler/scheduler-123")
            
            assert response.status_code == 200
            data = response.json()
            assert "deleted" in data["message"].lower()
    
    def test_delete_scheduler_not_found(self, client):
        """Test deleting non-existent scheduler."""
        with patch('app.main.delete_scheduler', return_value=False):
            response = client.delete("/api/scheduler/nonexistent")
            
            assert response.status_code == 404
    
    def test_test_scheduler(self, client):
        """Test manual scheduler trigger."""
        with patch('app.main.scheduler_service') as mock_service:
            mock_service.run_manual_alert = AsyncMock(return_value={
                "success": True,
                "email_sent": True,
                "content": "Test alert content"
            })
            
            response = client.post("/api/scheduler/scheduler-123/test")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_get_next_runs(self, client):
        """Test getting next scheduled run times."""
        with patch('app.main.scheduler_service') as mock_service:
            mock_service.get_next_run_times.return_value = {
                "morning": "2024-01-02T08:30:00",
                "evening": "2024-01-01T17:00:00"
            }
            
            response = client.get("/api/scheduler/next-runs")
            
            assert response.status_code == 200
            data = response.json()
            assert "morning" in data
            assert "evening" in data

"""
Pytest configuration and fixtures for Stock AI Backend tests.
"""
import pytest
import os
import sys
import tempfile
import json
from unittest.mock import MagicMock, patch, AsyncMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for tests."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # Create empty JSON files
    users_file = data_dir / "users.json"
    users_file.write_text("{}")
    
    schedulers_file = data_dir / "schedulers.json"
    schedulers_file.write_text("{}")
    
    return data_dir


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a test AI response."
    mock_response.choices[0].message.tool_calls = None
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_yfinance_ticker():
    """Mock yfinance Ticker for testing."""
    mock_ticker = MagicMock()
    mock_ticker.info = {
        "longName": "Apple Inc.",
        "shortName": "Apple",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "currentPrice": 150.0,
        "previousClose": 148.0,
        "regularMarketPrice": 150.0,
        "open": 149.0,
        "dayHigh": 151.0,
        "dayLow": 148.5,
        "volume": 50000000,
        "averageVolume": 45000000,
        "marketCap": 2500000000000,
        "trailingPE": 25.5,
        "forwardPE": 22.0,
        "trailingEps": 5.89,
        "dividendYield": 0.005,
        "fiftyTwoWeekHigh": 180.0,
        "fiftyTwoWeekLow": 120.0,
        "fiftyDayAverage": 145.0,
        "twoHundredDayAverage": 140.0,
        "beta": 1.2,
        "longBusinessSummary": "Apple Inc. designs, manufactures, and markets smartphones.",
        "website": "https://www.apple.com",
        "currency": "USD"
    }
    mock_ticker.news = [
        {
            "title": "Apple announces new product",
            "publisher": "Reuters",
            "link": "https://example.com/news1",
            "providerPublishTime": 1700000000,
            "type": "STORY"
        }
    ]
    return mock_ticker


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_scheduler_data():
    """Sample scheduler data for testing."""
    return {
        "user_id": "test-user-id-123",
        "prompt": "Analyze tech stocks",
        "trigger_time": "morning",
        "symbols": ["AAPL", "MSFT", "GOOGL"],
        "is_active": True
    }


@pytest.fixture
def test_client():
    """Create a test client for FastAPI app."""
    from app.main import app
    return TestClient(app)

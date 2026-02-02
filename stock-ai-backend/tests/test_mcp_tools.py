"""
Unit tests for mcp_tools.py - Financial data retrieval tools.
"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime


class TestGetStockInfo:
    """Tests for get_stock_info function."""
    
    def test_get_stock_info_success(self, mock_yfinance_ticker):
        """Test successful stock info retrieval."""
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_yfinance_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_stock_info("AAPL")
            
            assert result["symbol"] == "AAPL"
            assert result["name"] == "Apple Inc."
            assert result["sector"] == "Technology"
            assert result["current_price"] == 150.0
            assert result["market_cap"] == 2500000000000
            assert result["pe_ratio"] == 25.5
    
    def test_get_stock_info_error(self):
        """Test stock info retrieval with error."""
        mock_ticker = MagicMock()
        mock_ticker.info = {}
        mock_ticker.info.__getitem__ = MagicMock(side_effect=Exception("API Error"))
        
        with patch('app.mcp_tools.yf.Ticker', side_effect=Exception("API Error")):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_stock_info("INVALID")
            
            assert "error" in result


class TestGetHistoricalData:
    """Tests for get_historical_data function."""
    
    def test_get_historical_data_success(self):
        """Test successful historical data retrieval."""
        mock_ticker = MagicMock()
        mock_hist = pd.DataFrame({
            "Open": [148.0, 149.0, 150.0],
            "High": [150.0, 151.0, 152.0],
            "Low": [147.0, 148.0, 149.0],
            "Close": [149.0, 150.0, 151.0],
            "Volume": [1000000, 1100000, 1200000]
        }, index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]))
        mock_ticker.history.return_value = mock_hist
        
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_historical_data("AAPL", "1mo", "1d")
            
            assert result["symbol"] == "AAPL"
            assert result["period"] == "1mo"
            assert result["interval"] == "1d"
            assert len(result["data"]) == 3
            assert result["data"][0]["close"] == 149.0
    
    def test_get_historical_data_empty(self):
        """Test historical data retrieval with no data."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()
        
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_historical_data("INVALID", "1mo", "1d")
            
            assert "error" in result


class TestGetStockNews:
    """Tests for get_stock_news function."""
    
    def test_get_stock_news_success(self, mock_yfinance_ticker):
        """Test successful news retrieval."""
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_yfinance_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_stock_news("AAPL")
            
            assert len(result) >= 1
            assert result[0]["title"] == "Apple announces new product"
            assert result[0]["publisher"] == "Reuters"
    
    def test_get_stock_news_error(self):
        """Test news retrieval with error."""
        with patch('app.mcp_tools.yf.Ticker', side_effect=Exception("API Error")):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_stock_news("INVALID")
            
            assert len(result) == 1
            assert "error" in result[0]


class TestGetMarketIndices:
    """Tests for get_market_indices function."""
    
    def test_get_market_indices_success(self):
        """Test successful market indices retrieval."""
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "regularMarketPrice": 5000.0,
            "previousClose": 4950.0
        }
        mock_ticker.history.return_value = pd.DataFrame()
        
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_market_indices()
            
            assert isinstance(result, list)
            # Should have some indices
            assert len(result) > 0


class TestGetTopMovers:
    """Tests for get_top_movers function."""
    
    def test_get_top_movers_stocks(self):
        """Test top movers for stocks."""
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "shortName": "Test Stock",
            "currentPrice": 100.0,
            "previousClose": 95.0,
            "volume": 1000000
        }
        
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_top_movers("stocks", 5)
            
            assert "gainers" in result
            assert "losers" in result
    
    def test_get_top_movers_etf(self):
        """Test top movers for ETFs."""
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "shortName": "Test ETF",
            "currentPrice": 400.0,
            "previousClose": 395.0,
            "volume": 5000000
        }
        
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_top_movers("etf", 5)
            
            assert "gainers" in result
            assert "losers" in result


class TestAnalyzeStockTechnicals:
    """Tests for analyze_stock_technicals function."""
    
    def test_analyze_stock_technicals_success(self):
        """Test successful technical analysis."""
        mock_ticker = MagicMock()
        # Create enough data points for technical analysis
        dates = pd.date_range(start="2024-01-01", periods=200, freq="D")
        prices = [100 + i * 0.5 for i in range(200)]
        mock_hist = pd.DataFrame({
            "Close": prices
        }, index=dates)
        mock_ticker.history.return_value = mock_hist
        
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.analyze_stock_technicals("AAPL")
            
            assert result["symbol"] == "AAPL"
            assert "current_price" in result
            assert "sma_20" in result
            assert "sma_50" in result
            assert "rsi" in result
            assert "macd" in result
            assert "signals" in result
    
    def test_analyze_stock_technicals_empty_data(self):
        """Test technical analysis with no data."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()
        
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.analyze_stock_technicals("INVALID")
            
            assert "error" in result


class TestSearchStocks:
    """Tests for search_stocks function."""
    
    def test_search_stocks_by_symbol(self):
        """Test searching stocks by symbol."""
        from app.mcp_tools import mcp_tools
        
        result = mcp_tools.search_stocks("AAPL", 10)
        
        assert isinstance(result, list)
        # Should find Apple
        symbols = [r["symbol"] for r in result]
        assert "AAPL" in symbols
    
    def test_search_stocks_by_name(self):
        """Test searching stocks by name."""
        from app.mcp_tools import mcp_tools
        
        result = mcp_tools.search_stocks("Apple", 10)
        
        assert isinstance(result, list)
        assert len(result) > 0


class TestGetFinancials:
    """Tests for get_financials function."""
    
    def test_get_financials_success(self):
        """Test successful financials retrieval."""
        mock_ticker = MagicMock()
        mock_ticker.income_stmt = pd.DataFrame({
            datetime(2024, 1, 1): {"Revenue": 100000000, "NetIncome": 20000000}
        })
        mock_ticker.balance_sheet = pd.DataFrame({
            datetime(2024, 1, 1): {"TotalAssets": 500000000}
        })
        mock_ticker.cashflow = pd.DataFrame({
            datetime(2024, 1, 1): {"OperatingCashFlow": 30000000}
        })
        
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_financials("AAPL")
            
            assert result["symbol"] == "AAPL"
            assert "income_statement" in result
            assert "balance_sheet" in result
            assert "cash_flow" in result


class TestGetRecommendations:
    """Tests for get_recommendations function."""
    
    def test_get_recommendations_success(self):
        """Test successful recommendations retrieval."""
        mock_ticker = MagicMock()
        mock_recommendations = pd.DataFrame({
            "Firm": ["Goldman Sachs", "Morgan Stanley"],
            "To Grade": ["Buy", "Hold"],
            "From Grade": ["Hold", "Sell"],
            "Action": ["upgrade", "downgrade"]
        }, index=pd.to_datetime(["2024-01-01", "2024-01-02"]))
        mock_ticker.recommendations = mock_recommendations
        
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_recommendations("AAPL")
            
            assert result["symbol"] == "AAPL"
            assert "recommendations" in result
            assert len(result["recommendations"]) == 2
    
    def test_get_recommendations_empty(self):
        """Test recommendations retrieval with no data."""
        mock_ticker = MagicMock()
        mock_ticker.recommendations = None
        
        with patch('app.mcp_tools.yf.Ticker', return_value=mock_ticker):
            from app.mcp_tools import mcp_tools
            
            result = mcp_tools.get_recommendations("AAPL")
            
            assert result["symbol"] == "AAPL"
            assert result["recommendations"] == []

"""
Unit tests for ai_service.py - AI-powered stock analysis.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json


class TestAIStockAnalyst:
    """Tests for AIStockAnalyst class."""
    
    def test_execute_tool_get_stock_info(self):
        """Test _execute_tool with get_stock_info."""
        mock_result = {"symbol": "AAPL", "name": "Apple Inc."}
        
        with patch('app.ai_service.mcp_tools') as mock_mcp:
            mock_mcp.get_stock_info.return_value = mock_result
            
            from app.ai_service import AIStockAnalyst
            analyst = AIStockAnalyst()
            
            result = analyst._execute_tool("get_stock_info", {"symbol": "AAPL"})
            
            assert result == mock_result
            mock_mcp.get_stock_info.assert_called_once_with(symbol="AAPL")
    
    def test_execute_tool_get_market_indices(self):
        """Test _execute_tool with get_market_indices."""
        mock_result = [{"symbol": "^GSPC", "name": "S&P 500"}]
        
        with patch('app.ai_service.mcp_tools') as mock_mcp:
            mock_mcp.get_market_indices.return_value = mock_result
            
            from app.ai_service import AIStockAnalyst
            analyst = AIStockAnalyst()
            
            result = analyst._execute_tool("get_market_indices", {})
            
            assert result == mock_result
    
    def test_execute_tool_unknown(self):
        """Test _execute_tool with unknown tool."""
        from app.ai_service import AIStockAnalyst
        analyst = AIStockAnalyst()
        
        result = analyst._execute_tool("unknown_tool", {})
        
        assert "error" in result
        assert "Unknown tool" in result["error"]
    
    @pytest.mark.asyncio
    async def test_chat_simple_response(self, mock_openai_client):
        """Test chat with simple response (no tool calls)."""
        with patch('app.ai_service.OpenAI', return_value=mock_openai_client):
            from app.ai_service import AIStockAnalyst
            analyst = AIStockAnalyst()
            analyst.client = mock_openai_client
            
            result = await analyst.chat("What is the stock market?")
            
            assert "response" in result
            assert result["response"] == "This is a test AI response."
    
    @pytest.mark.asyncio
    async def test_chat_with_symbol(self, mock_openai_client):
        """Test chat with specific symbol."""
        with patch('app.ai_service.OpenAI', return_value=mock_openai_client):
            from app.ai_service import AIStockAnalyst
            analyst = AIStockAnalyst()
            analyst.client = mock_openai_client
            
            result = await analyst.chat("Analyze this stock", symbol="AAPL")
            
            assert "response" in result
            assert result["symbol"] == "AAPL"
    
    @pytest.mark.asyncio
    async def test_chat_with_tool_calls(self):
        """Test chat with tool calls."""
        mock_client = MagicMock()
        
        # First response with tool call
        first_response = MagicMock()
        first_message = MagicMock()
        first_message.content = None
        first_message.tool_calls = [MagicMock()]
        first_message.tool_calls[0].id = "call_123"
        first_message.tool_calls[0].function.name = "get_stock_info"
        first_message.tool_calls[0].function.arguments = '{"symbol": "AAPL"}'
        first_response.choices = [MagicMock()]
        first_response.choices[0].message = first_message
        
        # Second response without tool calls
        second_response = MagicMock()
        second_message = MagicMock()
        second_message.content = "Apple stock analysis complete."
        second_message.tool_calls = None
        second_response.choices = [MagicMock()]
        second_response.choices[0].message = second_message
        
        mock_client.chat.completions.create.side_effect = [first_response, second_response]
        
        with patch('app.ai_service.OpenAI', return_value=mock_client), \
             patch('app.ai_service.mcp_tools') as mock_mcp:
            mock_mcp.get_stock_info.return_value = {"symbol": "AAPL", "name": "Apple"}
            
            from app.ai_service import AIStockAnalyst
            analyst = AIStockAnalyst()
            analyst.client = mock_client
            
            result = await analyst.chat("Tell me about AAPL")
            
            assert result["response"] == "Apple stock analysis complete."
            assert result["data"] is not None
            assert "get_stock_info" in result["data"]
    
    @pytest.mark.asyncio
    async def test_chat_error_handling(self):
        """Test chat error handling."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('app.ai_service.OpenAI', return_value=mock_client):
            from app.ai_service import AIStockAnalyst
            analyst = AIStockAnalyst()
            analyst.client = mock_client
            
            result = await analyst.chat("Test message")
            
            assert "error" in result["response"].lower() or "apologize" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_generate_market_summary(self):
        """Test generate_market_summary."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Market is bullish today."
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('app.ai_service.OpenAI', return_value=mock_client), \
             patch('app.ai_service.mcp_tools') as mock_mcp:
            mock_mcp.get_market_indices.return_value = [{"symbol": "^GSPC", "price": 5000}]
            mock_mcp.get_top_movers.return_value = {"gainers": [], "losers": []}
            
            from app.ai_service import AIStockAnalyst
            analyst = AIStockAnalyst()
            analyst.client = mock_client
            
            result = await analyst.generate_market_summary()
            
            assert "summary" in result
            assert result["summary"] == "Market is bullish today."
            assert "indices" in result
            assert "movers" in result
    
    @pytest.mark.asyncio
    async def test_generate_market_summary_error(self):
        """Test generate_market_summary error handling."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('app.ai_service.OpenAI', return_value=mock_client), \
             patch('app.ai_service.mcp_tools') as mock_mcp:
            mock_mcp.get_market_indices.return_value = []
            mock_mcp.get_top_movers.return_value = {"gainers": [], "losers": []}
            
            from app.ai_service import AIStockAnalyst
            analyst = AIStockAnalyst()
            analyst.client = mock_client
            
            result = await analyst.generate_market_summary()
            
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_generate_stock_recommendation(self):
        """Test generate_stock_recommendation."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "BUY recommendation for AAPL."
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('app.ai_service.OpenAI', return_value=mock_client), \
             patch('app.ai_service.mcp_tools') as mock_mcp:
            mock_mcp.get_stock_info.return_value = {"symbol": "AAPL", "name": "Apple"}
            mock_mcp.analyze_stock_technicals.return_value = {"rsi": 55}
            mock_mcp.get_stock_news.return_value = []
            mock_mcp.get_recommendations.return_value = {"recommendations": []}
            
            from app.ai_service import AIStockAnalyst
            analyst = AIStockAnalyst()
            analyst.client = mock_client
            
            result = await analyst.generate_stock_recommendation("AAPL")
            
            assert result["symbol"] == "AAPL"
            assert "analysis" in result
            assert "BUY" in result["analysis"]
            assert "data" in result
    
    @pytest.mark.asyncio
    async def test_generate_stock_recommendation_error(self):
        """Test generate_stock_recommendation error handling."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('app.ai_service.OpenAI', return_value=mock_client), \
             patch('app.ai_service.mcp_tools') as mock_mcp:
            mock_mcp.get_stock_info.return_value = {"symbol": "AAPL"}
            mock_mcp.analyze_stock_technicals.return_value = {}
            mock_mcp.get_stock_news.return_value = []
            mock_mcp.get_recommendations.return_value = {}
            
            from app.ai_service import AIStockAnalyst
            analyst = AIStockAnalyst()
            analyst.client = mock_client
            
            result = await analyst.generate_stock_recommendation("AAPL")
            
            assert "error" in result


class TestToolDefinitions:
    """Tests for tool definitions."""
    
    def test_tools_are_defined(self):
        """Test that all tools are properly defined."""
        from app.ai_service import AIStockAnalyst
        analyst = AIStockAnalyst()
        
        tool_names = [t["function"]["name"] for t in analyst.tools]
        
        expected_tools = [
            "get_stock_info",
            "get_historical_data",
            "get_stock_news",
            "analyze_stock_technicals",
            "get_market_indices",
            "get_top_movers",
            "get_recommendations",
            "get_financials"
        ]
        
        for tool in expected_tools:
            assert tool in tool_names, f"Tool {tool} not found in definitions"
    
    def test_tool_schemas_valid(self):
        """Test that tool schemas are valid."""
        from app.ai_service import AIStockAnalyst
        analyst = AIStockAnalyst()
        
        for tool in analyst.tools:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]

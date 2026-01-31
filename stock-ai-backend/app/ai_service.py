import os
from openai import OpenAI
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from .mcp_tools import mcp_tools
import json

load_dotenv()


class AIStockAnalyst:
    """AI-powered stock analyst using OpenAI API with MCP tools."""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
        
        self.system_prompt = """You are an expert AI stock analyst with deep knowledge of financial markets, 
technical analysis, fundamental analysis, and market trends. You have access to real-time stock data 
through specialized tools.

Your responsibilities:
1. Analyze stocks, ETFs, and funds based on user queries
2. Provide buy/sell/hold recommendations with clear reasoning
3. Consider world news, market conditions, company fundamentals, and technical indicators
4. Explain complex financial concepts in simple terms
5. Be objective and always mention risks involved

When analyzing stocks:
- Consider both technical indicators (RSI, MACD, moving averages) and fundamentals (P/E, EPS, revenue growth)
- Factor in recent news and market sentiment
- Provide specific price targets when possible
- Always include risk warnings

Format your responses clearly with sections for:
- Summary
- Analysis
- Recommendation
- Risk Factors"""

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_stock_info",
                    "description": "Get comprehensive information about a stock including price, fundamentals, and company details",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "The stock ticker symbol (e.g., AAPL, MSFT)"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_historical_data",
                    "description": "Get historical price data for a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "The stock ticker symbol"
                            },
                            "period": {
                                "type": "string",
                                "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)",
                                "default": "1mo"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_stock_news",
                    "description": "Get recent news articles about a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "The stock ticker symbol"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_stock_technicals",
                    "description": "Perform technical analysis on a stock including RSI, MACD, and moving averages",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "The stock ticker symbol"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_market_indices",
                    "description": "Get current data for major market indices (S&P 500, Dow Jones, NASDAQ, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_movers",
                    "description": "Get top gaining and losing stocks or ETFs",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "market_type": {
                                "type": "string",
                                "description": "Type of securities (stocks or etf)",
                                "default": "stocks"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 10
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recommendations",
                    "description": "Get analyst recommendations for a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "The stock ticker symbol"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_financials",
                    "description": "Get financial statements (income statement, balance sheet, cash flow) for a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "The stock ticker symbol"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Execute a tool and return the result."""
        tool_map = {
            "get_stock_info": mcp_tools.get_stock_info,
            "get_historical_data": mcp_tools.get_historical_data,
            "get_stock_news": mcp_tools.get_stock_news,
            "analyze_stock_technicals": mcp_tools.analyze_stock_technicals,
            "get_market_indices": mcp_tools.get_market_indices,
            "get_top_movers": mcp_tools.get_top_movers,
            "get_recommendations": mcp_tools.get_recommendations,
            "get_financials": mcp_tools.get_financials,
        }
        
        if tool_name in tool_map:
            return tool_map[tool_name](**arguments)
        return {"error": f"Unknown tool: {tool_name}"}

    async def chat(self, message: str, symbol: Optional[str] = None, 
                   conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process a chat message and return AI response with tool results."""
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        user_message = message
        if symbol:
            user_message = f"[Regarding {symbol}] {message}"
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            tool_results = {}
            
            while assistant_message.tool_calls:
                messages.append(assistant_message)
                
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    result = self._execute_tool(tool_name, arguments)
                    tool_results[tool_name] = result
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
                assistant_message = response.choices[0].message
            
            return {
                "response": assistant_message.content,
                "symbol": symbol,
                "data": tool_results if tool_results else None
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}. Please check if the OpenAI API key is configured correctly.",
                "symbol": symbol,
                "data": None
            }

    async def generate_market_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive market summary."""
        try:
            indices = mcp_tools.get_market_indices()
            movers = mcp_tools.get_top_movers("stocks", 5)
            
            summary_prompt = f"""Based on the following market data, provide a brief market summary:

Market Indices: {json.dumps(indices)}
Top Movers: {json.dumps(movers)}

Provide a concise summary of:
1. Overall market sentiment
2. Key movements in major indices
3. Notable stock movements
4. Any potential concerns or opportunities"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": summary_prompt}
                ]
            )
            
            return {
                "summary": response.choices[0].message.content,
                "indices": indices,
                "movers": movers
            }
        except Exception as e:
            return {"error": str(e)}

    async def generate_stock_recommendation(self, symbol: str) -> Dict[str, Any]:
        """Generate a buy/sell/hold recommendation for a stock."""
        try:
            info = mcp_tools.get_stock_info(symbol)
            technicals = mcp_tools.analyze_stock_technicals(symbol)
            news = mcp_tools.get_stock_news(symbol)
            recommendations = mcp_tools.get_recommendations(symbol)
            
            analysis_prompt = f"""Analyze the following stock data and provide a clear BUY, SELL, or HOLD recommendation:

Stock Info: {json.dumps(info)}
Technical Analysis: {json.dumps(technicals)}
Recent News: {json.dumps(news[:5])}
Analyst Recommendations: {json.dumps(recommendations)}

Provide:
1. Clear recommendation (BUY/SELL/HOLD)
2. Confidence level (1-10)
3. Target price
4. Stop loss price
5. Detailed reasoning
6. Key risks"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            return {
                "symbol": symbol,
                "analysis": response.choices[0].message.content,
                "data": {
                    "info": info,
                    "technicals": technicals,
                    "news": news[:5],
                    "recommendations": recommendations
                }
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}


ai_analyst = AIStockAnalyst()

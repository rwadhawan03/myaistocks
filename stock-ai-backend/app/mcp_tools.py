import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json


class MCPStockTools:
    """MCP-based tools for stock data retrieval and analysis using yfinance."""
    
    @staticmethod
    def get_stock_info(symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock information."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "symbol": symbol.upper(),
                "name": info.get("longName", info.get("shortName", symbol)),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "current_price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "previous_close": info.get("previousClose", 0),
                "open": info.get("open", info.get("regularMarketOpen", 0)),
                "day_high": info.get("dayHigh", info.get("regularMarketDayHigh", 0)),
                "day_low": info.get("dayLow", info.get("regularMarketDayLow", 0)),
                "volume": info.get("volume", info.get("regularMarketVolume", 0)),
                "avg_volume": info.get("averageVolume", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "forward_pe": info.get("forwardPE", 0),
                "eps": info.get("trailingEps", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
                "50_day_avg": info.get("fiftyDayAverage", 0),
                "200_day_avg": info.get("twoHundredDayAverage", 0),
                "beta": info.get("beta", 0),
                "description": info.get("longBusinessSummary", ""),
                "website": info.get("website", ""),
                "currency": info.get("currency", "USD"),
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    @staticmethod
    def get_historical_data(symbol: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        """Get historical price data for a stock."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return {"error": "No historical data available", "symbol": symbol}
            
            data = []
            for date, row in hist.iterrows():
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"])
                })
            
            return {
                "symbol": symbol.upper(),
                "period": period,
                "interval": interval,
                "data": data,
                "start_date": data[0]["date"] if data else None,
                "end_date": data[-1]["date"] if data else None,
                "data_points": len(data)
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    @staticmethod
    def get_stock_news(symbol: str) -> List[Dict[str, Any]]:
        """Get recent news for a stock."""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            news_list = []
            for item in news[:10]:
                news_list.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", ""),
                    "link": item.get("link", ""),
                    "published": datetime.fromtimestamp(item.get("providerPublishTime", 0)).strftime("%Y-%m-%d %H:%M") if item.get("providerPublishTime") else "",
                    "type": item.get("type", ""),
                    "thumbnail": item.get("thumbnail", {}).get("resolutions", [{}])[0].get("url", "") if item.get("thumbnail") else ""
                })
            
            return news_list
        except Exception as e:
            return [{"error": str(e)}]

    @staticmethod
    def get_financials(symbol: str) -> Dict[str, Any]:
        """Get financial statements for a stock."""
        try:
            ticker = yf.Ticker(symbol)
            
            income_stmt = ticker.income_stmt
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            def df_to_dict(df):
                if df is None or df.empty:
                    return {}
                result = {}
                for col in df.columns[:4]:
                    col_data = {}
                    for idx, val in df[col].items():
                        if pd.notna(val):
                            col_data[str(idx)] = float(val) if isinstance(val, (int, float)) else str(val)
                    result[col.strftime("%Y-%m-%d") if hasattr(col, 'strftime') else str(col)] = col_data
                return result
            
            return {
                "symbol": symbol.upper(),
                "income_statement": df_to_dict(income_stmt),
                "balance_sheet": df_to_dict(balance_sheet),
                "cash_flow": df_to_dict(cash_flow)
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    @staticmethod
    def get_recommendations(symbol: str) -> Dict[str, Any]:
        """Get analyst recommendations for a stock."""
        try:
            ticker = yf.Ticker(symbol)
            recommendations = ticker.recommendations
            
            if recommendations is None or recommendations.empty:
                return {"symbol": symbol, "recommendations": []}
            
            rec_list = []
            for date, row in recommendations.tail(10).iterrows():
                rec_list.append({
                    "date": date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date),
                    "firm": row.get("Firm", ""),
                    "to_grade": row.get("To Grade", ""),
                    "from_grade": row.get("From Grade", ""),
                    "action": row.get("Action", "")
                })
            
            return {
                "symbol": symbol.upper(),
                "recommendations": rec_list
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    @staticmethod
    def get_market_indices() -> List[Dict[str, Any]]:
        """Get major market indices data."""
        indices = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ",
            "^RUT": "Russell 2000",
            "^VIX": "VIX",
            "^FTSE": "FTSE 100",
            "^N225": "Nikkei 225",
            "^HSI": "Hang Seng"
        }
        
        results = []
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="2d")
                
                current = info.get("regularMarketPrice", 0)
                prev_close = info.get("previousClose", 0)
                
                if current and prev_close:
                    change = current - prev_close
                    change_pct = (change / prev_close) * 100
                else:
                    change = 0
                    change_pct = 0
                
                results.append({
                    "symbol": symbol,
                    "name": name,
                    "price": round(current, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_pct, 2)
                })
            except Exception:
                continue
        
        return results

    @staticmethod
    def get_top_movers(market_type: str = "stocks", limit: int = 10) -> Dict[str, List[Dict]]:
        """Get top gainers and losers."""
        try:
            if market_type == "etf":
                symbols = ["SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "VEA", "VWO", "BND", "GLD", 
                          "SLV", "USO", "XLF", "XLE", "XLK", "XLV", "XLI", "XLP", "XLU", "ARKK"]
            else:
                symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", 
                          "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "NFLX",
                          "ADBE", "CRM", "INTC", "AMD", "CSCO", "PEP", "KO", "NKE", "MRK", "PFE"]
            
            movers = []
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    current = info.get("currentPrice", info.get("regularMarketPrice", 0))
                    prev_close = info.get("previousClose", 0)
                    
                    if current and prev_close:
                        change = current - prev_close
                        change_pct = (change / prev_close) * 100
                        
                        movers.append({
                            "symbol": symbol,
                            "name": info.get("shortName", symbol),
                            "price": round(current, 2),
                            "change": round(change, 2),
                            "change_percent": round(change_pct, 2),
                            "volume": info.get("volume", 0)
                        })
                except Exception:
                    continue
            
            movers.sort(key=lambda x: x["change_percent"], reverse=True)
            
            return {
                "gainers": movers[:limit],
                "losers": movers[-limit:][::-1]
            }
        except Exception as e:
            return {"error": str(e), "gainers": [], "losers": []}

    @staticmethod
    def analyze_stock_technicals(symbol: str) -> Dict[str, Any]:
        """Perform technical analysis on a stock."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="6mo")
            
            if hist.empty:
                return {"error": "No data available", "symbol": symbol}
            
            close_prices = hist["Close"]
            
            sma_20 = close_prices.rolling(window=20).mean().iloc[-1]
            sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
            sma_200 = close_prices.rolling(window=200).mean().iloc[-1] if len(close_prices) >= 200 else None
            
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            exp1 = close_prices.ewm(span=12, adjust=False).mean()
            exp2 = close_prices.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            macd_value = macd.iloc[-1]
            signal_value = signal.iloc[-1]
            
            current_price = close_prices.iloc[-1]
            
            signals = []
            if current_price > sma_20:
                signals.append("Above 20-day SMA (Bullish)")
            else:
                signals.append("Below 20-day SMA (Bearish)")
            
            if current_price > sma_50:
                signals.append("Above 50-day SMA (Bullish)")
            else:
                signals.append("Below 50-day SMA (Bearish)")
            
            if rsi > 70:
                signals.append("RSI Overbought")
            elif rsi < 30:
                signals.append("RSI Oversold")
            else:
                signals.append("RSI Neutral")
            
            if macd_value > signal_value:
                signals.append("MACD Bullish Crossover")
            else:
                signals.append("MACD Bearish Crossover")
            
            return {
                "symbol": symbol.upper(),
                "current_price": round(current_price, 2),
                "sma_20": round(sma_20, 2),
                "sma_50": round(sma_50, 2),
                "sma_200": round(sma_200, 2) if sma_200 else None,
                "rsi": round(rsi, 2),
                "macd": round(macd_value, 2),
                "macd_signal": round(signal_value, 2),
                "signals": signals,
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    @staticmethod
    def search_stocks(query: str, limit: int = 10) -> List[Dict[str, str]]:
        """Search for stocks by name or symbol."""
        try:
            search_results = yf.Tickers(query)
            results = []
            
            common_stocks = [
                ("AAPL", "Apple Inc."),
                ("MSFT", "Microsoft Corporation"),
                ("GOOGL", "Alphabet Inc."),
                ("AMZN", "Amazon.com Inc."),
                ("NVDA", "NVIDIA Corporation"),
                ("META", "Meta Platforms Inc."),
                ("TSLA", "Tesla Inc."),
                ("JPM", "JPMorgan Chase & Co."),
                ("V", "Visa Inc."),
                ("JNJ", "Johnson & Johnson"),
            ]
            
            query_upper = query.upper()
            for symbol, name in common_stocks:
                if query_upper in symbol or query.lower() in name.lower():
                    results.append({"symbol": symbol, "name": name})
            
            return results[:limit]
        except Exception as e:
            return [{"error": str(e)}]


mcp_tools = MCPStockTools()

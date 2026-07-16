"""Stock price tool using Alpha Vantage."""
import os
import requests
from langchain_core.tools import tool

# Read from env — falls back to the shared demo key
_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "6G1UIJIXT1599U9K")


@tool
def get_stock_price(symbol: str) -> dict:
    """Fetch the latest stock price for a given ticker symbol (e.g. 'AAPL', 'TSLA', 'GOOGL').
    Use this when the user asks about a stock price or share price.
    """
    try:
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey={_API_KEY}"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data  = response.json()
        quote = data.get("Global Quote", {})

        if not quote:
            return {"error": f"No data found for symbol '{symbol}'. Check the ticker and try again."}

        return {
            "symbol":             quote.get("01. symbol"),
            "price":              quote.get("05. price"),
            "change":             quote.get("09. change"),
            "change_percent":     quote.get("10. change percent"),
            "volume":             quote.get("06. volume"),
            "latest_trading_day": quote.get("07. latest trading day"),
        }
    except Exception as e:
        return {"error": str(e)}

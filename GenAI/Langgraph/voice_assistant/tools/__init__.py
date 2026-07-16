"""Tool registry.

To add a new tool:
  1. Create a file in this directory (e.g. tools/weather.py).
  2. Define a function decorated with @tool from langchain_core.tools.
  3. Import it below and append it to the TOOLS list.
"""
from datetime import datetime
from langchain_core.tools import tool

from tools.search import search_web
from tools.calculator import calculator
from tools.stock import get_stock_price
from tools.youtube import youtube_search, youtube_play


# ---------------------------------------------------------------------------
# Built-in utility tools
# ---------------------------------------------------------------------------

@tool
def get_current_time(dummy: str = "") -> str:
    """Returns the current date and time. Use when the user asks what time or date it is."""
    return datetime.now().strftime("%A, %B %d %Y at %I:%M %p")


# ---------------------------------------------------------------------------
# TOOLS list — everything here is automatically bound to the LLM.
# Add or remove tools here without touching any other file.
# ---------------------------------------------------------------------------
TOOLS: list = [
    get_current_time,
    search_web,
    calculator,
    get_stock_price,
    youtube_search,
    youtube_play,
]

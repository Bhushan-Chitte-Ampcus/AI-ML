"""Web search tool using DuckDuckGo (no API key required)."""
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

_search = DuckDuckGoSearchRun(region="us-en")


@tool
def search_web(query: str) -> str:
    """Search the web using DuckDuckGo and return a concise summary.
    Use this when the user asks about current events, news, or any
    topic that may require up-to-date information.
    """

    # """
    # Search the web using DuckDuckGo.

    # Use this tool for:
    # - Current events
    # - Latest news
    # - Weather
    # - Sports scores
    # - Recent technologies
    # - Information not likely contained in the LLM's training data

    # Input:
    #     A search query.

    # Returns:
    #     Search results as text.
    # """
    try:
        return _search.run(query)
    except Exception as e:
        return f"Search failed: {e}"

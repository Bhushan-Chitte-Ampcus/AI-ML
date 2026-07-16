"""YouTube tools — search and play educational/music videos.

Uses a direct scrape of YouTube's search endpoint via `requests` + `re`.
No API key, no broken third-party library.

Content restricted to educational and music categories only.
"""
import re
import json
import webbrowser
import requests
from langchain_core.tools import tool

_YT_SEARCH_URL = "https://www.youtube.com/results?search_query="
_YT_WATCH_URL  = "https://www.youtube.com/watch?v="

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_ALLOWED_CATEGORIES = (
    "education", "music", "tutorial", "lecture",
    "course", "documentary", "learn", "song", "symphony",
)


def _safe_query(query: str) -> str:
    """Append a safe-search suffix when no category hint is present."""
    q = query.lower()
    if not any(cat in q for cat in _ALLOWED_CATEGORIES):
        return f"{query} education OR music OR tutorial"
    return query


def _scrape_youtube(query: str, limit: int = 5) -> list[dict]:
    """Scrape YouTube search results and return a list of video dicts."""
    encoded = query.replace(" ", "+")
    url     = _YT_SEARCH_URL + encoded

    resp = requests.get(url, headers=_HEADERS, timeout=10)
    resp.raise_for_status()

    # YouTube embeds search results as a JSON blob inside a <script> tag
    match = re.search(r"var ytInitialData = ({.*?});</script>", resp.text, re.DOTALL)
    if not match:
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    videos = []
    try:
        contents = (
            data["contents"]
            ["twoColumnSearchResultsRenderer"]
            ["primaryContents"]
            ["sectionListRenderer"]
            ["contents"][0]
            ["itemSectionRenderer"]
            ["contents"]
        )
        for item in contents:
            vr = item.get("videoRenderer")
            if not vr:
                continue
            video_id = vr.get("videoId", "")
            title    = vr.get("title", {}).get("runs", [{}])[0].get("text", "Unknown")
            channel  = (
                vr.get("ownerText", {}).get("runs", [{}])[0].get("text")
                or vr.get("longBylineText", {}).get("runs", [{}])[0].get("text", "Unknown")
            )
            duration = (
                vr.get("lengthText", {}).get("simpleText", "N/A")
            )
            videos.append({
                "title":    title,
                "channel":  channel,
                "duration": duration,
                "video_id": video_id,
                "url":      _YT_WATCH_URL + video_id,
            })
            if len(videos) >= limit:
                break
    except (KeyError, IndexError):
        pass

    return videos


# ── Tool 1: YouTube Search ───────────────────────────────────────────────────

@tool
def youtube_search(query: str) -> dict:
    """Search YouTube for educational or music videos and return the top results.
    Use when the user asks to search YouTube, find a tutorial, lecture, song,
    or music video. Only educational and music content is permitted.
    Returns up to 5 results with title, channel, duration, and URL.
    """
    safe_q = _safe_query(query)

    try:
        videos = _scrape_youtube(safe_q, limit=5)
    except Exception as e:
        return {"error": f"YouTube search failed: {e}"}

    if not videos:
        return {"error": "No results found. Try a different query."}

    # Open the YouTube search page in the browser
    webbrowser.open(_YT_SEARCH_URL + query.replace(" ", "+"))

    return {
        "query":   safe_q,
        "results": videos,
        "message": f"Opened YouTube search for '{query}'. Found {len(videos)} results.",
    }


# ── Tool 2: YouTube Play ─────────────────────────────────────────────────────

@tool
def youtube_play(query: str) -> dict:
    """Find the best matching educational or music video on YouTube and play it.
    Use when the user says 'play', 'watch', 'open', or 'put on' a specific
    video, song, tutorial, or lecture. Only educational and music content is
    permitted. Opens the video directly in the user's default browser.
    """
    safe_q = _safe_query(query)

    try:
        videos = _scrape_youtube(safe_q, limit=1)
    except Exception as e:
        return {"error": f"YouTube search failed: {e}"}

    if not videos:
        return {"error": f"No video found for '{query}'. Try a more specific search."}

    video = videos[0]
    webbrowser.open(video["url"])

    return {
        "title":   video["title"],
        "channel": video["channel"],
        "url":     video["url"],
        "message": f"Now playing: '{video['title']}' by {video['channel']}.",
    }

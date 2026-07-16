"""In-memory session store.

Keeps per-session conversation history so multi-turn dialogue works correctly.
For production, swap the dict for Redis or a database-backed store.
"""
from langchain_core.messages import BaseMessage

# session_id → ordered list of LangChain messages
_store: dict[str, list[BaseMessage]] = {}


def get_history(session_id: str) -> list[BaseMessage]:
    """Return all messages for the given session (empty list if new)."""
    return _store.get(session_id, [])


def set_history(session_id: str, messages: list[BaseMessage]) -> None:
    """Persist the full updated message list for a session."""
    _store[session_id] = messages


def clear_history(session_id: str) -> None:
    """Delete all history for a session."""
    _store.pop(session_id, None)

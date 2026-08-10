"""Shared state definition for the voice assistant graph."""
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AssistantState(TypedDict):
    """State that flows through every node in the graph.

    messages:  full conversation history (human + AI turns).
               The ``add_messages`` reducer appends rather than replaces.
    user_name: optional name of the logged-in user, injected into the
               system prompt so the LLM addresses them by name.
    """
    messages:  Annotated[list, add_messages]
    user_name: str

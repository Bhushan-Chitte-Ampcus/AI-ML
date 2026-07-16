"""Shared state definition for the voice assistant graph."""
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AssistantState(TypedDict):
    """State that flows through every node in the graph.

    messages: full conversation history (human + AI turns).
              The ``add_messages`` reducer appends new messages rather than
              replacing the whole list, so history accumulates naturally.
    """
    messages: Annotated[list, add_messages]

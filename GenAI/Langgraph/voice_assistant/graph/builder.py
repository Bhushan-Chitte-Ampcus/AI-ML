"""Builds and compiles the LangGraph voice assistant graph.

Two compiled graphs are exported:

graph          — uses chatbot_node (ainvoke). Used by POST /api/chat.
graph_stream   — uses chatbot_node_stream (astream). Used by POST /api/chat/stream.
                 Enables per-token streaming via stream_mode='messages'.

Both graphs share the same topology and optional checkpointer.
"""
from langgraph.graph import StateGraph, START, END

from graph.state import AssistantState
from graph.nodes import chatbot_node, chatbot_node_stream, tool_node
from graph.edges import should_use_tool


def build_graph(checkpointer=None):
    """Standard graph — full response at once."""
    b = StateGraph(AssistantState)
    b.add_node("chatbot", chatbot_node)
    b.add_node("tools",   tool_node)
    b.add_edge(START, "chatbot")
    b.add_conditional_edges("chatbot", should_use_tool, {"tools": "tools", "end": END})
    b.add_edge("tools", "chatbot")
    return b.compile(checkpointer=checkpointer)


def build_graph_stream(checkpointer=None):
    """Streaming graph — per-token chunks flow through stream_mode='messages'."""
    b = StateGraph(AssistantState)
    b.add_node("chatbot", chatbot_node_stream)
    b.add_node("tools",   tool_node)
    b.add_edge(START, "chatbot")
    b.add_conditional_edges("chatbot", should_use_tool, {"tools": "tools", "end": END})
    b.add_edge("tools", "chatbot")
    return b.compile(checkpointer=checkpointer)


# Stateless singletons — replaced with DB-backed versions in db.py setup
graph        = build_graph()
graph_stream = build_graph_stream()

"""Graph nodes for the voice assistant.

Node design
-----------
Two chatbot nodes are provided:

chatbot_node        — used by the standard (non-streaming) graph.
                      Calls ainvoke, returns the full AIMessage at once.

chatbot_node_stream — used by the streaming graph.
                      Calls astream on the LLM so per-token chunks flow
                      through LangGraph's stream_mode='messages' pipeline.

Both share the same LLM instances, trimming logic, and error handling.

History trimming
----------------
Trims to MAX_HISTORY_MESSAGES before every LLM call to stay within
the 8192-token context window of the tool-use model.

Resilience
----------
If Groq returns BadRequestError / tool_use_failed, falls back to the
plain LLM (no tools) so the user always gets a reply.
"""
from __future__ import annotations

from functools import lru_cache

from langchain_core.messages import (
    SystemMessage, AIMessage, AIMessageChunk,
    ToolMessage, HumanMessage, BaseMessage
)
from langchain_groq import ChatGroq
from groq import BadRequestError
from langgraph.prebuilt import ToolNode

from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT, MAX_HISTORY_MESSAGES
from tools import TOOLS
from graph.state import AssistantState


# Pre-built LangGraph node that executes any tool the LLM requests
tool_node = ToolNode(TOOLS)


@lru_cache(maxsize=1)
def _get_llm_with_tools():
    llm = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0)
    return llm.bind_tools(TOOLS, tool_choice="auto") if TOOLS else llm


@lru_cache(maxsize=1)
def _get_llm_plain():
    return ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0)


def _trim_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    """Trim to MAX_HISTORY_MESSAGES, always starting with a HumanMessage."""
    if len(messages) <= MAX_HISTORY_MESSAGES:
        return messages
    trimmed = messages[-MAX_HISTORY_MESSAGES:]
    for i, msg in enumerate(trimmed):
        if isinstance(msg, HumanMessage):
            return trimmed[i:]
    return messages[-2:] if len(messages) >= 2 else messages


def _build_messages(state: AssistantState) -> list[BaseMessage]:
    # Personalise the system prompt with the user's name if available
    name = state.get("user_name", "").strip()
    if name:
        personal_prompt = (
            f"{SYSTEM_PROMPT} "
            f"The user's name is {name} — address them by name occasionally to be friendly."
        )
    else:
        personal_prompt = SYSTEM_PROMPT
    return [SystemMessage(content=personal_prompt)] + _trim_messages(state["messages"])


# ── Standard node (ainvoke — full response at once) ──────────────────────────

async def chatbot_node(state: AssistantState) -> dict:
    """Non-streaming chatbot node used by the standard graph."""
    messages = _build_messages(state)
    try:
        response = await _get_llm_with_tools().ainvoke(messages)
        return {"messages": [response]}
    except BadRequestError as e:
        if "tool_use_failed" not in str(e) and "failed_generation" not in str(e):
            raise
    # Fallback — no tools
    fallback = messages + [SystemMessage(content=(
        "Note: tool calling is temporarily unavailable. "
        "Answer from your own knowledge as best you can."
    ))]
    try:
        response = await _get_llm_plain().ainvoke(fallback)
    except Exception:
        response = AIMessage(content="I'm sorry, I ran into a problem. Please try again.")
    return {"messages": [response]}


# ── Streaming node (async generator — per-token chunks) ──────────────────────

async def chatbot_node_stream(state: AssistantState):
    """Streaming chatbot node — async generator that yields AIMessageChunks.

    LangGraph detects async generator nodes and pipes their yielded values
    through stream_mode='messages', enabling per-token SSE on the frontend.

    Falls back to the plain LLM (no tools) if Groq raises BadRequestError.
    """
    messages = _build_messages(state)
    chunks: list[AIMessageChunk] = []

    try:
        async for chunk in _get_llm_with_tools().astream(messages):
            chunks.append(chunk)
            yield {"messages": [chunk]}     # stream each token to the frontend

        # Also return the full merged message for state persistence
        if chunks:
            full: AIMessage = chunks[0]
            for c in chunks[1:]:
                full = full + c
            yield {"messages": [full]}
        return

    except BadRequestError as e:
        if "tool_use_failed" not in str(e) and "failed_generation" not in str(e):
            raise

    # Fallback — no tools, still streaming
    fallback = messages + [SystemMessage(content=(
        "Note: tool calling is temporarily unavailable. "
        "Answer from your own knowledge as best you can."
    ))]
    chunks = []
    try:
        async for chunk in _get_llm_plain().astream(fallback):
            chunks.append(chunk)
            yield {"messages": [chunk]}
        if chunks:
            full = chunks[0]
            for c in chunks[1:]:
                full = full + c
            yield {"messages": [full]}
    except Exception:
        yield {"messages": [AIMessage(content="I'm sorry, I ran into a problem. Please try again.")]}

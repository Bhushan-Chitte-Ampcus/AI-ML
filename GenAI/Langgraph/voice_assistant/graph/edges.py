"""Conditional edge logic for the voice assistant graph."""
from langchain_core.messages import AIMessage
from graph.state import AssistantState


def should_use_tool(state: AssistantState) -> str:
    """Route to tool execution or END.

    If the last AI message contains tool calls, route to the 'tools' node.
    Otherwise the conversation turn is complete — route to END.
    """
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "end"

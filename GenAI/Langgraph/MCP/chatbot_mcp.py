import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langgraph.graph import StateGraph, START
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

import os
import requests
import sys

if sys.platform.startswith("win"):
    # Only apply this fix when running on Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


load_dotenv()

llm = ChatGroq(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("LLM_API_KEY")
)

# MCP Client for local FastMCP server
mcp_script = os.path.join(os.path.dirname(__file__), "main.py")

client = MultiServerMCPClient(
    {
        "arith": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [mcp_script],
        },
        "expense": {
            "transport": "streamable_http",
            "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
        }
    }
)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

async def build_graph():

    tools = await client.get_tools()

    llm_with_tools = llm.bind_tools(tools)

    async def chat_node(state : ChatState):
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages":[response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")

    chatbot = graph.compile()

    return chatbot

async def main():
    chatbot= await build_graph()

    # result = await chatbot.ainvoke({"messages": [HumanMessage(content="Find the modulus of 132354 and 23 and give answer like a cricket commentator.")]})
    result = await chatbot.ainvoke({"messages": [HumanMessage(content="Add an expense - Rs 500 for campusX course on 9th July 2026")]})
    # result = await chatbot.ainvoke({"messages": [HumanMessage(content="can you 10, 20, 50")]})

    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
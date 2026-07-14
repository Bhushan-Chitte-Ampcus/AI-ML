# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from typing import TypedDict, Annotated
# from langchain_core.messages import BaseMessage
# from langchain_groq import ChatGroq
# from dotenv import load_dotenv
# import os
# from langgraph.checkpoint.memory import InMemorySaver

# load_dotenv()

# llm = ChatGroq(
#     model=os.getenv("LLM_MODEL"),
#     temperature=0.7,
#     api_key=os.getenv("LLM_API_KEY")
# )

# class ChatState(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]

# def chat_node(state: ChatState):
#     # take user query from state
#     messages = state["messages"]

#     # send to llm
#     response = llm.invoke(messages)

#     # response store to state
#     return {"messages" : [response]}    

# checkpointer = InMemorySaver()

# graph = StateGraph(ChatState)

# graph.add_node("chat_node", chat_node)

# graph.add_edge(START, "chat_node")
# graph.add_edge("chat_node", END)

# chatbot = graph.compile(checkpointer=checkpointer)

# ============================================================================================================

# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from typing import TypedDict, Annotated
# from langchain_core.messages import BaseMessage
# from langchain_groq import ChatGroq


# from dotenv import load_dotenv
# import os
# from langgraph.checkpoint.sqlite import SqliteSaver
# import sqlite3
# import asyncio
# import sys
# import logging
# import warnings
# import io
# from contextlib import redirect_stderr

# # Fix Windows asyncio ConnectionResetError
# if sys.platform == 'win32':
#     # Use ProactorEventLoop but suppress connection errors
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# # Suppress asyncio connection errors completely
# logging.getLogger('asyncio').setLevel(logging.CRITICAL)
# warnings.filterwarnings('ignore', message='.*10054.*')
# warnings.filterwarnings('ignore', category=RuntimeWarning)

# load_dotenv()

# llm = ChatGroq(
#     model=os.getenv("LLM_MODEL"),
#     temperature=0.7,
#     api_key=os.getenv("LLM_API_KEY"),
#     request_timeout=30  # 30 second timeout for API requests
# )

# class ChatState(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]

# def chat_node(state: ChatState) -> dict:
#     """Chat node that processes messages and returns LLM response.
    
#     Args:
#         state: ChatState containing list of messages
        
#     Returns:
#         Dictionary with LLM response message
        
#     Raises:
#         Exception: If LLM API call fails
#     """
#     try:
#         messages = state["messages"]
#         response = llm.invoke(messages)
#         return {"messages": [response]}
#     except Exception as e:
#         raise RuntimeError(f"Chat node error: {str(e)}") from e    

# conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
# checkpointer = SqliteSaver(conn=conn)

# graph = StateGraph(ChatState)

# graph.add_node("chat_node", chat_node)

# graph.add_edge(START, "chat_node")
# graph.add_edge("chat_node", END)

# chatbot = graph.compile(checkpointer=checkpointer)

# def retrieve_all_threads() -> list:
#     """Retrieve all conversation thread IDs from the database.
    
#     Returns:
#         List of thread ID strings
        
#     Raises:
#         Exception: If there's an error querying the checkpoint store
#     """
#     try:
#         all_threads = set()
#         for checkpoint in checkpointer.list(None):
#             if checkpoint and checkpoint.config and "configurable" in checkpoint.config:
#                 thread_id = checkpoint.config["configurable"].get("thread_id")
#                 if thread_id:
#                     all_threads.add(thread_id)
#         return list(all_threads)
#     except Exception as e:
#         print(f"Error retrieving threads: {str(e)}")
#         return []

# ============================================================================================================

# from langgraph.graph import StateGraph, START, END
# # StateGraph  -> core class for building a graph of nodes that share a common state object
# # START, END  -> special sentinel nodes marking the entry point and exit point of the graph

# from typing import TypedDict, Annotated
# # TypedDict  -> lets us define a dict with a fixed, typed schema (used for our graph's state)
# # Annotated  -> lets us attach extra metadata to a type hint (here: how to merge updates to a field)

# from langchain_core.messages import BaseMessage, HumanMessage
# # BaseMessage   -> parent class for all message types (HumanMessage, AIMessage, ToolMessage, SystemMessage)
# # HumanMessage  -> wraps user input specifically

# from langchain_groq import ChatGroq
# # ChatGroq -> LangChain's chat model wrapper for Groq's API, gives a unified .invoke()/.stream() interface

# from langgraph.checkpoint.sqlite import SqliteSaver
# # SqliteSaver -> checkpointer implementation that persists graph state to SQLite after every step,
# #                keyed by thread_id -> this is what enables memory across sessions/reruns

# from langgraph.graph.message import add_messages
# # add_messages -> special reducer function; instead of overwriting the "messages" state field,
# #                 it APPENDS new messages to the existing list (and dedupes by message id)

# from langgraph.prebuilt import ToolNode, tools_condition
# # ToolNode        -> prebuilt node that auto-executes whatever tool(s) the LLM requested
# # tools_condition -> prebuilt router function; checks if the last AI message contains tool calls

# from langchain_community.tools import DuckDuckGoSearchRun
# # DuckDuckGoSearchRun -> ready-made web search tool

# from langchain_core.tools import tool
# # tool -> decorator used to turn any plain Python function into a LangChain-compatible tool

# from dotenv import load_dotenv
# # load_dotenv -> loads variables from a .env file into the environment

# import sqlite3
# # sqlite3 -> used to open the raw DB connection for the checkpointer

# import requests
# # requests -> used to call the Alpha Vantage stock price API

# import os
# # os -> used to read environment variables (API keys, model name, etc.)

# load_dotenv()
# # Actually loads the .env file now, so os.getenv(...) calls below can read
# # LLM_MODEL, LLM_API_KEY, ALPHA_VANTAGE_API_KEY

# # --------------------------------------------------------------------------------
# # WINDOWS EVENT LOOP FIX
# # --------------------------------------------------------------------------------

# import asyncio
# import sys

# if sys.platform.startswith("win"):
#     # Only apply this fix when running on Windows
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     # Forces asyncio to use the Selector event loop instead of the default Proactor loop.
#     # This avoids the noisy "ConnectionResetError: WinError 10054" seen with async HTTP
#     # clients on Windows, since Selector doesn't use the IOCP-based transport that throws
#     # those errors on abrupt socket closes.

# # --------------------------------------------------------------------------------

# # ============================================================
# # 1. LLM
# # ============================================================

# llm = ChatGroq(
#     model = os.getenv("LLM_MODEL"),     # model name pulled from .env (e.g. "llama-3.3-70b-versatile")
#     api_key = os.getenv("LLM_API_KEY")  # Groq API key pulled from .env, not hardcoded (avoids leaking secrets)
# )
# # Instantiates the chat model client used throughout the graph

# # ============================================================
# # 2. TOOLS
# # ============================================================

# # ---------------- Tool 1: Web search ----------------
# search_tool = DuckDuckGoSearchRun(region="us-en")
# # Creates a search tool instance scoped to US-English results.
# # LangChain auto-generates this tool's name/description metadata from the class,
# # which the LLM reads when deciding whether to call it.

# # ---------------- Tool 2: Calculator ----------------
# @tool
# # The @tool decorator inspects this function's signature and docstring to build a tool
# # schema (name, argument types, description) that gets sent to the LLM's tool-calling API.
# def calculator(first_num: float, second_num: float, operation: str) -> dict:
#     """
#     Perform a basic arithmetic operation on two numbers.
#     Supported operations: add, sub, mul, div
#     """
#     # NOTE: This docstring isn't just documentation -- it's what the model reads to decide
#     # WHEN and HOW to call this tool, so its wording actually matters.

#     try:
#         if operation == "add":
#             result = first_num + second_num          # simple addition
#         elif operation == "sub":
#             result = first_num - second_num          # simple subtraction
#         elif operation == "mul":
#             result = first_num * second_num          # simple multiplication
#         elif operation == "div":
#             if second_num == 0:
#                 return {"error":"Division by zero is not allowed"}  # explicit guard against ZeroDivisionError
#             result = first_num / second_num           # division, only reached if second_num != 0
#         else:
#             return {"error":f"Unsupported operation '{operation}'"}  # handles unknown operation strings

#         return {"first_num":first_num, "second_num":second_num, "operation":operation, "result":result}
#         # Returns a dict echoing the inputs plus the result -- this dict becomes the content
#         # of a ToolMessage that the LLM reads to formulate its final answer

#     except Exception as e:
#         return {"error":str(e)}
#         # Catch-all for anything unexpected (e.g. bad types passed by the LLM)

# # ---------------- Tool 3: Stock price lookup ----------------
# @tool
# def get_stock_price(symbol:str) -> dict:
#     """
#     Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
#     using Alpha Vantage with API key in the URL.
#     """

#     url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={os.getenv('ALPHA_VANTAGE_API_KEY')}"
#     # Builds a GET request URL for Alpha Vantage's GLOBAL_QUOTE endpoint,
#     # interpolating the requested symbol and the API key from .env

#     r = requests.get(url)
#     # Fires the HTTP GET request synchronously (no error handling / timeout here --
#     # if Alpha Vantage rate-limits you, r.json() will just return their error/note payload)

#     return r.json()
#     # Returns the raw parsed JSON straight back to the LLM as the tool result

# # ---------------- Combine tools + bind to LLM ----------------
# tools = [search_tool, get_stock_price, calculator]
# # Bundles all three tools into a single list for registration

# llm_with_tools = llm.bind_tools(tools)
# # Attaches the tools' schemas to the LLM so every future .invoke() call includes
# # these tool definitions in the request -- this is what enables Groq's model to
# # emit structured tool-call requests instead of only plain text

# # ============================================================
# # 3. STATE
# # ============================================================

# class ChatState(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]
#     # Defines the graph's shared state as a single field: "messages", a list of BaseMessage objects.
#     # Annotated[..., add_messages] tells LangGraph: whenever a node returns {"messages": [...]},
#     # don't replace the whole list -- APPEND the new message(s) to what's already there.

# # ============================================================
# # 4. NODES
# # ============================================================

# def chat_node(state: ChatState):
#     """LLM node that may answer or request a tool call."""
#     messages = state["messages"]
#     # Pulls the full message history out of the current state

#     response = llm_with_tools.invoke(messages)
#     # Passes the entire history to the tool-bound LLM; response is an AIMessage that
#     # either contains a plain text answer OR a tool-call request (same message type,
#     # different fields populated)

#     return {"messages":[response]}
#     # Returns the new message wrapped in a dict matching the state schema --
#     # LangGraph merges this in via the add_messages reducer (i.e. appends, doesn't overwrite)

# tool_node = ToolNode(tools)
# # Prebuilt node (no need to hand-write it): when run, it looks at the most recent
# # AIMessage.tool_calls, calls the matching Python function(s) with the LLM-provided
# # arguments, and returns the results as ToolMessage objects

# # ============================================================
# # 5. CHECKPOINTER
# # ============================================================

# conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
# # Opens a raw SQLite connection to chatbot.db (created if it doesn't exist).
# # check_same_thread=False is required because Streamlit/LangGraph may access this
# # connection from a different thread than the one that created it -- SQLite normally
# # forbids that by default.

# checkpointer = SqliteSaver(conn=conn)
# # Wraps the raw connection so LangGraph can persist/restore graph state per thread_id automatically

# # ============================================================
# # 6. GRAPH
# # ============================================================

# graph = StateGraph(ChatState)
# # Instantiates the graph using our state schema

# graph.add_node("chat_node", chat_node)
# # Registers chat_node under the string name "chat_node" for use in edges

# graph.add_node("tools", tool_node)
# # Registers tool_node under the string name "tools" (LangGraph's prebuilt convention
# # expects this exact name to pair with tools_condition)

# graph.add_edge(START, "chat_node")
# # Every run starts by going straight to chat_node

# graph.add_conditional_edges("chat_node", tools_condition)
# # After chat_node runs, tools_condition inspects its output:
# #   - if the AIMessage has tool_calls -> routes to the node named "tools"
# #   - otherwise -> routes to END

# graph.add_edge("tools", "chat_node")
# # After tools execute, control always goes back to chat_node so the LLM can see
# # the tool results and respond -- this closes the ReAct-style loop
# # (LLM -> tool -> LLM -> ... -> final answer)

# chatbot = graph.compile(checkpointer=checkpointer)
# # Compiles the graph into a runnable object, wiring in the checkpointer so every
# # step's state gets persisted to chatbot.db. This "chatbot" object is what the
# # frontend imports and calls .stream() / .get_state() on.

# # ============================================================
# # 7. HELPER
# # ============================================================

# def retrieve_all_threads():
#     all_threads = set()
#     # Using a set to automatically dedupe thread_ids (each thread has multiple
#     # checkpoints -- one per graph step -- so the same thread_id appears many times)

#     for checkpoint in checkpointer.list(None):
#         # checkpointer.list(None) iterates over EVERY saved checkpoint across ALL
#         # threads in the SQLite DB (None = no filter applied)

#         all_threads.add(checkpoint.config["configurable"]["thread_id"])
#         # Pulls the thread_id out of each checkpoint's config and adds it to the set

#     return list(all_threads)
#     # Returns the unique thread IDs as a list -- this powers the Streamlit sidebar's
#     # conversation list. NOTE: set ordering is not guaranteed to reflect recency.

# =====================================================================================================================================

## MCP Integration


from langgraph.graph import StateGraph, START, END
# StateGraph  -> core class for building a graph of nodes that share a common state object
# START, END  -> special sentinel nodes marking the entry point and exit point of the graph

from typing import TypedDict, Annotated
# TypedDict  -> lets us define a dict with a fixed, typed schema (used for our graph's state)
# Annotated  -> lets us attach extra metadata to a type hint (here: how to merge updates to a field)

from langchain_core.messages import BaseMessage, HumanMessage
# BaseMessage   -> parent class for all message types (HumanMessage, AIMessage, ToolMessage, SystemMessage)
# HumanMessage  -> wraps user input specifically

from langchain_groq import ChatGroq
# ChatGroq -> LangChain's chat model wrapper for Groq's API, gives a unified .invoke()/.stream() interface

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
# SqliteSaver -> checkpointer implementation that persists graph state to SQLite after every step,
#                keyed by thread_id -> this is what enables memory across sessions/reruns

from langgraph.graph.message import add_messages
# add_messages -> special reducer function; instead of overwriting the "messages" state field,
#                 it APPENDS new messages to the existing list (and dedupes by message id)

from langgraph.prebuilt import ToolNode, tools_condition
# ToolNode        -> prebuilt node that auto-executes whatever tool(s) the LLM requested
# tools_condition -> prebuilt router function; checks if the last AI message contains tool calls

from langchain_community.tools import DuckDuckGoSearchRun
# DuckDuckGoSearchRun -> ready-made web search tool

from langchain_core.tools import tool, BaseTool
# tool -> decorator used to turn any plain Python function into a LangChain-compatible tool

from dotenv import load_dotenv
# load_dotenv -> loads variables from a .env file into the environment

import sqlite3
# sqlite3 -> used to open the raw DB connection for the checkpointer

import requests
# requests -> used to call the Alpha Vantage stock price API

import os
# os -> used to read environment variables (API keys, model name, etc.)

from langchain_mcp_adapters.client import MultiServerMCPClient
import aiosqlite
import threading

load_dotenv()
# Actually loads the .env file now, so os.getenv(...) calls below can read
# LLM_MODEL, LLM_API_KEY, ALPHA_VANTAGE_API_KEY

# --------------------------------------------------------------------------------
# WINDOWS EVENT LOOP FIX
# --------------------------------------------------------------------------------

import asyncio
import sys

if sys.platform.startswith("win"):
    # Only apply this fix when running on Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # Forces asyncio to use the Selector event loop instead of the default Proactor loop.
    # This avoids the noisy "ConnectionResetError: WinError 10054" seen with async HTTP
    # clients on Windows, since Selector doesn't use the IOCP-based transport that throws
    # those errors on abrupt socket closes.

# --------------------------------------------------------------------------------

# Dedicated async loop for backend tasks
_ASYNC_LOOP = asyncio.new_event_loop()
_ASYNC_THREAD = threading.Thread(target=_ASYNC_LOOP.run_forever, daemon=True)
_ASYNC_THREAD.start()

def _submit_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, _ASYNC_LOOP)

def run_async(coro):
    return _submit_async(coro).result()

def submit_async_task(coro):
    """Schedule a coroutine on the backend event loop."""
    return _submit_async(coro)

# ============================================================
# 1. LLM
# ============================================================

llm = ChatGroq(
    model = os.getenv("LLM_MODEL"),     # model name pulled from .env (e.g. "llama-3.3-70b-versatile")
    api_key = os.getenv("LLM_API_KEY")  # Groq API key pulled from .env, not hardcoded (avoids leaking secrets)
)
# Instantiates the chat model client used throughout the graph

# ============================================================
# 2. TOOLS
# ============================================================

# ---------------- Tool 1: Web search ----------------
search_tool = DuckDuckGoSearchRun(region="us-en")
# Creates a search tool instance scoped to US-English results.
# LangChain auto-generates this tool's name/description metadata from the class,
# which the LLM reads when deciding whether to call it.

# ---------------- Tool 3: Stock price lookup ----------------
@tool
def get_stock_price(symbol:str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
    using Alpha Vantage with API key in the URL.
    """

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={os.getenv('ALPHA_VANTAGE_API_KEY')}"
    # Builds a GET request URL for Alpha Vantage's GLOBAL_QUOTE endpoint,
    # interpolating the requested symbol and the API key from .env

    r = requests.get(url)
    # Fires the HTTP GET request synchronously (no error handling / timeout here --
    # if Alpha Vantage rate-limits you, r.json() will just return their error/note payload)

    return r.json()
    # Returns the raw parsed JSON straight back to the LLM as the tool result


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

def load_mcp_tools() -> list[BaseTool]:
    try:
        return run_async(client.get_tools())
    except Exception:
        return []

mcp_tools = load_mcp_tools()

# ---------------- Combine tools + bind to LLM ----------------
tools = [search_tool, get_stock_price, *mcp_tools]
# Bundles all three tools into a single list for registration

llm_with_tools = llm.bind_tools(tools) if tools else llm
# Attaches the tools' schemas to the LLM so every future .invoke() call includes
# these tool definitions in the request -- this is what enables Groq's model to
# emit structured tool-call requests instead of only plain text

# ============================================================
# 3. STATE
# ============================================================

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # Defines the graph's shared state as a single field: "messages", a list of BaseMessage objects.
    # Annotated[..., add_messages] tells LangGraph: whenever a node returns {"messages": [...]},
    # don't replace the whole list -- APPEND the new message(s) to what's already there.

# ============================================================
# 4. NODES
# ============================================================

async def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]
    # Pulls the full message history out of the current state

    response = await llm_with_tools.ainvoke(messages)
    # Passes the entire history to the tool-bound LLM; response is an AIMessage that
    # either contains a plain text answer OR a tool-call request (same message type,
    # different fields populated)

    return {"messages":[response]}
    # Returns the new message wrapped in a dict matching the state schema --
    # LangGraph merges this in via the add_messages reducer (i.e. appends, doesn't overwrite)

tool_node = ToolNode(tools) if tools else None
# Prebuilt node (no need to hand-write it): when run, it looks at the most recent
# AIMessage.tool_calls, calls the matching Python function(s) with the LLM-provided
# arguments, and returns the results as ToolMessage objects

# ============================================================
# 5. CHECKPOINTER
# ============================================================

async def _init_checkpointer():
    conn = await aiosqlite.connect(database="chatbot.db")
    return AsyncSqliteSaver(conn)

checkpointer = run_async(_init_checkpointer())

# -------------------
# 6. Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")

if tool_node:
    graph.add_node("tools", tool_node)
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")
else:
    graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper
# -------------------
async def _alist_threads():
    all_threads = set()
    async for checkpoint in checkpointer.alist(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)


def retrieve_all_threads():
    return run_async(_alist_threads())
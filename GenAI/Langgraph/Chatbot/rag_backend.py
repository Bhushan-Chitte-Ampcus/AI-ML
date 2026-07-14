from __future__ import annotations

import asyncio
import platform

# Windows: use SelectorEventLoop to avoid harmless ConnectionResetError noise
# from ProactorEventLoop during shutdown (well-known CPython/asyncio quirk).
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    from asyncio.proactor_events import _ProactorBasePipeTransport
    from functools import wraps

    def _silence_event_loop_closed(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except ConnectionResetError:
                pass
        return wrapper

    _ProactorBasePipeTransport.__del__ = _silence_event_loop_closed(
        _ProactorBasePipeTransport.__del__
    )


import os
import sqlite3
import tempfile
from typing import Annotated, Any, Dict, Optional, TypedDict

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import requests

load_dotenv()

# =============================================================================
# 1. LLM + Embeddings

llm = ChatGroq(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("LLM_API_KEY"),
)

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)
_EMBEDDINGS: Optional[HuggingFaceEmbeddings] = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    """Load the embedding model lazily and reuse a single cached instance."""
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        try:
            _EMBEDDINGS = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_NAME,
                model_kwargs={"device": "cpu"},
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load embedding model '{EMBEDDING_MODEL_NAME}': {exc}"
            ) from exc
    return _EMBEDDINGS


# =============================================================================
# 2. PDF retriever store

_THREAD_RETRIEVERS: Dict[str, Any] = {}
_THREAD_METADATA: Dict[str, dict] = {}


def _get_retriever(thread_id: Optional[str]):
    """Return the FAISS retriever for a thread, or None if not indexed."""
    if thread_id and str(thread_id) in _THREAD_RETRIEVERS:
        return _THREAD_RETRIEVERS[str(thread_id)]
    return None


def ingest_pdf(file_bytes: bytes, thread_id: str, filename: Optional[str] = None) -> dict:
    """
    Build a FAISS retriever for the uploaded PDF and store it for the thread.
    Returns a summary dict that can be surfaced in the UI.
    """
    if not file_bytes:
        raise ValueError("No bytes provided to ingest_pdf")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        temp_path = tmp.name

    try:
        docs = PyPDFLoader(temp_path).load()

        chunks = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
        ).split_documents(docs)

        retriever = FAISS.from_documents(chunks, _get_embeddings()).as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3},
        )

        display_name = filename or os.path.basename(temp_path)
        meta = {"filename": display_name, "documents": len(docs), "chunks": len(chunks)}

        _THREAD_RETRIEVERS[str(thread_id)] = retriever
        _THREAD_METADATA[str(thread_id)] = meta

        return meta

    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


# =============================================================================
# 3. Tools

search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed."}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation: {operation}"}
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
    using Alpha Vantage.
    """
    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey={os.getenv('ALPHA_VANTAGE_API_KEY')}"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch stock price for {symbol}: {e}"}


@tool
def rag_tool(query: str, config: RunnableConfig) -> dict:
    """
    Retrieve relevant information from the uploaded PDF for this chat thread.
    """
    # config is injected by LangGraph at runtime and stripped from the LLM schema.
    thread_id = config.get("configurable", {}).get("thread_id") if config else None
    retriever = _get_retriever(thread_id)

    if retriever is None:
        return {"error": "No document indexed for this chat. Upload a PDF first.", "query": query}

    docs = retriever.invoke(query)

    # Truncate chunks to keep tool response within Groq's function-calling token limit.
    MAX_CHUNK_CHARS = 600
    combined_context = "\n\n---\n\n".join(doc.page_content[:MAX_CHUNK_CHARS] for doc in docs)
    metadata = [{"page": doc.metadata.get("page"), "source": doc.metadata.get("source")} for doc in docs]

    return {
        "query": query,
        "context": combined_context,
        "num_chunks": len(docs),
        "metadata": metadata,
        "source_file": _THREAD_METADATA.get(str(thread_id), {}).get("filename"),
    }


tools = [search_tool, get_stock_price, calculator, rag_tool]
llm_with_tools = llm.bind_tools(tools)

# =============================================================================
# 4. State

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# =============================================================================
# 5. Nodes

def chat_node(state: ChatState, config=None):
    """LLM node: may respond directly or request a tool call."""
    system_message = SystemMessage(
        content=(
            "You are a helpful assistant. For questions about the uploaded PDF, "
            "call the 'rag_tool'. You can also use the web search, stock price, "
            "and calculator tools when helpful. If 'rag_tool' reports that no "
            "document is indexed, ask the user to upload a PDF."
        )
    )
    response = llm_with_tools.invoke([system_message, *state["messages"]], config=config)
    return {"messages": [response]}


tool_node = ToolNode(tools)

# =============================================================================
# 6. Checkpointer

conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# =============================================================================
# 7. Graph

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)

# =============================================================================
# 8. Helpers

def retrieve_all_threads() -> list:
    """Return all thread IDs persisted in the SQLite checkpoint store."""
    return list({cp.config["configurable"]["thread_id"] for cp in checkpointer.list(None)})


def thread_document_metadata(thread_id: str) -> dict:
    """Return the PDF metadata dict for a thread, or {} if none uploaded."""
    return _THREAD_METADATA.get(str(thread_id), {})
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

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

llm = ChatGroq(
    model=os.getenv("LLM_MODEL"),
    temperature=0.7,
    api_key=os.getenv("LLM_API_KEY")
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState) -> dict:
    """Chat node that processes messages and returns LLM response.
    
    Args:
        state: ChatState containing list of messages
        
    Returns:
        Dictionary with LLM response message
    """
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}    

conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads() -> list:
    """Retrieve all conversation thread IDs from the database.
    
    Returns:
        List of thread ID strings
        
    Raises:
        Exception: If there's an error querying the checkpoint store
    """
    try:
        all_threads = set()
        for checkpoint in checkpointer.list(None):
            if checkpoint and checkpoint.config and "configurable" in checkpoint.config:
                thread_id = checkpoint.config["configurable"].get("thread_id")
                if thread_id:
                    all_threads.add(thread_id)
        return list(all_threads)
    except Exception as e:
        print(f"Error retrieving threads: {str(e)}")
        return []


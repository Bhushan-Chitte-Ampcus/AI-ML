# import streamlit as st
# from backend import chatbot
# from langchain_core.messages import HumanMessage

# CONFIG = {"configurable" : {"thread_id" : "thread-1"}}

# if "message_history" not in st.session_state:
#     st.session_state["message_history"] = []

# for message in st.session_state["message_history"]:
#     with st.chat_message(message["role"]):
#         st.text(message["content"])

# user_input = st.chat_input("Type here")

# if user_input:
#     st.session_state["message_history"].append({"role":"user", "content":user_input})
#     with st.chat_message("user"):
#         st.text(user_input)

#     with st.chat_message("assistant"):
#         ai_message = st.write_stream(
#             message_chunk.content for message_chunk, metadata in chatbot.stream(
#                 {"messages":[HumanMessage(content=user_input)]},
#                 config={"configurable":{"thread_id":"thread-1"}},
#                 stream_mode="messages"
#             )
#         )
#     st.session_state["message_history"].append({"role":"assistant", "content":ai_message})

# # =================================================================================================================================

# import streamlit as st
# from backend import chatbot
# from langchain_core.messages import HumanMessage
# import uuid
# from datetime import datetime

# # utility functions

# def generate_thread_id():
#     thread_id = str(uuid.uuid4())
#     return thread_id

# def format_thread_display(thread_id):
#     """Format thread ID for display - show first 8 chars + timestamp if available"""
#     return f"Chat {thread_id[:8]}..."

# def reset_chat():
#     thread_id = generate_thread_id()
#     st.session_state["thread_id"] = thread_id
#     add_thread(st.session_state["thread_id"])
#     st.session_state["message_history"] = []

# def add_thread(thread_id):
#     if thread_id not in st.session_state["chat_threads"]:
#         st.session_state["chat_threads"].append(thread_id)

# def load_conversation(thread_id):
#     """Load conversation history with error handling"""
#     try:
#         state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
#         return state.values.get("messages", [])
#     except Exception as e:
#         st.error(f"Error loading conversation: {str(e)}")
#         return []

# # session setup
# if "message_history" not in st.session_state:
#     st.session_state["message_history"] = []

# if "thread_id" not in st.session_state:
#     st.session_state["thread_id"] = generate_thread_id()

# if "chat_threads" not in st.session_state:
#     st.session_state["chat_threads"] = []

# add_thread(st.session_state["thread_id"])

# # sidebar UI
# st.sidebar.title("LangGraph Chatbot")

# if st.sidebar.button("➕ New Chat", use_container_width=True):
#     reset_chat()
#     st.rerun()

# st.sidebar.header("My Conversations")

# for thread_id in st.session_state["chat_threads"][::-1]:
#     col1, col2 = st.sidebar.columns([4, 1])
    
#     with col1:
#         if st.button(format_thread_display(thread_id), use_container_width=True, key=f"load_{thread_id}"):
#             st.session_state["thread_id"] = thread_id
            
#             with st.spinner("Loading conversation..."):
#                 messages = load_conversation(thread_id)

#                 temp_messages = []

#                 for msg in messages:
#                     if isinstance(msg, HumanMessage):
#                         role = "user"
#                     else:
#                         role = "assistant"

#                     temp_messages.append({"role": role, "content": msg.content})

#                 st.session_state["message_history"] = temp_messages
            
#             st.rerun()

# # main UI
# for message in st.session_state["message_history"]:
#     with st.chat_message(message["role"]):
#         st.write(message["content"])  # Use st.write() for better formatting

# user_input = st.chat_input("Type here")

# if user_input:
#     st.session_state["message_history"].append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.write(user_input)

#     CONFIG = {"configurable": {"thread_id": str(st.session_state["thread_id"])}}

#     try:
#         with st.chat_message("assistant"):
#             # Collect the full message content while streaming
#             ai_message_content = ""
#             message_placeholder = st.empty()
            
#             for message_chunk, metadata in chatbot.stream(
#                 {"messages": [HumanMessage(content=user_input)]},
#                 config=CONFIG,
#                 stream_mode="messages"
#             ):
#                 if hasattr(message_chunk, 'content'):
#                     ai_message_content += message_chunk.content
#                     message_placeholder.write(ai_message_content)
            
#             # Save the complete message to history
#             if ai_message_content:
#                 st.session_state["message_history"].append(
#                     {"role": "assistant", "content": ai_message_content}
#                 )
#     except Exception as e:
#         st.error(f"Error getting response from chatbot: {str(e)}")
#         # Remove the last user message if there was an error
#         if st.session_state["message_history"] and st.session_state["message_history"][-1]["role"] == "user":
#             st.session_state["message_history"].pop()


# =================================================================================================================================

# import streamlit as st
# from backend import chatbot, retrieve_all_threads
# from langchain_core.messages import HumanMessage
# import uuid
# import asyncio
# import sys
# import logging
# import warnings
# import io
# import contextlib

# # Suppress asyncio connection errors on Windows
# if sys.platform == 'win32':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# logging.getLogger('asyncio').setLevel(logging.CRITICAL)
# logging.getLogger('proactor_events').setLevel(logging.CRITICAL)
# warnings.filterwarnings('ignore', message='.*10054.*')
# warnings.filterwarnings('ignore', category=RuntimeWarning)

# # utility functions

# def generate_thread_id():
#     thread_id = str(uuid.uuid4())
#     return thread_id

# def format_thread_display(thread_id):
#     """Format thread ID for display - show first 8 chars + timestamp if available"""
#     return f"Chat {thread_id[:8]}..."

# def reset_chat():
#     thread_id = generate_thread_id()
#     st.session_state["thread_id"] = thread_id
#     add_thread(st.session_state["thread_id"])
#     st.session_state["message_history"] = []

# def add_thread(thread_id):
#     if thread_id not in st.session_state["chat_threads"]:
#         st.session_state["chat_threads"].append(thread_id)

# def load_conversation(thread_id):
#     """Load conversation history with error handling"""
#     try:
#         state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
#         return state.values.get("messages", [])
#     except Exception as e:
#         st.error(f"Error loading conversation: {str(e)}")
#         return []

# # session setup
# if "message_history" not in st.session_state:
#     st.session_state["message_history"] = []

# if "thread_id" not in st.session_state:
#     st.session_state["thread_id"] = generate_thread_id()

# if "chat_threads" not in st.session_state:
#     try:
#         st.session_state["chat_threads"] = retrieve_all_threads()
#     except Exception as e:
#         st.error(f"Failed to load conversation history: {str(e)}")
#         st.session_state["chat_threads"] = []

# add_thread(st.session_state["thread_id"])

# # sidebar UI
# st.sidebar.title("LangGraph Chatbot")

# if st.sidebar.button("New Chat", use_container_width=True):
#     reset_chat()
#     st.rerun()

# st.sidebar.header("My Conversations")

# for thread_id in st.session_state["chat_threads"][::-1]:
#     with st.sidebar.container(border=True):
#         col1, col2 = st.columns([0.8, 0.2])
        
#         with col1:
#             if st.button(format_thread_display(thread_id), use_container_width=True, key=f"load_{thread_id}"):
#                 st.session_state["thread_id"] = thread_id
                
#                 with st.spinner("Loading conversation..."):
#                     messages = load_conversation(thread_id)

#                     temp_messages = []

#                     for msg in messages:
#                         if isinstance(msg, HumanMessage):
#                             role = "user"
#                         else:
#                             role = "assistant"

#                         temp_messages.append({"role": role, "content": msg.content})

#                     st.session_state["message_history"] = temp_messages
                
#                 st.rerun()
        
#         with col2:
#             if st.button("🗑️", key=f"delete_{thread_id}", help="Delete conversation"):
#                 st.session_state["chat_threads"].remove(thread_id)
#                 if st.session_state["thread_id"] == thread_id:
#                     reset_chat()
#                 st.rerun()

# # main UI
# for message in st.session_state["message_history"]:
#     with st.chat_message(message["role"]):
#         st.write(message["content"])  # Use st.write() for better formatting

# user_input = st.chat_input("Type here")

# if user_input:
#     st.session_state["message_history"].append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.write(user_input)

#     # CONFIG = {"configurable": {"thread_id": str(st.session_state["thread_id"])}}
#     CONFIG={
#         "configurable":{"thread_id":str(st.session_state["thread_id"])},
#         "metadata":{
#             "thread_id":st.session_state["thread_id"]
#         },
#         "run_name":"chat_turn"
#     }

#     try:
#         with st.chat_message("assistant"):
#             # Collect the full message content while streaming
#             ai_message_content = ""
#             message_placeholder = st.empty()
            
#             try:
#                 for message_chunk, metadata in chatbot.stream(
#                     {"messages": [HumanMessage(content=user_input)]},
#                     config=CONFIG,
#                     stream_mode="messages"
#                 ):
#                     if hasattr(message_chunk, 'content'):
#                         ai_message_content += message_chunk.content
#                         message_placeholder.write(ai_message_content)
#             except (ConnectionError, BrokenPipeError, OSError) as e:
#                 # Handle connection errors gracefully
#                 if ai_message_content:
#                     message_placeholder.write(ai_message_content + "\n\n⚠️ *Connection interrupted but message was received*")
#                 else:
#                     st.error("Connection lost while streaming response. Please try again.")
            
#             # Save the complete message to history
#             if ai_message_content:
#                 st.session_state["message_history"].append(
#                     {"role": "assistant", "content": ai_message_content}
#                 )
#     except Exception as e:
#         st.error(f"Error getting response from chatbot: {str(e)}")
#         # Remove the last user message if there was an error
#         if st.session_state["message_history"] and st.session_state["message_history"][-1]["role"] == "user":
#             st.session_state["message_history"].pop()


# =================================================================================================================================

# import streamlit as st
# from backend import chatbot, retrieve_all_threads
# from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
# import uuid

# # =========================== Utilities ===========================
# def generate_thread_id():
#     return uuid.uuid4()

# def reset_chat():
#     thread_id = generate_thread_id()
#     st.session_state["thread_id"] = thread_id
#     add_thread(thread_id)
#     st.session_state["message_history"] = []

# def add_thread(thread_id):
#     if thread_id not in st.session_state["chat_threads"]:
#         st.session_state["chat_threads"].append(thread_id)

# def load_conversation(thread_id):
#     state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
#     # Check if messages key exists in state values, return empty list if not
#     return state.values.get("messages", [])

# # ======================= Session Initialization ===================
# if "message_history" not in st.session_state:
#     st.session_state["message_history"] = []

# if "thread_id" not in st.session_state:
#     st.session_state["thread_id"] = generate_thread_id()

# if "chat_threads" not in st.session_state:
#     st.session_state["chat_threads"] = retrieve_all_threads()

# add_thread(st.session_state["thread_id"])

# # ============================ Sidebar ============================
# st.sidebar.title("LangGraph Chatbot")

# if st.sidebar.button("New Chat"):
#     reset_chat()

# st.sidebar.header("My Conversations")
# for thread_id in st.session_state["chat_threads"][::-1]:
#     if st.sidebar.button(str(thread_id)):
#         st.session_state["thread_id"] = thread_id
#         messages = load_conversation(thread_id)

#         temp_messages = []
#         for msg in messages:
#             role = "user" if isinstance(msg, HumanMessage) else "assistant"
#             temp_messages.append({"role": role, "content": msg.content})
#         st.session_state["message_history"] = temp_messages

# # ============================ Main UI ============================

# # Render history
# for message in st.session_state["message_history"]:
#     with st.chat_message(message["role"]):
#         st.text(message["content"])

# user_input = st.chat_input("Type here")

# if user_input:
#     # Show user's message
#     st.session_state["message_history"].append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.text(user_input)

#     CONFIG = {
#         "configurable": {"thread_id": st.session_state["thread_id"]},
#         "metadata": {"thread_id": st.session_state["thread_id"]},
#         "run_name": "chat_turn",
#     }

#     # Assistant streaming block
#     with st.chat_message("assistant"):
#         # Use a mutable holder so the generator can set/modify it
#         status_holder = {"box": None}

#         def ai_only_stream():
#             for message_chunk, metadata in chatbot.stream(
#                 {"messages": [HumanMessage(content=user_input)]},
#                 config=CONFIG,
#                 stream_mode="messages",
#             ):
#                 # Lazily create & update the SAME status container when any tool runs
#                 if isinstance(message_chunk, ToolMessage):
#                     tool_name = getattr(message_chunk, "name", "tool")
#                     if status_holder["box"] is None:
#                         status_holder["box"] = st.status(
#                             f"🔧 Using `{tool_name}` …", expanded=True
#                         )
#                     else:
#                         status_holder["box"].update(
#                             label=f"🔧 Using `{tool_name}` …",
#                             state="running",
#                             expanded=True,
#                         )

#                 # Stream ONLY assistant tokens
#                 if isinstance(message_chunk, AIMessage):
#                     yield message_chunk.content

#         ai_message = st.write_stream(ai_only_stream())

#         # Finalize only if a tool was actually used
#         if status_holder["box"] is not None:
#             status_holder["box"].update(
#                 label="Tool finished", state="complete", expanded=False
#             )

#     # Save assistant message
#     st.session_state["message_history"].append(
#         {"role": "assistant", "content": ai_message}
#     )

# # =================================================================================================================================


import queue
import uuid

import streamlit as st
from backend import chatbot, retrieve_all_threads, submit_async_task
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# =========================== Utilities ===========================
def generate_thread_id():
    return uuid.uuid4()


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get("messages", [])


# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

add_thread(st.session_state["thread_id"])

# ============================ Sidebar ============================
st.sidebar.title("LangGraph MCP Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")
for thread_id in st.session_state["chat_threads"][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            temp_messages.append({"role": role, "content": msg.content})
        st.session_state["message_history"] = temp_messages

# ============================ Main UI ============================

# Render history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type here")

if user_input:
    # Show user's message
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }

    # Assistant streaming block
    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            event_queue: queue.Queue = queue.Queue()

            async def run_stream():
                try:
                    async for message_chunk, metadata in chatbot.astream(
                        {"messages": [HumanMessage(content=user_input)]},
                        config=CONFIG,
                        stream_mode="messages",
                    ):
                        event_queue.put((message_chunk, metadata))
                except Exception as exc:
                    event_queue.put(("error", exc))
                finally:
                    event_queue.put(None)

            submit_async_task(run_stream())

            while True:
                item = event_queue.get()
                if item is None:
                    break
                message_chunk, metadata = item
                if message_chunk == "error":
                    raise metadata

                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    # Save assistant message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )
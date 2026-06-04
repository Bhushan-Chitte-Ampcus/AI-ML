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

import streamlit as st
from backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

# utility functions

def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

def format_thread_display(thread_id):
    """Format thread ID for display - show first 8 chars + timestamp if available"""
    return f"Chat {thread_id[:8]}..."

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"] = []

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    """Load conversation history with error handling"""
    try:
        state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
        return state.values.get("messages", [])
    except Exception as e:
        st.error(f"Error loading conversation: {str(e)}")
        return []

# session setup
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    try:
        st.session_state["chat_threads"] = retrieve_all_threads()
    except Exception as e:
        st.error(f"Failed to load conversation history: {str(e)}")
        st.session_state["chat_threads"] = []

add_thread(st.session_state["thread_id"])

# sidebar UI
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("➕ New Chat", use_container_width=True):
    reset_chat()
    st.rerun()

st.sidebar.header("My Conversations")

for thread_id in st.session_state["chat_threads"][::-1]:
    with st.sidebar.container(border=True):
        col1, col2 = st.columns([0.8, 0.2])
        
        with col1:
            if st.button(format_thread_display(thread_id), use_container_width=True, key=f"load_{thread_id}"):
                st.session_state["thread_id"] = thread_id
                
                with st.spinner("Loading conversation..."):
                    messages = load_conversation(thread_id)

                    temp_messages = []

                    for msg in messages:
                        if isinstance(msg, HumanMessage):
                            role = "user"
                        else:
                            role = "assistant"

                        temp_messages.append({"role": role, "content": msg.content})

                    st.session_state["message_history"] = temp_messages
                
                st.rerun()
        
        with col2:
            if st.button("🗑️", key=f"delete_{thread_id}", help="Delete conversation"):
                st.session_state["chat_threads"].remove(thread_id)
                if st.session_state["thread_id"] == thread_id:
                    reset_chat()
                st.rerun()

# main UI
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])  # Use st.write() for better formatting

user_input = st.chat_input("Type here")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    CONFIG = {"configurable": {"thread_id": str(st.session_state["thread_id"])}}

    try:
        with st.chat_message("assistant"):
            # Collect the full message content while streaming
            ai_message_content = ""
            message_placeholder = st.empty()
            
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if hasattr(message_chunk, 'content'):
                    ai_message_content += message_chunk.content
                    message_placeholder.write(ai_message_content)
            
            # Save the complete message to history
            if ai_message_content:
                st.session_state["message_history"].append(
                    {"role": "assistant", "content": ai_message_content}
                )
    except Exception as e:
        st.error(f"Error getting response from chatbot: {str(e)}")
        # Remove the last user message if there was an error
        if st.session_state["message_history"] and st.session_state["message_history"][-1]["role"] == "user":
            st.session_state["message_history"].pop()
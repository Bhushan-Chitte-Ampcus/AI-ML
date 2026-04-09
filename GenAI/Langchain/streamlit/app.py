import streamlit as st
import os
import transformers
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

from langchain_huggingface import HuggingFaceEmbeddings, ChatHuggingFace, HuggingFacePipeline

# -----------------------------
# Setup
# -----------------------------
transformers.logging.set_verbosity_error()
load_dotenv()

os.environ["HF_HOME"] = "D:/huggingface_cache"

st.set_page_config(page_title="CricketRAG Bot", page_icon="🏏")

st.title("CricketRAG Chatbot")
st.write("Ask anything about cricket players!")

# -----------------------------
# Load Models (Cache for speed)
# -----------------------------
@st.cache_resource
def load_models():

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    llm_pipeline = HuggingFacePipeline.from_model_id(
        model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        task="text-generation",
        model_kwargs={
            "torch_dtype": "auto",
            "device_map": "auto"
        },
        pipeline_kwargs=dict(
            temperature=0.5,
            max_new_tokens=80
        )
    )

    llm = ChatHuggingFace(llm=llm_pipeline)

    return embedding, llm


embedding, llm = load_models()

# -----------------------------
# Knowledge Base
# -----------------------------
documents = [
    "Virat Kohli is an Indian cricketer known for his aggressive batting and leadership.",
    "MS Dhoni is a former Indian captain famous for his calm demeanor and finishing skills.",
    "Sachin Tendulkar holds the record for 100 international centuries.",
    "Rohit Sharma has scored three double centuries in ODI cricket.",
    "Jasprit Bumrah is known for his deadly yorkers.",
    "Kapil Dev led India to its first Cricket World Cup victory in 1983.",
    "Rahul Dravid was known as The Wall due to his solid defense.",
    "Anil Kumble took more than 600 wickets in Test cricket.",
    "Yuvraj Singh hit six sixes in one over in the 2007 T20 World Cup.",
    "Ravindra Jadeja is one of the best all-rounders in modern cricket."
]

# Precompute embeddings
doc_embeddings = embedding.embed_documents(documents)

# -----------------------------
# Chat Interface
# -----------------------------
query = st.chat_input("Ask a question...")

if query:

    with st.spinner("Thinking..."):

        query_embedding = embedding.embed_query(query)

        scores = cosine_similarity([query_embedding], doc_embeddings)[0]

        index = scores.argmax()
        retrieved_doc = documents[index]

        prompt = f"""
        Context: {retrieved_doc}
        Question: {query}
        Answer:
        """

        response = llm.invoke(prompt)

    st.chat_message("user").write(query)
    st.chat_message("assistant").write(response.content)

    with st.expander("Retrieved Context"):
        st.write(retrieved_doc)
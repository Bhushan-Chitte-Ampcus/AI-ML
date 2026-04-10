from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
import os
from dotenv import load_dotenv
import transformers
import streamlit as st
from langchain_core.load import load
import json

# -------------------- Setup --------------------
load_dotenv()

transformers.logging.set_verbosity_error()

os.environ["HF_HOME"] = "D:/huggingface_cache"

hf_token = os.getenv("HF_TOKEN")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token

st.set_page_config(page_title="Research Tool")
st.title("Research Tool")

# -------------------- Load Model (Cached) --------------------
@st.cache_resource
def load_model():
    llm = HuggingFacePipeline.from_model_id(
        model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        task="text-generation",
        pipeline_kwargs={
            "temperature": 0.5,
            "max_new_tokens": 120,
            "do_sample": True
        }
    )
    return ChatHuggingFace(llm=llm)

model = load_model()

# -------------------- UI --------------------

paper_input = st.selectbox("Select Research Paper Name", ["Attention Is All You Need", "BERT: Pre-training of Deep Bidirectional Transformers", "GPT-3: Language Models are Few-Shot Learners", "Diffusion Models Beat GANs on Image Synthesis"])
style_input = st.selectbox("Select Explaination Style", ["Beginner-Friendly", "Technical", "Code-Oriented", "Mathematical"])
length_input = st.selectbox("Select Explaination Length", ["Short (1-2 paragraphs)", "Medium (3-5 paragraphs)", "Long (detail explaination)"])

with open("./template.json") as f:
    template = load(json.load(f))

prompt = template.invoke({
    "paper_input":paper_input,
    "style_input":style_input,
    "length_input":length_input
})

if st.button("Generate Response"):
    with st.spinner("Generating response..."):
        try:
            result = model.invoke(prompt)

            # Clean response
            response = result.content
            if "<|assistant|>" in response:
                response = response.split("<|assistant|>")[-1]

            st.subheader("Response")
            st.write(response.strip())

        except Exception as e:
            st.error(f"Error: {str(e)}")
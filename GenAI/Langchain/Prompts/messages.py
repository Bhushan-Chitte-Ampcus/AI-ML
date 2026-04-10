from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import transformers
import os
import re

load_dotenv()

transformers.logging.set_verbosity_error()

os.environ["HF_HOME"] = "D:/huggingface_cache"
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

llm = HuggingFacePipeline.from_model_id(
    model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    task="text-generation",
    pipeline_kwargs={
        "temperature": 0.5,
        "max_new_tokens": 80,
        "do_sample": True,
        "return_full_text": False
    }
)

model = ChatHuggingFace(llm=llm)


# ---------------- Response Cleaner ----------------
def clean_response(text: str) -> str:
    """Remove unwanted tokens and repeated sections."""
    
    # Remove assistant tokens
    text = re.sub(r"<\|assistant\|>", "", text)
    text = re.sub(r"<\|.*?\|>", "", text)

    # Remove repeated sentences
    sentences = text.split(". ")
    seen = set()
    cleaned = []

    for s in sentences:
        if s not in seen:
            cleaned.append(s)
            seen.add(s)

    return ". ".join(cleaned).strip()


# ----------------------------------------------------

messages = [
    SystemMessage(content="You are a helpful assistant"),
    HumanMessage(content="Tell me about langchain")
]

result = model.invoke(messages)
response = clean_response(result.content)

messages.append(AIMessage(content=response))

print(messages)

# ----------------------------------------------------

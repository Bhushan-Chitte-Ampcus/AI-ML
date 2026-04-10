from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import transformers
import os
import re

# ---------------- Environment Setup ----------------
load_dotenv()

transformers.logging.set_verbosity_error()
os.environ["HF_HOME"] = "D:/huggingface_cache"

hf_token = os.getenv("HF_TOKEN")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token

# ---------------- Load LLM ----------------
llm = HuggingFacePipeline.from_model_id(
    model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    task="text-generation",
    pipeline_kwargs={
        "temperature": 0.5,
        "max_new_tokens": 120,
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


# ---------------- Chat Loop ----------------
print("Chat started (type 'q' to quit)\n")

# messages
chat_history = [
    SystemMessage(content="You are a helpful AI Assistant")
]

while True:

    user_input = input("You: ").strip()
    chat_history.append(HumanMessage(content=user_input))

    if user_input.lower() == "q":
        print("Chat ended.")
        break

    try:
        result = model.invoke(chat_history)
        response = clean_response(result.content)
        
        chat_history.append(AIMessage(content=response))
        
        print(f"AI: {response}\n")

    except Exception as e:
        print(f"Error: {e}")

print(chat_history)
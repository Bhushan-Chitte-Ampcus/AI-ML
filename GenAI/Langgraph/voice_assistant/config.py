"""Central configuration — reads from .env file."""
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# llama3-groq-70b-8192-tool-use-preview is fine-tuned for reliable tool calling.
# Alternatives if you hit rate limits:
#   llama-3.1-70b-versatile
#   llama3-70b-8192
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-groq-70b-8192-tool-use-preview")

# Maximum number of messages (human + AI turns) kept in the context window.
# Each human+AI exchange = 2 messages, so 20 = last 10 exchanges.
# Groq's tool-use model has an 8192-token limit — 20 messages is a safe default.
# Raise it if you need longer memory, lower it if you hit token limit errors.
MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))

# System prompt — keep answers concise (spoken aloud) but allow tool use
SYSTEM_PROMPT: str = (
    "You are CortexAI, an advanced AI voice assistant. "
    "Keep answers concise and conversational — ideally 1-3 sentences — "
    "since your response will be spoken aloud. "
    "When you need current information, calculations, stock prices, or YouTube videos, "
    "use the available tools. Always call tools with valid, complete arguments."
)

"""Request / response models for the voice assistant API."""
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    text: str        # assistant's reply text (also spoken on the frontend)
    session_id: str

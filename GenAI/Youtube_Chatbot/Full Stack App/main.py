from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import re
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="YouTube Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for loaded video sessions
video_sessions: dict = {}


def extract_video_id(url_or_id: str) -> str:
    """Extract YouTube video ID from URL or return as-is if already an ID."""
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError("Invalid YouTube URL or video ID")


class LoadVideoRequest(BaseModel):
    video_url: str
    hf_token: Optional[str] = None


class ChatRequest(BaseModel):
    video_id: str
    question: str


class LoadVideoResponse(BaseModel):
    video_id: str
    title: str
    chunk_count: int
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/")
def root():
    return {"status": "ok", "message": "YouTube Chatbot API is running"}


@app.post("/api/load-video", response_model=LoadVideoResponse)
def load_video(request: LoadVideoRequest):
    """Load a YouTube video, fetch its transcript, embed it, and store in FAISS."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS

        video_id = extract_video_id(request.video_url)

        if video_id in video_sessions:
            session = video_sessions[video_id]
            return LoadVideoResponse(
                video_id=video_id,
                title=session["title"],
                chunk_count=session["chunk_count"],
                message="Video already loaded (using cached session)",
            )

        # Fetch transcript
        try:
            ytt = YouTubeTranscriptApi()
            transcript_list = ytt.list(video_id)
            transcript_ = transcript_list.find_transcript(["en", "hi", "en-US", "en-GB"])
            data = transcript_.fetch()
            transcript = " ".join(chunk.text for chunk in data)
        except TranscriptsDisabled:
            raise HTTPException(status_code=400, detail="Transcripts are disabled for this video.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch transcript: {str(e)}")

        # Split
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.create_documents([transcript])

        # Embed
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        vector_store = FAISS.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

        # Store session
        hf_token = request.hf_token or os.getenv("HF_TOKEN")
        video_sessions[video_id] = {
            "retriever": retriever,
            "chunk_count": len(chunks),
            "title": f"YouTube Video ({video_id})",
            "hf_token": hf_token,
        }

        return LoadVideoResponse(
            video_id=video_id,
            title=f"YouTube Video ({video_id})",
            chunk_count=len(chunks),
            message="Video loaded and indexed successfully!",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Ask a question about a loaded video."""
    if request.video_id not in video_sessions:
        raise HTTPException(
            status_code=404,
            detail="Video not loaded. Please load the video first via /api/load-video",
        )

    session = video_sessions[request.video_id]

    try:
        from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
        from langchain_core.prompts import PromptTemplate
        from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
        from langchain_core.output_parsers import StrOutputParser

        hf_token = session.get("hf_token") or os.getenv("HF_TOKEN")
        if not hf_token:
            raise HTTPException(status_code=400, detail="HuggingFace token not provided.")

        retriever = session["retriever"]

        # Retrieve docs for sources
        retrieved_docs = retriever.invoke(request.question)
        sources = [doc.page_content[:200] + "..." for doc in retrieved_docs]

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        llm = HuggingFaceEndpoint(
            repo_id="Qwen/Qwen2.5-7B-Instruct",
            temperature=0.3,
            max_new_tokens=512,
            huggingfacehub_api_token=hf_token,
        )
        model = ChatHuggingFace(llm=llm)

        prompt = PromptTemplate(
            template="""You are a helpful assistant.
Answer only from the provided transcript context.
If the context is insufficient, just say you don't know.

{context}
Question: {question}
""",
            input_variables=["context", "question"],
        )

        parser = StrOutputParser()

        parallel_chain = RunnableParallel(
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
            }
        )
        main_chain = parallel_chain | prompt | model | parser

        answer = main_chain.invoke(request.question)

        return ChatResponse(answer=answer, sources=sources)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
def list_sessions():
    return {
        "sessions": [
            {"video_id": vid, "title": s["title"], "chunk_count": s["chunk_count"]}
            for vid, s in video_sessions.items()
        ]
    }


@app.delete("/api/sessions/{video_id}")
def delete_session(video_id: str):
    if video_id not in video_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    del video_sessions[video_id]
    return {"message": f"Session {video_id} deleted"}


# python -m uvicorn main:app --reload

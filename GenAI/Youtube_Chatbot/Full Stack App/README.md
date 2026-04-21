# 🎬 TubeChat — YouTube RAG Chatbot

Ask anything about any YouTube video using AI.  
Built with FastAPI + LangChain + FAISS + HuggingFace + a sleek HTML frontend.

---

## Architecture

```
YouTube URL
    ↓
[youtube-transcript-api]  → raw transcript text
    ↓
[LangChain RecursiveTextSplitter]  → chunks (1000 chars, 200 overlap)
    ↓
[HuggingFace Embeddings]  → paraphrase-multilingual-MiniLM-L12-v2
    ↓
[FAISS Vector Store]  → in-memory index
    ↓
[Retriever (top-4 similar chunks)]
    ↓
[Qwen2.5-7B-Instruct via HuggingFace Endpoint]
    ↓
Answer
```

---

## Setup

### 1. Clone & install backend

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set up environment

```bash
cp .env.example .env
# Edit .env and add your HuggingFace token
```

Get your free token at: https://huggingface.co/settings/tokens

### 3. Run the backend

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at http://localhost:8000  
Interactive API docs at http://localhost:8000/docs

### 4. Open the frontend

Just open `frontend/index.html` in your browser — no build step needed!

Or serve it:
```bash
cd frontend
python -m http.server 3000
# Open http://localhost:3000
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/load-video` | Load & index a YouTube video |
| `POST` | `/api/chat` | Ask a question about a loaded video |
| `GET` | `/api/sessions` | List all loaded video sessions |
| `DELETE` | `/api/sessions/{video_id}` | Remove a session |

### Load Video Request
```json
{
  "video_url": "https://youtube.com/watch?v=Gfr50f6ZBvo",
  "hf_token": "hf_your_token_here"  // optional if set in .env
}
```

### Chat Request
```json
{
  "video_id": "Gfr50f6ZBvo",
  "question": "Who is Demis Hassabis?"
}
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Uvicorn |
| Transcript | youtube-transcript-api |
| Splitting | LangChain RecursiveCharacterTextSplitter |
| Embeddings | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Vector Store | FAISS (in-memory) |
| LLM | Qwen/Qwen2.5-7B-Instruct via HuggingFace Endpoints |
| Orchestration | LangChain (RunnableParallel, PromptTemplate) |
| Frontend | Vanilla HTML/CSS/JS (no build needed) |

---

## Notes

- Videos with disabled captions will return an error
- Sessions are in-memory — they reset when the server restarts
- The HF token can be provided per-request or via `.env`
- Supports English and Hindi transcripts by default

"""API route definitions."""
import io
import json
import edge_tts
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from api.schemas import ChatRequest, ChatResponse
from api.session import get_history, set_history, clear_history

router = APIRouter(prefix="/api")

TTS_VOICE = "en-IN-NeerjaNeural"


# ── Helper: resolve graph + config ──────────────────────────────────────────

def _graph_and_config(session_id: str, streaming: bool = False):
    """Return (graph, config, history) for the current persistence mode."""
    import graph.builder as gb
    from db import is_db_enabled

    g = gb.graph_stream if streaming else gb.graph

    if is_db_enabled():
        config = {"configurable": {"thread_id": session_id}}
        return g, config, None
    else:
        history = get_history(session_id)
        return g, {}, history


# ── POST /api/chat  (non-streaming, kept for compatibility) ──────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Full-response endpoint — waits for the complete LLM reply."""
    graph, config, history = _graph_and_config(request.session_id)

    if history is not None:
        # In-memory mode: prepend history manually
        result = await graph.ainvoke(
            {"messages": history + [HumanMessage(content=request.message)]},
            config=config,
        )
        set_history(request.session_id, result["messages"])
    else:
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
        )

    return ChatResponse(
        text=result["messages"][-1].content,
        session_id=request.session_id,
    )


# ── POST /api/chat/stream  (SSE streaming) ───────────────────────────────────

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE streaming endpoint — emits tokens as they arrive from the LLM.

    SSE event format
    ----------------
    data: {"type": "token", "text": "<chunk>"}   — one token / chunk
    data: {"type": "done",  "text": "<full>"}    — complete text, end of stream
    data: {"type": "error", "text": "<msg>"}     — error occurred
    """
    graph, config, history = _graph_and_config(request.session_id, streaming=True)

    async def event_generator():
        full_text = []
        try:
            input_msgs = (
                history + [HumanMessage(content=request.message)]
                if history is not None
                else [HumanMessage(content=request.message)]
            )

            # stream_mode="messages" yields (message_chunk, metadata) tuples
            # Each chunk is an AIMessageChunk with partial content
            async for msg_chunk, metadata in graph.astream(
                {"messages": input_msgs},
                config=config,
                stream_mode="messages",
            ):
                # Only emit content from the chatbot node, not tool results
                node = metadata.get("langgraph_node", "")
                if (
                    node == "chatbot"
                    and hasattr(msg_chunk, "content")
                    and msg_chunk.content
                    # Skip tool-call chunks (no visible text)
                    and not getattr(msg_chunk, "tool_calls", None)
                    and not getattr(msg_chunk, "tool_call_chunks", None)
                ):
                    token = msg_chunk.content
                    full_text.append(token)
                    yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"

            # Persist history for in-memory mode
            if history is not None and full_text:
                from langchain_core.messages import AIMessage
                set_history(request.session_id, history + [
                    HumanMessage(content=request.message),
                    AIMessage(content="".join(full_text)),
                ])

            complete = "".join(full_text)
            yield f"data: {json.dumps({'type': 'done', 'text': complete})}\n\n"

        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'text': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── GET /api/tts ─────────────────────────────────────────────────────────────

@router.get("/tts")
async def tts(text: str = Query(..., description="Text to synthesise")):
    """Convert text to speech using Microsoft Edge TTS and stream back an MP3."""
    buf = io.BytesIO()
    communicate = edge_tts.Communicate(text=text, voice=TTS_VOICE)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-store"},
    )


# ── DELETE /api/session/{session_id} ─────────────────────────────────────────

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    clear_history(session_id)
    return {"status": "cleared", "session_id": session_id}


# ── GET /api/health ──────────────────────────────────────────────────────────

@router.get("/health")
async def health():
    from db import is_db_enabled
    return {"status": "ok", "persistent_memory": is_db_enabled()}

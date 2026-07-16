"""Application entry point.

Run with:
    python main.py
or:
    uvicorn main:app --reload --port 8000

PostgreSQL setup
----------------
Set DATABASE_URL in .env to enable persistent conversation memory:

    DATABASE_URL=postgresql://user:password@localhost:5432/cortexai

If DATABASE_URL is not set the app starts normally with in-memory sessions.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from api.routes import router
from db import setup_db, teardown_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: open DB pool and set up checkpointer schema.
    Shutdown: close the pool cleanly.
    """
    await setup_db()
    yield
    await teardown_db()


app = FastAPI(title="CortexAI", version="1.0.0", lifespan=lifespan)

app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.get("/favicon.ico", include_in_schema=False)
@app.get("/favicon.svg", include_in_schema=False)
async def favicon():
    """Serve the CortexAI favicon — silences the browser 404."""
    return FileResponse("static/favicon.svg", media_type="image/svg+xml")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

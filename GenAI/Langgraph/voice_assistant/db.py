"""PostgreSQL connection pool and LangGraph checkpointer lifecycle.

Call setup_db() on application startup and teardown_db() on shutdown.
After setup_db() succeeds, graph.builder.graph points to the DB-backed
compiled graph and all conversation history is persisted automatically.

Connection string priority
--------------------------
1. DATABASE_URL env var (full connection string, takes precedence)
2. Individual DB_USER / DB_PASSWORD / DB_HOST / DB_PORT / DB_NAME vars
"""
from __future__ import annotations

import os
import logging
from dotenv import load_dotenv

load_dotenv()  # ensure .env is loaded even if db.py is imported before config.py

import psycopg
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

logger = logging.getLogger(__name__)

# Module-level references — populated by setup_db()
_pool: AsyncConnectionPool | None = None
_checkpointer: AsyncPostgresSaver | None = None


def _build_conn_str() -> str:
    """Return a psycopg3-compatible connection string.

    Prefers DATABASE_URL if set; otherwise assembles one from the
    individual DB_* environment variables.
    Returns an empty string if neither is configured.
    """
    # Option 1 — full URL
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return url.replace("postgres://", "postgresql://", 1)

    # Option 2 — individual vars (URL-encode password so @ % etc. are safe)
    from urllib.parse import quote_plus
    user     = os.getenv("DB_USER", "").strip()
    password = quote_plus(os.getenv("DB_PASSWORD", "").strip())
    host     = os.getenv("DB_HOST", "localhost").strip()
    port     = os.getenv("DB_PORT", "5432").strip()
    dbname   = os.getenv("DB_NAME", "").strip()

    if user and dbname:
        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    return ""


async def setup_db() -> None:
    """Open the connection pool, run schema setup, re-compile the graph.

    Key detail: AsyncPostgresSaver.setup() uses CREATE INDEX CONCURRENTLY
    which cannot run inside a transaction block. We call it on a direct
    autocommit connection, then hand off to the pool for all runtime queries.

    Safe to call multiple times — exits early if already initialised.
    """
    global _pool, _checkpointer

    conn_str = _build_conn_str()
    if not conn_str:
        logger.warning(
            "No PostgreSQL configuration found (DATABASE_URL or DB_USER/DB_NAME). "
            "Running without persistent memory — history will be lost on restart."
        )
        return

    if _pool is not None:
        return  # already initialised

    try:
        # ── Step 1: run schema migrations on an autocommit connection ──
        # CREATE INDEX CONCURRENTLY requires autocommit=True
        setup_conn = await psycopg.AsyncConnection.connect(
            conn_str, autocommit=True
        )
        async with setup_conn:
            setup_checkpointer = AsyncPostgresSaver(setup_conn)
            await setup_checkpointer.setup()

        logger.info("LangGraph checkpoint schema verified/created.")

        # ── Step 2: open the pool for all runtime queries ──────────────
        _pool = AsyncConnectionPool(
            conninfo=conn_str,
            max_size=10,
            open=False,
        )
        await _pool.open()

        _checkpointer = AsyncPostgresSaver(_pool)

        # ── Step 3: re-compile both graphs with the live checkpointer ──
        import graph.builder as gb
        gb.graph        = gb.build_graph(checkpointer=_checkpointer)
        gb.graph_stream = gb.build_graph_stream(checkpointer=_checkpointer)

        logger.info(
            "PostgreSQL checkpointer ready — conversation memory is persistent. "
            "(host=%s  db=%s)",
            os.getenv("DB_HOST", "localhost"),
            os.getenv("DB_NAME", ""),
        )

    except Exception as exc:
        logger.error(
            "Failed to connect to PostgreSQL (%s). "
            "Falling back to in-memory session store.", exc
        )
        if _pool is not None:
            await _pool.close()
        _pool         = None
        _checkpointer = None


async def teardown_db() -> None:
    """Close the connection pool gracefully on server shutdown."""
    global _pool, _checkpointer
    if _pool is not None:
        await _pool.close()
        _pool         = None
        _checkpointer = None
        logger.info("PostgreSQL connection pool closed.")


def is_db_enabled() -> bool:
    """Return True if the PostgreSQL checkpointer is active."""
    return _checkpointer is not None

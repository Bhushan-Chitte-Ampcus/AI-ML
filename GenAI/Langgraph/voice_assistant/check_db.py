"""Check whether LangGraph checkpoint data is being saved to PostgreSQL.

Run with:
    python check_db.py

Steps:
  1. Connects to the DB using the same credentials as the app
  2. Verifies the 4 LangGraph tables exist
  3. Shows row counts
  4. Prints the most recent 5 conversation threads with message previews
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Fix for Windows: psycopg requires SelectorEventLoop, not ProactorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()


def _build_conn_str() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return url.replace("postgres://", "postgresql://", 1)
    from urllib.parse import quote_plus
    user     = os.getenv("DB_USER", "postgres")
    password = quote_plus(os.getenv("DB_PASSWORD", ""))   # encodes @ % etc.
    host     = os.getenv("DB_HOST", "localhost")
    port     = os.getenv("DB_PORT", "5432")
    dbname   = os.getenv("DB_NAME", "cortexai")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


async def main():
    import psycopg

    conn_str = _build_conn_str()
    print(f"\nConnecting to: {conn_str.split('@')[-1]}")  # hide credentials

    try:
        aconn = await psycopg.AsyncConnection.connect(conn_str)
    except Exception as e:
        print(f"\n✗  Could not connect to PostgreSQL: {e}")
        return

    print("✓  Connected\n")

    async with aconn:
        # ── 1. Check tables exist ────────────────────────────────
        print("=" * 55)
        print("  TABLE                        ROWS")
        print("=" * 55)

        tables = [
            "checkpoints",
            "checkpoint_blobs",
            "checkpoint_writes",
            "checkpoint_migrations",
        ]

        counts = {}
        for table in tables:
            try:
                async with aconn.cursor() as cur:
                    await cur.execute(
                        "SELECT COUNT(*) FROM information_schema.tables "
                        "WHERE table_name = %s AND table_schema = 'public'",
                        (table,)
                    )
                    exists = (await cur.fetchone())[0] > 0

                    if exists:
                        await cur.execute(f"SELECT COUNT(*) FROM {table}")
                        count = (await cur.fetchone())[0]
                        counts[table] = count
                        print(f"  ✓  {table:<28} {count}")
                    else:
                        print(f"  ✗  {table:<28} NOT FOUND")
                        counts[table] = None
            except Exception as e:
                print(f"  ✗  {table:<28} ERROR: {e}")

        print("=" * 55)

        # ── 2. Check if any data was saved ───────────────────────
        cp_count = counts.get("checkpoints")
        if cp_count is None:
            print("\n✗  checkpoints table missing — has the server started yet?")
            print("   Run 'python main.py' first, then send a message from the frontend.")
            return

        if cp_count == 0:
            print("\n⚠  No checkpoints found.")
            print("   Either no messages have been sent yet, or the server")
            print("   started without DB configured (check startup logs).")
            return

        print(f"\n✓  {cp_count} checkpoint(s) found — data IS being persisted!\n")

        # ── 3. Show recent threads ───────────────────────────────
        print("  RECENT CONVERSATION THREADS (last 5)")
        print("=" * 55)
        try:
            async with aconn.cursor() as cur:
                await cur.execute("""
                    SELECT DISTINCT ON (thread_id)
                        thread_id,
                        checkpoint_id,
                        metadata
                    FROM checkpoints
                    ORDER BY thread_id, checkpoint_id DESC
                    LIMIT 5
                """)
                rows = await cur.fetchall()

            if not rows:
                print("  No threads found.")
            else:
                for thread_id, checkpoint_id, metadata in rows:
                    print(f"\n  Thread : {thread_id}")
                    print(f"  Latest : {checkpoint_id}")
                    if metadata and isinstance(metadata, dict):
                        step = metadata.get("step", "?")
                        print(f"  Step   : {step}")
        except Exception as e:
            print(f"  Could not read threads: {e}")

        # ── 4. Show blob channel breakdown ───────────────────────
        print("\n" + "=" * 55)
        print("  CHECKPOINT BLOBS BY CHANNEL")
        print("=" * 55)
        try:
            async with aconn.cursor() as cur:
                await cur.execute("""
                    SELECT channel, COUNT(*) as cnt
                    FROM checkpoint_blobs
                    GROUP BY channel
                    ORDER BY cnt DESC
                """)
                rows = await cur.fetchall()
            for channel, cnt in rows:
                print(f"  {channel:<35} {cnt}")
        except Exception as e:
            print(f"  Could not read blobs: {e}")

    print("\n" + "=" * 55)
    print("  Done.")
    print("=" * 55 + "\n")


asyncio.run(main())

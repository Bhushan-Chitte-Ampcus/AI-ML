"""PostgreSQL tool — run SQL queries, retrieve, insert, and update records.

Safety rules
------------
- SELECT  : always allowed
- INSERT  : allowed
- UPDATE  : allowed (must include WHERE clause)
- CREATE  : allowed (tables, indexes)
- DROP    : BLOCKED — too destructive
- DELETE  : BLOCKED — use UPDATE with a soft-delete column instead
- TRUNCATE: BLOCKED
- Parameterised values are used where supported to prevent SQL injection.

Connection
----------
Reads the same DB_* / DATABASE_URL variables as the rest of the app.
Uses a fresh synchronous psycopg connection per call (simple, stateless).
"""
from __future__ import annotations

import os
import json
from urllib.parse import quote_plus
from langchain_core.tools import tool

# ── Blocked SQL keywords (case-insensitive, word-boundary matched) ──────────
_BLOCKED = ['drop', 'truncate', 'delete']


def _build_conn_str() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return url.replace("postgres://", "postgresql://", 1)
    user     = os.getenv("DB_USER", "postgres").strip()
    password = quote_plus(os.getenv("DB_PASSWORD", "").strip())   # URL-encodes @ % etc.
    host     = os.getenv("DB_HOST", "localhost").strip()
    port     = os.getenv("DB_PORT", "5432").strip()
    dbname   = os.getenv("DB_NAME", "").strip()
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def _is_safe(sql: str) -> tuple[bool, str]:
    """Return (is_safe, reason). Blocks destructive statements."""
    import re
    sql_upper = sql.upper()
    for kw in _BLOCKED:
        if re.search(rf'\b{kw.upper()}\b', sql_upper):
            return False, f"'{kw.upper()}' statements are not allowed for safety reasons."
    # UPDATE without WHERE is risky
    if re.search(r'\bUPDATE\b', sql_upper) and not re.search(r'\bWHERE\b', sql_upper):
        return False, "UPDATE without a WHERE clause is not allowed — it would modify all rows."
    return True, ""


def _run_query(sql: str, params: list | None = None) -> dict:
    """Execute a single SQL statement and return results as a dict."""
    import psycopg

    safe, reason = _is_safe(sql)
    if not safe:
        return {"error": reason}

    conn_str = _build_conn_str()
    try:
        with psycopg.connect(conn_str, autocommit=False) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or [])
                sql_upper = sql.strip().upper()

                if sql_upper.startswith("SELECT") or sql_upper.startswith("WITH"):
                    cols = [d.name for d in cur.description] if cur.description else []
                    rows = cur.fetchall()
                    return {
                        "columns": cols,
                        "rows":    [dict(zip(cols, row)) for row in rows],
                        "count":   len(rows),
                    }
                else:
                    conn.commit()
                    return {
                        "status":        "success",
                        "rows_affected": cur.rowcount,
                    }
    except Exception as e:
        return {"error": str(e)}


# ── Tool 1: Run SQL query ────────────────────────────────────────────────────

@tool
def pg_query(sql: str) -> str:
    """Run a SQL SELECT query on the PostgreSQL database and return results.

    Use this when the user asks to query data, list records, count rows,
    or retrieve information from the database.

    Args:
        sql: A valid SELECT SQL statement. Example:
             "SELECT * FROM users WHERE active = true LIMIT 10"

    Returns a JSON string with columns, rows, and count.
    """
    result = _run_query(sql)
    return json.dumps(result, default=str, indent=2)


# ── Tool 2: List tables ──────────────────────────────────────────────────────

@tool
def pg_list_tables(schema: str = "public") -> str:
    """List all tables in the PostgreSQL database.

    Use this when the user asks what tables exist, what the schema looks like,
    or wants to explore the database structure.

    Args:
        schema: The schema name to list tables from (default: 'public').
    """
    sql = """
        SELECT
            table_name,
            pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS size
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """
    result = _run_query(sql, [schema])
    return json.dumps(result, default=str, indent=2)


# ── Tool 3: Describe table ───────────────────────────────────────────────────

@tool
def pg_describe_table(table_name: str) -> str:
    """Show the column definitions of a specific table in the database.

    Use this when the user asks about a table's structure, columns, or data types.

    Args:
        table_name: Name of the table to describe. Example: "users"
    """
    sql = """
        SELECT
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = %s
          AND table_schema = 'public'
        ORDER BY ordinal_position
    """
    result = _run_query(sql, [table_name])
    return json.dumps(result, default=str, indent=2)


# ── Tool 4: Insert record ────────────────────────────────────────────────────

@tool
def pg_insert(table: str, data: str) -> str:
    """Insert a new record into a PostgreSQL table.

    Use this when the user asks to add, create, or insert a record into the database.

    Args:
        table: The target table name. Example: "employees"
        data:  A JSON string of column→value pairs to insert.
               Example: '{"name": "Alice", "role": "Engineer", "active": true}'
    """
    try:
        record = json.loads(data)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON in 'data' parameter."})

    if not record:
        return json.dumps({"error": "No data provided to insert."})

    cols        = list(record.keys())
    values      = list(record.values())
    col_str     = ", ".join(f'"{c}"' for c in cols)
    placeholder = ", ".join(["%s"] * len(cols))
    sql         = f'INSERT INTO "{table}" ({col_str}) VALUES ({placeholder})'

    result = _run_query(sql, values)
    return json.dumps(result, default=str, indent=2)


# ── Tool 5: Update record ────────────────────────────────────────────────────

@tool
def pg_update(table: str, data: str, where: str) -> str:
    """Update existing records in a PostgreSQL table.

    Use this when the user asks to modify, update, or change a record.

    Args:
        table: The target table name. Example: "employees"
        data:  A JSON string of column→new value pairs to set.
               Example: '{"role": "Senior Engineer", "active": true}'
        where: A SQL WHERE clause (without the WHERE keyword) to identify
               which rows to update. Example: 'id = 42'
               REQUIRED — updates without a filter are not allowed.
    """
    try:
        record = json.loads(data)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON in 'data' parameter."})

    if not record:
        return json.dumps({"error": "No data provided to update."})
    if not where or not where.strip():
        return json.dumps({"error": "A WHERE clause is required for UPDATE."})

    set_parts = ", ".join(f'"{k}" = %s' for k in record.keys())
    values    = list(record.values())
    sql       = f'UPDATE "{table}" SET {set_parts} WHERE {where}'

    result = _run_query(sql, values)
    return json.dumps(result, default=str, indent=2)

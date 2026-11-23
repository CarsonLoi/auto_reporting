#!/usr/bin/env python3
"""Strictly read-only SQL query runner with statement timeout, EXPLAIN support, and export.

Blocks all DML/DDL statements before sending anything to the database.
Loads credentials exclusively from `.env`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|GRANT|REVOKE|MERGE|CALL|EXEC|EXECUTE|COPY|VACUUM|ATTACH|DETACH)\b",
    re.IGNORECASE,
)


def strip_sql_comments_and_strings(sql: str) -> str:
    """Remove SQL comments and single-quoted string literals before keyword scanning."""
    no_block = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    no_line = re.sub(r"--[^\n]*", " ", no_block)
    no_strings = re.sub(r"'(?:''|[^'])*'", "''", no_line)
    return no_strings.strip()


def validate_read_only_sql(sql: str) -> None:
    cleaned = strip_sql_comments_and_strings(sql).rstrip(";").strip()
    if not cleaned:
        raise ValueError("SQL query is empty.")
    if ";" in cleaned:
        raise ValueError("Multiple SQL statements are prohibited. Submit exactly one read-only statement.")
    first_token = cleaned.split(None, 1)[0].upper()
    if first_token not in {"SELECT", "WITH", "EXPLAIN", "SHOW", "PRAGMA"}:
        raise ValueError(f"Blocked non-read-only statement starting with '{first_token}'.")
    match = FORBIDDEN_KEYWORDS.search(cleaned)
    if match:
        raise ValueError(f"Blocked forbidden SQL keyword '{match.group(1).upper()}' in read-only mode.")


def build_engine(timeout_seconds: int) -> Engine:
    load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        dialect = os.getenv("DB_DIALECT", "postgresql").strip()
        driver = os.getenv("DB_DRIVER", "psycopg2").strip()
        host = os.getenv("DB_HOST", "localhost").strip()
        port = os.getenv("DB_PORT", "5432").strip()
        name = os.getenv("DB_NAME", "").strip()
        user = quote_plus(os.getenv("DB_USER", "").strip())
        password = quote_plus(os.getenv("DB_PASSWORD", "").strip())
        sslmode = os.getenv("DB_SSLMODE", "").strip()

        if dialect == "sqlite":
            database_url = f"sqlite:///{name}"
        else:
            scheme = f"{dialect}+{driver}" if driver else dialect
            query = f"?sslmode={sslmode}" if sslmode and dialect == "postgresql" else ""
            database_url = f"{scheme}://{user}:{password}@{host}:{port}/{name}{query}"

    connect_args: dict[str, Any] = {}
    if database_url.startswith("postgresql"):
        connect_args["options"] = (
            f"-c default_transaction_read_only=on -c statement_timeout={timeout_seconds * 1000}"
        )

    return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a strictly read-only SQL query.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sql", help="Inline SQL string.")
    group.add_argument("--sql-file", help="Path to a .sql file.")
    parser.add_argument("--params", default="{}", help="JSON object of bind parameters.")
    parser.add_argument("--explain", action="store_true", help="Prepend EXPLAIN to inspect the query plan.")
    parser.add_argument("--timeout", type=int, default=None, help="Query timeout in seconds.")
    parser.add_argument("--max-rows", type=int, default=None, help="Maximum rows to fetch.")
    parser.add_argument("--out", default=None, help="Output file path (.csv, .json, or .parquet).")
    args = parser.parse_args()

    load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
    timeout = args.timeout or int(os.getenv("DB_QUERY_TIMEOUT_SECONDS", "60"))
    max_rows = args.max_rows or int(os.getenv("DB_MAX_ROWS", "100000"))

    sql_text = args.sql if args.sql else Path(args.sql_file).read_text(encoding="utf-8")
    validate_read_only_sql(sql_text)

    if args.explain and not sql_text.lstrip().upper().startswith("EXPLAIN"):
        sql_text = f"EXPLAIN {sql_text}"

    params = json.loads(args.params)
    engine = build_engine(timeout)

    t0 = time.perf_counter()
    with engine.connect() as conn:
        result = conn.execute(text(sql_text), params)
        columns = list(result.keys())
        rows = result.fetchmany(max_rows + 1)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

    truncated = len(rows) > max_rows
    if truncated:
        rows = rows[:max_rows]

    df = pd.DataFrame(rows, columns=columns)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        ext = out_path.suffix.lower()
        if ext == ".csv":
            df.to_csv(out_path, index=False)
        elif ext == ".json":
            df.to_json(out_path, orient="records", indent=2, date_format="iso")
        elif ext == ".parquet":
            df.to_parquet(out_path, index=False)
        else:
            print(f"ERROR: Unsupported output extension '{ext}'. Use .csv, .json, or .parquet.", file=sys.stderr)
            return 1
        print(
            json.dumps(
                {
                    "status": "OK",
                    "rows": len(df),
                    "columns": columns,
                    "truncated": truncated,
                    "elapsed_ms": elapsed_ms,
                    "output": str(out_path),
                },
                indent=2,
            )
        )
    else:
        print(df.to_string(index=False, max_rows=50))
        print(f"\n[{len(df)} rows | truncated={truncated} | {elapsed_ms} ms]")

    return 0


if __name__ == "__main__":
    sys.exit(main())

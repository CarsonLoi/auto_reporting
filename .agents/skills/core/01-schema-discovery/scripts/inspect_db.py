#!/usr/bin/env python3
"""Read-only, warehouse-agnostic database catalog & empirical relationship profiler.

Reads credentials exclusively from `.env` (never prints secrets).
Supports:
  --summary                      List schemas, tables, dialect, and quote rules.
  --schema <name> --profile-all  Profile columns, sample rows, and enum values.
  --table <schema.table>         Profile a single table in detail.
  --check-unique <schema.table> --columns c1,c2
                                 Empirically test candidate key uniqueness.
  --test-join <left> <right> --on "left_col=right_col"
                                 Empirically test LEFT JOIN fanout ratio.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine


def build_engine() -> Engine:
    """Create a read-only SQLAlchemy engine from `.env`."""
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

    timeout = int(os.getenv("DB_QUERY_TIMEOUT_SECONDS", "60"))
    connect_args: dict[str, Any] = {}
    if database_url.startswith("postgresql"):
        connect_args["options"] = f"-c default_transaction_read_only=on -c statement_timeout={timeout * 1000}"

    return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)


def quote_ident(engine: Engine, ident: str) -> str:
    return engine.dialect.identifier_preparer.quote(ident)


def parse_table_ref(ref: str, default_schema: str | None) -> tuple[str | None, str]:
    if "." in ref:
        schema, table = ref.split(".", 1)
        return schema.strip('"[]`'), table.strip('"[]`')
    return default_schema, ref.strip('"[]`')


def qualified_name(engine: Engine, schema: str | None, table: str) -> str:
    if schema:
        return f"{quote_ident(engine, schema)}.{quote_ident(engine, table)}"
    return quote_ident(engine, table)


def limit_query(engine: Engine, base_sql: str, n: int) -> str:
    dialect = engine.dialect.name.lower()
    if "mssql" in dialect:
        return base_sql.replace("SELECT ", f"SELECT TOP {n} ", 1)
    return f"{base_sql} LIMIT {n}"


def cmd_summary(engine: Engine, schema_filter: str | None) -> dict[str, Any]:
    insp = inspect(engine)
    schemas = [schema_filter] if schema_filter else insp.get_schema_names()
    excluded = {"information_schema", "pg_catalog", "pg_toast", "sys", "mysql", "performance_schema"}
    result: dict[str, Any] = {
        "dialect": engine.dialect.name,
        "driver": engine.dialect.driver,
        "identifier_quote": engine.dialect.identifier_preparer.initial_quote,
        "schemas": {},
    }
    for sch in schemas:
        if sch.lower() in excluded:
            continue
        tables = insp.get_table_names(schema=sch)
        views = insp.get_view_names(schema=sch)
        if tables or views:
            result["schemas"][sch] = {"tables": tables, "views": views}
    return result


def profile_table(
    engine: Engine,
    schema: str | None,
    table: str,
    sample_rows: int = 5,
    max_enum_values: int = 25,
) -> dict[str, Any]:
    insp = inspect(engine)
    cols = insp.get_columns(table, schema=schema)
    pk = insp.get_pk_constraint(table, schema=schema)
    fks = insp.get_foreign_keys(table, schema=schema)
    qname = qualified_name(engine, schema, table)

    profile: dict[str, Any] = {
        "schema": schema,
        "table": table,
        "qualified_name": qname,
        "primary_key": pk.get("constrained_columns", []) if pk else [],
        "foreign_keys": fks,
        "columns": [],
        "row_count": None,
        "sample_rows": [],
    }

    with engine.connect() as conn:
        try:
            row_count = None
            if engine.dialect.name.lower() == "postgresql":
                est = conn.execute(
                    text(
                        "SELECT n_live_tup FROM pg_catalog.pg_stat_user_tables "
                        "WHERE schemaname = COALESCE(:sch, current_schema()) AND relname = :tbl"
                    ),
                    {"sch": schema, "tbl": table},
                ).scalar()
                if est is not None and int(est) > 0:
                    row_count = int(est)
                    profile["row_count_source"] = "pg_stat_user_tables.n_live_tup"
            if row_count is None:
                exact = conn.execute(text(f"SELECT COUNT(*) FROM {qname}")).scalar()
                row_count = int(exact) if exact is not None else None
                profile["row_count_source"] = "exact_count"
            profile["row_count"] = row_count
        except Exception as exc:
            profile["row_count_error"] = str(exc)

        try:
            sql = limit_query(engine, f"SELECT * FROM {qname}", sample_rows)
            res = conn.execute(text(sql))
            keys = list(res.keys())
            profile["sample_rows"] = [
                {k: (None if v is None else str(v)) for k, v in zip(keys, row)}
                for row in res.fetchall()
            ]
        except Exception as exc:
            profile["sample_rows_error"] = str(exc)

        for col in cols:
            cname = col["name"]
            ctype = str(col["type"])
            col_entry: dict[str, Any] = {
                "verbatim_name": cname,
                "quoted_name": quote_ident(engine, cname),
                "type": ctype,
                "nullable": bool(col.get("nullable", True)),
            }
            is_text_like = any(t in ctype.lower() for t in ("char", "text", "str", "enum", "bool"))
            if is_text_like and max_enum_values > 0:
                try:
                    qcol = quote_ident(engine, cname)
                    enum_sql = limit_query(
                        engine,
                        f"SELECT DISTINCT {qcol} FROM {qname} WHERE {qcol} IS NOT NULL ORDER BY 1",
                        max_enum_values + 1,
                    )
                    vals = [str(r[0]) for r in conn.execute(text(enum_sql)).fetchall()]
                    if len(vals) <= max_enum_values:
                        col_entry["distinct_values"] = vals
                    else:
                        col_entry["distinct_values_truncated"] = vals[:max_enum_values]
                except Exception:
                    pass
            profile["columns"].append(col_entry)

    return profile


def cmd_check_unique(engine: Engine, schema: str | None, table: str, columns: list[str]) -> dict[str, Any]:
    qname = qualified_name(engine, schema, table)
    quoted_cols = [quote_ident(engine, c.strip()) for c in columns]
    if len(quoted_cols) == 1:
        distinct_expr = f"COUNT(DISTINCT {quoted_cols[0]})"
    else:
        concat_expr = " || '|' || ".join(f"COALESCE(CAST({c} AS VARCHAR), '__NULL__')" for c in quoted_cols)
        distinct_expr = f"COUNT(DISTINCT ({concat_expr}))"

    sql = f"SELECT COUNT(*) AS total_rows, {distinct_expr} AS distinct_keys FROM {qname}"
    with engine.connect() as conn:
        row = conn.execute(text(sql)).mappings().first()
    total = int(row["total_rows"])
    distinct = int(row["distinct_keys"])
    return {
        "table": qname,
        "columns": columns,
        "total_rows": total,
        "distinct_keys": distinct,
        "is_unique": total == distinct,
        "duplicate_rows": total - distinct,
    }


def cmd_test_join(
    engine: Engine,
    left_ref: str,
    right_ref: str,
    on_expr: str,
    default_schema: str | None,
    sample_limit: int,
) -> dict[str, Any]:
    l_sch, l_tbl = parse_table_ref(left_ref, default_schema)
    r_sch, r_tbl = parse_table_ref(right_ref, default_schema)
    lq = qualified_name(engine, l_sch, l_tbl)
    rq = qualified_name(engine, r_sch, r_tbl)

    clauses = []
    for pair in on_expr.split(","):
        if "=" not in pair:
            raise ValueError(f"Invalid --on pair '{pair}'. Expected left_col=right_col.")
        lc, rc = [p.strip() for p in pair.split("=", 1)]
        clauses.append(f"l.{quote_ident(engine, lc)} = r.{quote_ident(engine, rc)}")
    join_cond = " AND ".join(clauses)

    left_sub = limit_query(engine, f"SELECT * FROM {lq}", sample_limit)
    sql = f"""
    WITH left_sample AS ({left_sub})
    SELECT
        (SELECT COUNT(*) FROM left_sample) AS left_rows,
        COUNT(*) AS joined_rows
    FROM left_sample l
    LEFT JOIN {rq} r ON {join_cond}
    """
    with engine.connect() as conn:
        row = conn.execute(text(sql)).mappings().first()
    left_rows = int(row["left_rows"])
    joined_rows = int(row["joined_rows"])
    fanout_ratio = round(joined_rows / left_rows, 4) if left_rows > 0 else 0.0
    return {
        "left_table": lq,
        "right_table": rq,
        "join_condition": join_cond,
        "left_sample_rows": left_rows,
        "joined_rows": joined_rows,
        "fanout_ratio": fanout_ratio,
        "fanout_detected": joined_rows > left_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only warehouse schema & join profiler.")
    parser.add_argument("--summary", action="store_true", help="List dialect, schemas, and tables.")
    parser.add_argument("--schema", default=None, help="Target schema name.")
    parser.add_argument("--profile-all", action="store_true", help="Profile all tables in --schema.")
    parser.add_argument("--table", default=None, help="Profile a single table (schema.table or table).")
    parser.add_argument("--sample-rows", type=int, default=5, help="Sample rows per table (default: 5).")
    parser.add_argument("--max-enum-values", type=int, default=25, help="Max distinct enum values per text column.")
    parser.add_argument("--check-unique", default=None, help="Check key uniqueness on schema.table.")
    parser.add_argument("--columns", default="", help="Comma-separated columns for --check-unique.")
    parser.add_argument("--test-join", nargs=2, metavar=("LEFT", "RIGHT"), help="Test LEFT JOIN fanout.")
    parser.add_argument("--on", dest="on_expr", default="", help="Join pairs: left_col=right_col[,...]")
    parser.add_argument("--sample-limit", type=int, default=10000, help="Left sample cap for --test-join.")
    parser.add_argument("--out", default=None, help="Optional JSON output file path.")
    args = parser.parse_args()

    engine = build_engine()
    default_schema = args.schema or os.getenv("DB_SCHEMA") or None

    if args.summary:
        output: Any = cmd_summary(engine, args.schema)
    elif args.table:
        sch, tbl = parse_table_ref(args.table, default_schema)
        output = profile_table(engine, sch, tbl, args.sample_rows, args.max_enum_values)
    elif args.profile_all:
        insp = inspect(engine)
        tables = insp.get_table_names(schema=default_schema)
        output = [
            profile_table(engine, default_schema, tbl, args.sample_rows, args.max_enum_values)
            for tbl in tables
        ]
    elif args.check_unique:
        if not args.columns:
            parser.error("--columns is required with --check-unique")
        sch, tbl = parse_table_ref(args.check_unique, default_schema)
        output = cmd_check_unique(engine, sch, tbl, args.columns.split(","))
    elif args.test_join:
        if not args.on_expr:
            parser.error("--on is required with --test-join")
        output = cmd_test_join(engine, args.test_join[0], args.test_join[1], args.on_expr, default_schema, args.sample_limit)
    else:
        parser.print_help()
        return 1

    rendered = json.dumps(output, indent=2, default=str)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        print(f"Wrote schema profile to {out_path}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())

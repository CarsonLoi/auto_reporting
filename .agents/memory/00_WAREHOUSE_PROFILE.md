# Warehouse Profile

> **Always read this file first before writing any SQL.**
> Maintained by `01-schema-discovery` and user configuration.

## Engine & Connection Metadata

| Property | Value | Notes |
| :--- | :--- | :--- |
| **Database Engine** | `PostgreSQL` | Standard PostgreSQL engine (confirmed by user) |
| **SQLAlchemy Dialect** | `postgresql+psycopg2` | Configured via `DATABASE_URL` or `DB_DIALECT=postgresql` in `.env` |
| **Default Schema(s)** | `public` *(verify via `inspect_db.py --summary`)* | Update once schemas are discovered |
| **Case Sensitivity** | Unquoted identifiers fold to `lowercase`; quoted identifiers are case-sensitive | Always quote mixed-case, space-containing, or reserved-word identifiers |
| **Read-Only Enforcement** | `STRICT` | Enforced both in client SQL validator (`SELECT`/`WITH`/`EXPLAIN` only) and server session option `default_transaction_read_only=on` |
| **Default Query Timeout** | `60s` | Enforced via server `statement_timeout=60000` (configurable via `DB_QUERY_TIMEOUT_SECONDS`) |

## Dialect Syntax Rules (PostgreSQL)

| Construct | PostgreSQL Syntax | Example |
| :--- | :--- | :--- |
| **Identifier Quoting** | Double quotes `"` | `"table min"`, `"Order Date"`, `"public"."sales"` |
| **Row Limit** | `LIMIT N` | `SELECT * FROM "public"."sales" LIMIT 5` |
| **Safe Division** | `1.0 * num / NULLIF(den, 0)` or `num::NUMERIC / NULLIF(den, 0)` | `SUM("net")::NUMERIC / NULLIF(SUM("gross"), 0)` |
| **Date Truncation** | `DATE_TRUNC('day'\|'week'\|'month', col)` | `DATE_TRUNC('month', "event_ts")` |
| **Date Arithmetic** | `col - INTERVAL '7 days'` / `col + INTERVAL '1 day'` | `CURRENT_DATE - INTERVAL '1 day'` |
| **Calendar Spine** | `generate_series(start_dt, end_dt, INTERVAL '1 day')::DATE` | Native zero-activity date spine |
| **Conditional Aggregation** | `SUM(x) FILTER (WHERE cond)` | `COUNT(*) FILTER (WHERE "status" = 'PAID')` |
| **String Concatenation** | `\|\|` or `CONCAT_WS(' ', a, b)` | `"first_name" \|\| ' ' \|\| "last_name"` |
| **Type Casting** | `::NUMERIC(18,4)` or `CAST(x AS NUMERIC(18,4))` | Prevents integer division truncation |
| **EXPLAIN Command** | `EXPLAIN (FORMAT TEXT)` | Inspects partition pruning, index scans, and join strategy |

## Catalog Discovery Strategy (PostgreSQL)

- **Primary Catalog:** `information_schema.tables`, `information_schema.columns`, and `pg_catalog.pg_stat_user_tables`.
- **Fast Row Count Estimate:** Query `pg_stat_user_tables.n_live_tup` first to avoid full sequential scans on large fact tables; fall back to `COUNT(*)` only when estimates are unavailable or exact filtered counts are required.
- **Partition / Index Inspection:** Check `pg_indexes` and `pg_inherits` / `pg_partitioned_table` during `01-schema-discovery`, and always filter on indexed/partitioned date columns in `base_filtered`.

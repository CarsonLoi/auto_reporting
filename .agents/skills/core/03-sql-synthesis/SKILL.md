---
name: 03-sql-synthesis
description: Write dialect-safe, read-only, anti-fanout modular CTE SQL and execute queries safely with timeouts and EXPLAIN verification.
---

# Skill 03: Dialect-Safe SQL Synthesis & Read-Only Execution

## Purpose
Synthesize accurate, performant, dialect-safe SQL queries using modular CTEs, execute them strictly read-only with timeouts and `EXPLAIN` verification, and save query results for validation and reporting.

## Prerequisites
- Read `.agents/memory/00_WAREHOUSE_PROFILE.md` and `.agents/memory/05_LESSONS_AND_QUIRKS.md`.
- Load only the required `02_DATA_DICTIONARY/domain_*.md`, `01_SCHEMA_TOPOLOGY.md`, `03_KPI_GLOSSARY.md`, `04_TIME_AND_CALENDAR.md`, and `06_GOLDEN_SQL_PATTERNS.md`.
- Consult `.agents/skills/vendor/postgres-best-practices/SKILL.md` for CTE tuning, indexing, and query optimization patterns.

## Mandatory SQL Engineering Rules

1. **Strictly Read-Only:** Only `SELECT`, `WITH ... SELECT`, or `EXPLAIN` statements.
2. **Verbatim Quoted Identifiers:** Quote physical table and column names exactly as recorded in `02_DATA_DICTIONARY/` using the quote character from `00_WAREHOUSE_PROFILE.md`.
3. **Modular 3-Stage CTE Architecture:**
   - `base_filtered`: Apply partition/date pruning and canonical base filters first.
   - `pre_aggregated`: Aggregate each event/fact table to the target grain **before** joining to another event table or dimension.
   - `final_joined`: `LEFT JOIN` to verified 1:1 dimensions and compute ratio-of-sums KPIs.
4. **Dimension Spines:** When reporting across fixed dates, stores, tables, or categories, build a calendar × dimension spine and `LEFT JOIN` pre-aggregated metrics so zero-activity rows never disappear.
5. **Defensive Math & Ratio-of-Sums:**
   - Always use `1.0 * SUM(num) / NULLIF(SUM(den), 0)` (never `AVG(pct)` and never unguarded division).
   - Cast integer numerators to `NUMERIC` / `DOUBLE PRECISION`.
6. **Never `SELECT *` in Final Report Queries:** Explicitly project and alias every output column.

## Execution & EXPLAIN Verification

1. **Check the query plan first on large tables:**
   ```bash
   uv run python .agents/skills/core/03-sql-synthesis/scripts/run_query.py --sql-file "output/query.sql" --explain
   ```
   Verify partition pruning and absence of accidental Cartesian joins.

2. **Execute read-only and export structured output:**
   ```bash
   uv run python .agents/skills/core/03-sql-synthesis/scripts/run_query.py --sql-file "output/query.sql" --out "output/query_result.csv" --timeout 60
   ```
   Supported output formats: `.csv`, `.json`, `.parquet` (inferred from `--out` extension).

3. **Proceed immediately to `04-numbers-validation`** before showing any numbers to the user.

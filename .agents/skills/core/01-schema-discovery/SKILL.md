---
name: 01-schema-discovery
description: Warehouse-agnostic, strictly read-only schema profiling, empirical relationship inference, and join fanout verification.
---

# Skill 01: Schema Discovery & Empirical Relationship Mapping

## Purpose
Connect to any relational data warehouse in strictly read-only mode, discover schemas, tables, and verbatim column names without assuming `fact_*`/`dim_*` prefixes or uniform naming, empirically verify candidate join keys and cardinality, and persist findings into `.agents/memory/`.

## Prerequisites
- `.env` configured with read-only database credentials.
- Read `.agents/memory/00_WAREHOUSE_PROFILE.md` first.

## Workflow

### Step 1: Detect Warehouse Dialect & Catalog Metadata
Run the read-only profiler to inspect schemas, tables, and dialect metadata:
```bash
uv run python .agents/skills/core/01-schema-discovery/scripts/inspect_db.py --summary
```
Record engine type, identifier quote character (`"`, `` ` ``, or `[]`), row-limit syntax (`LIMIT` vs `TOP`), and default schema in `.agents/memory/00_WAREHOUSE_PROFILE.md`.

### Step 2: Profile Tables, Verbatim Columns, Sample Rows & Enums
For each schema or target table (never assume prefixes):
```bash
uv run python .agents/skills/core/01-schema-discovery/scripts/inspect_db.py --schema <schema> --profile-all --sample-rows 5 --max-enum-values 25
```
Capture:
- Exact verbatim table and column names (preserving spaces, mixed case, symbols like `"table min"`).
- Data types and nullability.
- 5 representative sample rows per table.
- Distinct categorical/enum values for low-cardinality text/code columns.
- Candidate date/partition/freshness columns and estimated row counts.

### Step 3: Empirical Key Uniqueness & Join Fanout Testing
Never assume foreign-key constraints exist in analytics warehouses. Empirically test candidate joins:
1. Check key uniqueness (`COUNT(*)` vs `COUNT(DISTINCT key)`) on candidate primary keys:
   ```bash
   uv run python .agents/skills/core/01-schema-discovery/scripts/inspect_db.py --check-unique <schema>.<table> --columns <col1,col2>
   ```
2. Test join fanout (`LEFT JOIN` row count vs base row count) before marking any join `VERIFIED`:
   ```bash
   uv run python .agents/skills/core/01-schema-discovery/scripts/inspect_db.py --test-join <left_table> <right_table> --on "<left_col>=<right_col>"
   ```
   - If `joined_rows > left_rows`, flag as a **1:N / M:N Fanout Hazard** in `01_SCHEMA_TOPOLOGY.md` and document the required pre-aggregation or SCD2 active filter.

### Step 4: Persist Findings to Memory Vault
1. Update `.agents/memory/00_WAREHOUSE_PROFILE.md`.
2. Upsert `.agents/memory/02_DATA_DICTIONARY/_table_index.md` with every discovered table, grain, row count, and domain shard pointer.
3. Create/update domain-sharded files `.agents/memory/02_DATA_DICTIONARY/domain_<name>.md` with verbatim column names, types, aliases, enums, and quirks.
4. Upsert `.agents/memory/01_SCHEMA_TOPOLOGY.md` with a Mermaid `erDiagram`, Verified Join Matrix, and Known Fanout Hazards.
5. Run `06-memory-consolidation` to update `00_MEMORY_INDEX.md` and emit the Memory Diff.

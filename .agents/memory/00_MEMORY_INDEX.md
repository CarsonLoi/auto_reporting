# Memory Vault Index

Master Table of Contents for `.agents/memory/`. Updated via targeted upserts by `06-memory-consolidation`.

## Vault Map

| File | Scope | Status | Last Updated |
| :--- | :--- | :--- | :--- |
| [00_WAREHOUSE_PROFILE.md](00_WAREHOUSE_PROFILE.md) | SQL dialect, quoting rules, catalog views, limits | Configured (PostgreSQL) | 2026-11-22 |
| [01_SCHEMA_TOPOLOGY.md](01_SCHEMA_TOPOLOGY.md) | Mermaid ER diagram, verified join matrix, fanout hazards | Uninitialized | 2026-11-22 |
| [02_DATA_DICTIONARY/_table_index.md](02_DATA_DICTIONARY/_table_index.md) | Master table list, grain, row counts, domain pointers | Uninitialized | 2026-11-22 |
| [03_KPI_GLOSSARY.md](03_KPI_GLOSSARY.md) | Canonical KPI SQL formulas, filters, ratio-of-sums | Uninitialized | 2026-11-22 |
| [04_TIME_AND_CALENDAR.md](04_TIME_AND_CALENDAR.md) | Operational day cutoffs, fiscal calendar, YoY/WoW rules | Uninitialized | 2026-11-22 |
| [05_LESSONS_AND_QUIRKS.md](05_LESSONS_AND_QUIRKS.md) | Solved SQL bugs, dirty data traps, permanent fixes | Initialized | 2026-11-22 |
| [06_GOLDEN_SQL_PATTERNS.md](06_GOLDEN_SQL_PATTERNS.md) | Verified reusable CTEs & dimension spines | Configured (PostgreSQL) | 2026-11-22 |
| [07_REPORT_BLUEPRINTS/_blueprint_catalog.md](07_REPORT_BLUEPRINTS/_blueprint_catalog.md) | Registry of learned reports & backtest status | Uninitialized | 2026-11-22 |
| [08_VIZ_STANDARDS.md](08_VIZ_STANDARDS.md) | Color palette, typography, chart selection rules | Initialized | 2026-11-22 |

---

## Rolling Changelog (Last 10 Entries)

| Date | Skill | Summary of Upsert |
| :--- | :--- | :--- |
| 2026-11-22 | 06-memory-consolidation | Configured `00_WAREHOUSE_PROFILE.md` and `06_GOLDEN_SQL_PATTERNS.md` for PostgreSQL dialect. |
| 2026-11-22 | Bootstrap | Initialized starter Memory Vault templates. |

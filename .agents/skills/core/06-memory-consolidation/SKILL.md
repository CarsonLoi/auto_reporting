---
name: 06-memory-consolidation
description: Mandatory post-task memory upsert workflow that keeps .agents/memory/ concise, accurate, and Git-tracked, and emits a Knowledge Committed to Memory diff block.
---

# Skill 06: Memory Consolidation (Mandatory Post-Task Upsert)

## Purpose
Ensure the agent continuously self-improves without bloating local LLM context. After every task that uncovers new warehouse metadata, verified joins, KPI definitions, calendar cutoffs, SQL quirks, golden patterns, or report blueprints, consolidate findings into `.agents/memory/` via **targeted upserts**.

## Rules for Targeted Upserts

1. **Edit in Place — Never Append Blindly:**
   - If a table, join, KPI, or quirk already exists, update the existing row/section in place rather than adding duplicates.
2. **Keep Entries Concise:**
   - `05_LESSONS_AND_QUIRKS.md`: Strictly `Symptom -> Root Cause -> Permanent Fix`, max 3 lines per entry.
   - `02_DATA_DICTIONARY/`: Shard by domain (`domain_<name>.md`) and keep `_table_index.md` to 1 line per table.
   - `00_MEMORY_INDEX.md`: Maintain a **rolling last-10 changelog** (drop entries older than the 10 most recent).
3. **Verify Before Writing:**
   - Only mark joins `VERIFIED` in `01_SCHEMA_TOPOLOGY.md` if empirically tested.
   - Only mark blueprints `VERIFIED` in `07_REPORT_BLUEPRINTS/_blueprint_catalog.md` if 100% historical backtest passed.
4. **Never Store Secrets or Raw PII:**
   - Never write credentials, connection strings, or sensitive customer PII rows into `.agents/memory/`.

## Upsert Checklist

- [ ] New dialect/quoting/limit behavior → `00_WAREHOUSE_PROFILE.md`
- [ ] New verified joins or fanout hazards → `01_SCHEMA_TOPOLOGY.md`
- [ ] New tables/columns/enums → `02_DATA_DICTIONARY/_table_index.md` + `domain_<name>.md`
- [ ] New/refined KPI SQL formulas → `03_KPI_GLOSSARY.md`
- [ ] New business-day cutoffs / calendar rules → `04_TIME_AND_CALENDAR.md`
- [ ] Solved SQL bugs / dirty data traps → `05_LESSONS_AND_QUIRKS.md`
- [ ] Reusable verified CTEs → `06_GOLDEN_SQL_PATTERNS.md`
- [ ] Learned sample reports → `07_REPORT_BLUEPRINTS/_blueprint_catalog.md` + `<id>_blueprint.md`
- [ ] Updated index & rolling last-10 changelog → `00_MEMORY_INDEX.md`

## Mandatory Chat Output Format

At the end of your response, include this exact summary block:

```markdown
### 🧠 Knowledge Committed to Memory
- **Updated:** `<file_path>` — <1-line summary of upsert>
- **Updated:** `.agents/memory/00_MEMORY_INDEX.md` — Recorded changelog entry.
```

If no new durable knowledge was discovered during a routine re-run, state:
> **🧠 Knowledge Committed to Memory:** No schema, KPI, or quirk changes detected; Memory Vault unchanged.

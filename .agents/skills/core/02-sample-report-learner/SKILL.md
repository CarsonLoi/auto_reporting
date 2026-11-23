---
name: 02-sample-report-learner
description: Reverse-engineer user-supplied sample reports (.xlsx, .pdf, .csv, .html), map database lineage, run mandatory 100% historical backtest, and save reusable Report Blueprints.
---

# Skill 02: Sample Report Learner & Historical Backtest

## Purpose
Ingest existing sample reports dropped into `references/`, extract their exact structure, styling, live Excel formulas, and cached values, synthesize parameterized SQL, and prove **100% numerical parity** ($\pm 0.01$) against historical database records before saving a reusable Report Blueprint.

## Prerequisites
- Sample report placed in `references/`.
- Schema mapped via `01-schema-discovery`.
- Consult vendor skills as needed:
  - `.agents/skills/vendor/xlsx/SKILL.md` for Excel formula/layout conventions.
  - `.agents/skills/vendor/pdf/SKILL.md` for PDF table extraction.
  - `.agents/skills/vendor/systematic-debugging/SKILL.md` for diagnosing backtest mismatches.

## Workflow

### Step 1: Deconstruct the Sample Report
Run the parser on the reference file:
```bash
uv run python .agents/skills/core/02-sample-report-learner/scripts/parse_reference_report.py "references/<sample_file>" --out "output/parsed_<report_id>.json"
```
Inspect the extracted JSON for:
- Sheet names, headers, merged cells, freeze panes, column widths, number formats, fonts, and fill colors.
- **Both** live formulas (`data_only=False`) and cached numeric values (`data_only=True`) for `.xlsx`.
- Exact date range, filters, groupings, subtotal/grand-total rows, and ratio-of-sums formulas.

### Step 2: Map Columns & KPIs to Database Lineage
- Cross-reference report headers and sample values against `.agents/memory/02_DATA_DICTIONARY/_table_index.md` and relevant `domain_*.md` shards.
- Identify operational business-day cutoffs (e.g., 06:00–05:59), timezone shifts, soft-delete/void exclusions, and currency/unit conversions.
- Draft parameterized SQL following `03-sql-synthesis`.

### Step 3: Mandatory 100% Historical Backtest
1. Execute the synthesized SQL for the **exact date range** shown in the sample report via `03-sql-synthesis/scripts/run_query.py`.
2. Compare every metric cell and grand total against the sample report's cached values.
3. **Zero-Tolerance Rule:** Every figure must match within $\pm 0.01$ (rounding tolerance).
4. **If ANY mismatch occurs:**
   - Do **NOT** rationalize or approximate it away.
   - Invoke `.agents/skills/vendor/systematic-debugging/SKILL.md` (4-phase root-cause tracing):
     - Check business-day cutoff / timezone offset.
     - Check hidden filters (voids, test accounts, cancelled statuses, internal transfers).
     - Check join fanout or missing zero-activity dimension rows.
     - Check ratio-of-sums vs average-of-ratios.
   - Iterate until 100% parity is empirically verified.

### Step 4: Persist the Report Blueprint & Memory
1. Create `.agents/memory/07_REPORT_BLUEPRINTS/<report_id>_blueprint.md` (following `_blueprint_template.md`) with:
   - Full visual layout, styling palette, number formats, and live Excel formula mappings.
   - Parameterized verified SQL.
   - Reconciliation invariants and backtest evidence (`Max Delta: 0.00`).
2. Register the blueprint in `.agents/memory/07_REPORT_BLUEPRINTS/_blueprint_catalog.md` as `VERIFIED`.
3. Upsert newly confirmed KPIs into `03_KPI_GLOSSARY.md`, calendar cutoffs into `04_TIME_AND_CALENDAR.md`, and any discovered traps into `05_LESSONS_AND_QUIRKS.md`.
4. Run `06-memory-consolidation`.

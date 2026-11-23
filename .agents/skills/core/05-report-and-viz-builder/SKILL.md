---
name: 05-report-and-viz-builder
description: Render executive Excel workbooks (with live formulas), interactive Plotly HTML dashboards, publication-grade Matplotlib/Seaborn figures, and PDF briefs into output/ with post-render QA.
---

# Skill 05: Report & Visualization Builder

## Purpose
Transform validated datasets into executive-ready deliverables in `output/`—preserving native Excel formulas, applying corporate visual standards from `.agents/memory/08_VIZ_STANDARDS.md`, running programmatic post-render QA, and writing concise Executive Highlights.

## Prerequisites
- Dataset has passed all 5 gates in `04-numbers-validation`.
- Read `.agents/memory/08_VIZ_STANDARDS.md` and (if applicable) `.agents/memory/07_REPORT_BLUEPRINTS/<report_id>_blueprint.md`.
- Consult vendor skills as appropriate:
  - `.agents/skills/vendor/xlsx/SKILL.md` — Excel formulas, formatting, column auto-fit, freeze panes.
  - `.agents/skills/vendor/data-visualization/SKILL.md` — Executive BI Plotly dashboards.
  - `.agents/skills/vendor/scientific-visualization/SKILL.md` — Publication-grade Matplotlib/Seaborn figures.
  - `.agents/skills/vendor/statsmodels/SKILL.md` — Statistical models, regressions, forecasting.
  - `.agents/skills/vendor/pdf/SKILL.md` — PDF export and layout.

## Deliverable Standards

### 1. Executive Excel Workbooks (`.xlsx`)
- Use live Excel formulas (`=SUM(...)`, `=IFERROR(num/den, 0)`) on all totals, subtotals, and ratio columns—never hardcode calculated totals.
- Apply header styling (`#1B365D` navy fill, white bold font), zebra striping (`#F8FAFC`), explicit number formats (`$#,##0`, `#,##0`, `0.0%`), freeze panes on header row, auto-filter, and auto-fitted column widths with padding.

### 2. Interactive HTML Dashboards (`.html`)
- Self-contained responsive HTML with KPI summary cards, interactive Plotly charts (hover tooltips with exact figures, zero-baseline on bars, compact K/M/B axis labels), and a clean executive summary table.

### 3. Static Figures & PDF Briefs (`.png` / `.pdf`)
- Export static figures at `300 DPI`, clean typography, removed top/right spines, and clear title + date-range subtitle.

## CLI Renderer Usage

```bash
# Excel workbook with live SUM totals & styling
uv run python .agents/skills/core/05-report-and-viz-builder/scripts/render_deliverable.py \
  --mode excel \
  --input "output/query_result.csv" \
  --output "output/executive_report.xlsx" \
  --title "Monthly Performance Report" \
  --sum-cols "revenue,cost,gross_margin"

# Interactive HTML dashboard (KPI cards + Plotly chart + table)
uv run python .agents/skills/core/05-report-and-viz-builder/scripts/render_deliverable.py \
  --mode html \
  --input "output/query_result.csv" \
  --output "output/dashboard.html" \
  --title "Monthly Performance Dashboard" \
  --x-col "business_date" \
  --y-cols "revenue,gross_margin"

# High-DPI static chart (PNG or PDF)
uv run python .agents/skills/core/05-report-and-viz-builder/scripts/render_deliverable.py \
  --mode chart \
  --input "output/query_result.csv" \
  --output "output/trend_chart.png" \
  --title "Revenue Trend" \
  --x-col "business_date" \
  --y-cols "revenue"
```

## Mandatory Post-Render QA & Executive Narrative
1. **Programmatic Re-Open QA:** Every generated `.xlsx` is re-opened via `openpyxl` to verify sheet names, row counts, formula presence, and zero Excel error tokens (`#DIV/0!`, `#REF!`, `#VALUE!`, `#NAME?`). HTML/PNG/PDF outputs are verified non-empty and structurally valid.
2. **Executive Highlights:** Present 3–5 concise, evidence-backed bullet points summarizing headline numbers, key drivers, variances, and any caveats/anomalies flagged in Gate 5.
3. **Proceed to `06-memory-consolidation`** if any new schema, KPI, or blueprint knowledge was learned.

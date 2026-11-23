# Autonomous Data Extraction, Analysis, Validation & Reporting Agent

A **local-first, warehouse-agnostic AI Data Engineering, Quantitative Analysis, and BI Reporting Agent** designed for the **Codex VS Code extension** (and compatible local LLM agent harnesses via Ollama or vLLM).

## Capabilities

1. **Warehouse-Agnostic Schema Discovery:** Connects in strictly read-only mode, inspects `information_schema` / system catalogs dynamically without assuming `fact_*`/`dim_*` prefixes, preserves verbatim physical identifiers (including spaces/special characters), and empirically tests join keys and cardinality.
2. **Sample Report Reverse-Engineering & Backtesting:** Parses user-supplied `.xlsx`, `.pdf`, `.csv`, and `.html` reports from `references/`, extracts live formulas, cached values, and styling, backtests synthesized SQL against historical records until numbers match 100%, and persists reusable Markdown Blueprints.
3. **Mandatory 5-Point Validation Gate:** Enforces ETL freshness checks, join fanout detection, un-joined control-total reconciliation ($\pm 0.01$), cross-tab/chart parity (ratio-of-sums), and anomaly/null scanning before any output ships.
4. **Executive Reporting & Statistical Analysis:** Generates formula-preserving Excel workbooks (`openpyxl`), interactive HTML dashboards (`plotly`), publication-grade figures (`matplotlib`/`seaborn`), PDF briefs, and statistical models (`statsmodels`).
5. **Git-Tracked Persistent Memory Vault:** Evolves `.agents/memory/` via structured upserts after every task so discovered schemas, KPIs, calendar cutoffs, and SQL quirks persist across sessions.

---

## Quick Start

### 1. Environment Setup
```bash
uv sync
cp .env.example .env
```
Edit `.env` with your **read-only** database credentials (never commit `.env`).

### 2. Configure Warehouse Profile
Update `.agents/memory/00_WAREHOUSE_PROFILE.md` with your SQL dialect (PostgreSQL, Yellowbrick, Snowflake, SQL Server, MySQL, SQLite, DuckDB, etc.) or ask the agent to detect it during `01-schema-discovery`.

### 3. Run Initial Schema Discovery
```bash
uv run python .agents/skills/core/01-schema-discovery/scripts/inspect_db.py --summary
```

### 4. Drop Sample Reports (Optional)
Place existing `.xlsx`, `.pdf`, `.csv`, or `.html` reports into `references/` and instruct the agent to run `02-sample-report-learner`.

---

## Project Structure

```text
.
├── AGENTS.md                                      # Master router & guardrails (auto-loaded by Codex)
├── README.md                                      # Project specification & bootstrap guide
├── .env.example                                   # Template for read-only DB credentials
├── .gitignore                                     # Excludes .env, output/, __pycache__, .venv/
├── pyproject.toml                                 # Locked Python dependencies for `uv sync`
├── .agents/
│   ├── memory/                                    # Persistent Markdown Knowledge Vault (Git-tracked)
│   │   ├── 00_MEMORY_INDEX.md
│   │   ├── 00_WAREHOUSE_PROFILE.md
│   │   ├── 01_SCHEMA_TOPOLOGY.md
│   │   ├── 02_DATA_DICTIONARY/
│   │   │   ├── _table_index.md
│   │   │   └── domain_template.md
│   │   ├── 03_KPI_GLOSSARY.md
│   │   ├── 04_TIME_AND_CALENDAR.md
│   │   ├── 05_LESSONS_AND_QUIRKS.md
│   │   ├── 06_GOLDEN_SQL_PATTERNS.md
│   │   ├── 07_REPORT_BLUEPRINTS/
│   │   │   ├── _blueprint_catalog.md
│   │   │   └── _blueprint_template.md
│   │   └── 08_VIZ_STANDARDS.md
│   └── skills/
│       ├── core/                                  # Custom workflow playbooks + Python CLI helpers
│       │   ├── 01-schema-discovery/
│       │   ├── 02-sample-report-learner/
│       │   ├── 03-sql-synthesis/
│       │   ├── 04-numbers-validation/
│       │   ├── 05-report-and-viz-builder/
│       │   └── 06-memory-consolidation/
│       └── vendor/                                # Offline-audited open-source skills
│           ├── xlsx/
│           ├── pdf/
│           ├── postgres-best-practices/
│           ├── verification-before-completion/
│           ├── systematic-debugging/
│           ├── scientific-visualization/
│           ├── statsmodels/
│           └── data-visualization/
├── references/                                    # Drop folder for user's sample reports
└── output/                                        # Generated reports, charts & audit logs
```

---

## Helper CLI Scripts

All helper scripts enforce read-only execution and read connection settings exclusively from `.env`:

- `inspect_db.py` — Read-only catalog discovery, column profiling, sample rows, distinct enum values, key uniqueness, and join fanout testing.
- `parse_reference_report.py` — Extracts Excel live formulas, cached values, styles, merged cells, PDF tables, CSV schemas, and HTML tables.
- `run_query.py` — Executes strictly read-only SQL (`SELECT`/`WITH`/`EXPLAIN`) with statement timeout, row limits, `EXPLAIN` support, and CSV/JSON/Parquet export.
- `audit_numbers.py` — Automated 5-Point Validation Gate (ETL freshness, join fanout, control-total reconciliation, cross-tab/chart parity, anomaly & null scan).
- `render_deliverable.py` — Builds formula-preserving Excel workbooks, interactive Plotly HTML dashboards, Matplotlib/Seaborn figures, and PDF briefs into `output/`.

---

## Bootstrap Prompt (For Re-Initializing on Any PC)

> *"Read `README.md` and autonomously initialize and prepare the entire project workspace—including `AGENTS.md`, the `.agents/` folder structure, starter memory markdowns, core skills with Python helper scripts, `pyproject.toml` via `uv`, and the audited vendor skills."*

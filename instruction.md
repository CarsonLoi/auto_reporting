# Autonomous Data Extraction, Analysis, Validation & Reporting Agent

## 1. Project Context & Vision

This project is a **local-first, warehouse-agnostic AI Data Engineering, Quantitative Analysis, and BI Reporting Agent** designed for the **Codex VS Code extension** (powered by local LLMs via Ollama or vLLM).

Its objective is to operate as an autonomous Senior Data Engineer and BI Analyst that can:
1. **Understand Any Relational Data Warehouse:** Connect in strictly read-only mode, discover schemas dynamically without assuming table prefixes (e.g., `fact_*`/`dim_*`) or uniform column names (handling spaces/special characters like `"table min"`), and empirically verify join keys and cardinality.
2. **Learn & Reproduce Existing Reports:** Ingest user-provided sample reports (`.xlsx`, `.pdf`, `.csv`, `.html`) from `references/`, reverse-engineer their layout, styling, and live formulas, backtest the SQL against historical database records until numbers match 100%, and persist reusable Markdown Blueprints.
3. **Validate Numbers Rigorously:** Enforce a mandatory **5-Point Validation Gate** (ETL freshness, join fanout detection, un-joined control total reconciliation, cross-tab/chart parity, and anomaly/null scanning) plus an empirical evidence gate before delivering any output.
4. **Analyze & Visualize Data:** Generate executive Excel workbooks (preserving native formulas), interactive Plotly/ECharts HTML dashboards, publication-grade Matplotlib/Seaborn figures, and statistical models (`statsmodels`).
5. **Continuously Self-Improve:** Maintain a Git-tracked **Markdown Memory Vault** that evolves via structured upserts after every task—recording newly discovered tables, KPI definitions, operational calendar cutoffs, and SQL quirks so the agent never repeats a mistake.

---

## 2. Complete Project Structure

```text
data-report-agent/
├── AGENTS.md                                      # Master router & guardrails (auto-loaded by Codex)
├── README.md                                      # Complete project specification & agent bootstrap guide
├── .env.example                                   # Template for read-only DB credentials
├── .gitignore                                     # Excludes .env, output/, __pycache__, .venv/
├── pyproject.toml                                 # Locked Python dependencies for `uv sync`
│
├── .agents/
│   ├── memory/                                    # PERSISTENT KNOWLEDGE VAULT (Git-tracked)
│   │   ├── 00_MEMORY_INDEX.md                     # Master TOC + rolling last-10 changelog
│   │   ├── 00_WAREHOUSE_PROFILE.md                # SQL dialect, quoting rules, catalog views, limits
│   │   ├── 01_SCHEMA_TOPOLOGY.md                  # Mermaid ER diagram, verified join matrix, fanout hazards
│   │   ├── 02_DATA_DICTIONARY/                    # Sharded by domain to protect local LLM context
│   │   │   ├── _table_index.md                    # 1-line summary of every table, grain & row count
│   │   │   └── domain_<name>.md                   # Verbatim column names, types, aliases, enums
│   │   ├── 03_KPI_GLOSSARY.md                     # Canonical KPI SQL formulas, filters, ratio-of-sums
│   │   ├── 04_TIME_AND_CALENDAR.md                # Operational day cutoffs, fiscal weeks, YoY/WoW rules
│   │   ├── 05_LESSONS_AND_QUIRKS.md               # Solved SQL bugs, dirty data traps, permanent fixes
│   │   ├── 06_GOLDEN_SQL_PATTERNS.md              # Verified, reusable CTEs & dimension spines
│   │   ├── 07_REPORT_BLUEPRINTS/                  # Learned templates from user sample reports
│   │   │   ├── _blueprint_catalog.md              # Registry of all learned reports & backtest status
│   │   │   └── <report_id>_blueprint.md           # Layout, styling, SQL lineage & reconciliation rules
│   │   └── 08_VIZ_STANDARDS.md                    # Color palette, typography, chart selection rules
│   │
│   └── skills/
│       ├── core/                                  # CUSTOM WORKFLOW SKILLS (Playbooks + CLI Helpers)
│       │   ├── 01-schema-discovery/
│       │   │   ├── SKILL.md                       # Warehouse-agnostic schema & relationship mapping
│       │   │   └── scripts/inspect_db.py          # Read-only catalog & sample-row profiler
│       │   ├── 02-sample-report-learner/
│       │   │   ├── SKILL.md                       # Reverse-engineer sample reports + historical backtest
│       │   │   └── scripts/parse_reference_report.py  # Extracts Excel formulas, cached values, styles, PDF tables
│       │   ├── 03-sql-synthesis/
│       │   │   ├── SKILL.md                       # Dialect-safe CTE writing, pre-aggregation, spines
│       │   │   └── scripts/run_query.py           # Read-only query runner with timeout & EXPLAIN
│       │   ├── 04-numbers-validation/
│       │   │   ├── SKILL.md                       # 5-point reconciliation, ETL freshness & chart parity
│       │   │   └── scripts/audit_numbers.py       # Automated control-total & cross-tab audit script
│       │   ├── 05-report-and-viz-builder/
│       │   │   ├── SKILL.md                       # Excel/HTML/PDF report & chart synthesis
│       │   │   └── scripts/render_deliverable.py  # openpyxl / Plotly / Matplotlib / WeasyPrint renderer
│       │   └── 06-memory-consolidation/
│       │       └── SKILL.md                       # Post-task upsert rules & Memory Diff reporting
│       │
│       └── vendor/                                # CHERRY-PICKED OPEN-SOURCE SKILLS (Offline-Audited)
│           ├── xlsx/SKILL.md                      # anthropics/skills (Excel formulas & structure)
│           ├── pdf/SKILL.md                       # anthropics/skills (PDF table extraction & export)
│           ├── postgres-best-practices/SKILL.md   # supabase/agent-skills (SQL tuning & indexing)
│           ├── verification-before-completion/SKILL.md  # obra/superpowers (Empirical evidence gate)
│           ├── systematic-debugging/SKILL.md      # obra/superpowers (4-phase root-cause tracing)
│           ├── scientific-visualization/SKILL.md  # K-Dense-AI/scientific-agent-skills (Publication charts)
│           ├── statsmodels/SKILL.md               # K-Dense-AI/scientific-agent-skills (Statistical modeling)
│           └── data-visualization/SKILL.md        # atlassian-labs/data-visualization-skill (Executive BI Plotly)
│
├── references/                                    # Drop folder for user's existing sample reports
└── output/                                        # Generated reports, charts & audit logs land here
```

---

## 3. Persistent Memory Vault Specification (`.agents/memory/`)

To prevent local LLM context rot, memory is split into modular files and updated via **targeted upserts** (editing existing rows/rules in place rather than blindly appending logs).

| Memory File | Purpose & Contents | Maintained By |
| :--- | :--- | :--- |
| **`00_MEMORY_INDEX.md`** | Master table of contents + rolling last-10 changelog entries. | Skill 06 |
| **`00_WAREHOUSE_PROFILE.md`** | Engine type (PostgreSQL, Yellowbrick, Snowflake, SQL Server, etc.), identifier quote char (`"`, `` ` ``, `[]`), row-limit syntax (`LIMIT` vs `TOP`), date/time syntax, and catalog strategy. | Skill 01 / User |
| **`01_SCHEMA_TOPOLOGY.md`** | Mermaid `erDiagram`, Verified Join Matrix (exact quoted join clauses, cardinality, SCD2 rules), and known fanout/chasm hazards. | Skill 01 / 06 |
| **`02_DATA_DICTIONARY/_table_index.md`** | Fast lookup of all discovered tables, grain, row counts, and pointers to `domain_*.md` files. | Skill 01 / 06 |
| **`02_DATA_DICTIONARY/domain_*.md`** | Sharded by domain. Stores **verbatim physical column names** (e.g., `"table min"`), types, nullability, human aliases/synonyms, actual sampled enum values, and quirks. | Skill 01 / 06 |
| **`03_KPI_GLOSSARY.md`** | Official KPI SQL formulas, mandatory base filters, ratio-of-sums rules, rounding, and display formats. | Skill 02 / 06 |
| **`04_TIME_AND_CALENDAR.md`** | Operational business-day cutoffs (e.g., 06:00–05:59), week start day, fiscal calendar, and YoY/WoW like-for-like comparison rules. | Skill 02 / 06 |
| **`05_LESSONS_AND_QUIRKS.md`** | Dated log of solved SQL traps and dirty data edge cases (`Symptom -> Root Cause -> Permanent Fix`, max 3 lines per entry). | Skill 03 / 04 / 06 |
| **`06_GOLDEN_SQL_PATTERNS.md`** | Verified, reusable CTE templates (dimension spines, rolling windows, YoY comparisons). | Skill 03 / 06 |
| **`07_REPORT_BLUEPRINTS/_blueprint_catalog.md`** | Registry of all learned reports, source reference files, and historical backtest verification status. | Skill 02 |
| **`07_REPORT_BLUEPRINTS/<id>_blueprint.md`** | Full visual layout, styling (colors, fonts, number formats), parameterized verified SQL, and reconciliation invariants. | Skill 02 |
| **`08_VIZ_STANDARDS.md`** | Corporate color palette, typography, zero-baseline rules, compact axis formatting, and chart selection standards. | Skill 05 / User |

---

## 4. Core Skills Specification (`.agents/skills/core/`)

1. **`01-schema-discovery`** (`SKILL.md` + `scripts/inspect_db.py`)
   - Queries `information_schema` / system catalogs in read-only mode.
   - Infers relationships empirically via normalized column-name overlap, key uniqueness checks (`COUNT(*)` vs `COUNT(DISTINCT key)`), and sample `LEFT JOIN` fanout tests—without assuming `fact_*`/`dim_*` prefixes.
   - Profiles 5 sample rows and distinct categorical values per table, persisting exact verbatim identifiers to `01_SCHEMA_TOPOLOGY.md` and `02_DATA_DICTIONARY/`.
2. **`02-sample-report-learner`** (`SKILL.md` + `scripts/parse_reference_report.py`)
   - Deconstructs sample reports in `references/` (`.xlsx` live formulas + cached values + styles, `.pdf` tables, `.csv`, `.html`).
   - Maps columns to database lineage and runs a **mandatory Historical Backtest** against the sample's date range.
   - Diagnoses any discrepancy (using `systematic-debugging`) until numbers match 100%, then saves `.agents/memory/07_REPORT_BLUEPRINTS/<report_id>_blueprint.md`.
3. **`03-sql-synthesis`** (`SKILL.md` + `scripts/run_query.py`)
   - Writes dialect-safe, modular CTEs (`base_filtered` → `pre_aggregated` → `final_joined`).
   - Enforces partition pruning, pre-aggregation before joining multiple event tables, dimension spines (`LEFT JOIN`) so zero-activity rows never disappear, and `NULLIF(..., 0)` defensive math.
4. **`04-numbers-validation`** (`SKILL.md` + `scripts/audit_numbers.py`)
   - **Mandatory 5-Point Validation Gate:**
     1. *ETL Freshness & Completeness Check* (halts if latest day has 0 rows or incomplete load).
     2. *Join Fanout Check* (verifies dimension joins did not inflate base row counts).
     3. *Un-Joined Control Total Reconciliation* (grouped report totals must match direct base-table sums within $\pm 0.01$).
     4. *Cross-Tab & Chart-to-Table Parity* (summary tabs match detail tabs; chart series match table numbers; all aggregate percentages use ratio-of-sums).
     5. *Anomaly & Null Integrity Scan* (zero `NaN`, `Inf`, `#DIV/0!`, `#REF!`; flags extreme outliers).
5. **`05-report-and-viz-builder`** (`SKILL.md` + `scripts/render_deliverable.py`)
   - Renders Excel workbooks (native `=SUM`/`=IFERROR` formulas, auto-fit columns, freeze panes), interactive Plotly/ECharts HTML dashboards, and high-DPI PDF briefs into `output/`.
   - Re-opens generated files programmatically for QA and outputs a concise 3–5 bullet Executive Highlights narrative.
6. **`06-memory-consolidation`** (`SKILL.md`)
   - Mandatory post-task skill. Upserts new schema facts, KPI formulas, and SQL quirks into `.agents/memory/`, updates `00_MEMORY_INDEX.md`, and prints a **"🧠 Knowledge Committed to Memory"** diff block in chat.

---

## 5. Required Vendor Skills Manifest (`.agents/skills/vendor/`)

Only copy these **8 specific, offline-safe open-source skill folders/files** into `.agents/skills/vendor/` (never install full repositories or telemetry-enabled plugin wrappers):

| Target Folder (`.agents/skills/vendor/...`) | Source GitHub Repository | Source Path | Role in Project | License |
| :--- | :--- | :--- | :--- | :--- |
| `xlsx/` | `anthropics/skills` | `skills/xlsx` | Reading/writing Excel workbooks & preserving live formulas | Apache 2.0 |
| `pdf/` | `anthropics/skills` | `skills/pdf` | Extracting tables from legacy PDF reports & generating PDFs | Apache 2.0 |
| `postgres-best-practices/` | `supabase/agent-skills` | `skills/supabase-postgres-best-practices` | SQL query optimization, indexing & CTE tuning (pure Markdown) | MIT |
| `verification-before-completion/` | `obra/superpowers` | `verification-before-completion/SKILL.md` | Enforces empirical evidence before declaring any task done | MIT |
| `systematic-debugging/` | `obra/superpowers` | `systematic-debugging/SKILL.md` | 4-phase root-cause tracing for SQL & backtest discrepancies | MIT |
| `scientific-visualization/` | `K-Dense-AI/scientific-agent-skills` | `scientific-skills/scientific-visualization` | Publication-grade multi-panel figures (Matplotlib/Seaborn) | MIT |
| `statsmodels/` | `K-Dense-AI/scientific-agent-skills` | `scientific-skills/statsmodels` | Statistical modeling, regression & time-series analysis | MIT |
| `data-visualization/` | `atlassian-labs/data-visualization-skill` | `SKILL.md` + `references/` | Executive BI charts & interactive dashboards (Plotly) | Apache 2.0 |

---

## 6. Root Router Specification (`AGENTS.md`)

`AGENTS.md` sits at the root of the workspace and governs every Codex session with:
- **Phase 1 (Progressive Context Loading):** Always read `00_WAREHOUSE_PROFILE.md` and `05_LESSONS_AND_QUIRKS.md` first; load only the relevant `domain_*.md`, `03_KPI_GLOSSARY.md`, `04_TIME_AND_CALENDAR.md`, `07_REPORT_BLUEPRINTS/`, or `08_VIZ_STANDARDS.md` files needed for the task.
- **Phase 2 (On-Demand Skill Activation):** Route tasks dynamically to `.agents/skills/core/*` and `.agents/skills/vendor/*`.
- **Non-Negotiable Guardrails:**
  1. Strictly read-only DB access (`SELECT` only; credentials exclusively from `.env`).
  2. Warehouse- and naming-agnostic SQL (verbatim quoted identifiers per `00_WAREHOUSE_PROFILE.md`).
  3. Zero unvalidated numbers (must pass `04-numbers-validation` + `verification-before-completion`).
  4. 100% historical backtest required for learned reference reports (use `systematic-debugging` on mismatches).
  5. Ratio-of-sums rule (`SUM(num) / NULLIF(SUM(denom), 0)`, never `AVG(pct)`).
  6. Mandatory post-task memory consolidation (`06-memory-consolidation`).

---

## 7. Agent Self-Bootstrap Specification (For the AI Agent)

> **Prompt to Initialize on Any PC in Codex VS Code:**
> *"Read `README.md` and autonomously initialize and prepare the entire project workspace—including `AGENTS.md`, the `.agents/` folder structure, starter memory markdowns, core skills with Python helper scripts, `pyproject.toml` via `uv`, and the audited vendor skills."*

When instructed to initialize this project, the AI agent must execute the following autonomously:

1. **Scaffold Directory Tree:** Create the complete directory layout defined in Section 2 (`references/`, `output/`, `.agents/memory/`, `.agents/memory/02_DATA_DICTIONARY/`, `.agents/memory/07_REPORT_BLUEPRINTS/`, `.agents/skills/core/`, `.agents/skills/vendor/`).
2. **Generate `AGENTS.md`:** Create the root `AGENTS.md` implementing the exact lifecycle, skill routing paths (`.agents/skills/core/` and `.agents/skills/vendor/`), and all 6 non-negotiable guardrails from Section 6.
3. **Generate Starter Memory Markdowns:** Create all 12 starter files in `.agents/memory/` with clean, warehouse-agnostic Markdown templates.
4. **Create Core Skills & Helper Scripts:** Write all 6 `SKILL.md` playbooks in `.agents/skills/core/` along with their read-only Python helper scripts (`inspect_db.py`, `parse_reference_report.py`, `run_query.py`, `audit_numbers.py`, `render_deliverable.py`).
5. **Prepare Python Environment:** Create `.gitignore` (excluding `.env`, `output/`, `.venv/`, `__pycache__/`), `.env.example` (for read-only DB connection parameters), and `pyproject.toml` (including `pandas`, `polars`, `openpyxl`, `pypdf`, `sqlalchemy`, `psycopg2-binary`, `plotly`, `matplotlib`, `seaborn`, `statsmodels`, `jinja2`, `python-dotenv`), then run `uv sync`.
6. **Fetch & Security-Audit Vendor Skills:** Download only the 8 specific vendor skill folders/files listed in Section 5 into `.agents/skills/vendor/`. Immediately run a static security scan across `.agents/skills/vendor/`:
   ```bash
   grep -rnE "http://|https://|curl |wget |requests\.|urllib|fetch\(|socket\.|eval\(|exec\(|\.env|os\.environ" .agents/skills/vendor/
   ```
   Verify zero unauthorized outbound network calls, telemetry, or credential harvesting, and report the audit results.
7. **Confirm Readiness:** Output a concise readiness checklist of created files and environment status, then prompt the user to provide their `.env` read-only DB connection details and warehouse dialect to begin `01-schema-discovery`.
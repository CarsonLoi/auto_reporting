# Autonomous Data Extraction, Analysis, Validation & Reporting Agent — Complete Specification (`v2`)

> **Purpose of this Document:** This is the complete, as-built technical blueprint and handoff guide for migrating, reviewing, or re-bootstrapping this project on a new PC using the **Codex VS Code extension** (powered by local LLMs via Ollama/vLLM or cloud models). Reading this file gives any new Codex session full situational awareness of the entire repository, architecture, PostgreSQL configuration, CLI tooling, audited vendor skills, and operating guardrails.

---

## 1. Project Context & Vision

This workspace implements a **local-first, PostgreSQL-configured (warehouse-agnostic) AI Data Engineering, Quantitative Analysis, and BI Reporting Agent** designed for **Codex VS Code**.

Its core capabilities are:
1. **Strictly Read-Only Schema & Relationship Discovery:** Connects to PostgreSQL (or any SQLAlchemy-supported relational warehouse) in strictly read-only mode (`default_transaction_read_only=on`, `statement_timeout`, and client-side SQL validation), discovers schemas without assuming `fact_*`/`dim_*` prefixes, preserves verbatim physical identifiers (e.g., `"table min"`, `"Order Date"`), and empirically verifies key uniqueness and join fanout.
2. **Sample Report Reverse-Engineering & 100% Historical Backtesting:** Parses user-supplied `.xlsx`, `.pdf`, `.csv`, and `.html` reports from `references/`, extracts live Excel formulas + cached values + styles, maps database lineage, backtests synthesized SQL until numbers match **100% ($\pm 0.01$)**, and saves reusable Markdown Report Blueprints.
3. **Mandatory 5-Point Numbers Validation Gate:** Enforces ETL freshness checks, join fanout detection, un-joined control-total reconciliation ($\pm 0.01$), cross-tab & ratio-of-sums parity, and anomaly/null/Excel-error scanning before any number is delivered.
4. **Executive Deliverable & Visualization Synthesis:** Renders formula-preserving Excel workbooks (`openpyxl`), interactive HTML dashboards (`plotly` + `jinja2`), 300-DPI publication figures (`matplotlib`/`seaborn`), PDF reports, and statistical analyses (`statsmodels`) into `output/`, followed by programmatic post-render QA.
5. **Self-Improving Git-Tracked Memory Vault:** Evolves `.agents/memory/` via targeted in-place upserts after every task and reports a **"🧠 Knowledge Committed to Memory"** diff block so learned schemas, KPIs, calendar cutoffs, and SQL quirks persist across sessions and across PCs via Git.

---

## 2. Complete As-Built Project Structure

```text
Auto Report/
├── AGENTS.md                                      # Master router & guardrails (auto-loaded by Codex)
├── README.md                                      # Quick-start guide & CLI summary
├── instruction.md                                 # Original v1 project specification
├── instruction_v2.md                              # Complete as-built specification & New-PC handoff guide (this file)
├── .env.example                                   # Template for read-only PostgreSQL/DB credentials
├── .gitignore                                     # Excludes .env, .venv/, output/*, __pycache__/
├── pyproject.toml                                 # Python >=3.11 dependencies for `uv sync`
├── uv.lock                                        # Locked dependency resolution (43 packages)
│
├── .agents/
│   ├── memory/                                    # PERSISTENT KNOWLEDGE VAULT (Git-tracked, 12 files)
│   │   ├── 00_MEMORY_INDEX.md                     # Master TOC + rolling last-10 changelog
│   │   ├── 00_WAREHOUSE_PROFILE.md                # Configured for PostgreSQL (quoting, limits, catalog, timeouts)
│   │   ├── 01_SCHEMA_TOPOLOGY.md                  # Mermaid ER diagram, verified join matrix, fanout hazards
│   │   ├── 02_DATA_DICTIONARY/                    # Domain-sharded schema dictionary (protects LLM context)
│   │   │   ├── _table_index.md                    # 1-line summary of every table, grain & row count
│   │   │   └── domain_template.md                 # Template for creating `domain_<name>.md` shards
│   │   ├── 03_KPI_GLOSSARY.md                     # Canonical KPI SQL formulas, filters, ratio-of-sums rules
│   │   ├── 04_TIME_AND_CALENDAR.md                # Business-day cutoffs, fiscal calendar, YoY/WoW rules
│   │   ├── 05_LESSONS_AND_QUIRKS.md               # Solved SQL traps (`Symptom -> Root Cause -> Permanent Fix`)
│   │   ├── 06_GOLDEN_SQL_PATTERNS.md              # PostgreSQL 3-stage CTE, `generate_series` spine, WoW/YoY
│   │   ├── 07_REPORT_BLUEPRINTS/                  # Learned templates from `references/`
│   │   │   ├── _blueprint_catalog.md              # Registry of learned reports & backtest status
│   │   │   └── _blueprint_template.md             # Template for `<report_id>_blueprint.md`
│   │   └── 08_VIZ_STANDARDS.md                    # Executive color palette, typography, zero-baseline rules
│   │
│   └── skills/
│       ├── core/                                  # 6 CUSTOM WORKFLOW SKILLS + 5 PYTHON CLI HELPERS
│       │   ├── 01-schema-discovery/
│       │   │   ├── SKILL.md
│       │   │   └── scripts/inspect_db.py
│       │   ├── 02-sample-report-learner/
│       │   │   ├── SKILL.md
│       │   │   └── scripts/parse_reference_report.py
│       │   ├── 03-sql-synthesis/
│       │   │   ├── SKILL.md
│       │   │   └── scripts/run_query.py
│       │   ├── 04-numbers-validation/
│       │   │   ├── SKILL.md
│       │   │   └── scripts/audit_numbers.py
│       │   ├── 05-report-and-viz-builder/
│       │   │   ├── SKILL.md
│       │   │   └── scripts/render_deliverable.py
│       │   └── 06-memory-consolidation/
│       │       └── SKILL.md
│       │
│       └── vendor/                                # 8 OFFLINE-AUDITED OPEN-SOURCE SKILLS (133 files total)
│           ├── xlsx/                              # 53 files — anthropics/skills
│           ├── pdf/                               # 12 files — anthropics/skills
│           ├── postgres-best-practices/           # 36 files — supabase/agent-skills
│           ├── verification-before-completion/    #  1 file  — obra/superpowers
│           ├── systematic-debugging/              #  1 file  — obra/superpowers
│           ├── scientific-visualization/          # 18 files — K-Dense-AI/scientific-agent-skills
│           ├── statsmodels/                       # 10 files — K-Dense-AI/scientific-agent-skills
│           └── data-visualization/                #  2 files — atlassian-labs/data-visualization-skill
│
├── references/                                    # Drop folder for user's sample reports (.gitkeep)
└── output/                                        # Generated reports, charts & audit logs (.gitkeep; gitignored)
```

---

## 3. Target Warehouse Configuration (PostgreSQL)

The workspace is pre-configured for **PostgreSQL (`postgresql+psycopg2`)** in `.agents/memory/00_WAREHOUSE_PROFILE.md`:

| Setting | Configured Value |
| :--- | :--- |
| **Engine / Dialect** | PostgreSQL (`postgresql+psycopg2`) |
| **Identifier Quoting** | Double quotes `"` for verbatim physical names (e.g., `"table min"`, `"Order Date"`) |
| **Row Limiting** | `LIMIT N` |
| **Safe Division** | `numerator::NUMERIC / NULLIF(denominator, 0)` |
| **Date & Spine Syntax** | `DATE_TRUNC(...)`, `INTERVAL '...'`, `generate_series(start, end, INTERVAL '1 day')::DATE`, `FILTER (WHERE ...)` |
| **Fast Row Counts** | `inspect_db.py` queries `pg_catalog.pg_stat_user_tables.n_live_tup` first on PostgreSQL to avoid slow full-table `COUNT(*)` scans, falling back to exact `COUNT(*)` only if unavailable |
| **Read-Only Enforcement** | Dual-layer: (1) client-side SQL AST/regex guardrail blocking all non-`SELECT`/`WITH`/`EXPLAIN` statements and multi-statement queries, and (2) server-side PostgreSQL connection options `-c default_transaction_read_only=on -c statement_timeout=<ms>` |

---

## 4. Persistent Memory Vault (`.agents/memory/`)

To prevent context rot on local LLMs, Codex loads memory **progressively**:
- **Always read first:** `00_WAREHOUSE_PROFILE.md` and `05_LESSONS_AND_QUIRKS.md`.
- **Read on demand:** Only the specific shards required for the active request.

| File | Role | Current Status |
| :--- | :--- | :--- |
| `00_MEMORY_INDEX.md` | Master TOC + rolling last-10 changelog | Active |
| `00_WAREHOUSE_PROFILE.md` | PostgreSQL dialect, quoting, catalog & timeout rules | **Configured (PostgreSQL)** |
| `01_SCHEMA_TOPOLOGY.md` | Mermaid `erDiagram`, Verified Join Matrix, Fanout Hazards | Ready for `01-schema-discovery` |
| `02_DATA_DICTIONARY/_table_index.md` | 1-line index of all discovered tables, grain & row counts | Ready for `01-schema-discovery` |
| `02_DATA_DICTIONARY/domain_template.md` | Blueprint for domain shards (`domain_<name>.md`) | Template ready |
| `03_KPI_GLOSSARY.md` | Official KPI SQL formulas, base filters & ratio-of-sums | Ready for discovery/backtest |
| `04_TIME_AND_CALENDAR.md` | Operational day cutoffs, timezones, fiscal & YoY/WoW rules | Ready for discovery/backtest |
| `05_LESSONS_AND_QUIRKS.md` | Dated `Symptom -> Root Cause -> Permanent Fix` entries (max 3 lines) | Seeded with global rules |
| `06_GOLDEN_SQL_PATTERNS.md` | PostgreSQL 3-stage CTE, `generate_series` spine, WoW/YoY | **Configured (PostgreSQL)** |
| `07_REPORT_BLUEPRINTS/_blueprint_catalog.md` | Registry of learned reference reports & backtest verdicts | Ready for `02-sample-report-learner` |
| `07_REPORT_BLUEPRINTS/_blueprint_template.md` | Template for `<report_id>_blueprint.md` | Template ready |
| `08_VIZ_STANDARDS.md` | Colorblind-safe executive palette, typography, zero-baseline rules | Configured |

---

## 5. Core Skills & Verified Python CLI Scripts (`.agents/skills/core/`)

All 5 Python helper scripts have been **smoke-tested end-to-end (`5/5 PASS`)** covering verbatim space-containing identifiers, read-only DDL blocking, 5-point auditing, Excel formula rendering + re-open QA, HTML/PNG rendering, and Excel parsing.

### 1. `01-schema-discovery` — `scripts/inspect_db.py`
Read-only catalog discovery, table profiling, key uniqueness verification, and join fanout testing.
```bash
# List schemas, tables, views & quote char
uv run python .agents/skills/core/01-schema-discovery/scripts/inspect_db.py --summary

# Profile all tables in a schema (5 sample rows + up to 25 distinct enum values per text col)
uv run python .agents/skills/core/01-schema-discovery/scripts/inspect_db.py --schema public --profile-all --sample-rows 5 --max-enum-values 25

# Profile a single table
uv run python .agents/skills/core/01-schema-discovery/scripts/inspect_db.py --table public.orders

# Empirically verify candidate key uniqueness (COUNT(*) vs COUNT(DISTINCT key))
uv run python .agents/skills/core/01-schema-discovery/scripts/inspect_db.py --check-unique public.orders --columns order_id

# Empirically test LEFT JOIN fanout ratio before marking a join VERIFIED
uv run python .agents/skills/core/01-schema-discovery/scripts/inspect_db.py --test-join public.order_items public.orders --on "order_id=order_id"
```

### 2. `02-sample-report-learner` — `scripts/parse_reference_report.py`
Extracts Excel live formulas (`data_only=False`), cached values (`data_only=True`), styles, merged cells, freeze panes, column widths, PDF tables (`pdfplumber`/`pypdf`), CSV schemas, and HTML tables (`BeautifulSoup`).
```bash
uv run python .agents/skills/core/02-sample-report-learner/scripts/parse_reference_report.py "references/<sample_file>" --out "output/parsed_report.json"
```

### 3. `03-sql-synthesis` — `scripts/run_query.py`
Strictly read-only SQL runner (`SELECT`, `WITH`, `EXPLAIN` only; blocks DML/DDL and multi-statement queries) with timeout, row cap, bind parameters, `EXPLAIN`, and `.csv`/`.json`/`.parquet` export.
```bash
# Inspect query plan first
uv run python .agents/skills/core/03-sql-synthesis/scripts/run_query.py --sql-file "output/query.sql" --explain

# Execute read-only and export to CSV/JSON/Parquet
uv run python .agents/skills/core/03-sql-synthesis/scripts/run_query.py --sql-file "output/query.sql" --params '{"start_date": "2026-11-01"}' --out "output/query_result.csv" --timeout 60
```

### 4. `04-numbers-validation` — `scripts/audit_numbers.py`
Automated **Mandatory 5-Point Validation Gate** (exits `0` only on full `PASS`; exits `2` on any `FAIL`):
1. **ETL Freshness & Completeness** (`--freshness-date-col`, `--expected-date`)
2. **Join Fanout Check** (`--pre-join-rows`, `--post-join-rows`)
3. **Un-Joined Control Total Reconciliation** (`--control-totals`, default tolerance `±0.01`)
4. **Cross-Tab & Ratio-of-Sums Parity** (`--summary-data`, `--ratio-checks`)
5. **Anomaly, Null & Excel Error Token Scan** (`NaN`, `Inf`, `#DIV/0!`, `#REF!`, `|z| > 4.0`)
```bash
uv run python .agents/skills/core/04-numbers-validation/scripts/audit_numbers.py \
  --data "output/query_result.csv" \
  --freshness-date-col "business_date" --expected-date "2026-11-22" \
  --pre-join-rows 1000 --post-join-rows 1000 \
  --control-totals '{"revenue": 125000.50}' \
  --ratio-checks '[{"name": "margin_pct", "num": "margin", "den": "revenue"}]' \
  --report-out "output/audit_report.json"
```

### 5. `05-report-and-viz-builder` — `scripts/render_deliverable.py`
Builds styled deliverables into `output/` and automatically runs post-render programmatic QA:
- `--mode excel`: Navy headers, zebra stripes, freeze panes, auto-filter, auto-fit widths, live `=SUM(...)` totals, re-opened via `openpyxl` to verify formulas & zero Excel error tokens.
- `--mode html`: Self-contained responsive dashboard with KPI cards, interactive Plotly chart, and formatted data table.
- `--mode chart`: 300-DPI Matplotlib figure with clean spines, zero-baseline bar charts, and executive palette.
```bash
uv run python .agents/skills/core/05-report-and-viz-builder/scripts/render_deliverable.py --mode excel --input "output/query_result.csv" --output "output/report.xlsx" --title "Executive Report" --sum-cols "revenue,cost,margin"
uv run python .agents/skills/core/05-report-and-viz-builder/scripts/render_deliverable.py --mode html --input "output/query_result.csv" --output "output/dashboard.html" --title "Executive Dashboard" --x-col "business_date" --y-cols "revenue,margin"
uv run python .agents/skills/core/05-report-and-viz-builder/scripts/render_deliverable.py --mode chart --input "output/query_result.csv" --output "output/trend.png" --title "Revenue Trend" --x-col "business_date" --y-cols "revenue"
```

### 6. `06-memory-consolidation` — `SKILL.md`
Mandatory post-task memory upsert workflow ensuring in-place updates, domain sharding, rolling 10-entry changelog maintenance, and the chat **"🧠 Knowledge Committed to Memory"** diff block.

---

## 6. Vendor Skills Manifest & Security Audit (`.agents/skills/vendor/`)

All 8 vendor skills are cherry-picked directly from upstream repositories (exact verified paths recorded below — no telemetry wrappers, no full-repo bloat):

| Target Folder (`.agents/skills/vendor/...`) | Upstream Repository | Verified Source Path | Files | Role | License |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `xlsx/` | `anthropics/skills` | `skills/xlsx` | 53 | Excel formulas, styling, recalc & validation | Apache 2.0 |
| `pdf/` | `anthropics/skills` | `skills/pdf` | 12 | PDF table extraction & PDF report export | Apache 2.0 |
| `postgres-best-practices/` | `supabase/agent-skills` | `skills/supabase-postgres-best-practices` | 36 | PostgreSQL indexing, query & CTE optimization | MIT |
| `verification-before-completion/` | `obra/superpowers` | `skills/verification-before-completion/SKILL.md` | 1 | Empirical evidence gate before claiming done | MIT |
| `systematic-debugging/` | `obra/superpowers` | `skills/systematic-debugging/SKILL.md` | 1 | 4-phase root-cause tracing for SQL/backtest bugs | MIT |
| `scientific-visualization/` | `K-Dense-AI/scientific-agent-skills` | `skills/scientific-visualization` | 18 | Publication-grade Matplotlib/Seaborn figures | MIT |
| `statsmodels/` | `K-Dense-AI/scientific-agent-skills` | `skills/statsmodels` | 10 | Statistical modeling, regression & time-series | MIT |
| `data-visualization/` | `atlassian-labs/data-visualization-skill` | `skills/visualization/SKILL.md` + `references/` | 2 | Executive BI charts & Plotly dashboards | Apache 2.0 |

### Static Security Audit Result (`PASS`)
Scanned across all 133 vendor files for `http://|https://|curl |wget |requests\.|urllib|fetch\(|socket\.|eval\(|exec\(|\.env|os\.environ`:
- **0** matches for `curl`, `wget`, `requests.`, `fetch(`, `eval(`, `exec(`, or `.env`.
- Only benign matches exist in executable scripts: OOXML/SVG XML namespace URI constants (`schemas.openxmlformats.org`, `w3.org/2000/svg`), academic color-palette citations in `scientific-visualization/assets/color_palettes.py`, `urllib.parse.unquote` for local `.zip` member paths, and local `os.environ.copy()` / `AF_UNIX` socket checks in `xlsx/scripts/office/soffice.py` for headless LibreOffice recalculation.

---

## 7. Governance & Non-Negotiable Guardrails (`AGENTS.md`)

`AGENTS.md` sits at the repository root and is auto-loaded by Codex on every session:
1. **Strictly Read-Only DB Access:** `SELECT`, `WITH ... SELECT`, and `EXPLAIN` only; credentials exclusively from `.env` (never hardcoded, printed, or committed).
2. **Warehouse- and Naming-Agnostic SQL:** Never assume `fact_*`/`dim_*` or snake_case; always quote physical identifiers verbatim per `00_WAREHOUSE_PROFILE.md`.
3. **Zero Unvalidated Numbers:** Every table, KPI, chart, and file must pass the **5-Point Validation Gate** (`04-numbers-validation`) + `verification-before-completion`.
4. **100% Historical Backtest for Sample Reports:** Learned reports from `references/` must match historical database numbers within $\pm 0.01$ before saving a blueprint; any mismatch triggers `systematic-debugging`.
5. **Ratio-of-Sums Rule:** All aggregate rates/percentages MUST be `SUM(numerator) / NULLIF(SUM(denominator), 0)` — never `AVG(pct)`.
6. **Mandatory Post-Task Memory Consolidation:** Upsert learned facts into `.agents/memory/` via `06-memory-consolidation` and emit the **"🧠 Knowledge Committed to Memory"** diff block.

---

## 8. Python Dependencies (`pyproject.toml`)

Managed via `uv` (`requires-python = ">=3.11"`):
- **Data & SQL:** `pandas`, `polars`, `sqlalchemy`, `psycopg2-binary`, `python-dotenv`, `tabulate`
- **Documents & Parsing:** `openpyxl`, `pypdf`, `pdfplumber`, `beautifulsoup4`, `lxml`
- **Visualization & Stats:** `plotly`, `matplotlib`, `seaborn`, `statsmodels`, `jinja2`

---

## 9. New PC Setup & Codex VS Code Migration Guide

### Scenario A: Moving This Complete Repository to a New PC (Recommended)
1. **Prerequisites on New PC:** Install Python 3.11+, [`uv`](https://docs.astral.sh/uv/), Git, and the **Codex VS Code extension**.
2. **Transfer Repository:** Clone from your Git remote (or copy the entire folder excluding `.venv/` and `.env`).
3. **Restore Environment:**
   ```bash
   uv sync
   cp .env.example .env
   ```
4. **Configure PostgreSQL Credentials:** Edit `.env` with your **read-only** PostgreSQL user (`DATABASE_URL` or `DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD`).
5. **Drop Sample Reports (Optional):** Copy existing `.xlsx`/`.pdf`/`.csv`/`.html` reports into `references/`.
6. **Open in VS Code (Codex Extension) and Run This First Prompt:**
   > *"Read `AGENTS.md`, `instruction_v2.md`, `.agents/memory/00_WAREHOUSE_PROFILE.md`, and `.agents/memory/05_LESSONS_AND_QUIRKS.md`. Confirm the environment is ready, then run `01-schema-discovery` (`inspect_db.py --summary`) against my PostgreSQL database configured in `.env` and populate `.agents/memory/`."*

### Scenario B: Bootstrapping From Scratch on a New PC Using Only `instruction_v2.md`
If you only copy `instruction_v2.md` to a brand-new folder, give Codex this prompt:
> *"Read `instruction_v2.md` and autonomously scaffold the entire workspace—including `AGENTS.md`, `README.md`, `.env.example`, `.gitignore`, `pyproject.toml` (synced via `uv sync`), the 12 `.agents/memory/` files configured for PostgreSQL, all 6 `.agents/skills/core/` playbooks + 5 Python CLI helpers, and the 8 audited vendor skills from their verified upstream paths in Section 6. Run the static security scan and an end-to-end smoke test of all 5 scripts, then confirm readiness."*

---
name: 04-numbers-validation
description: Mandatory 5-Point Validation Gate for ETL freshness, join fanout detection, un-joined control-total reconciliation, cross-tab/chart parity, and anomaly/null scanning.
---

# Skill 04: Numbers Validation (Mandatory 5-Point Validation Gate)

## Purpose
Guarantee zero unvalidated numbers ever reach the user. Every dataset, KPI, table, chart, and report MUST pass all 5 gates below **and** `.agents/skills/vendor/verification-before-completion/SKILL.md` before delivery.

## The Mandatory 5-Point Validation Gate

### Gate 1: ETL Freshness & Completeness Check
- Verify the latest expected business date in the target base table has `row_count > 0` and is not an incomplete partial load (compare latest day's row count against trailing 7-day median; flag if `< 50%` unless intraday was explicitly requested).
- **HALT** if the latest expected date has 0 rows.

### Gate 2: Join Fanout Detection
- Compare base-table row count (post-filter, pre-join) against post-join row count (pre-aggregation).
- **HALT** if `post_join_rows > pre_join_rows` (indicates a 1:N / M:N dimension join bug or missing SCD2 active filter).

### Gate 3: Un-Joined Control Total Reconciliation ($\pm 0.01$)
- Run a direct, un-joined `SELECT SUM(metric)` on the base table with the exact same date range and base filters.
- Reconcile against the sum of the grouped report output.
- **HALT** if `|report_total - control_total| > 0.01`.

### Gate 4: Cross-Tab & Chart-to-Table Parity (Ratio-of-Sums)
- Verify every summary tab grand total equals the detail tab grand total ($\pm 0.01$).
- Verify every chart series matches its underlying table values exactly.
- Verify all aggregate percentages/rates equal `SUM(numerator) / SUM(denominator)` (never `AVG(pct)`).

### Gate 5: Anomaly & Null Integrity Scan
- Scan every numeric output column for `NaN`, `Inf`, `-Inf`, `#DIV/0!`, `#REF!`, `#VALUE!`, `#NAME?`, or unexpected `NULL`s.
- Flag extreme statistical outliers (`|z-score| > 4.0` or sudden sign flips) for human review.

## Automated Audit Execution

Run the validation script against your dataset and audit configuration:
```bash
uv run python .agents/skills/core/04-numbers-validation/scripts/audit_numbers.py \
  --data "output/query_result.csv" \
  --control-totals '{"revenue": 125000.50, "units": 4120}' \
  --ratio-checks '[{"name": "margin_pct", "num": "gross_margin", "den": "revenue"}]' \
  --report-out "output/audit_report.json"
```
Optional flags:
- `--summary-data "output/summary_result.csv"` for Cross-Tab Parity (Gate 4).
- `--freshness-table "<schema>.<table>" --freshness-date-col "<col>" --expected-date "YYYY-MM-DD"` for live DB ETL Freshness Check (Gate 1).
- `--pre-join-rows <N> --post-join-rows <M>` for Join Fanout Check (Gate 2).
- `--tolerance 0.01` (default `0.01`).

## Failure Protocol
If **any** gate exits with `FAIL`:
1. Do **NOT** deliver the report or present numbers as final.
2. Invoke `.agents/skills/vendor/systematic-debugging/SKILL.md` to trace and fix the root cause.
3. Re-run `audit_numbers.py` until all 5 gates report `PASS`.
4. Record any newly discovered SQL trap or dirty data quirk in `.agents/memory/05_LESSONS_AND_QUIRKS.md`.

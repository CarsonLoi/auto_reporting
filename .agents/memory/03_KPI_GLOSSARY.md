# Canonical KPI Glossary

> **Non-Negotiable Rule (Ratio-of-Sums):** Every rate, percentage, margin, hold %, or weighted average MUST be aggregated as `SUM(numerator) / NULLIF(SUM(denominator), 0)`. Never use `AVG(pct)`.
> Maintained by `02-sample-report-learner` and `06-memory-consolidation`.

## KPI Definitions

| KPI Name | Aliases | Canonical SQL Formula | Mandatory Base Filters | Display Format | Grain / Notes | Verified By |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| *(pending discovery / backtest)* | | | | | | |

---

## KPI Calculation Invariants

- **Null Handling:** Wrap additive numerators/denominators in `COALESCE(col, 0)` only when `NULL` semantically means zero (never mask missing dimension joins).
- **Integer Division:** Always cast numerators to `NUMERIC` / `DOUBLE PRECISION` (`1.0 * SUM(num) / NULLIF(SUM(den), 0)`) to avoid integer truncation.
- **Currency & Units:** Document exact unit (e.g., USD, HKD, cents vs dollars, basis points vs percent) in every KPI entry above.

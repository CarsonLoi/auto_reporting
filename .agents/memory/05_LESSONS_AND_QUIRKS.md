# Lessons Learned & SQL Quirks

> **Always read this file first before writing any SQL.**
> Format: Dated entries with **`Symptom -> Root Cause -> Permanent Fix`** (strictly max 3 lines per entry). Update in place when a quirk evolves.

## Active Quirks & Permanent Fixes

| Date | Area | Symptom -> Root Cause -> Permanent Fix |
| :--- | :--- | :--- |
| 2026-11-22 | Global SQL | **Symptom:** Aggregate percentages drift from Excel totals. **Root Cause:** Averaging pre-calculated row ratios (`AVG(pct)`). **Permanent Fix:** Always compute `1.0 * SUM(num) / NULLIF(SUM(den), 0)`. |
| 2026-11-22 | Global SQL | **Symptom:** Zero-activity categories vanish from periodic reports. **Root Cause:** `INNER JOIN` or direct `GROUP BY` on sparse event tables. **Permanent Fix:** Build a calendar × dimension spine and `LEFT JOIN` pre-aggregated metrics. |

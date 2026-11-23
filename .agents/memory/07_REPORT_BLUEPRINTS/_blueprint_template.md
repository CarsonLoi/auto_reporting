# Report Blueprint: `<Report Name>` (`<report_id>`)

- **Source Sample File:** `references/<filename>`
- **Target Output Format(s):** `.xlsx` / `.html` / `.pdf`
- **Cadence:** Daily / Weekly / Monthly / Ad-hoc
- **Backtest Period Verified:** `YYYY-MM-DD` to `YYYY-MM-DD`
- **Backtest Result:** `PASS (Max Delta: 0.00)`

---

## 1. Visual Layout & Styling Specification

- **Sheets / Sections:**
  1. `Summary` — KPI header cards + roll-up table + trend chart
  2. `Detail` — Granular breakdown table
- **Typography & Palette:**
  - Header Fill: `#1B365D`, Header Font: `#FFFFFF` Bold 11pt
  - Zebra Stripe Fill: `#F4F7FA`
  - Total Row: Bold, top thin border, bottom double border
- **Number Formats:**
  - Currency: `$#,##0;($#,##0);"-"`
  - Integer: `#,##0`
  - Percentage: `0.0%`
- **Excel Formulas to Preserve:**
  - Row/Column totals via `=SUM(...)`
  - Ratios via `=IFERROR(numerator/denominator, 0)` (ratio-of-sums on total row!)

---

## 2. Parameterized Verified SQL

```sql
-- Parameters: :start_date, :end_date
-- Verified 100% against references/<filename>
SELECT 1;
```

---

## 3. Reconciliation Invariants

1. **Control Total Check:** Sum of `<primary_metric>` across all detail rows == un-joined base table sum for `:start_date`..`:end_date` ($\pm 0.01$).
2. **Cross-Tab Parity:** `Summary` grand total == `Detail` grand total.
3. **Ratio-of-Sums:** Grand total percentage == `SUM(num) / SUM(den)`.

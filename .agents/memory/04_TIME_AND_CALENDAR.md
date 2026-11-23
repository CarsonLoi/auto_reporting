# Time, Operational Calendar & Period Comparison Rules

> Maintained by `02-sample-report-learner` and `06-memory-consolidation`.
> Never assume standard midnight UTC days or ISO weeks without verifying against the warehouse and sample reports.

## Operational Day & Timezone Rules

| Setting | Value | Notes |
| :--- | :--- | :--- |
| **Warehouse Storage Timezone** | `TBD` | e.g., UTC, Asia/Hong_Kong, America/New_York |
| **Reporting Display Timezone** | `TBD` | |
| **Operational Business-Day Cutoff** | `TBD` | e.g., `00:00–23:59` or `06:00–05:59 next day` |
| **Canonical Business Date Expression** | `TBD` | e.g., `CAST("event_ts" - INTERVAL '6 hours' AS DATE)` |

## Fiscal & Reporting Calendar

| Setting | Value | Notes |
| :--- | :--- | :--- |
| **Week Start Day** | `TBD` | e.g., Monday (ISO) or Sunday |
| **Fiscal Year Start** | `TBD` | e.g., Jan 1, Apr 1, Jul 1 |
| **Calendar Dimension Table** | `TBD` | Physical table name if one exists |

## Period-over-Period Comparison Rules

- **WoW (Week-over-Week):** `TBD` (e.g., same day-of-week `- 7 days`)
- **MoM (Month-over-Month):** `TBD` (e.g., MTD vs prior MTD through same day-of-month)
- **YoY (Year-over-Year):** `TBD` (e.g., calendar date `- 1 year` vs aligned 52-week `364 days` like-for-like)
- **Partial-Day / ETL Cutoff Handling:** Exclude incomplete current day unless explicitly requested as intraday; verify via `04-numbers-validation` Gate 1.

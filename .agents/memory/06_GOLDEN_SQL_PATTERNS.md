# Golden SQL Patterns (PostgreSQL)

> Verified, PostgreSQL-safe reusable CTE templates. Always quote verbatim physical identifiers per `.agents/memory/00_WAREHOUSE_PROFILE.md`.

## Pattern 1: Modular 3-Stage CTE Structure (Anti-Fanout)

```sql
WITH base_filtered AS (
    -- Stage 1: Partition/index pruning & canonical base filters ONLY
    SELECT
        "business_date",
        "entity_id",
        "metric_a",
        "metric_b"
    FROM "public"."events_table"
    WHERE "business_date" >= :start_date
      AND "business_date" <= :end_date
),
pre_aggregated AS (
    -- Stage 2: Aggregate to target grain BEFORE joining dimensions or other event tables
    SELECT
        "business_date",
        "entity_id",
        SUM("metric_a") AS total_a,
        SUM("metric_b") AS total_b
    FROM base_filtered
    GROUP BY 1, 2
),
final_joined AS (
    -- Stage 3: Safe LEFT JOIN to verified 1:1 dimension keys + ratio-of-sums KPIs
    SELECT
        p."business_date",
        d."entity_name",
        p.total_a,
        p.total_b,
        p.total_a::NUMERIC / NULLIF(p.total_b, 0) AS ratio_a_to_b
    FROM pre_aggregated p
    LEFT JOIN "public"."entity_dim" d
      ON p."entity_id" = d."entity_id"
)
SELECT *
FROM final_joined
ORDER BY "business_date", "entity_name";
```

## Pattern 2: Native PostgreSQL `generate_series` Calendar × Dimension Spine

```sql
WITH date_spine AS (
    SELECT gs::DATE AS business_date
    FROM generate_series(:start_date::DATE, :end_date::DATE, INTERVAL '1 day') AS gs
),
entity_spine AS (
    SELECT DISTINCT "entity_id", "entity_name"
    FROM "public"."entity_dim"
    WHERE "is_active" = TRUE
),
spine AS (
    SELECT d.business_date, e."entity_id", e."entity_name"
    FROM date_spine d
    CROSS JOIN entity_spine e
),
metrics AS (
    SELECT
        "business_date"::DATE AS business_date,
        "entity_id",
        SUM("amount") AS total_amount
    FROM "public"."events_table"
    WHERE "business_date" >= :start_date
      AND "business_date" <= :end_date
    GROUP BY 1, 2
)
SELECT
    s.business_date,
    s."entity_name",
    COALESCE(m.total_amount, 0) AS total_amount
FROM spine s
LEFT JOIN metrics m
  ON s.business_date = m.business_date
 AND s."entity_id" = m."entity_id"
ORDER BY 1, 2;
```

## Pattern 3: Period-over-Period (WoW / YoY) Comparison with Safe Variance

```sql
WITH daily AS (
    SELECT
        "business_date"::DATE AS business_date,
        SUM("revenue") AS revenue
    FROM "public"."events_table"
    WHERE "business_date" >= (:start_date::DATE - INTERVAL '7 days')
      AND "business_date" <= :end_date::DATE
    GROUP BY 1
)
SELECT
    cur.business_date,
    cur.revenue AS current_revenue,
    prev.revenue AS prior_week_revenue,
    (cur.revenue - prev.revenue) AS wow_abs_delta,
    (cur.revenue - prev.revenue)::NUMERIC / NULLIF(prev.revenue, 0) AS wow_pct_delta
FROM daily cur
LEFT JOIN daily prev
  ON prev.business_date = cur.business_date - INTERVAL '7 days'
WHERE cur.business_date >= :start_date::DATE
ORDER BY cur.business_date;
```

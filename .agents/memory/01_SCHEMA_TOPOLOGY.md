# Schema Topology & Verified Join Matrix

> Maintained by `01-schema-discovery` and `06-memory-consolidation`.
> **Rule:** Never guess join keys or cardinality. Only mark a join as `VERIFIED` after empirical uniqueness (`COUNT(*)` vs `COUNT(DISTINCT key)`) and sample `LEFT JOIN` fanout testing.

## Entity-Relationship Diagram

```mermaid
erDiagram
    %% Populated automatically during 01-schema-discovery
    %% Example:
    %% ORDERS ||--o{ ORDER_ITEMS : "order_id"
```

---

## Verified Join Matrix

| Left Table | Right Table | Exact Quoted Join Clause | Cardinality (L:R) | SCD2 / Active Filter | Fanout Tested? | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| *(pending discovery)* | | | | | | |

---

## Known Fanout & Chasm Hazards

Document any multi-grain joins or many-to-many bridges that **must** be pre-aggregated before joining:

| Hazard ID | Tables Involved | Root Cause | Mandatory Mitigation |
| :--- | :--- | :--- | :--- |
| *(none recorded yet)* | | | |

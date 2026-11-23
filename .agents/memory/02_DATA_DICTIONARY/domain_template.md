# Domain Dictionary: `<Domain Name>`

> **Verbatim Identifier Rule:** Record physical table and column names **exactly as stored in the database**, including spaces, mixed case, and punctuation (e.g., `"table min"`, `"Gross $"`).

## Table: `<schema>."<Table Name>"`

- **Grain:** 1 row per `<entity / event>`
- **Primary / Candidate Key(s):** `"<col_1>"` (Verified unique: Yes/No)
- **Partition / Date Column:** `"<date_col>"`
- **Typical Row Volume:** `<N>` rows
- **Notes / Quirks:** `<soft-delete flag, timezone, currency units, etc.>`

### Columns

| Verbatim Column Name | Data Type | Nullable | Human Alias / Synonyms | Sampled Enum / Example Values | Notes / Quirks |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `"example_id"` | `BIGINT` | No | ID, Record ID | `1001, 1002` | Primary key |
| `"table min"` | `NUMERIC(10,2)` | Yes | Table Minimum, Min Bet | `50.00, 100.00, 500.00` | Contains space — must quote |

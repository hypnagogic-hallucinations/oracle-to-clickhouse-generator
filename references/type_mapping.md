# Oracle → ClickHouse Type Mapping

## Rules Summary

- Oracle `NOT NULL` → ClickHouse non-nullable type (e.g. `String`)
- Oracle nullable (no NOT NULL constraint) → `Nullable(<type>)`
- Date/time semantics override Oracle `DATE` type (see date rules)

---

## Full Type Mapping Table

| Oracle Type | ClickHouse Type (NOT NULL) | ClickHouse Type (nullable) | Notes |
|---|---|---|---|
| `VARCHAR2(n)` | `String` | `Nullable(String)` | |
| `NVARCHAR2(n)` | `String` | `Nullable(String)` | Unicode → String in CH |
| `CHAR(n)` | `FixedString(n)` | `Nullable(FixedString(n))` | |
| `NCHAR(n)` | `FixedString(n)` | `Nullable(FixedString(n))` | |
| `CLOB` / `NCLOB` | `String` | `Nullable(String)` | |
| `NUMBER` | `Float64` | `Nullable(Float64)` | No precision/scale |
| `NUMBER(p)` where p≤9 | `Int32` | `Nullable(Int32)` | Integer-only |
| `NUMBER(p)` where p>9 | `Int64` | `Nullable(Int64)` | Integer-only |
| `NUMBER(p,s)` where s>0 | `Decimal(p,s)` | `Nullable(Decimal(p,s))` | Fixed-point |
| `NUMBER(p,0)` or `NUMBER(p)` | `Int32`/`Int64` based on p | as above | |
| `INTEGER` / `INT` | `Int32` | `Nullable(Int32)` | |
| `SMALLINT` | `Int16` | `Nullable(Int16)` | |
| `FLOAT` / `FLOAT(n)` | `Float64` | `Nullable(Float64)` | |
| `BINARY_FLOAT` | `Float32` | `Nullable(Float32)` | |
| `BINARY_DOUBLE` | `Float64` | `Nullable(Float64)` | |
| `DATE` (date+time semantics) | `DateTime` | `Nullable(DateTime)` | Use column name to disambiguate |
| `DATE` (date-only semantics) | `Date` | `Nullable(Date)` | |
| `TIMESTAMP` / `TIMESTAMP(n)` | `DateTime` | `Nullable(DateTime)` | Sub-second precision dropped |
| `TIMESTAMP WITH TIME ZONE` | `DateTime` | `Nullable(DateTime)` | TZ info dropped |
| `TIMESTAMP WITH LOCAL TIME ZONE` | `DateTime` | `Nullable(DateTime)` | |
| `INTERVAL YEAR TO MONTH` | `String` | `Nullable(String)` | No native equivalent |
| `INTERVAL DAY TO SECOND` | `String` | `Nullable(String)` | No native equivalent |
| `BLOB` / `RAW` / `LONG RAW` | `String` | `Nullable(String)` | Store as hex or base64 string |
| `XMLTYPE` | `String` | `Nullable(String)` | |
| `BOOLEAN` | `UInt8` | `Nullable(UInt8)` | 0/1 convention |

---

## Date Disambiguation Heuristic

Applied when Oracle type is `DATE` (which in Oracle stores both date and time):

| Column name pattern | CH Type | Rename suffix |
|---|---|---|
| ends with `_dt`, `_datetime`, `_timestamp` | `DateTime` | `_dt` |
| ends with `_date`, `_day` | `Date` | `_date` |
| contains `create`, `update`, `modif`, `start`, `end`, `close` | `DateTime` | `_dt` |
| no clear indicator | `DateTime` (default, more conservative) | `_dt` |

---

## NUMBER Precision Decision Tree

```
NUMBER with no precision/scale
  → Float64 / Nullable(Float64)

NUMBER(p) — no scale (integer context)
  p ≤ 4  → Int16 / Nullable(Int16)
  p ≤ 9  → Int32 / Nullable(Int32)
  p ≤ 18 → Int64 / Nullable(Int64)
  p > 18 → Decimal(p,0) / Nullable(Decimal(p,0))

NUMBER(p,s) — has scale
  s = 0  → treat as NUMBER(p) above
  s > 0  → Decimal(p,s) / Nullable(Decimal(p,s))
```

---

## ClickHouse DDL Template

```sql
CREATE TABLE {new_table_name} ON CLUSTER ch_cluster
(
    {col1}    {type1},
    {col2}    {type2},
    -- ... all columns
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/{new_table_name}', '{replica}')
ORDER BY ({pk_col1}, {pk_col2})
SETTINGS index_granularity = 8192;

GRANT SELECT ON {new_table_name} TO plm_pdmpi_ch ON CLUSTER ch_cluster;
```

**Notes:**
- `ON CLUSTER ch_cluster` appears on both CREATE TABLE and GRANT
- ENGINE is `ReplicatedMergeTree` for clustered deployment
- `ORDER BY` uses renamed PK column names
- If no PK defined in Oracle DDL, use first NOT NULL column and add a comment: `-- NOTE: No PK found in source DDL; using <col> as ORDER BY key`
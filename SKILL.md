---
name: oracle-to-ch
description: >
  Use this skill whenever a user provides an Oracle DDL (CREATE TABLE statement) and wants to:
  (1) rename columns following semiconductor/enterprise naming conventions,
  (2) generate professional column descriptions (definition + reference + sample data),
  (3) fill a DataHub upload Excel template (upload_datahub_template.xlsx), and/or
  (4) produce a ClickHouse DDL (with type mapping, nullable handling, ORDER BY from PK, and GRANT statement).
  Trigger on any combination of: "Oracle DDL", "轉換欄位名稱", "DataHub template", "ClickHouse DDL",
  "column naming", "欄位命名", "ch ddl", "clickhouse 建表", "datahub upload", "oracle 轉 clickhouse".
  Always use this skill for the full pipeline even if the user only mentions one step.

product_suite: plm   # Define the product suite (e.g. plm, blm, scm) — also in config.yml
product: pdmpi       # Define the product (e.g. pdmpi, pdmti, genpdm, ntbd) — also in config.yml
---

# Oracle DDL → Column Rename + DataHub Excel + ClickHouse DDL

## Overview

This skill executes a 3-stage pipeline:

```
Oracle DDL
   │
   ▼
[Stage 1] Column rename (naming rules) + Description generation (Claude AI)
   │
   ├──▶ [Stage 2] Fill DataHub upload Excel template
   │
   └──▶ [Stage 3] Output ClickHouse DDL
```

---

## Stage 1 — Column Renaming + Description Generation

### Step 1a: Parse the Oracle DDL

Extract from the DDL:
- Table name
- Each column: original name, data type, NOT NULL constraint, COMMENT (if present)
- Primary Key constraint (for ClickHouse ORDER BY)

### Step 1b: Apply Column Naming Rules

**Read the full naming rule table in `references/naming_rules.md` before renaming.**

Key principles:
- All column names should be in snake_case and all in lower case, same as table name
- Words ≤ 6 characters are generally NOT abbreviated (readability & meaningfulness first)
- Positive-list rules MUST always be applied (no exceptions)
- Apply rules to each word segment of the column name independently
- Suffix rules (_date/_dt) take precedence: check if the column carries date+time or date-only semantics

After renaming, produce a **mapping table** in a Markdown file (output/column_mapping_for_{new_table_name}.md):

| Original Column | New Column | Change? |
|---|---|---|
| cust_code | cust_cd | ✅ |
| name | name | — |

### Step 1c: Generate Column Descriptions

For each column, generate a description in **English** with this structure:

```
[Definition] <1–2 sentence definition using semiconductor/enterprise domain terminology>
[Reference] <what this field references or links to, e.g. "References PART_MASTER.PART_NO">
[Sample Data] <realistic example value(s), e.g. "e.g. 'A123', 'B456'">  ← include only if determinable
```

Sources to use (in priority order):
1. Original DDL COMMENT and reference / foreign key constraint in DDL
2. Column name semantics + data type
3. Semiconductor / PLM / ERP domain knowledge

---

## Stage 2 — Fill DataHub Excel Template

**Template file**: `assets/upload_datahub_template.xlsx`

### Template Structure (20 columns)

| Col | Header | Description |
|-----|--------|-------------|
| A | `PROD URN` | DataHub PROD environment URN |
| B | `STG URN` | DataHub STG environment URN |
| C | `TEST URN` | DataHub TEST environment URN |
| D | `Type` | Literal string: `"Table"` or `"Column"` |
| E | `table_name` | ClickHouse table name |
| F | `col_name` | Column name (Column rows only) |
| G | `desc` | Previous/external description (leave blank) |
| H | `prev desc` | Previous description (leave blank) |
| I | `sample row data` | Sample data (leave blank) |
| J | `top unique values` | Top unique values (leave blank) |
| K | `other info` | Other info (leave blank) |
| **L** | **`col_desc`** | **AI-generated column description ← primary output** |
| M | `confidence score` | AI confidence score (leave blank) |
| N | `reasoning` | AI reasoning (leave blank) |
| O | `score of col_desc by PM` | PM review score (leave blank) |
| P | `Score of confidence by PM` | PM confidence score (leave blank) |
| Q | `Remark by PM` | PM remark (leave blank) |
| R | `Desc by PM` | PM supplementary description (leave blank) |
| S | `Remarks by DevOps` | DevOps remark (leave blank) |
| T | `Evidence by DevOps` | DevOps evidence (leave blank) |

### Row Fill Rules

```
Row 1  (header row — DO NOT MODIFY):
  A: PROD URN | B: STG URN | C: TEST URN | D: Type | E: table_name |
  F: col_name | G: desc | H: prev desc | I: sample row data |
  J: top unique values | K: other info | L: col_desc | M–T: review cols

Row 2  (Table row — one per table):
  A: <prod_urn>   B: <stg_urn>   C: <test_urn>
  D: "Table"      E: {new_table_name}
  F–T: (leave empty)

Row 3+ (Column rows — one row per column):
  A–C: (empty)    D: "Column"    E: {new_table_name}
  F: {new_col_name}              L: {col_desc}
  G–K, M–T: (leave empty — for human/downstream review)
```

### URN Placeholder Format

> **Design note**: All three columns (PROD URN / STG URN / TEST URN) in the DataHub
> upload template receive the **same URN value**. The URN identifies the ClickHouse
> dataset entity in DataHub — it does not encode environment information.

If the user does not supply a URN, construct it from `config.yml`:

```
urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.{product_suite}.{new_table_name},PROD)
```

This same value is written to columns A, B, and C (PROD URN / STG URN / TEST URN).

### Running the Excel Fill Script

If there are multiple tables from Oracle DDL, run the script for each table:

```bash
# All three --*-url flags receive the same URN (by design; see URN Placeholder Format)
python scripts/fill_upload_excel.py \
  --template assets/upload_datahub_template.xlsx \
  --data /tmp/stage1_output.json \
  --output output/datahub_upload_{table_name}.xlsx \
  --prod-url "urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.{product_suite}.{table},PROD)" \
  --stg-url  "urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.{product_suite}.{table},PROD)" \
  --test-url "urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.{product_suite}.{table},PROD)"
```

---

## Stage 3 — ClickHouse DDL

**Read `references/type_mapping.md`** for the full Oracle → ClickHouse type mapping table.

### DDL Template

```sql
CREATE TABLE {product_suite}.{new_table_name} ON CLUSTER ch_cluster
(
    -- columns here (see type mapping rules)
)
ENGINE = ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/{new_table_name}', '{replica}')
ORDER BY ({pk_columns});

GRANT SELECT ON {product_suite}.{new_table_name} TO {product_suite}_{product}_ch ON CLUSTER ch_cluster;
```

### Nullable Rules

- Oracle `NOT NULL` → ClickHouse non-nullable type (e.g. `String`)
- Oracle nullable (no NOT NULL) → wrap in `Nullable(...)` (e.g. `Nullable(String)`)

### Date/DateTime Rules

- Column carries **date + time** → `DateTime` (not nullable if NOT NULL, else `Nullable(DateTime)`)
- Column carries **date only** → `Date` (not nullable if NOT NULL, else `Nullable(Date)`)
- Detection: check column name suffix (`_dt`, `_datetime`, `_timestamp`) → DateTime; (`_date`, `_day`) → Date
- Also check Oracle type: `DATE` in Oracle is ambiguous — use column name suffix to disambiguate; default to `DateTime` if ambiguous
- `TIMESTAMP` → always `DateTime`

### ORDER BY

Use the columns listed in the Oracle `PRIMARY KEY` constraint (renamed to new names).
If no PK is defined, use the first NOT NULL column and note this assumption.

### After generating DDL

1. Output a **Type Mapping Reference Table** in a Markdown file (output/column_mapping_for_{new_table_name}.md).
   - Include a **Select SQL** section at the top: `SELECT {orig_col} AS {new_col}, ... FROM {orig_table_name}`.

2. Generate a **Detailed Column Description Excel** (output/column_desc_{new_table_name}.xlsx) using `scripts/generate_desc_excel.py`.
   - Columns: Original Oracle Column, New ClickHouse Column, Oracle Type, ClickHouse Type, Nullable, Original Column Desc, New Column Desc.

| Original Oracle Column | New ClickHouse Column | Oracle Type | ClickHouse Type | Nullable | New Column Desc |
|---|---|---|---|---|---|
| CUST_CODE | cust_cd | VARCHAR2(50) NOT NULL | String | No | [Definition] ... |
| CREATE_DATE | create_dt | DATE | DateTime | Yes | [Definition] ... |

---

## Output Checklist

After completing all stages, confirm:

- [ ] Select SQL (with {orig_col} AS {new_col} syntax) shown to user
- [ ] Column name mapping table shown to user
- [ ] Descriptions generated for all columns
- [ ] DataHub Upload Excel file written and presented
- [ ] Detailed Column Description Excel file written and presented
- [ ] ClickHouse DDL block shown (with {product_suite}. prefix)
- [ ] Type mapping reference table shown with column descriptions
- [ ] GRANT statement included at end of DDL

---

## Self-Check Progress Tracker

Use this checklist to track how far you are in the pipeline for each table.

### 📋 Stage 0 — Setup
- [ ] `config.yml` reviewed: `product_suite` and `product` are set correctly
- [ ] Template file `assets/upload_datahub_template.xlsx` is present
- [ ] Oracle DDL source is ready to input

### 🔄 Stage 1 — Column Rename + Description
- [ ] Oracle DDL parsed (table name, columns, PK constraints extracted)
- [ ] `references/naming_rules.md` read in full before renaming
- [ ] All **positive-list rules** applied (no exceptions)
- [ ] **Date/time suffix rules** applied (`_dt` vs `_date` per semantics)
- [ ] **`is_` prefix rule** applied (`_flag` or `_type` suffix)
- [ ] Column descriptions generated for all columns (Definition + Reference + Sample Data)
- [ ] Output: `output/column_mapping_for_{table_name}.md` created ✅

### 📊 Stage 2 — DataHub Upload Excel
- [ ] URNs confirmed or placeholder URNs from `config.yml` used
- [ ] `scripts/fill_upload_excel.py` executed successfully
- [ ] Output: `output/datahub_upload_{table_name}.xlsx` created ✅
- [ ] Verified: Row 2 is Table row (`D="Table"`, `E=table_name`, URNs in A/B/C)
- [ ] Verified: Row 3+ are Column rows (`D="Column"`, `F=col_name`, `L=col_desc`)

### 🗄️ Stage 3 — ClickHouse DDL
- [ ] `references/type_mapping.md` read in full
- [ ] All columns type-mapped (Oracle → ClickHouse)
- [ ] Nullable rules applied (NOT NULL → non-nullable, else Nullable)
- [ ] Date/DateTime distinction resolved for all date columns
- [ ] ORDER BY set from PK (or first NOT NULL with `-- NOTE:` comment)
- [ ] Output: `output/{table_name}_ch.sql` created ✅
- [ ] GRANT statement included

### 📝 Detailed Column Description Excel
- [ ] `scripts/generate_desc_excel.py` executed successfully
- [ ] Output: `output/column_desc_{table_name}.xlsx` created ✅
- [ ] All 7 columns present: Original Oracle Column, New ClickHouse Column, Oracle Type, ClickHouse Type, Nullable, Original Column Desc, New Column Desc

### ✅ Final Handoff Verification
- [ ] All output files are in `output/` directory
- [ ] Select SQL reviewed by user
- [ ] Column mapping table reviewed by user
- [ ] ClickHouse DDL reviewed and tested
- [ ] DataHub Upload Excel submitted to DataHub team

---

## Reference Files

- `config.yml` — User-configurable settings (product_suite, product, URN templates)
- `references/naming_rules.md` — Full column renaming rule table (read in Stage 1b)
- `references/type_mapping.md` — Oracle → ClickHouse type mapping (read in Stage 3)
- `scripts/fill_upload_excel.py` — Script to write the DataHub Excel template
- `scripts/generate_desc_excel.py` — Script to write the Detailed Column Description Excel
- `assets/upload_datahub_template.xlsx` — Blank DataHub upload template (20 columns)

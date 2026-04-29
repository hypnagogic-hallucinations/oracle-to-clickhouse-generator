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

product_suite = plm  # Define the product suite (e.g. plm, blm, scm)
product = pdmpi # Define the product (e.g. pdmpi, pdmti, genpdm, ntbd)
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

**Template format** (`upload_datahub_template.xlsx`):

```
Row 1 (header): PROD | STG | UAT | Source | Column | Column Desc
Row 2:          <prod_url> | <stg_url> | <uat_url> | (empty) | (empty) | (empty)
Row 3:          (empty x3) | <table_name> | <table_name> | (empty)
Row 4+:         (empty x4) | <new_col_name> | <description>
```

Rules:
- Columns A–C (PROD/STG/UAT): user must supply URLs; use placeholder `https://datahub.example.com` if not provided
- Column D (Source): only filled in row 3 with the new table name
- Column E (Column): row 3 = new table name; rows 4+ = new column names (renamed)
- Column F (Column Desc): rows 4+ = generated descriptions
- Use the script at `scripts/fill_upload_excel.py` to write the file

### Running the Excel fill script

If there are multiple tables from Oracle DDL, run the script for each table

```bash
python3 scripts/fill_upload_excel.py \
  --template /path/to/upload_datahub_template.xlsx \
  --data /tmp/stage1_output.json \
  --output /mnt/user-data/outputs/datahub_upload_<table>.xlsx \
  --prod-url "https://..." \
  --stg-url "https://..." \
  --uat-url "https://..."
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
ENGINE = ReplacingMergeTree() ORDER BY ({pk_columns});

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

## Reference Files

- `references/naming_rules.md` — Full column renaming rule table (read in Stage 1b)
- `references/type_mapping.md` — Oracle → ClickHouse type mapping (read in Stage 3)
- `scripts/fill_upload_excel.py` — Script to write the DataHub Excel template
- `assets/upload_datahub_template.xlsx` — Blank template file
# Oracle → ClickHouse Metadata Generator

> AI-assisted pipeline to rename Oracle DDL columns, generate DataHub metadata, and produce ClickHouse DDL — following semiconductor/enterprise naming conventions.

---

## What This Does

Given an Oracle `CREATE TABLE` DDL, this pipeline produces:

| Output | File | Description |
|--------|------|-------------|
| Column mapping | `output/column_mapping_for_{table}.md` | Rename mapping table + Select SQL |
| DataHub upload | `output/datahub_upload_{table}.xlsx` | Ready-to-upload DataHub Excel (20-col template) |
| Column descriptions | `output/column_desc_{table}.xlsx` | Detailed description Excel (7 columns) |
| ClickHouse DDL | `output/{table}_ch.sql` | `CREATE TABLE` + `GRANT` statement |

---

## Quick Start

### 1. Prerequisites

```bash
pip install openpyxl
```

### 2. Configure Your Project

Edit `config.yml`:

```yaml
product_suite: plm    # e.g. plm, blm, scm
product: pdmpi        # e.g. pdmpi, pdmti, genpdm, ntbd
```

### 3. Run the Pipeline

**Stage 1** — Invoke Claude AI with your Oracle DDL and this SKILL (see `SKILL.md`).
Claude will produce the column mapping Markdown and a `stage1_output.json`.

**Stage 2** — Fill the DataHub upload Excel:

```bash
python scripts/fill_upload_excel.py \
  --template assets/upload_datahub_template.xlsx \
  --data /tmp/stage1_output.json \
  --output output/datahub_upload_plm_part.xlsx \
  --prod-url "urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.plm.plm_part,PROD)" \
  --stg-url  "urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.plm.plm_part,PROD)" \
  --test-url "urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.plm.plm_part,PROD)"
```

**Stage 3** — Generate the detailed column description Excel:

```bash
python scripts/generate_desc_excel.py \
  --data /tmp/stage1_output.json \
  --output output/column_desc_plm_part.xlsx
```

---

## Project Structure

```
metadata-generator/
├── config.yml                        ← 🔧 Edit this first (product_suite, product)
├── SKILL.md                          ← AI Skill definition (pipeline rules)
├── assets/
│   └── upload_datahub_template.xlsx  ← Blank DataHub upload template (20 columns)
├── references/
│   ├── naming_rules.md               ← Column renaming rules (positive-list + suffix)
│   └── type_mapping.md               ← Oracle → ClickHouse type mapping
├── scripts/
│   ├── fill_upload_excel.py          ← Stage 2: fill DataHub upload Excel
│   └── generate_desc_excel.py        ← Stage 3: generate column description Excel
├── sample_oracle_ddl/                ← Example Oracle DDL inputs
│   ├── plm_mtn_log.sql
│   ├── plm_part.sql
│   └── plm_service_route.sql
└── output/                           ← All generated files land here
    ├── column_mapping_for_*.md
    ├── datahub_upload_*.xlsx
    ├── column_desc_*.xlsx
    └── *_ch.sql
```

---

## DataHub Upload Template Structure

The template (`assets/upload_datahub_template.xlsx`) has **20 columns**:

| Col | Header | Filled By |
|-----|--------|-----------|
| A | PROD URN | Script |
| B | STG URN | Script |
| C | TEST URN | Script |
| D | Type | Script (`"Table"` or `"Column"`) |
| E | table_name | Script |
| F | col_name | Script |
| G–K | desc, prev desc, sample data, … | Human / downstream |
| **L** | **col_desc** | **Script (AI-generated description)** |
| M–T | confidence, reasoning, PM/DevOps review | Human / downstream |

---

## Naming Rules Summary

Key rules applied during column renaming (see `references/naming_rules.md` for full list):

| Rule | Example |
|------|---------|
| `code` → `cd` | `cust_code` → `cust_cd` |
| `eng` → `user` | `mtn_eng` → `mtn_user` |
| `is_<x>` → `<x>_flag` / `<x>_type` | `is_dummy_part` → `dummy_part_flag` |
| Date+time columns → `_dt` suffix | `crea_date` → `create_dt` |
| Date-only columns → `_date` suffix | `birth_date` stays `birth_date` |
| `product` → `prod` | `product_type` → `prod_type` |
| `quantity` → `qty` | `product_quantity` → `prod_qty` |

---

## Self-Check Progress Tracker

Copy this checklist per table to track your progress:

```
### Table: _______________

Stage 0 — Setup
[ ] config.yml reviewed (product_suite + product set)
[ ] Oracle DDL source ready

Stage 1 — Column Rename + Description
[ ] DDL parsed
[ ] naming_rules.md read
[ ] All positive-list rules applied
[ ] Date/time suffix rules applied
[ ] is_ prefix rule applied
[ ] Descriptions generated for all columns
[ ] output/column_mapping_for_{table}.md created

Stage 2 — DataHub Upload Excel
[ ] URNs ready (or placeholder URNs used)
[ ] fill_upload_excel.py executed
[ ] output/datahub_upload_{table}.xlsx verified

Stage 3 — ClickHouse DDL
[ ] type_mapping.md read
[ ] All columns type-mapped
[ ] Nullable rules applied
[ ] ORDER BY from PK (or fallback with NOTE)
[ ] output/{table}_ch.sql created
[ ] GRANT statement included

Detailed Description Excel
[ ] generate_desc_excel.py executed
[ ] output/column_desc_{table}.xlsx verified

Final Handoff
[ ] All files in output/ directory
[ ] DataHub Upload Excel submitted to DataHub team
[ ] ClickHouse DDL reviewed and deployed
```

---

## FAQ

**Q: Can I process multiple tables at once?**
Run each stage script once per table. Stage 1 (AI rename + describe) handles one DDL at a time via Claude; scripts are then run per-table.

**Q: What if there's no PRIMARY KEY in the Oracle DDL?**
The pipeline uses the first `NOT NULL` column as `ORDER BY` key and adds a `-- NOTE:` comment in the SQL.

**Q: How do I change the ClickHouse cluster name?**
Update `clickhouse.cluster` in `config.yml`.

**Q: Why do all three URL flags (--prod-url, --stg-url, --test-url) use the same URN value?**
The DataHub upload template has three URN columns (PROD URN / STG URN / TEST URN), but in this setup all three columns receive the **same URN** — the one that identifies the ClickHouse dataset entity. The three-column structure is a DataHub convention; it does not mean the dataset is deployed in three separate environments.

**Q: What is the URN format?**
`urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.{product_suite}.{table_name},PROD)`
Replace `{product_suite}` and `{table_name}` with actual values, e.g.:
`urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.plm.plm_part,PROD)`

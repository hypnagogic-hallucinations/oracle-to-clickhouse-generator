#!/usr/bin/env python3
"""
fill_upload_excel.py — Fill the DataHub upload template (upload_datahub_template.xlsx)
with renamed columns and generated descriptions from Stage 1 output.

Template structure (20 columns, Row 1 = header):
  A: PROD URN  | B: STG URN    | C: TEST URN   | D: Type       | E: table_name
  F: col_name  | G: desc       | H: prev desc  | I: sample row | J: top unique values
  K: other info| L: col_desc   | M: confidence | N: reasoning  | O–T: PM/DevOps review

Fill rules:
  Row 2  (Table row): A=prod_urn, B=stg_urn, C=test_urn, D="Table", E=table_name
  Row 3+ (Column rows): D="Column", E=table_name, F=col_name, L=col_desc

Usage:
    python scripts/fill_upload_excel.py \\
        --template assets/upload_datahub_template.xlsx \\
        --data /tmp/stage1_output.json \\
        --output output/datahub_upload_<table>.xlsx \\
        --prod-url "urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.plm.<table>,PROD)" \\
        --stg-url  "urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.plm.<table>,STG)" \\
        --test-url "urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.plm.<table>,TEST)"

stage1_output.json schema:
{
    "new_table_name": "plm_part",
    "columns": [
        {
            "new_name": "part_no",
            "description": "[Definition] ... [Reference] ... [Sample Data] ..."
        },
        ...
    ]
}
"""

import argparse
import json
import shutil
from openpyxl import load_workbook
from openpyxl.styles import Alignment


# Column index constants (1-based, matching template header row)
COL_PROD_URN   = 1   # A: PROD URN
COL_STG_URN    = 2   # B: STG URN
COL_TEST_URN   = 3   # C: TEST URN
COL_TYPE       = 4   # D: Type       — "Table" or "Column"
COL_TABLE_NAME = 5   # E: table_name
COL_COL_NAME   = 6   # F: col_name
COL_COL_DESC   = 12  # L: col_desc   — primary AI output


def fill_template(template_path, data_path, output_path, prod_url, stg_url, test_url):
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    new_table_name = data["new_table_name"]
    columns = data["columns"]

    shutil.copy2(template_path, output_path)
    wb = load_workbook(output_path)
    ws = wb.active

    # Clear any existing data rows (row 2+) while preserving header (row 1)
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for cell in row:
            cell.value = None

    wrap_top = Alignment(wrap_text=True, vertical="top")

    # ── Row 2: Table row ─────────────────────────────────────────────────────
    ws.cell(row=2, column=COL_PROD_URN).value   = prod_url
    ws.cell(row=2, column=COL_STG_URN).value    = stg_url
    ws.cell(row=2, column=COL_TEST_URN).value   = test_url
    ws.cell(row=2, column=COL_TYPE).value        = "Table"
    ws.cell(row=2, column=COL_TABLE_NAME).value  = new_table_name

    # ── Row 3+: Column rows (one per column) ─────────────────────────────────
    for i, col in enumerate(columns, start=3):
        ws.cell(row=i, column=COL_TYPE).value       = "Column"
        ws.cell(row=i, column=COL_TABLE_NAME).value = new_table_name

        ws.cell(row=i, column=COL_COL_NAME).value   = col["new_name"]
        ws.cell(row=i, column=COL_COL_NAME).alignment = wrap_top

        # Accept both "new_desc" (generate_desc_excel schema) and "description" keys
        desc = col.get("new_desc") or col.get("description", "")
        ws.cell(row=i, column=COL_COL_DESC).value     = desc
        ws.cell(row=i, column=COL_COL_DESC).alignment = wrap_top

    # ── Column widths ─────────────────────────────────────────────────────────
    ws.column_dimensions["A"].width = 80   # PROD URN (long URN strings)
    ws.column_dimensions["B"].width = 80   # STG URN
    ws.column_dimensions["C"].width = 80   # TEST URN
    ws.column_dimensions["D"].width = 10   # Type
    ws.column_dimensions["E"].width = 30   # table_name
    ws.column_dimensions["F"].width = 30   # col_name
    ws.column_dimensions["L"].width = 80   # col_desc

    wb.save(output_path)
    print(f"[OK] Written: {output_path}")
    print(f"     Table  : {new_table_name}")
    print(f"     Columns: {len(columns)}")


def main():
    parser = argparse.ArgumentParser(
        description="Fill the DataHub upload Excel template with Stage 1 output data."
    )
    parser.add_argument("--template", required=True,
                        help="Path to the blank upload_datahub_template.xlsx")
    parser.add_argument("--data", required=True,
                        help="Path to stage1_output.json")
    parser.add_argument("--output", required=True,
                        help="Output path for the filled .xlsx file")
    parser.add_argument("--prod-url",
                        default="urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.{product_suite}.{table},PROD)",
                        help="DataHub PROD URN string")
    parser.add_argument("--stg-url",
                        default="urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.{product_suite}.{table},PROD)",
                        help="DataHub STG URN string")
    parser.add_argument("--test-url",
                        default="urn:li:dataset:(urn:li:dataPlatform:clickhouse,scmdp.{product_suite}.{table},PROD)",
                        help="DataHub TEST URN string")
    args = parser.parse_args()

    fill_template(
        template_path=args.template,
        data_path=args.data,
        output_path=args.output,
        prod_url=args.prod_url,
        stg_url=args.stg_url,
        test_url=args.test_url,
    )


if __name__ == "__main__":
    main()
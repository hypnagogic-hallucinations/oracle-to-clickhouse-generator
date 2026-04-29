#!/usr/bin/env python3
"""
fill_upload_excel.py — Fill the DataHub upload template (upload_datahub_template.xlsx)
with renamed columns and generated descriptions from Stage 1 output.

Usage:
    python3 fill_upload_excel.py \
        --template /path/to/upload_datahub_template.xlsx \
        --data /tmp/stage1_output.json \
        --output /mnt/user-data/outputs/datahub_upload_<table>.xlsx \
        --prod-url "https://datahub.example.com" \
        --stg-url  "https://datahub-stg.example.com" \
        --uat-url  "https://datahub-uat.example.com"

stage1_output.json schema:
{
    "new_table_name": "prod_part_master",
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
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


def fill_template(template_path, data_path, output_path, prod_url, stg_url, uat_url):
    with open(data_path) as f:
        data = json.load(f)

    new_table_name = data["new_table_name"]
    columns = data["columns"]

    shutil.copy2(template_path, output_path)
    wb = load_workbook(output_path)
    ws = wb.active

    # Clear existing sample data rows (row 4+) preserving header structure
    for row in ws.iter_rows(min_row=4, max_row=ws.max_row):
        for cell in row:
            cell.value = None

    # Row 2: DataHub URLs (columns A, B, C)
    ws["A2"] = prod_url
    ws["B2"] = stg_url
    ws["C2"] = uat_url

    # Row 3: table name in Source (D) and Column (E)
    ws["D3"] = new_table_name
    ws["E3"] = new_table_name

    # Rows 4+: one row per column
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    wrap = Alignment(wrap_text=True, vertical="top")

    for i, col in enumerate(columns, start=4):
        ws.cell(row=i, column=5).value = col["new_name"]
        # Handle both possible keys for description
        desc = col.get("new_desc") or col.get("description")
        ws.cell(row=i, column=6).value = desc
        ws.cell(row=i, column=5).alignment = wrap
        ws.cell(row=i, column=6).alignment = wrap

    # Auto-width for column F (descriptions can be long)
    ws.column_dimensions["E"].width = 30
    ws.column_dimensions["F"].width = 80

    wb.save(output_path)
    print(f"✅ Written: {output_path}")
    print(f"   Table: {new_table_name}")
    print(f"   Columns: {len(columns)}")


def main():
    parser = argparse.ArgumentParser(description="Fill DataHub upload Excel template")
    parser.add_argument("--template", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--prod-url", default="https://datahub.example.com")
    parser.add_argument("--stg-url",  default="https://datahub-stg.example.com")
    parser.add_argument("--uat-url",  default="https://datahub-uat.example.com")
    args = parser.parse_args()

    fill_template(
        template_path=args.template,
        data_path=args.data,
        output_path=args.output,
        prod_url=args.prod_url,
        stg_url=args.stg_url,
        uat_url=args.uat_url,
    )


if __name__ == "__main__":
    main()
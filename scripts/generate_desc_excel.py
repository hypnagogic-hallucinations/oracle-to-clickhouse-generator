#!/usr/bin/env python3
"""
generate_desc_excel.py — Generate a detailed column description Excel file.

Usage:
    python3 generate_desc_excel.py \
        --data /tmp/mapping_data.json \
        --output output/column_desc_<table>.xlsx

mapping_data.json schema:
{
    "new_table_name": "plm_part",
    "columns": [
        {
            "orig_name": "PART_ID",
            "new_name": "part_id",
            "orig_type": "VARCHAR2(50) NOT NULL",
            "new_type": "String",
            "nullable": "No",
            "orig_desc": "Part ID (Primary Key)",
            "new_desc": "[Definition] ... [Reference] ... [Sample Data] ..."
        },
        ...
    ]
}
"""

import argparse
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


def generate_excel(data_path, output_path):
    with open(data_path) as f:
        data = json.load(f)

    columns = data["columns"]

    wb = Workbook()
    ws = wb.active
    ws.title = "Column Descriptions"

    # Header
    headers = [
        "Original Oracle Column",
        "New ClickHouse Column",
        "Oracle Type",
        "ClickHouse Type",
        "Nullable",
        "Original Column Desc",
        "New Column Desc"
    ]
    
    # Header colors
    default_header_fill = PatternFill(start_color="9FCEEB", end_color="9FCEEB", fill_type="solid")
    special_header_fill = PatternFill(start_color="FCD58E", end_color="FCD58E", fill_type="solid")
    
    # Data colors
    default_data_fill = PatternFill(start_color="F0F8FE", end_color="FFFDF7", fill_type="solid")
    special_data_fill = PatternFill(start_color="FFFDF7", end_color="F0F8FE", fill_type="solid")
    
    # Styles
    calibri_font = Font(name="Calibri", size=11)
    calibri_bold_font = Font(name="Calibri", size=11, bold=True)
    
    left_alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    center_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True) # for headers
    
    light_side = Side(style="thin", color="F2F2F2")
    black_side = Side(style="thin", color="000000")
    
    # Internal border (default)
    internal_border = Border(left=light_side, right=light_side, top=light_side, bottom=light_side)
    
    special_cols = []
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        
        is_special = "New" in header or "ClickHouse" in header
        if is_special:
            cell.fill = special_header_fill
            special_cols.append(col_num)
        else:
            cell.fill = default_header_fill
            
        cell.font = calibri_bold_font
        cell.border = internal_border
        cell.alignment = left_alignment # All left-aligned as requested

    # Data
    for row_num, col in enumerate(columns, 2):
        row_data = [
            col.get("orig_name", ""),
            col.get("new_name", ""),
            col.get("orig_type", ""),
            col.get("new_type", ""),
            col.get("nullable", ""),
            col.get("orig_desc", ""),
            col.get("new_desc", "")
        ]
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = value
            
            if col_num in special_cols:
                cell.fill = special_data_fill
            elif value:
                cell.fill = default_data_fill
                
            cell.font = calibri_font
            cell.border = internal_border
            cell.alignment = left_alignment

    # Apply black outer border
    max_row = len(columns) + 1
    max_col = len(headers)
    
    for r in range(1, max_row + 1):
        # Left edge
        ws.cell(row=r, column=1).border = Border(
            left=black_side, 
            right=ws.cell(row=r, column=1).border.right,
            top=ws.cell(row=r, column=1).border.top,
            bottom=ws.cell(row=r, column=1).border.bottom
        )
        # Right edge
        ws.cell(row=r, column=max_col).border = Border(
            left=ws.cell(row=r, column=max_col).border.left,
            right=black_side,
            top=ws.cell(row=r, column=max_col).border.top,
            bottom=ws.cell(row=r, column=max_col).border.bottom
        )
        
    for c in range(1, max_col + 1):
        # Top edge
        ws.cell(row=1, column=c).border = Border(
            left=ws.cell(row=1, column=c).border.left,
            right=ws.cell(row=1, column=c).border.right,
            top=black_side,
            bottom=ws.cell(row=1, column=c).border.bottom
        )
        # Bottom edge
        ws.cell(row=max_row, column=c).border = Border(
            left=ws.cell(row=max_row, column=c).border.left,
            right=ws.cell(row=max_row, column=c).border.right,
            top=ws.cell(row=max_row, column=c).border.top,
            bottom=black_side
        )

    # Column widths
    widths = [25, 25, 25, 20, 10, 40, 60]
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = width

    wb.save(output_path)
    print(f"[OK] Generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate detailed column description Excel")
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    generate_excel(data_path=args.data, output_path=args.output)


if __name__ == "__main__":
    main()

"""
==============================================================================
SMART INVENTORY & DEMAND FORECASTING SYSTEM
AUTOMATED EXCEL PURCHASE ORDER GENERATOR (po_generator.py)
Transforms Phase 2 Critical Alerts into formatted, supplier-ready Excel POs.
==============================================================================
"""

import os
import sys
import re
from datetime import datetime, timedelta
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Paths
DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DIR)
REPORT_CSV = os.path.join(PROJECT_ROOT, "core_engine", "inventory_analysis_report.csv")
PO_OUTPUT_DIR = os.path.join(DIR, "purchase_orders")
os.makedirs(PO_OUTPUT_DIR, exist_ok=True)

def slugify(text):
    """Converts company name to a safe filename string."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', text.strip())

def generate_supplier_purchase_order(supplier_id, supplier_name, lead_time_days, items_df, po_dir):
    """
    Generates a corporate-styled, professional Excel Purchase Order (.xlsx)
    for a specific supplier containing their critical replenishment SKUs.
    """
    order_date = datetime.now().date()
    expected_delivery = order_date + timedelta(days=lead_time_days)
    po_number = f"PO-{order_date.strftime('%Y%m%d')}-S{supplier_id:03d}"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Purchase Order"
    ws.views.sheetView[0].showGridLines = True

    # Palette Colors
    navy_dark = "1F4E78"
    navy_light = "D9E1F2"
    gray_light = "F2F2F2"
    border_gray = "D9D9D9"

    # Font styles
    title_font = Font(name="Calibri", size=18, bold=True, color="FFFFFF")
    section_hdr_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True, color="000000")
    regular_font = Font(name="Calibri", size=11, color="000000")
    footer_font = Font(name="Calibri", size=9, italic=True, color="595959")

    # Fills
    navy_fill = PatternFill(start_color=navy_dark, end_color=navy_dark, fill_type="solid")
    soft_fill = PatternFill(start_color=navy_light, end_color=navy_light, fill_type="solid")
    zebra_fill = PatternFill(start_color=gray_light, end_color=gray_light, fill_type="solid")
    white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

    # Borders
    thin_side = Side(border_style="thin", color=border_gray)
    cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    double_bottom = Border(top=thin_side, bottom=Side(border_style="double", color=navy_dark))

    # Alignments
    left_align = Alignment(horizontal="left", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    center_align = Alignment(horizontal="center", vertical="center")

    # 1. HEADER BANNER
    ws.merge_cells("A1:I2")
    banner_cell = ws["A1"]
    banner_cell.value = "SMART INVENTORY RESTOCK PURCHASE ORDER"
    banner_cell.font = title_font
    banner_cell.fill = navy_fill
    banner_cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)

    ws["A3"] = "Automated System Generated Procurement Order | Autonomous Supply Chain Engine"
    ws["A3"].font = Font(name="Calibri", size=10, italic=True, color="595959")

    # 2. METADATA CARDS: VENDOR INFO & ORDER INFO
    ws.merge_cells("A5:D5")
    ws["A5"] = "VENDOR DETAILS (SUPPLIER)"
    ws["A5"].font = section_hdr_font
    ws["A5"].fill = navy_fill
    ws["A5"].alignment = left_align

    vendor_details = [
        ("Company Name:", supplier_name),
        ("Supplier ID:", f"SUP-{supplier_id:04d}"),
        ("Standard Lead Time:", f"{lead_time_days} Business Days"),
        ("Contract Status:", "Active Verified Vendor")
    ]
    for idx, (lbl, val) in enumerate(vendor_details, start=6):
        ws[f"A{idx}"] = lbl
        ws[f"A{idx}"].font = bold_font
        ws.merge_cells(f"B{idx}:D{idx}")
        ws[f"B{idx}"] = val
        ws[f"B{idx}"].font = regular_font

    # Right Box: Order Information
    ws.merge_cells("E5:I5")
    ws["E5"] = "PURCHASE ORDER METADATA"
    ws["E5"].font = section_hdr_font
    ws["E5"].fill = navy_fill
    ws["E5"].alignment = left_align

    order_details = [
        ("PO Number:", po_number),
        ("Order Date:", order_date.strftime("%d-%b-%Y")),
        ("Expected Delivery Date:", expected_delivery.strftime("%d-%b-%Y")),
        ("Delivery Destination:", "Central Distribution Center, New Delhi")
    ]
    for idx, (lbl, val) in enumerate(order_details, start=6):
        ws[f"E{idx}"] = lbl
        ws[f"E{idx}"].font = bold_font
        ws.merge_cells(f"F{idx}:I{idx}")
        ws[f"F{idx}"] = val
        ws[f"F{idx}"].font = regular_font

    # 3. LINE ITEMS TABLE
    start_row = 11
    headers = [
        "Item #", "SKU Code", "Product Description", "Warehouse", 
        "Current Stock", "Reorder Point (ROP)", "Order Qty", "Unit Cost (INR)", "Total Amount (INR)"
    ]

    for col_idx, h_text in enumerate(headers, start=1):
        cell = ws.cell(row=start_row, column=col_idx)
        cell.value = h_text
        cell.font = header_font
        cell.fill = navy_fill
        cell.alignment = center_align if col_idx in [1, 2, 5, 6, 7] else (right_align if col_idx in [8, 9] else left_align)

    current_r = start_row + 1
    item_counter = 1

    for _, row in items_df.iterrows():
        sku = row['sku_code']
        name = row['product_name']
        wh_name = row.get('warehouse_name', 'Main Hub')
        curr = int(row['current_stock'])
        rop = int(row['reorder_point'])
        qty = int(row['rec_order_qty'])
        cost = float(row['unit_cost'])

        row_fill = zebra_fill if item_counter % 2 == 0 else white_fill

        data_vals = [
            (item_counter, center_align, None),
            (sku, center_align, None),
            (name, left_align, None),
            (wh_name, left_align, None),
            (curr, center_align, "#,##0"),
            (rop, center_align, "#,##0"),
            (qty, center_align, "#,##0"),
            (cost, right_align, "Rs. #,##0.00"),
            (f"=G{current_r}*H{current_r}", right_align, "Rs. #,##0.00") # Dynamic Formula
        ]

        for col_idx, (val, align, num_fmt) in enumerate(data_vals, start=1):
            c = ws.cell(row=current_r, column=col_idx)
            c.value = val
            c.font = regular_font
            c.fill = row_fill
            c.alignment = align
            c.border = cell_border
            if num_fmt:
                c.number_format = num_fmt

        current_r += 1
        item_counter += 1

    # 4. TOTALS & FINANCIAL SUMMARY
    subtotal_row = current_r
    tax_row = current_r + 1
    grand_total_row = current_r + 2

    # Subtotal
    ws.merge_cells(f"A{subtotal_row}:H{subtotal_row}")
    ws[f"A{subtotal_row}"] = "Subtotal (Pre-Tax Amount):"
    ws[f"A{subtotal_row}"].font = bold_font
    ws[f"A{subtotal_row}"].alignment = right_align
    c_sub = ws[f"I{subtotal_row}"]
    c_sub.value = f"=SUM(I{start_row + 1}:I{subtotal_row - 1})"
    c_sub.font = bold_font
    c_sub.alignment = right_align
    c_sub.number_format = "Rs. #,##0.00"
    c_sub.border = cell_border

    # GST Tax (18%)
    ws.merge_cells(f"A{tax_row}:H{tax_row}")
    ws[f"A{tax_row}"] = "Estimated GST (18%):"
    ws[f"A{tax_row}"].font = regular_font
    ws[f"A{tax_row}"].alignment = right_align
    c_tax = ws[f"I{tax_row}"]
    c_tax.value = f"=I{subtotal_row}*0.18"
    c_tax.font = regular_font
    c_tax.alignment = right_align
    c_tax.number_format = "Rs. #,##0.00"
    c_tax.border = cell_border

    # Grand Total
    ws.merge_cells(f"A{grand_total_row}:H{grand_total_row}")
    ws[f"A{grand_total_row}"] = "TOTAL PURCHASE ORDER AMOUNT:"
    ws[f"A{grand_total_row}"].font = Font(name="Calibri", size=12, bold=True, color=navy_dark)
    ws[f"A{grand_total_row}"].alignment = right_align
    c_grand = ws[f"I{grand_total_row}"]
    c_grand.value = f"=I{subtotal_row}+I{tax_row}"
    c_grand.font = Font(name="Calibri", size=12, bold=True, color=navy_dark)
    c_grand.alignment = right_align
    c_grand.fill = soft_fill
    c_grand.number_format = "Rs. #,##0.00"
    c_grand.border = double_bottom

    # 5. AUTHORIZATION
    sign_row = grand_total_row + 3
    ws.merge_cells(f"A{sign_row}:D{sign_row}")
    ws[f"A{sign_row}"] = "Prepared By: Smart Inventory Automation Engine"
    ws[f"A{sign_row}"].font = footer_font

    ws.merge_cells(f"F{sign_row}:I{sign_row}")
    ws[f"F{sign_row}"] = "Authorized Procurement Officer"
    ws[f"F{sign_row}"].font = bold_font
    ws[f"F{sign_row}"].alignment = right_align

    ws.merge_cells(f"F{sign_row + 1}:I{sign_row + 1}")
    ws[f"F{sign_row + 1}"] = "____________________________ (Sign & Stamp)"
    ws[f"F{sign_row + 1}"].alignment = right_align

    # Column dimensions
    ws.column_dimensions["A"].width = 8   # Item #
    ws.column_dimensions["B"].width = 16  # SKU
    ws.column_dimensions["C"].width = 34  # Description
    ws.column_dimensions["D"].width = 24  # Warehouse
    ws.column_dimensions["E"].width = 14  # Current Stock
    ws.column_dimensions["F"].width = 18  # ROP
    ws.column_dimensions["G"].width = 14  # Order Qty
    ws.column_dimensions["H"].width = 18  # Unit Cost
    ws.column_dimensions["I"].width = 22  # Total Amount

    supplier_slug = slugify(supplier_name)
    filename = f"Purchase_Order_{supplier_slug}_{order_date.strftime('%Y%m%d')}.xlsx"
    filepath = os.path.join(po_dir, filename)
    wb.save(filepath)

    return filepath, filename, len(items_df)

def generate_all_critical_purchase_orders():
    print("=" * 75)
    print("[PHASE 3] AUTONOMOUS PURCHASE ORDER GENERATION ENGINE (OPENPYXL)")
    print("=" * 75)

    if not os.path.exists(REPORT_CSV):
        print(f"[-] Report file not found at {REPORT_CSV}. Running Phase 2 first...")
        from core_engine.demand_forecaster import run_forecasting_engine
        run_forecasting_engine()

    df = pd.read_csv(REPORT_CSV)
    print(f"[+] Loaded {len(df)} inventory records from Phase 2 analysis.")

    # Filter critical red alert SKUs
    red_df = df[df['status_code'] == 'RED']
    print(f"[*] Found {len(red_df)} SKUs in CRITICAL RED status requiring restock.")

    if len(red_df) == 0:
        print("[i] No items require reordering today. All inventory healthy!")
        return []

    # Group by Supplier
    grouped = red_df.groupby('supplier_id')
    print(f"[*] Grouping low-stock items into supplier purchase batches ({len(grouped)} distinct suppliers)...")

    generated_pos = []
    total_items_ordered = 0

    for supplier_id, group in grouped:
        supplier_name = group['supplier_name'].iloc[0]
        lead_time = int(group['lead_time_days'].iloc[0])

        filepath, filename, item_count = generate_supplier_purchase_order(
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            lead_time_days=lead_time,
            items_df=group,
            po_dir=PO_OUTPUT_DIR
        )

        generated_pos.append({
            'po_file': filename,
            'supplier_name': supplier_name,
            'items_count': item_count,
            'filepath': filepath
        })
        total_items_ordered += item_count
        print(f"  [+] Generated: {filename} ({item_count} critical SKUs for {supplier_name})")

    print("\n" + "=" * 75)
    print(f"[SUCCESS] PHASE 3 COMPLETE: {len(generated_pos)} PURCHASE ORDERS GENERATED SUCCESSFULLY!")
    print(f"Output Directory: {PO_OUTPUT_DIR}")
    print("=" * 75)

    return generated_pos

if __name__ == "__main__":
    generate_all_critical_purchase_orders()

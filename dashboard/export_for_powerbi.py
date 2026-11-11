"""
==============================================================================
SMART INVENTORY & DEMAND FORECASTING SYSTEM
POWER BI EXPORT & DATASET CONVERTER (export_for_powerbi.py)
Creates clean, relational flat-files for Power BI Desktop data modeling.
==============================================================================
"""

import os
import sys
import pandas as pd

DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_config import get_db_connection

def export_powerbi_data():
    print("=" * 65)
    print("[*] EXPORTING CLEAN DATASET FOR MICROSOFT POWER BI DESKTOP")
    print("=" * 65)

    conn, engine_type = get_db_connection()

    # Query unified analytical view
    query = """
        SELECT 
            p.sku_code AS "SKU Code",
            p.product_name AS "Product Name",
            c.category_name AS "Category",
            sup.supplier_name AS "Supplier Name",
            sup.lead_time_days AS "Supplier Lead Time (Days)",
            w.warehouse_name AS "Warehouse",
            w.city AS "Warehouse City",
            i.current_stock AS "Current Stock Level",
            i.safety_stock AS "Safety Stock Buffer",
            i.reorder_point AS "Reorder Point (ROP)",
            p.unit_cost AS "Unit Cost Price (INR)",
            p.selling_price AS "Unit Selling Price (INR)",
            ROUND(i.current_stock * p.unit_cost, 2) AS "Holding Asset Value (INR)",
            CASE 
                WHEN i.current_stock <= i.reorder_point THEN 'CRITICAL RED'
                WHEN i.current_stock <= ROUND(i.reorder_point * 1.25) THEN 'WARNING YELLOW'
                ELSE 'HEALTHY GREEN'
            END AS "Stock Health Status",
            CASE 
                WHEN i.current_stock <= i.reorder_point THEN p.standard_reorder_qty + (i.reorder_point - i.current_stock)
                ELSE 0
            END AS "Suggested Reorder Qty"
        FROM Inventory i
        JOIN Products p ON i.product_id = p.product_id
        JOIN Categories c ON p.category_id = c.category_id
        JOIN Suppliers sup ON p.supplier_id = sup.supplier_id
        JOIN Warehouses w ON i.warehouse_id = w.warehouse_id;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    output_csv = os.path.join(DIR, "inventory_powerbi_dataset.csv")
    df.to_csv(output_csv, index=False)

    print(f"[+] Successfully exported {len(df)} rows to: {output_csv}")
    print("[+] Ready for 1-click import into Microsoft Power BI Desktop!")

if __name__ == "__main__":
    export_powerbi_data()

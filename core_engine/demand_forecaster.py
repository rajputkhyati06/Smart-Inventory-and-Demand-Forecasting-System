"""
==============================================================================
SMART INVENTORY & DEMAND FORECASTING SYSTEM
DEMAND FORECASTING & REORDER ENGINE (demand_forecaster.py)
Ingests sales transactions, calculates rolling demand, computes ROP, and flags alerts.
==============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np

# Add project root to sys.path so we can import modules seamlessly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_config import get_db_connection
from core_engine.inventory_math import (
    calculate_safety_stock,
    calculate_reorder_point,
    calculate_recommended_order_quantity,
    classify_stock_health
)

def run_forecasting_engine(use_postgres=False):
    print("=" * 75)
    print("[PHASE 2] EXECUTING DEMAND FORECASTING & REORDER INTELLIGENCE ENGINE")
    print("=" * 75)

    conn, engine_type = get_db_connection(use_postgres=use_postgres)
    print(f"[*] Connected to Data Warehouse [{engine_type.upper()}]")

    # Step 1: Query historical sales transactions with product & supplier metadata
    query_sales = """
        SELECT 
            s.product_id,
            p.sku_code,
            p.product_name,
            c.category_name,
            sup.supplier_id,
            sup.supplier_name,
            sup.lead_time_days,
            p.unit_cost,
            p.selling_price,
            p.standard_reorder_qty,
            s.warehouse_id,
            w.warehouse_name,
            s.transaction_date,
            s.quantity_sold
        FROM Sales_Transactions s
        JOIN Products p ON s.product_id = p.product_id
        JOIN Categories c ON p.category_id = c.category_id
        JOIN Suppliers sup ON p.supplier_id = sup.supplier_id
        JOIN Warehouses w ON s.warehouse_id = w.warehouse_id
        ORDER BY s.product_id, s.transaction_date ASC;
    """
    sales_df = pd.read_sql_query(query_sales, conn)
    print(f"[+] Loaded {len(sales_df):,} historical transaction rows for analysis.")

    # Step 2: Query current warehouse inventory levels
    query_inventory = """
        SELECT 
            i.inventory_id,
            i.product_id,
            i.warehouse_id,
            i.current_stock
        FROM Inventory i;
    """
    inventory_df = pd.read_sql_query(query_inventory, conn)
    print(f"[+] Loaded {len(inventory_df):,} live warehouse inventory lines.")

    # Step 3: Compute Statistical Demand Metrics per (product_id, warehouse_id)
    # Using the most recent 90-day window for responsive forecasting
    sales_df['transaction_date'] = pd.to_datetime(sales_df['transaction_date'])
    max_date = sales_df['transaction_date'].max()
    ninety_days_ago = max_date - pd.Timedelta(days=90)
    recent_sales = sales_df[sales_df['transaction_date'] >= ninety_days_ago]

    # Aggregate daily sales per product per warehouse
    daily_agg = recent_sales.groupby(['product_id', 'warehouse_id', 'transaction_date'])['quantity_sold'].sum().reset_index()

    # Calculate Mean Daily Demand (d) and Standard Deviation (sigma_d)
    stats_df = daily_agg.groupby(['product_id', 'warehouse_id'])['quantity_sold'].agg(
        avg_daily_demand='mean',
        std_daily_demand='std'
    ).reset_index()

    # Fill NaN std (if single transaction) with 0.1
    stats_df['std_daily_demand'] = stats_df['std_daily_demand'].fillna(0.1)

    # Step 4: Merge Metadata, Inventory & Statistics
    prod_meta = sales_df[['product_id', 'sku_code', 'product_name', 'category_name', 
                          'supplier_id', 'supplier_name', 'lead_time_days', 
                          'unit_cost', 'selling_price', 'standard_reorder_qty']].drop_duplicates()
    
    wh_meta = sales_df[['warehouse_id', 'warehouse_name']].drop_duplicates()

    merged = pd.merge(inventory_df, stats_df, on=['product_id', 'warehouse_id'], how='left')
    merged = pd.merge(merged, prod_meta, on='product_id', how='left')
    merged = pd.merge(merged, wh_meta, on='warehouse_id', how='left')

    # Fill any missing demand stats with overall product mean
    overall_mean = sales_df.groupby('product_id')['quantity_sold'].mean().to_dict()
    merged['avg_daily_demand'] = merged['avg_daily_demand'].fillna(merged['product_id'].map(overall_mean)).fillna(5.0)
    merged['std_daily_demand'] = merged['std_daily_demand'].fillna(2.0)

    # Step 5: Apply Mathematical Formulas (Safety Stock, ROP, Order Qty, Health Status)
    results = []
    db_updates = []

    for _, row in merged.iterrows():
        avg_demand = round(float(row['avg_daily_demand']), 2)
        std_demand = round(float(row['std_daily_demand']), 2)
        lead_time = int(row['lead_time_days'])
        curr_stock = int(row['current_stock'])
        std_batch = int(row['standard_reorder_qty'])

        # Core Mathematical Calculations
        safety_stock = calculate_safety_stock(std_demand, lead_time, service_factor=1.65)
        reorder_point = calculate_reorder_point(avg_demand, lead_time, safety_stock)
        rec_order_qty = calculate_recommended_order_quantity(std_batch, reorder_point, curr_stock)
        status_code, status_label, urgency = classify_stock_health(curr_stock, reorder_point)

        # Total holding value & potential purchase order cost
        stock_value = round(curr_stock * float(row['unit_cost']), 2)
        po_cost = round(rec_order_qty * float(row['unit_cost']), 2)

        results.append({
            'product_id': row['product_id'],
            'warehouse_id': row['warehouse_id'],
            'warehouse_name': row['warehouse_name'],
            'sku_code': row['sku_code'],
            'product_name': row['product_name'],
            'category_name': row['category_name'],
            'supplier_id': row['supplier_id'],
            'supplier_name': row['supplier_name'],
            'lead_time_days': lead_time,
            'unit_cost': float(row['unit_cost']),
            'selling_price': float(row['selling_price']),
            'current_stock': curr_stock,
            'avg_daily_demand': avg_demand,
            'demand_std_dev': std_demand,
            'safety_stock': safety_stock,
            'reorder_point': reorder_point,
            'rec_order_qty': rec_order_qty,
            'status_code': status_code,
            'status_label': status_label,
            'urgency': urgency,
            'stock_value': stock_value,
            'potential_po_cost': po_cost
        })

        db_updates.append((safety_stock, reorder_point, int(row['product_id']), int(row['warehouse_id'])))

    result_df = pd.DataFrame(results)

    # Step 6: Update Database with Dynamic Safety Stock and ROP
    cursor = conn.cursor()
    cursor.executemany("""
        UPDATE Inventory 
        SET safety_stock = ?, reorder_point = ?, last_updated = CURRENT_TIMESTAMP
        WHERE product_id = ? AND warehouse_id = ?;
    """, db_updates)
    conn.commit()
    conn.close()
    print("[+] Successfully updated Inventory table with dynamic Safety Stock & ROP values.")

    # Step 7: Export Analysis Report to CSV (Ready for Power BI in Phase 4)
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory_analysis_report.csv")
    result_df.to_csv(report_path, index=False)
    print(f"[+] Exported live intelligence report to CSV: {report_path}")

    # Step 8: Print Executive Alert Dashboard
    red_alerts = result_df[result_df['status_code'] == 'RED']
    yellow_alerts = result_df[result_df['status_code'] == 'YELLOW']
    green_healthy = result_df[result_df['status_code'] == 'GREEN']

    print("\n" + "=" * 75)
    print("EXECUTIVE INVENTORY HEALTH SUMMARY")
    print("=" * 75)
    print(f"  * Total Warehouse SKUs Tracked : {len(result_df)}")
    print(f"  * [RED] Critical Restock Needed  : {len(red_alerts)} SKUs (ACTION REQUIRED)")
    print(f"  * [YELLOW] Buffer Warning Zone  : {len(yellow_alerts)} SKUs")
    print(f"  * [GREEN] Healthy Stock Levels   : {len(green_healthy)} SKUs")
    print("=" * 75)

    print("\n[CRITICAL RED ALERT SKUs] (Current Stock <= Reorder Point):")
    print("-" * 75)
    print(f"{'SKU CODE':<14} | {'PRODUCT NAME':<24} | {'STOCK':<5} | {'ROP':<5} | {'DEFICIT':<7} | {'SUPPLIER':<20}")
    print("-" * 75)
    for _, item in red_alerts.head(10).iterrows():
        deficit = item['reorder_point'] - item['current_stock']
        print(f"{item['sku_code']:<14} | {item['product_name'][:23]:<24} | {item['current_stock']:<5} | {item['reorder_point']:<5} | -{deficit:<6} | {item['supplier_name'][:20]:<20}")
    print("-" * 75)

    print("\n" + "=" * 75)
    print("[SUCCESS] PHASE 2 COMPLETE: MATHEMATICAL BRAIN SUCCESSFULLY EXECUTED!")
    print("=" * 75)

    return result_df

if __name__ == "__main__":
    run_forecasting_engine()

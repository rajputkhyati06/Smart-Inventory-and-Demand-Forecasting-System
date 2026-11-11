"""
==============================================================================
SMART INVENTORY & DEMAND FORECASTING SYSTEM
POSTGRESQL SEED & DUMP GENERATOR (generate_postgres_dump.py)
Creates a complete standalone PostgreSQL dump file with 4,500+ records.
==============================================================================
"""

import os
import random
from datetime import datetime, timedelta

DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE = os.path.join(DIR, "schema_postgres.sql")
OUTPUT_SQL_FILE = os.path.join(DIR, "inventory_postgres_dump.sql")

def generate_postgres_sql():
    print("[*] Generating complete PostgreSQL DDL + DML dump...")

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    lines = []
    lines.append("-- ==============================================================================")
    lines.append("-- SMART INVENTORY SYSTEM - COMPLETE POSTGRESQL DATABASE DUMP")
    lines.append(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("-- Ready to execute in pgAdmin 4 (Query Tool) or via psql CLI")
    lines.append("-- ==============================================================================\n")
    lines.append("BEGIN;\n")
    lines.append(schema_sql)
    lines.append("\n-- ==============================================================================")
    lines.append("-- SEED DATA INSERTIONS")
    lines.append("-- ==============================================================================\n")

    # 1. Suppliers
    suppliers = [
        ("TechLogix Components Pvt Ltd", "Rajesh Sharma", "orders@techlogix.in", "+91 9811223344", 4, "Sector 62, Noida, UP"),
        ("Apex Electronics & Hardware", "Priya Verma", "sales@apexelectronics.com", "+91 9822334455", 7, "Okhla Phase III, New Delhi"),
        ("Metro Digital Supply Corp", "Amitabh Sen", "supply@metrodigital.co", "+91 9833445566", 5, "Nehru Place, New Delhi"),
        ("Nexa Audio & Wearables Ltd", "Sunil Kapoor", "b2b@nexaglobal.in", "+91 9844556677", 10, "Naraina Industrial Area, New Delhi"),
        ("Alpha Peripheral Traders", "Neha Singhal", "orders@alphatrade.in", "+91 9855667788", 3, "Civil Lines, Bijnor, UP"),
        ("Zenith Smart Devices LLP", "Vikas Malhotra", "contact@zenithdevices.com", "+91 9866778899", 12, "Bhiwandi Logistics Hub, Mumbai")
    ]
    lines.append("-- 1. Insert Suppliers")
    for s in suppliers:
        lines.append(f"INSERT INTO Suppliers (supplier_name, contact_person, contact_email, phone, lead_time_days, address) "
                     f"VALUES ('{s[0]}', '{s[1]}', '{s[2]}', '{s[3]}', {s[4]}, '{s[5]}');")
    lines.append("")

    # 2. Categories
    categories = [
        ("Mobile Accessories", "Charging cables, fast chargers, power banks, phone holders"),
        ("Computer Peripherals", "Keyboards, mice, webcams, USB hubs, mousepads"),
        ("Audio Devices", "Bluetooth earbuds, noise-canceling headphones, mini speakers"),
        ("Wearables & Fitness", "Smartwatches, fitness bands, replacement silicone straps"),
        ("Smart Home & Lighting", "Smart LED bulbs, smart plugs, desk ambient lights")
    ]
    lines.append("-- 2. Insert Categories")
    for c in categories:
        lines.append(f"INSERT INTO Categories (category_name, description) VALUES ('{c[0]}', '{c[1]}');")
    lines.append("")

    # 3. Warehouses
    warehouses = [
        ("Northern Hub Warehouse", "Bijnor", "Uttar Pradesh", 50000),
        ("Central Distribution Center", "New Delhi", "Delhi NCR", 120000),
        ("Western Depot", "Mumbai", "Maharashtra", 80000)
    ]
    lines.append("-- 3. Insert Warehouses")
    for w in warehouses:
        lines.append(f"INSERT INTO Warehouses (warehouse_name, city, state, total_capacity_units) "
                     f"VALUES ('{w[0]}', '{w[1]}', '{w[2]}', {w[3]});")
    lines.append("")

    # 4. Products
    products = [
        ("SKU-MOB-001", "65W GaN Fast Charger", 1, 1, 650.00, 1199.00, 80),
        ("SKU-MOB-002", "Braided USB-C to C Cable (2m)", 1, 1, 140.00, 349.00, 150),
        ("SKU-MOB-003", "20000mAh Power Bank (22.5W)", 1, 3, 950.00, 1699.00, 60),
        ("SKU-MOB-004", "MagSafe Car Mount Holder", 1, 5, 280.00, 699.00, 50),
        ("SKU-MOB-005", "3-in-1 Wireless Charging Stand", 1, 3, 850.00, 1599.00, 40),

        ("SKU-CMP-001", "Wireless Ergonomic Mouse", 2, 2, 420.00, 899.00, 75),
        ("SKU-CMP-002", "RGB Mechanical Keyboard (Blue Switch)", 2, 2, 1250.00, 2499.00, 45),
        ("SKU-CMP-003", "1080p FHD Pro Webcam", 2, 5, 780.00, 1499.00, 50),
        ("SKU-CMP-004", "7-in-1 Aluminum USB-C Hub", 2, 1, 620.00, 1299.00, 60),
        ("SKU-CMP-005", "Extended Desk Mat (900x400mm)", 2, 5, 210.00, 499.00, 100),

        ("SKU-AUD-001", "TWS Earbuds with ANC (Active Noise)", 3, 4, 1100.00, 2299.00, 70),
        ("SKU-AUD-002", "Over-Ear Wireless Headphones", 3, 4, 1450.00, 2999.00, 40),
        ("SKU-AUD-003", "Portable Bluetooth Speaker (10W)", 3, 3, 580.00, 1199.00, 85),
        ("SKU-AUD-004", "Gaming Headset with Boom Mic", 3, 4, 820.00, 1699.00, 50),
        ("SKU-AUD-005", "Collar Clip-on Lavalier Mic", 3, 5, 180.00, 499.00, 120),

        ("SKU-WER-001", "Smart Fitness Tracker Band 7", 4, 4, 850.00, 1799.00, 65),
        ("SKU-WER-002", "AMOLED Bluetooth Calling Smartwatch", 4, 6, 1600.00, 3299.00, 50),
        ("SKU-WER-003", "Silicone Magnetic Watch Strap (22mm)", 4, 5, 95.00, 299.00, 150),
        ("SKU-WER-004", "Stainless Steel Mesh Loop Band", 4, 5, 160.00, 449.00, 100),
        ("SKU-WER-005", "Smart Sports GPS Watch", 4, 6, 2800.00, 5499.00, 30),

        ("SKU-SMT-001", "Smart WiFi LED Bulb (9W RGB)", 5, 6, 240.00, 599.00, 120),
        ("SKU-SMT-002", "16A Smart Wi-Fi Plug with Energy Monitor", 5, 6, 380.00, 899.00, 90),
        ("SKU-SMT-003", "RGB Smart LED Light Strip (5m)", 5, 3, 450.00, 999.00, 80),
        ("SKU-SMT-004", "Motion Sensor Night Light", 5, 1, 130.00, 349.00, 140),
        ("SKU-SMT-005", "Smart IR Universal Remote Blaster", 5, 6, 390.00, 799.00, 60)
    ]
    lines.append("-- 4. Insert Products")
    for p in products:
        lines.append(f"INSERT INTO Products (sku_code, product_name, category_id, supplier_id, unit_cost, selling_price, standard_reorder_qty) "
                     f"VALUES ('{p[0]}', '{p[1]}', {p[2]}, {p[3]}, {p[4]}, {p[5]}, {p[6]});")
    lines.append("")

    # 5. Inventory
    lines.append("-- 5. Insert Inventory (with deliberate critical low stock on SKUs 1, 2, 7, 11, 16 to trigger ROP)")
    for prod_id in range(1, 26):
        for wh_id in [1, 2]:
            if prod_id in [1, 2, 7, 11, 16]:
                curr_stock = random.randint(4, 15) # CRITICAL LOW
            elif prod_id in [3, 8, 12, 17, 21]:
                curr_stock = random.randint(30, 55) # BUFFER WARNING
            else:
                curr_stock = random.randint(110, 320) # HEALTHY

            lines.append(f"INSERT INTO Inventory (product_id, warehouse_id, current_stock, safety_stock, reorder_point, max_stock_capacity) "
                         f"VALUES ({prod_id}, {wh_id}, {curr_stock}, 0, 0, 500);")
    lines.append("")

    # 6. Sales Transactions (180 days)
    lines.append("-- 6. Insert Sales Transactions (180 Days of Daily Logs)")
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)
    payment_methods = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery", "Net Banking"]

    txn_values = []
    current_date = start_date
    batch_count = 0

    while current_date <= end_date:
        is_weekend = current_date.weekday() in (5, 6)
        
        for prod_idx, p in enumerate(products, start=1):
            price = p[5]
            base_sales = random.randint(3, 16)
            if is_weekend:
                base_sales = int(base_sales * random.uniform(1.3, 1.6))
            if random.random() < 0.08:
                base_sales += random.randint(8, 20)

            wh_id = random.choices([2, 1, 3], weights=[50, 35, 15])[0]
            total_rev = round(base_sales * price, 2)
            method = random.choice(payment_methods)
            d_str = current_date.strftime("%Y-%m-%d")

            txn_values.append(f"({prod_idx}, {wh_id}, '{d_str}', {base_sales}, {price}, {total_rev}, '{method}')")

            # Batch insert in chunks of 500 for optimal SQL parsing speed
            if len(txn_values) >= 500:
                lines.append(f"INSERT INTO Sales_Transactions (product_id, warehouse_id, transaction_date, quantity_sold, unit_sale_price, total_revenue, payment_method) VALUES\n" + ",\n".join(txn_values) + ";")
                txn_values = []
                batch_count += 1

        current_date += timedelta(days=1)

    if txn_values:
        lines.append(f"INSERT INTO Sales_Transactions (product_id, warehouse_id, transaction_date, quantity_sold, unit_sale_price, total_revenue, payment_method) VALUES\n" + ",\n".join(txn_values) + ";")

    lines.append("\nCOMMIT;\n")

    with open(OUTPUT_SQL_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))

    print(f"[+] Successfully generated PostgreSQL Dump: {OUTPUT_SQL_FILE}")
    print(f"[+] Total SQL Dump Size: {os.path.getsize(OUTPUT_SQL_FILE):,} bytes")

if __name__ == "__main__":
    generate_postgres_sql()

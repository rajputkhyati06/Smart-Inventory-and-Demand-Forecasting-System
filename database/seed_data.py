"""
==============================================================================
SMART INVENTORY & DEMAND FORECASTING SYSTEM
DATABASE POPULATION / SEED SCRIPT (seed_data.py)
Generates 180+ days of realistic retail sales history and warehouse inventory.
==============================================================================
"""

import os
import sqlite3
import random
from datetime import datetime, timedelta

# Database file paths
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "inventory.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")

def initialize_database():
    print("=" * 65)
    print("[PHASE 1] INITIALIZING DATABASE & SEEDING REALISTIC DATA")
    print("=" * 65)

    # 1. Connect & Execute Schema
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    print("[+] Database schema initialized from 'schema.sql'")

    # Clear existing data if any (for clean re-runs)
    tables = ["Sales_Transactions", "Inventory", "Products", "Warehouses", "Categories", "Suppliers"]
    for t in tables:
        cursor.execute(f"DELETE FROM {t}")
    conn.commit()

    # 2. Seed Suppliers (With realistic lead times in days)
    suppliers = [
        ("TechLogix Components Pvt Ltd", "Rajesh Sharma", "orders@techlogix.in", "+91 9811223344", 4, "Sector 62, Noida, UP"),
        ("Apex Electronics & Hardware", "Priya Verma", "sales@apexelectronics.com", "+91 9822334455", 7, "Okhla Phase III, New Delhi"),
        ("Metro Digital Supply Corp", "Amitabh Sen", "supply@metrodigital.co", "+91 9833445566", 5, "Nehru Place, New Delhi"),
        ("Nexa Audio & Wearables Ltd", "Sunil Kapoor", "b2b@nexaglobal.in", "+91 9844556677", 10, "Naraina Industrial Area, New Delhi"),
        ("Alpha Peripheral Traders", "Neha Singhal", "orders@alphatrade.in", "+91 9855667788", 3, "Civil Lines, Bijnor, UP"),
        ("Zenith Smart Devices LLP", "Vikas Malhotra", "contact@zenithdevices.com", "+91 9866778899", 12, "Bhiwandi Logistics Hub, Mumbai")
    ]
    cursor.executemany("""
        INSERT INTO Suppliers (supplier_name, contact_person, contact_email, phone, lead_time_days, address)
        VALUES (?, ?, ?, ?, ?, ?)
    """, suppliers)
    print(f"[+] Seeded {len(suppliers)} Suppliers with variable delivery lead-times (3 - 12 days).")

    # 3. Seed Categories
    categories = [
        ("Mobile Accessories", "Charging cables, fast chargers, power banks, phone holders"),
        ("Computer Peripherals", "Keyboards, mice, webcams, USB hubs, mousepads"),
        ("Audio Devices", "Bluetooth earbuds, noise-canceling headphones, mini speakers"),
        ("Wearables & Fitness", "Smartwatches, fitness bands, replacement silicone straps"),
        ("Smart Home & Lighting", "Smart LED bulbs, smart plugs, desk ambient lights")
    ]
    cursor.executemany("""
        INSERT INTO Categories (category_name, description)
        VALUES (?, ?)
    """, categories)
    print(f"[+] Seeded {len(categories)} Product Categories.")

    # 4. Seed Warehouses
    warehouses = [
        ("Northern Hub Warehouse", "Bijnor", "Uttar Pradesh", 50000),
        ("Central Distribution Center", "New Delhi", "Delhi NCR", 120000),
        ("Western Depot", "Mumbai", "Maharashtra", 80000)
    ]
    cursor.executemany("""
        INSERT INTO Warehouses (warehouse_name, city, state, total_capacity_units)
        VALUES (?, ?, ?, ?)
    """, warehouses)
    print(f"[+] Seeded {len(warehouses)} Regional Warehouses.")

    # 5. Seed 25 High-Volume Retail Products
    products = [
        # Mobile Accessories (Cat 1)
        ("SKU-MOB-001", "65W GaN Fast Charger", 1, 1, 650.00, 1199.00, 80),
        ("SKU-MOB-002", "Braided USB-C to C Cable (2m)", 1, 1, 140.00, 349.00, 150),
        ("SKU-MOB-003", "20000mAh Power Bank (22.5W)", 1, 3, 950.00, 1699.00, 60),
        ("SKU-MOB-004", "MagSafe Car Mount Holder", 1, 5, 280.00, 699.00, 50),
        ("SKU-MOB-005", "3-in-1 Wireless Charging Stand", 1, 3, 850.00, 1599.00, 40),

        # Computer Peripherals (Cat 2)
        ("SKU-CMP-001", "Wireless Ergonomic Mouse", 2, 2, 420.00, 899.00, 75),
        ("SKU-CMP-002", "RGB Mechanical Keyboard (Blue Switch)", 2, 2, 1250.00, 2499.00, 45),
        ("SKU-CMP-003", "1080p FHD Pro Webcam", 2, 5, 780.00, 1499.00, 50),
        ("SKU-CMP-004", "7-in-1 Aluminum USB-C Hub", 2, 1, 620.00, 1299.00, 60),
        ("SKU-CMP-005", "Extended Desk Mat (900x400mm)", 2, 5, 210.00, 499.00, 100),

        # Audio Devices (Cat 3)
        ("SKU-AUD-001", "TWS Earbuds with ANC (Active Noise)", 3, 4, 1100.00, 2299.00, 70),
        ("SKU-AUD-002", "Over-Ear Wireless Headphones", 3, 4, 1450.00, 2999.00, 40),
        ("SKU-AUD-003", "Portable Bluetooth Speaker (10W)", 3, 3, 580.00, 1199.00, 85),
        ("SKU-AUD-004", "Gaming Headset with Boom Mic", 3, 4, 820.00, 1699.00, 50),
        ("SKU-AUD-005", "Collar Clip-on Lavalier Mic", 3, 5, 180.00, 499.00, 120),

        # Wearables & Fitness (Cat 4)
        ("SKU-WER-001", "Smart Fitness Tracker Band 7", 4, 4, 850.00, 1799.00, 65),
        ("SKU-WER-002", "AMOLED Bluetooth Calling Smartwatch", 4, 6, 1600.00, 3299.00, 50),
        ("SKU-WER-003", "Silicone Magnetic Watch Strap (22mm)", 4, 5, 95.00, 299.00, 150),
        ("SKU-WER-004", "Stainless Steel Mesh Loop Band", 4, 5, 160.00, 449.00, 100),
        ("SKU-WER-005", "Smart Sports GPS Watch", 4, 6, 2800.00, 5499.00, 30),

        # Smart Home & Lighting (Cat 5)
        ("SKU-SMT-001", "Smart WiFi LED Bulb (9W RGB)", 5, 6, 240.00, 599.00, 120),
        ("SKU-SMT-002", "16A Smart Wi-Fi Plug with Energy Monitor", 5, 6, 380.00, 899.00, 90),
        ("SKU-SMT-003", "RGB Smart LED Light Strip (5m)", 5, 3, 450.00, 999.00, 80),
        ("SKU-SMT-004", "Motion Sensor Night Light", 5, 1, 130.00, 349.00, 140),
        ("SKU-SMT-005", "Smart IR Universal Remote Blaster", 5, 6, 390.00, 799.00, 60)
    ]

    cursor.executemany("""
        INSERT INTO Products (sku_code, product_name, category_id, supplier_id, unit_cost, selling_price, standard_reorder_qty)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, products)
    print(f"[+] Seeded {len(products)} Product SKUs across 5 categories.")

    # 6. Generate 180 Days of Daily Sales History (Past 6 Months)
    print("[*] Generating 180 days of realistic sales transaction records...")
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)
    
    transactions = []
    payment_methods = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery", "Net Banking"]
    
    cursor.execute("SELECT product_id, selling_price FROM Products")
    prod_data = cursor.fetchall()
    
    current_date = start_date
    while current_date <= end_date:
        is_weekend = current_date.weekday() in (5, 6) # Saturday or Sunday
        
        for prod_id, price in prod_data:
            base_sales = random.randint(3, 16)
            if is_weekend:
                base_sales = int(base_sales * random.uniform(1.3, 1.6)) # Weekend surge
            
            if random.random() < 0.08:
                base_sales += random.randint(8, 20) # Occasional spike

            # Assign warehouse: 50% Delhi, 35% Bijnor, 15% Mumbai
            wh_id = random.choices([2, 1, 3], weights=[50, 35, 15])[0]
            
            total_rev = round(base_sales * price, 2)
            method = random.choice(payment_methods)
            
            transactions.append((
                prod_id,
                wh_id,
                current_date.strftime("%Y-%m-%d"),
                base_sales,
                price,
                total_rev,
                method
            ))
            
        current_date += timedelta(days=1)

    cursor.executemany("""
        INSERT INTO Sales_Transactions (product_id, warehouse_id, transaction_date, quantity_sold, unit_sale_price, total_revenue, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, transactions)
    print(f"[+] Generated {len(transactions):,} sales transactions over 180 days.")

    # 7. Initialize Inventory Table (Central Warehouse Delhi & Northern Hub Bijnor)
    inventory_records = []
    
    for prod_id, _ in prod_data:
        for wh_id in [1, 2]: # Bijnor and Delhi
            if prod_id in [1, 2, 7, 11, 16]: # Critical low stock (triggers Reorder PO)
                curr_stock = random.randint(4, 15)
            elif prod_id in [3, 8, 12, 17, 21]: # Moderate buffer stock
                curr_stock = random.randint(30, 55)
            else: # Healthy stock
                curr_stock = random.randint(110, 320)
                
            inventory_records.append((
                prod_id,
                wh_id,
                curr_stock,
                0, # placeholder safety_stock
                0, # placeholder ROP
                500
            ))

    cursor.executemany("""
        INSERT INTO Inventory (product_id, warehouse_id, current_stock, safety_stock, reorder_point, max_stock_capacity)
        VALUES (?, ?, ?, ?, ?, ?)
    """, inventory_records)
    print(f"[+] Seeded {len(inventory_records)} Warehouse inventory lines.")

    conn.commit()
    conn.close()

    print("\n" + "=" * 65)
    print("[SUCCESS] PHASE 1 COMPLETE: SQL DATABASE SUCCESSFULLY POPULATED!")
    print(f"Database File: {DB_PATH}")
    print("=" * 65)

if __name__ == "__main__":
    initialize_database()

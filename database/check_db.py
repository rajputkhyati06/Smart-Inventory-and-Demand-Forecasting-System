import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- DATABASE SUMMARY CHECK ---")
tables = ["Suppliers", "Categories", "Warehouses", "Products", "Inventory", "Sales_Transactions"]
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f"Table '{t}': {count:,} rows")

print("\n--- SAMPLE PRODUCTS & STOCK ---")
cursor.execute("""
    SELECT p.sku_code, p.product_name, c.category_name, p.unit_cost, p.selling_price, i.current_stock
    FROM Products p
    JOIN Categories c ON p.category_id = c.category_id
    JOIN Inventory i ON p.product_id = i.product_id
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1][:25]:<25} | {row[2]:<20} | Cost: Rs.{row[3]} | Price: Rs.{row[4]} | Stock: {row[5]}")

conn.close()

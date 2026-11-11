"""
==============================================================================
SMART INVENTORY SYSTEM - POSTGRESQL LOADER (load_to_postgres.py)
Automates creation and seeding of PostgreSQL database.
==============================================================================
"""

import os
import sys
import getpass
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DIR = os.path.dirname(os.path.abspath(__file__))
DUMP_FILE = os.path.join(DIR, "inventory_postgres_dump.sql")

def setup_postgres():
    print("=" * 65)
    print("🐘 POSTGRESQL DATABASE AUTOMATED SETUP & SEEDING")
    print("=" * 65)

    host = input("Enter PostgreSQL Host [default: localhost]: ").strip() or "localhost"
    port = input("Enter PostgreSQL Port [default: 5432]: ").strip() or "5432"
    user = input("Enter PostgreSQL User [default: postgres]: ").strip() or "postgres"
    password = getpass.getpass(f"Enter PostgreSQL Password for '{user}': ")

    target_db = "inventory_management_db"

    # Step 1: Connect to default postgres DB to create target database if needed
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if DB exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (target_db,))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f'CREATE DATABASE "{target_db}";')
            print(f"[+] Database '{target_db}' created successfully.")
        else:
            print(f"[i] Database '{target_db}' already exists.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[-] Error connecting to PostgreSQL: {e}")
        return

    # Step 2: Connect to target DB and execute SQL Dump
    try:
        print(f"[*] Executing schema and seeding data into '{target_db}'...")
        conn_target = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=target_db
        )
        cursor_target = conn_target.cursor()

        with open(DUMP_FILE, "r", encoding="utf-8") as f:
            sql_script = f.read()

        cursor_target.execute(sql_script)
        conn_target.commit()

        print("=" * 65)
        print(f"[SUCCESS] POSTGRESQL DATABASE '{target_db}' IS READY!")
        print("=" * 65)

        # Quick stats check
        for table in ["Suppliers", "Categories", "Warehouses", "Products", "Inventory", "Sales_Transactions"]:
            cursor_target.execute(f"SELECT COUNT(*) FROM {table}")
            cnt = cursor_target.fetchone()[0]
            print(f"  • Table '{table}': {cnt:,} rows")

        cursor_target.close()
        conn_target.close()

    except Exception as e:
        print(f"[-] Error executing dump: {e}")

if __name__ == "__main__":
    setup_postgres()

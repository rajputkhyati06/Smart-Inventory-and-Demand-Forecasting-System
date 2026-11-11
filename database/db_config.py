"""
==============================================================================
SMART INVENTORY SYSTEM - DATABASE ADAPTER & CONFIGURATION (db_config.py)
Provides seamless database connections for PostgreSQL or SQLite.
==============================================================================
"""

import os
import sqlite3

DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(DIR, "inventory.db")

# PostgreSQL Configuration Defaults (Can be edited or set via env vars)
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASS = os.getenv("PG_PASS", "postgres")
PG_DB   = os.getenv("PG_DB", "inventory_management_db")

def get_db_connection(use_postgres=False):
    """
    Returns an active database connection and engine type ('postgres' or 'sqlite').
    """
    if use_postgres:
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                user=PG_USER,
                password=PG_PASS,
                dbname=PG_DB
            )
            return conn, "postgres"
        except Exception as e:
            print(f"[!] PostgreSQL connection failed ({e}). Falling back to local SQLite database.")

    # Default / Fallback: SQLite
    conn = sqlite3.connect(SQLITE_PATH)
    return conn, "sqlite"

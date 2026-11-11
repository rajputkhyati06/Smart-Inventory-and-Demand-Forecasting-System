-- ==============================================================================
-- SMART INVENTORY & DEMAND FORECASTING SYSTEM
-- DATABASE SCHEMA (Third Normal Form - 3NF)
-- Compatible with SQLite & PostgreSQL
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- 1. SUPPLIERS TABLE
-- Stores vendor details and delivery lead times (crucial for ROP calculation)
CREATE TABLE IF NOT EXISTS Suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT NOT NULL,
    contact_person TEXT,
    contact_email TEXT NOT NULL,
    phone TEXT,
    lead_time_days INTEGER NOT NULL CHECK(lead_time_days > 0), -- Days taken to deliver replenishment
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CATEGORIES TABLE
-- Classifies products into business departments
CREATE TABLE IF NOT EXISTS Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- 3. WAREHOUSES TABLE
-- Tracks storage locations and total storage capacities
CREATE TABLE IF NOT EXISTS Warehouses (
    warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
    warehouse_name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    total_capacity_units INTEGER NOT NULL CHECK(total_capacity_units > 0)
);

-- 4. PRODUCTS TABLE
-- Product catalog with cost, selling price, and reorder batch quantity
CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku_code TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL CHECK(unit_cost > 0),
    selling_price DECIMAL(10, 2) NOT NULL CHECK(selling_price >= unit_cost),
    standard_reorder_qty INTEGER NOT NULL DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE RESTRICT,
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id) ON DELETE RESTRICT
);

-- 5. INVENTORY TABLE
-- Live storage levels, computed safety stock, and dynamic reorder threshold (ROP)
CREATE TABLE IF NOT EXISTS Inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    current_stock INTEGER NOT NULL DEFAULT 0 CHECK(current_stock >= 0),
    safety_stock INTEGER NOT NULL DEFAULT 0,
    reorder_point INTEGER NOT NULL DEFAULT 0,
    max_stock_capacity INTEGER NOT NULL DEFAULT 500,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, warehouse_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id) REFERENCES Warehouses(warehouse_id) ON DELETE CASCADE
);

-- 6. SALES_TRANSACTIONS TABLE
-- Historical sales ledger storing daily checkout quantities for demand forecasting
CREATE TABLE IF NOT EXISTS Sales_Transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    quantity_sold INTEGER NOT NULL CHECK(quantity_sold > 0),
    unit_sale_price DECIMAL(10, 2) NOT NULL,
    total_revenue DECIMAL(10, 2) NOT NULL,
    payment_method TEXT DEFAULT 'UPI',
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id) REFERENCES Warehouses(warehouse_id) ON DELETE CASCADE
);

-- INDEXES FOR HIGH-SPEED ANALYTICAL QUERIES
CREATE INDEX IF NOT EXISTS idx_sales_prod_date ON Sales_Transactions(product_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_inventory_prod ON Inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier ON Products(supplier_id);

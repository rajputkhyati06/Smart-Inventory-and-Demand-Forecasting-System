-- ==============================================================================
-- SMART INVENTORY & DEMAND FORECASTING SYSTEM
-- POSTGRESQL NATIVE SCHEMA (Third Normal Form - 3NF)
-- Designed for PostgreSQL 14 / 15 / 16 / 17 / 18
-- ==============================================================================

-- Drop tables if they exist (clean restart)
DROP TABLE IF EXISTS Sales_Transactions CASCADE;
DROP TABLE IF EXISTS Inventory CASCADE;
DROP TABLE IF EXISTS Products CASCADE;
DROP TABLE IF EXISTS Warehouses CASCADE;
DROP TABLE IF EXISTS Categories CASCADE;
DROP TABLE IF EXISTS Suppliers CASCADE;

-- 1. SUPPLIERS TABLE
-- Stores vendor details and delivery lead-time days (essential for ROP formula)
CREATE TABLE Suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100),
    contact_email VARCHAR(150) NOT NULL,
    phone VARCHAR(20),
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days > 0), -- Days taken to deliver restock
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. CATEGORIES TABLE
-- Segregates product SKUs into retail departments
CREATE TABLE Categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- 3. WAREHOUSES TABLE
-- Tracks regional storage godowns and unit holding capacities
CREATE TABLE Warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    warehouse_name VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    total_capacity_units INTEGER NOT NULL CHECK (total_capacity_units > 0)
);

-- 4. PRODUCTS TABLE
-- Master product catalog with SKU code, unit cost, price, and standard batch size
CREATE TABLE Products (
    product_id SERIAL PRIMARY KEY,
    sku_code VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(200) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES Categories(category_id) ON DELETE RESTRICT,
    supplier_id INTEGER NOT NULL REFERENCES Suppliers(supplier_id) ON DELETE RESTRICT,
    unit_cost NUMERIC(10, 2) NOT NULL CHECK (unit_cost > 0),
    selling_price NUMERIC(10, 2) NOT NULL CHECK (selling_price >= unit_cost),
    standard_reorder_qty INTEGER NOT NULL DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. INVENTORY TABLE
-- Live storage levels, computed safety stock buffer, and dynamic reorder threshold (ROP)
CREATE TABLE Inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES Products(product_id) ON DELETE CASCADE,
    warehouse_id INTEGER NOT NULL REFERENCES Warehouses(warehouse_id) ON DELETE CASCADE,
    current_stock INTEGER NOT NULL DEFAULT 0 CHECK (current_stock >= 0),
    safety_stock INTEGER NOT NULL DEFAULT 0,
    reorder_point INTEGER NOT NULL DEFAULT 0,
    max_stock_capacity INTEGER NOT NULL DEFAULT 500,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_product_warehouse UNIQUE (product_id, warehouse_id)
);

-- 6. SALES_TRANSACTIONS TABLE
-- Historical checkout log storing daily units sold for moving-average demand forecasting
CREATE TABLE Sales_Transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES Products(product_id) ON DELETE CASCADE,
    warehouse_id INTEGER NOT NULL REFERENCES Warehouses(warehouse_id) ON DELETE CASCADE,
    transaction_date DATE NOT NULL,
    quantity_sold INTEGER NOT NULL CHECK (quantity_sold > 0),
    unit_sale_price NUMERIC(10, 2) NOT NULL,
    total_revenue NUMERIC(10, 2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'UPI'
);

-- HIGH PERFORMANCE INDEXES FOR ANALYTICAL AGGREGATION & JOINS
CREATE INDEX idx_sales_prod_date ON Sales_Transactions(product_id, transaction_date);
CREATE INDEX idx_sales_warehouse ON Sales_Transactions(warehouse_id);
CREATE INDEX idx_inventory_prod ON Inventory(product_id);
CREATE INDEX idx_products_supplier ON Products(supplier_id);
CREATE INDEX idx_products_category ON Products(category_id);

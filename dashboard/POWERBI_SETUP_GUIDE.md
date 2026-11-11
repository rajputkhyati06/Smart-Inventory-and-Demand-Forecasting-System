# 📊 Microsoft Power BI Desktop - Step-by-Step Setup Guide

This guide explains how to connect **Microsoft Power BI Desktop** to your project's dataset and build the **3 Interactive Dashboard Pages** for your final year presentation.

---

## 📂 1. Import Data into Power BI (10 Seconds)

1. Open **Power BI Desktop**.
2. Click on **Get Data** $\rightarrow$ Select **Text/CSV**.
3. Browse and select your dataset:
   `c:\Users\rajpu\OneDrive\Desktop\STARTUP\dashboard\inventory_powerbi_dataset.csv`
4. Click **Load**. (All 50 warehouse SKUs with calculated ROP and Stock Values will load instantly).

---

## 📐 2. Key DAX Measures to Create (Right-click Dataset -> New Measure)

#### 1. Total Stock Asset Value:
```dax
Total Inventory Value = SUM(inventory_powerbi_dataset[Holding Asset Value (INR)])
```

#### 2. Critical Stock-Out Alerts Count:
```dax
Critical Red Alerts = CALCULATE(COUNTROWS(inventory_powerbi_dataset), inventory_powerbi_dataset[Stock Health Status] = "CRITICAL RED")
```

#### 3. Healthy Stock Count:
```dax
Healthy Stock Count = CALCULATE(COUNTROWS(inventory_powerbi_dataset), inventory_powerbi_dataset[Stock Health Status] = "HEALTHY GREEN")
```

---

## 🎨 3. Dashboard Page Layout (3 Pages to Create)

### 📌 Page 1: Executive Overview Command Center
* **Top KPI Cards:**
  * Card 1: `Total Inventory Value` (Formatted as Currency ₹).
  * Card 2: `Critical Red Alerts` (Colored Red font).
  * Card 3: `Healthy Stock Count` (Colored Green font).
* **Donut Chart:**
  * **Legend:** `Stock Health Status`
  * **Values:** Count of `SKU Code`
  * **Colors:** Red for *CRITICAL RED*, Green for *HEALTHY GREEN*.
* **Bar Chart:**
  * **X-Axis:** `Category`
  * **Y-Axis:** `Holding Asset Value (INR)`

---

### 📌 Page 2: Stock Health & ROP Matrix Table
* **Matrix / Table Visual:**
  * **Columns:** `SKU Code`, `Product Name`, `Warehouse City`, `Current Stock Level`, `Reorder Point (ROP)`, `Suggested Reorder Qty`, `Stock Health Status`.
* **Conditional Formatting:**
  * Apply background color on `Stock Health Status`:
    * If `CRITICAL RED` $\rightarrow$ Soft Red (`#F8D7DA`)
    * If `HEALTHY GREEN` $\rightarrow$ Soft Green (`#D4EDDA`)
* **Slicer (Filter):** Add a Slicer for `Category` and `Warehouse City` on the left sidebar.

---

### 📌 Page 3: Supplier Lead Time & Performance
* **Bar Chart:**
  * **X-Axis:** `Supplier Name`
  * **Y-Axis:** `Supplier Lead Time (Days)`
* **Card / Callout:**
  * Total Distinct Suppliers: `DISTINCTCOUNT(inventory_powerbi_dataset[Supplier Name])`

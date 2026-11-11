# Smart Inventory & Demand Forecasting System

An intelligent inventory optimization and dynamic reorder point prediction platform built for retail businesses and small-to-medium enterprises. Developed as a B.Tech Computer Science & Engineering Final Year Project at **RV Institute of Technology, Bijnor (Affiliated to Dr. A.P.J. Abdul Kalam Technical University, Lucknow)**.

---

## Overview

Traditional retail operations rely heavily on manual spreadsheets or fixed reorder thresholds, resulting in either costly stockouts (lost revenue) or excess inventory holding costs. 

This system bridges that gap by continuously analyzing point-of-sale transaction patterns, calculating safety stock with lead-time variability, and triggering automated supplier purchase orders before critical stock depletion occurs.

---

## Core Capabilities

- **Demand Forecasting Engine:** Computes rolling average daily demand (\(d\)) and demand variance (\(\sigma_d\)) across a 90-day historical window.
- **Dynamic Safety Stock & ROP:** 
  $$\text{Safety Stock } (SS) = \lceil Z \times \sigma_d \times \sqrt{L} \rceil$$
  $$\text{Reorder Point } (ROP) = \lceil (d \times L) + SS \rceil$$
  Where:
  - \(Z = 1.65\) corresponds to a 95% service level
  - \(\sigma_d\) = Standard deviation of daily sales
  - \(L\) = Supplier lead time in days
  - \(d\) = Average daily sales rate
- **Automated Purchase Order Generator:** Groups low-stock SKUs by supplier, calculates required batch sizes, and formats professional Excel purchase orders with tax and cost calculations.
- **Interactive Web Command Center:** Built with Streamlit for live inventory health inspection, stock level distribution charts, simulated checkout transactions, and purchase order tracking.
- **Merchant Web Interface:** Lightweight HTML5, CSS3, and JavaScript frontend for single-screen quick adjustments and merchant simulations.
- **Dual Database Layer:** Seamlessly switches between local SQLite for zero-configuration testing and PostgreSQL for enterprise deployments.

---

## System Architecture

```
+-------------------------------------------------------------+
|                 Merchant / Executive Users                  |
+------------------------------+------------------------------+
                               |
            +------------------+------------------+
            |                                     |
    [Streamlit Web App]                   [HTML5/JS Portal]
            |                                     |
            +------------------+------------------+
                               |
               +---------------+---------------+
               |   Core Mathematical Engine    |
               |  (Rolling Demand, SS, ROP)    |
               +---------------+---------------+
                               |
               +---------------+---------------+
               |    Automated Procurement      |
               |  (Excel Purchase Orders)      |
               +---------------+---------------+
                               |
        +----------------------+----------------------+
        |                                             |
 [SQLite Database]                           [PostgreSQL 18]
```

---

## Project Structure

```
STARTUP/
│
├── app.py                             # Interactive Streamlit dashboard
├── test_system_integration.py         # End-to-end test suite
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git exclusion rules
├── VIVA_DEMO_AND_DEFENSE_GUIDE.md     # Academic demonstration guide
│
├── core_engine/
│   ├── inventory_math.py              # Statistical forecasting formulas
│   └── demand_forecaster.py           # Database batch analysis runner
│
├── automation/
│   ├── po_generator.py                # Automated Excel PO generator
│   └── purchase_orders/               # Generated supplier order workbooks
│
├── database/
│   ├── db_config.py                   # SQLite / PostgreSQL connector
│   ├── schema.sql                     # SQLite schema
│   ├── schema_postgres.sql            # PostgreSQL 3NF schema
│   ├── seed_data.py                   # Realistic transaction data generator
│   └── inventory.db                   # Populated local database
│
├── dashboard/
│   ├── export_for_powerbi.py          # Power BI dataset exporter
│   └── POWERBI_SETUP_GUIDE.md         # Business intelligence guide
│
└── frontend/
    ├── index.html                     # Merchant web portal
    ├── style.css                      # Visual styling
    └── app.js                         # Dynamic client calculations
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Installation

Clone this repository:
```bash
git clone https://github.com/rajputkhyati06/Smart-Inventory-and-Demand-Forecasting-System.git
cd Smart-Inventory-and-Demand-Forecasting-System
```

Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Running the Application

Launch the Streamlit web dashboard:
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

To launch the Merchant HTML portal, open `frontend/index.html` directly in any web browser.

### 4. Running System Integration Tests

Verify system integrity, mathematical calculations, and automated purchase order generation:
```bash
python test_system_integration.py
```

---

## Academic Credits & Acknowledgements

- **Institution:** RV Institute of Technology (RVIT), Bijnor (AKTU Code: 350)
- **Department:** Department of Computer Science & Engineering
- **Project Guide:** Dr. Ajay Singh
- **Project Team Members:**
  - Khyati Rajput (Lead, Roll No: 2305010100024)
  - Kashish Tyagi (Roll No: 2305010100023)
  - Aaditya Yadav
  - Aksha Parveen (Roll No: 2305010100005)

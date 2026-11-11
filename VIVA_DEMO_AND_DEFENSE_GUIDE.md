# 🎓 Final Year B.Tech Viva Demo & Defense Guide
### Project: Smart Inventory and Demand Forecasting System
**Institution:** RV Institute of Technology, Bijnor  
**Guide:** Dr. Ajay Singh (Assistant Professor, Dept. of CSE)  
**Team Members:** Khyati Rajput, Kashish Tyagi, Aaditya Yadav, Aksha Parveen  

---

## ⏱️ Part 1: The 3-Minute Live System Demonstration Flow

When the external examiners ask: *"Show me the project demo"*, follow this exact 3-minute sequence:

### 🎬 Minute 1: Launch & Executive Overview (Lead: Khyati Rajput)
1. **Double click on Desktop:** `Launch_Smart_Inventory_App.bat`.
2. The browser opens automatically showing the **Executive Command Center**:
   * Point to the top cards: *"Sir, as you can see, our system monitors 50 warehouse SKUs with an active asset valuation of over ₹9.4 Lakhs."*
   * Point to the Red Alert indicator: *"The system has detected that 24 SKUs are in CRITICAL RED status, meaning their current warehouse stock is lower than their calculated Reorder Point."*
   * Show the **Donut Chart** and the **Top 8 Critical Deficit Chart**.

### 🎬 Minute 2: Live POS Checkout & Instant Alert Trigger (Lead: Aaditya Yadav)
1. In the sidebar, click on **"🛒 Live POS Simulator"**:
   * *"Sir, let us simulate a live customer shopping at the counter right now."*
2. Select any product (e.g., `MagSafe Car Mount Holder`) that currently has healthy stock.
3. Set Quantity Sold to `25` units and click **"🛒 Complete Customer Sale"**.
4. **Watch the live trigger:**
   * The database decrements stock atomically (ACID compliance).
   * The system immediately recomputes the threshold.
   * A red banner pops up: **"🚨 ALERT: Stock has breached Reorder Point! Product is now in CRITICAL RED status!"**
   * *Examiners love seeing this real-time reactivity!*

### 🎬 Minute 3: Automated Purchase Order Dispatch in Excel (Lead: Kashish Tyagi & Aksha Parveen)
1. In the sidebar, click on **"📑 Automated Purchase Orders"**.
2. Click **"⚡ Generate Fresh Purchase Orders"**.
3. Point to the table of generated workbooks:
   * *"Instead of the manager manually typing supplier sheets, our OpenPyXL engine has automatically grouped all low-stock items by their respective suppliers."*
4. Click **"⬇️ Download Excel PO"** for any supplier (e.g. `TechLogix`).
5. Open the downloaded Excel file on the screen:
   * Show the **navy header**, **auto-generated PO Number**, **expected delivery date**, and click on the Total cell to show the **live dynamic Excel formula (`=G12*H12`)**.

---

## 🛡️ Part 2: Role-Wise Viva Defense Breakdown

### 🟢 1. Khyati Rajput (Lead / Problem & Business Impact)
* **What examiners will ask you:**
  * *Q: Why do small retailers need this when they already have Excel?*
  * **Answer:** *"Sir, regular Excel spreadsheets are static. They don't have multi-table relational integrity, they don't calculate standard deviation of daily demand, they don't account for supplier lead-time delays, and they cannot autonomously trigger orders. Our system is dynamic and autonomous."*
  * *Q: How does this make money as a startup?*
  * **Answer:** *"We use a SaaS subscription model (₹1,499/month per retail store). If an electronics or grocery store prevents even a single out-of-stock incident per month, they save ₹15,000 to ₹25,000, giving them a 10x Return on Investment (ROI)."*

### 🟡 2. Kashish Tyagi (Literature Review & Architecture)
* **What examiners will ask you:**
  * *Q: How is your system different from classical EOQ (Economic Order Quantity)?*
  * **Answer:** *"Sir, Ford Harris's 1913 EOQ assumes that customer demand is constant throughout the year. In real life, demand fluctuates wildly on weekends and festival days. Our system uses rolling 90-day demand averages and statistical variance ($\sigma_d$) to dynamically adapt."*
  * *Q: Why did you choose a 3-Tier Architecture?*
  * **Answer:** *"To ensure modularity and separation of concerns. Tier 1 (PostgreSQL/SQLite) manages data persistence, Tier 2 (Python) handles mathematical calculations, and Tier 3 (Power BI/Streamlit) handles visual presentation. We can upgrade the database or change dashboard styles without touching our core math logic."*

### 🔵 3. Aaditya Yadav (Pipeline & Mathematical Formulas)
* **What examiners will ask you:**
  * *Q: Explain the Safety Stock formula on the whiteboard.*
  * **Answer:** *"$\text{Safety Stock} = Z \times \sigma_d \times \sqrt{L}$. Here, $Z = 1.65$ represents a 95% cycle service level, $\sigma_d$ is the standard deviation of daily customer sales representing demand volatility, and $L$ is the vendor lead time in days. The square root of $L$ is used because demand variance accumulates over time as a random walk."*
  * *Q: How do you calculate Reorder Point (ROP)?*
  * **Answer:** *"$\text{ROP} = (\text{Average Daily Demand } d \times \text{Lead Time } L) + \text{Safety Stock}$. When stock reaches this number, the remaining units will last exactly until the supplier arrives, with safety stock protecting against unexpected surges."*

### 🟣 4. Aksha Parveen (Database Design 3NF & Technology Stack)
* **What examiners will ask you:**
  * *Q: Why is your database in Third Normal Form (3NF)?*
  * **Answer:** *"Sir, to eliminate data redundancy and prevent insertion, update, and deletion anomalies. For example, supplier details are kept in the `Suppliers` table and referenced by `supplier_id` in `Products`. If a supplier changes their phone number, we update it in exactly one place without corrupting historical sales transactions."*
  * *Q: Why use Python OpenPyXL instead of just exporting a CSV?*
  * **Answer:** *"Suppliers and corporate accounting departments require formatted, branded Purchase Orders with headers, date calculations, tax subtotals, and embedded formulas. OpenPyXL generates true binary `.xlsx` spreadsheets programmatically without requiring Microsoft Office on the host server."*

---

## 🎯 Part 3: Top 5 Tricky Examiner Questions (Quick-Fire Answers)

1. **"What if demand suddenly doubles during Diwali?"**
   * *Answer:* *"Our rolling-window engine calculates daily variance ($\sigma_d$). When sales surge, the standard deviation rises, which dynamically increases the Safety Stock buffer to absorb the shock."*
2. **"Why use SQLite and PostgreSQL together?"**
   * *Answer:* *"PostgreSQL is our enterprise production server for multi-user ACID concurrency. We also built an automated SQLite fallback adapter so the application can run offline at edge retail counters with zero server configuration."*
3. **"How does the system know when a supplier is late?"**
   * *Answer:* *"Each supplier record in the `Suppliers` table has a contracted `lead_time_days` attribute. The system tracks order dates and delivery dates to measure lead-time variance."*
4. **"Is your system scalable to 50,000 SKUs?"**
   * *Answer:* *"Yes, Sir. We implemented B-tree indexes on `(product_id, transaction_date)` and vectorized our calculations using Pandas and NumPy, which execute in C-speed in under 3 seconds."*
5. **"What will you add in Future Scope?"**
   * *Answer:* *"IoT RFID smart shelves for auto-decrementing physical stock, LSTM deep learning models for multi-year seasonal forecasting, and the WhatsApp Business API for instant supplier order confirmations."*

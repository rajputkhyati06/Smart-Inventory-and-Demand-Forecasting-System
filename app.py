"""
==============================================================================
SMART INVENTORY AND DEMAND FORECASTING SYSTEM
WEB APPLICATION & COMMAND CENTER (app.py)
Streamlit Interactive Dashboard for Executives, Managers, and Procurement Teams
==============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Setup Project Paths
DIR = os.path.dirname(os.path.abspath(__file__))
if DIR not in sys.path:
    sys.path.insert(0, DIR)

from database.db_config import get_db_connection
from core_engine.demand_forecaster import run_forecasting_engine
from automation.po_generator import generate_all_critical_purchase_orders

# Streamlit Page Config
st.set_page_config(
    page_title="Smart Inventory & Demand Forecasting System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean enterprise aesthetics
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1F4E78;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #555555;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F8F9FA;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #1F4E78;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .red-badge {
        background-color: #F8D7DA;
        color: #721C24;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .green-badge {
        background-color: #D4EDDA;
        color: #155724;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load data
@st.cache_data(ttl=60)
def load_inventory_data():
    report_csv = os.path.join(DIR, "core_engine", "inventory_analysis_report.csv")
    if not os.path.exists(report_csv):
        run_forecasting_engine()
    df = pd.read_csv(report_csv)
    return df

# Main Title Header
st.markdown('<p class="main-title">📦 Smart Inventory & Demand Forecasting System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Autonomous Decision Support & Procurement Platform | B.Tech CSE Final Year Project</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://img.icons8.com/fluency/96/warehouse-1.png", width=70)
st.sidebar.title("System Navigation")
menu = st.sidebar.radio(
    "Select View Mode:",
    ["📊 Executive Command Center", "🔍 Stock Health Explorer", "📑 Automated Purchase Orders", "🛒 Live POS Simulator"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Team Members:**")
st.sidebar.markdown("• Khyati Rajput (2305010100024)")
st.sidebar.markdown("• Kashish Tyagi (2305010100023)")
st.sidebar.markdown("• Aaditya Yadav (2305010100004)")
st.sidebar.markdown("• Aksha Parveen (2305010100005)")
st.sidebar.markdown("**Guide:** Dr. Ajay Singh (RVIT Bijnor)")

# Load data
df = load_inventory_data()

# ==============================================================================
# TAB 1: EXECUTIVE COMMAND CENTER
# ==============================================================================
if menu == "📊 Executive Command Center":
    # Top KPI Metrics Cards
    total_skus = len(df)
    red_count = len(df[df['status_code'] == 'RED'])
    green_count = len(df[df['status_code'] == 'GREEN'])
    total_stock_value = df['stock_value'].sum()
    total_po_deficit_cost = df[df['status_code'] == 'RED']['potential_po_cost'].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total SKUs Monitored", value=f"{total_skus} Units", delta="Multi-Warehouse")
    with col2:
        st.metric(label="Critical Stock-Out Alerts", value=f"{red_count} SKUs", delta="- Action Needed", delta_color="inverse")
    with col3:
        st.metric(label="Healthy Inventory", value=f"{green_count} SKUs", delta="Safe Operating Levels")
    with col4:
        st.metric(label="Total Holding Asset Value", value=f"₹{total_stock_value:,.2f}", delta="Active Capital")

    st.markdown("---")

    # Visual Charts (Plotly)
    c1, c2 = st.columns([1, 1.4])

    with c1:
        st.subheader("Inventory Health Distribution")
        status_counts = df['status_code'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        status_map = {'RED': '#E74C3C', 'YELLOW': '#F39C12', 'GREEN': '#27AE60'}
        fig_donut = px.pie(
            status_counts, 
            values='Count', 
            names='Status', 
            hole=0.5,
            color='Status',
            color_discrete_map=status_map
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(showlegend=True, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.subheader("Top 8 Critical SKUs (Current Stock vs ROP)")
        critical_subset = df[df['status_code'] == 'RED'].sort_values(by='current_stock').head(8)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=critical_subset['sku_code'],
            y=critical_subset['current_stock'],
            name='Current Stock (Godown)',
            marker_color='#E74C3C'
        ))
        fig_bar.add_trace(go.Bar(
            x=critical_subset['sku_code'],
            y=critical_subset['reorder_point'],
            name='Reorder Point (ROP Threshold)',
            marker_color='#1F4E78'
        ))
        fig_bar.update_layout(
            barmode='group',
            xaxis_title="Product SKU Code",
            yaxis_title="Units",
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Category Breakdown Chart
    st.subheader("Inventory Holding Capital by Product Category")
    cat_df = df.groupby('category_name')['stock_value'].sum().reset_index().sort_values(by='stock_value', ascending=False)
    fig_cat = px.bar(
        cat_df, 
        x='category_name', 
        y='stock_value', 
        labels={'stock_value': 'Stock Value (INR)', 'category_name': 'Category'},
        color='stock_value',
        color_continuous_scale='Blues'
    )
    fig_cat.update_layout(margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_cat, use_container_width=True)

# ==============================================================================
# TAB 2: INVENTORY HEALTH & REORDER EXPLORER
# ==============================================================================
elif menu == "🔍 Stock Health Explorer":
    st.subheader("Live Inventory Monitoring & Threshold Explorer")

    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        if st.button("🔄 Recalculate ROP Engine", type="primary"):
            with st.spinner("Analyzing 90-day moving sales demand and volatility..."):
                run_forecasting_engine()
                st.cache_data.clear()
                st.rerun()

    # Filters
    f1, f2, f3 = st.columns(3)
    with f1:
        cat_filter = st.selectbox("Filter by Category:", ["All Categories"] + list(df['category_name'].unique()))
    with f2:
        wh_filter = st.selectbox("Filter by Warehouse:", ["All Warehouses"] + list(df['warehouse_name'].unique()))
    with f3:
        status_filter = st.selectbox("Filter by Stock Status:", ["All Statuses", "RED (Critical Restock)", "GREEN (Healthy)"])

    filtered_df = df.copy()
    if cat_filter != "All Categories":
        filtered_df = filtered_df[filtered_df['category_name'] == cat_filter]
    if wh_filter != "All Warehouses":
        filtered_df = filtered_df[filtered_df['warehouse_name'] == wh_filter]
    if status_filter.startswith("RED"):
        filtered_df = filtered_df[filtered_df['status_code'] == 'RED']
    elif status_filter.startswith("GREEN"):
        filtered_df = filtered_df[filtered_df['status_code'] == 'GREEN']

    # Search bar
    search_q = st.text_input("🔍 Search by SKU Code or Product Name:", "")
    if search_q:
        filtered_df = filtered_df[
            filtered_df['sku_code'].str.contains(search_q, case=False) | 
            filtered_df['product_name'].str.contains(search_q, case=False)
        ]

    st.write(f"Showing **{len(filtered_df)}** records:")

    display_cols = [
        'status_code', 'sku_code', 'product_name', 'category_name', 
        'warehouse_name', 'current_stock', 'safety_stock', 'reorder_point', 
        'rec_order_qty', 'unit_cost', 'supplier_name'
    ]
    renamed_df = filtered_df[display_cols].rename(columns={
        'status_code': 'Status',
        'sku_code': 'SKU',
        'product_name': 'Product Name',
        'category_name': 'Category',
        'warehouse_name': 'Warehouse',
        'current_stock': 'Current Stock',
        'safety_stock': 'Safety Stock (SS)',
        'reorder_point': 'Reorder Point (ROP)',
        'rec_order_qty': 'Suggested Order',
        'unit_cost': 'Cost Price (₹)',
        'supplier_name': 'Supplier'
    })

    st.dataframe(renamed_df, use_container_width=True, height=450)

# ==============================================================================
# TAB 3: AUTOMATED PURCHASE ORDERS (PROCUREMENT HUB)
# ==============================================================================
elif menu == "📑 Automated Purchase Orders":
    st.subheader("Autonomous Purchase Order (PO) Procurement Hub")
    st.write("When items hit critical ROP thresholds, the Phase 3 engine automatically compiles formatted Microsoft Excel order documents ready for vendor dispatch.")

    po_dir = os.path.join(DIR, "automation", "purchase_orders")

    col_po1, col_po2 = st.columns([1, 2])
    with col_po1:
        if st.button("⚡ Generate Fresh Purchase Orders", type="primary"):
            with st.spinner("Compiling critical items into supplier workbooks..."):
                generate_all_critical_purchase_orders()
                st.success("Generated all supplier POs successfully!")
                st.rerun()

    st.markdown("---")
    st.subheader("Generated Purchase Order Workbooks Ready for Download:")

    if os.path.exists(po_dir):
        files = [f for f in os.listdir(po_dir) if f.endswith(".xlsx")]
        if files:
            for idx, po_file in enumerate(files, start=1):
                po_path = os.path.join(po_dir, po_file)
                file_size_kb = os.path.getsize(po_path) / 1024

                card_col1, card_col2 = st.columns([3, 1])
                with card_col1:
                    st.markdown(f"**{idx}. 📄 `{po_file}`**")
                    st.caption(f"Formatted Excel Workbook ({file_size_kb:.1f} KB) with dynamic line item formulas and tax calculations.")
                with card_col2:
                    with open(po_path, "rb") as fp:
                        st.download_button(
                            label="⬇️ Download Excel PO",
                            data=fp,
                            file_name=po_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_btn_{idx}"
                        )
                st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)
        else:
            st.info("No PO files generated yet. Click the button above to generate them.")

# ==============================================================================
# TAB 4: LIVE POS CHECKOUT SIMULATOR
# ==============================================================================
elif menu == "🛒 Live POS Simulator":
    st.subheader("Live Point-of-Sale (POS) Simulation")
    st.write("Simulate a customer checkout transaction at the billing counter to watch warehouse stock decrement and observe how dynamic reordering triggers in real time.")

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        selected_prod = st.selectbox("Select Product being sold:", df['product_name'].unique())
        selected_wh = st.selectbox("Fulfilling Warehouse:", df['warehouse_name'].unique())
        qty_sold = st.number_input("Quantity Sold to Customer:", min_value=1, max_value=50, value=15)

        prod_row = df[(df['product_name'] == selected_prod) & (df['warehouse_name'] == selected_wh)].iloc[0]
        st.info(f"**Current Stock Level:** `{prod_row['current_stock']}` units | **ROP Threshold:** `{prod_row['reorder_point']}` units")

        if st.button("🛒 Complete Customer Sale", type="primary"):
            conn, engine_type = get_db_connection()
            cursor = conn.cursor()

            # Decrement stock in database
            new_stock = max(0, int(prod_row['current_stock']) - int(qty_sold))
            cursor.execute("""
                UPDATE Inventory 
                SET current_stock = ?, last_updated = CURRENT_TIMESTAMP
                WHERE product_id = ? AND warehouse_id = ?;
            """, (new_stock, int(prod_row['product_id']), int(prod_row['warehouse_id'])))

            # Log transaction in sales ledger
            today_str = pd.Timestamp.now().strftime("%Y-%m-%d")
            unit_price = float(prod_row['selling_price'])
            tot_rev = round(qty_sold * unit_price, 2)
            cursor.execute("""
                INSERT INTO Sales_Transactions (product_id, warehouse_id, transaction_date, quantity_sold, unit_sale_price, total_revenue, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, 'UPI');
            """, (int(prod_row['product_id']), int(prod_row['warehouse_id']), today_str, int(qty_sold), unit_price, tot_rev))

            conn.commit()
            conn.close()

            # Trigger fresh engine calculation
            run_forecasting_engine()
            st.cache_data.clear()

            st.success(f"Transaction Logged! Sold {qty_sold} units of '{selected_prod}'. Remaining Stock: {new_stock} units.")
            if new_stock <= int(prod_row['reorder_point']):
                st.error("🚨 ALERT: Stock has breached the Reorder Point! Product is now in CRITICAL RED status!")
            st.rerun()

    with sim_col2:
        st.markdown("**How this impresses examiners during your Viva:**")
        st.markdown("""
        1. **Live ACID Transactions:** When you click *"Complete Customer Sale"*, it issues an atomic SQL `UPDATE` and `INSERT` to the database.
        2. **Instant Pipeline Reactivity:** The Python forecasting brain immediately re-evaluates rolling averages.
        3. **Dynamic Threshold Evaluation:** If the sale causes stock to dip below ROP, the UI instantly flips the item from **GREEN** to **CRITICAL RED**!
        """)

"""
==============================================================================
SMART INVENTORY & DEMAND FORECASTING SYSTEM
CORE MATHEMATICAL FORMULAS ENGINE (inventory_math.py)
Implements industrial supply chain algorithms: Safety Stock, ROP, and EOQ.
==============================================================================
"""

import math

def calculate_safety_stock(std_dev_demand: float, lead_time_days: int, service_factor: float = 1.65) -> int:
    """
    Computes Safety Stock buffer inventory:
        Safety Stock = Z * sigma_d * sqrt(L)

    Parameters:
        std_dev_demand (float): Standard deviation of daily sales (demand volatility).
        lead_time_days (int): Vendor delivery lead time in days.
        service_factor (float): Statistical Z-score (1.65 = 95% service availability).

    Returns:
        int: Recommended buffer safety stock units (rounded up).
    """
    if lead_time_days <= 0 or std_dev_demand < 0:
        return 0
    safety_stock = service_factor * std_dev_demand * math.sqrt(lead_time_days)
    return max(1, math.ceil(safety_stock))


def calculate_reorder_point(avg_daily_demand: float, lead_time_days: int, safety_stock: int) -> int:
    """
    Computes Dynamic Reorder Point (ROP):
        ROP = (Average Daily Demand * Lead Time) + Safety Stock

    Parameters:
        avg_daily_demand (float): Mean units sold per day over recent rolling window.
        lead_time_days (int): Vendor delivery lead time in days.
        safety_stock (int): Calculated buffer safety stock.

    Returns:
        int: Exact inventory threshold (in units) that triggers reordering.
    """
    lead_time_demand = avg_daily_demand * lead_time_days
    rop = lead_time_demand + safety_stock
    return math.ceil(rop)


def calculate_recommended_order_quantity(standard_batch_qty: int, rop: int, current_stock: int) -> int:
    """
    Computes the suggested purchase order quantity when stock drops below ROP:
        Order Qty = Standard Batch + (ROP - Current Stock)
    Ensures stock is replenished back above safe operating levels.
    """
    deficit = max(0, rop - current_stock)
    return standard_batch_qty + deficit


def classify_stock_health(current_stock: int, reorder_point: int) -> tuple:
    """
    Categorizes the inventory health into 3 actionable status tiers:
        - RED: Current Stock <= ROP (Immediate Restock Needed)
        - YELLOW: Current Stock <= ROP * 1.25 (Approaching Threshold)
        - GREEN: Current Stock > ROP * 1.25 (Healthy Stock)

    Returns:
        tuple: (status_code, status_label, urgency_level)
    """
    if current_stock <= reorder_point:
        return ("RED", "CRITICAL STOCK-OUT RISK", "HIGH")
    elif current_stock <= math.ceil(reorder_point * 1.25):
        return ("YELLOW", "WARNING: APPROACHING ROP", "MEDIUM")
    else:
        return ("GREEN", "HEALTHY INVENTORY", "LOW")

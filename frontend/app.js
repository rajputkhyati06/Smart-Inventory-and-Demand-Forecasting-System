/**
 * ==============================================================================
 * SMARTSTOCK AI — MERCHANT DECISION PORTAL JAVASCRIPT ENGINE (app.js)
 * Real-time reactive calculations, state management, and catalog rendering.
 * ==============================================================================
 */

// Core Application State
let catalogData = [];
let activeFilter = 'all';

// Sample Realistic Products Dataset (Pre-populated for instant Viva Demonstration)
const initialDemoProducts = [
    { id: 1, sku: 'SKU-MOB-001', name: '65W GaN Fast Charger', category: 'Mobile Accessories', stock: 12, dailySales: 10, leadTime: 5, unitCost: 650, price: 1199, supplier: 'TechLogix Components Pvt Ltd' },
    { id: 2, sku: 'SKU-MOB-002', name: 'Braided USB-C Cable (2m)', category: 'Mobile Accessories', stock: 10, dailySales: 14, leadTime: 4, unitCost: 140, price: 349, supplier: 'TechLogix Components Pvt Ltd' },
    { id: 3, sku: 'SKU-CMP-002', name: 'RGB Mechanical Keyboard', category: 'Computer Peripherals', stock: 8, dailySales: 6, leadTime: 7, unitCost: 1250, price: 2499, supplier: 'Apex Electronics & Hardware' },
    { id: 4, sku: 'SKU-AUD-001', name: 'TWS Earbuds with ANC', category: 'Audio Devices', stock: 14, dailySales: 9, leadTime: 10, unitCost: 1100, price: 2299, supplier: 'Nexa Audio & Wearables Ltd' },
    { id: 5, sku: 'SKU-WER-002', name: 'AMOLED Calling Smartwatch', category: 'Wearables & Fitness', stock: 6, dailySales: 5, leadTime: 12, unitCost: 1600, price: 3299, supplier: 'Zenith Smart Devices LLP' },
    { id: 6, sku: 'SKU-SMT-001', name: 'Smart WiFi LED Bulb 9W', category: 'Smart Home', stock: 240, dailySales: 12, leadTime: 6, unitCost: 240, price: 599, supplier: 'Zenith Smart Devices LLP' },
    { id: 7, sku: 'SKU-CMP-001', name: 'Wireless Ergonomic Mouse', category: 'Computer Peripherals', stock: 185, dailySales: 8, leadTime: 7, unitCost: 420, price: 899, supplier: 'Apex Electronics & Hardware' },
    { id: 8, sku: 'SKU-MOB-003', name: '20000mAh Power Bank', category: 'Mobile Accessories', stock: 220, dailySales: 11, leadTime: 5, unitCost: 950, price: 1699, supplier: 'Metro Digital Supply Corp' }
];

// DOM Elements
const dailySalesSlider = document.getElementById('dailySales');
const dailySalesVal = document.getElementById('dailySalesVal');
const currentStockInput = document.getElementById('currentStock');
const leadTimeInput = document.getElementById('leadTime');
const unitCostInput = document.getElementById('unitCost');
const sellingPriceInput = document.getElementById('sellingPrice');
const prodNameInput = document.getElementById('prodName');
const supplierInput = document.getElementById('supplierName');

// Decision Elements
const decisionBanner = document.getElementById('decisionBanner');
const bannerIcon = document.getElementById('bannerIcon');
const bannerTitle = document.getElementById('bannerTitle');
const bannerDesc = document.getElementById('bannerDesc');
const resSafetyStock = document.getElementById('resSafetyStock');
const resROP = document.getElementById('resROP');
const resDeficit = document.getElementById('resDeficit');
const resDaysLeft = document.getElementById('resDaysLeft');
const recommendationText = document.getElementById('recommendationText');
const recTotalCost = document.getElementById('recTotalCost');
const recTotalRev = document.getElementById('recTotalRev');

// KPI Elements
const kpiRedCount = document.getElementById('kpiRedCount');
const kpiGreenCount = document.getElementById('kpiGreenCount');
const kpiTotalCount = document.getElementById('kpiTotalCount');
const kpiStockValue = document.getElementById('kpiStockValue');

// Initialize on DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
    catalogData = [...initialDemoProducts];
    
    // Setup event listeners
    dailySalesSlider.addEventListener('input', handleSliderChange);
    currentStockInput.addEventListener('input', computeLiveDecision);
    leadTimeInput.addEventListener('input', computeLiveDecision);
    unitCostInput.addEventListener('input', computeLiveDecision);
    sellingPriceInput.addEventListener('input', computeLiveDecision);
    
    document.getElementById('calcBtn').addEventListener('click', computeLiveDecision);
    document.getElementById('stockForm').addEventListener('submit', handleAddItem);
    document.getElementById('loadDemoBtn').addEventListener('click', loadSampleData);
    document.getElementById('exportPoBtn').addEventListener('click', downloadCurrentPO);

    // Filter Chips
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            e.target.classList.add('active');
            activeFilter = e.target.getAttribute('data-filter');
            renderCatalogTable();
        });
    });

    // Initial Compute & Render
    computeLiveDecision();
    updateKPIs();
    renderCatalogTable();
});

// Slider Handler
function handleSliderChange(e) {
    dailySalesVal.textContent = `${e.target.value} units/day`;
    computeLiveDecision();
}

/**
 * CORE INVENTORY ALGORITHM
 * Math:
 * 1. Std Dev of daily demand (approx 30% volatility in retail): sigma_d = d * 0.35
 * 2. Safety Stock: SS = ceil(1.65 * sigma_d * sqrt(L))
 * 3. Reorder Point: ROP = ceil((d * L) + SS)
 */
function calculateMetrics(currentStock, dailySales, leadTime, unitCost, sellingPrice) {
    const stdDev = dailySales * 0.35; // Retail volatility factor
    const zScore = 1.65; // 95% cycle service level
    
    const safetyStock = Math.ceil(zScore * stdDev * Math.sqrt(leadTime));
    const leadTimeDemand = dailySales * leadTime;
    const rop = Math.ceil(leadTimeDemand + safetyStock);
    
    const deficit = currentStock - rop;
    const isCritical = currentStock <= rop;
    const daysLeft = dailySales > 0 ? (currentStock / dailySales).toFixed(1) : 0;
    
    // Suggested Order Qty
    const standardBatch = Math.max(50, dailySales * 7);
    const suggestedOrder = isCritical ? (standardBatch + Math.abs(deficit)) : 0;
    const estCost = suggestedOrder * unitCost;
    const estRev = suggestedOrder * sellingPrice;

    return {
        safetyStock,
        rop,
        deficit,
        isCritical,
        daysLeft,
        suggestedOrder,
        estCost,
        estRev,
        statusCode: isCritical ? 'RED' : 'GREEN'
    };
}

// Compute Decision from Current Form Values
function computeLiveDecision() {
    const currentStock = parseInt(currentStockInput.value) || 0;
    const dailySales = parseInt(dailySalesSlider.value) || 1;
    const leadTime = parseInt(leadTimeInput.value) || 1;
    const unitCost = parseFloat(unitCostInput.value) || 0;
    const sellingPrice = parseFloat(sellingPriceInput.value) || 0;
    const prodName = prodNameInput.value || 'Item';
    const supplier = supplierInput.value || 'Assigned Supplier';

    const metrics = calculateMetrics(currentStock, dailySales, leadTime, unitCost, sellingPrice);

    // Update Numerical Output Tiles
    resSafetyStock.textContent = `${metrics.safetyStock} Units`;
    resROP.textContent = `${metrics.rop} Units`;
    resDaysLeft.textContent = `${metrics.daysLeft} Days`;

    if (metrics.deficit <= 0) {
        resDeficit.textContent = `${metrics.deficit} Units`;
        resDeficit.className = 'm-val text-red';
    } else {
        resDeficit.textContent = `+${metrics.deficit} Units (Safe)`;
        resDeficit.className = 'm-val text-green';
    }

    // Update Decision Banner & Recommendations
    if (metrics.isCritical) {
        decisionBanner.className = 'decision-banner banner-red';
        bannerIcon.textContent = '🚨';
        bannerTitle.textContent = 'CRITICAL RED ALERT: RESTOCK IMMEDIATELY!';
        bannerDesc.innerHTML = `Stock will run out in <strong>${metrics.daysLeft} days</strong>, which is shorter than the <strong>${leadTime}-day</strong> supplier delivery window!`;
        
        recommendationText.innerHTML = `Place a replenishment purchase order for <strong>${metrics.suggestedOrder} units</strong> of <em>${prodName}</em> with <strong>${supplier}</strong> today to avoid lost customer sales.`;
    } else {
        decisionBanner.className = 'decision-banner banner-green';
        bannerIcon.textContent = '✅';
        bannerTitle.textContent = 'STATUS GREEN: INVENTORY LEVEL HEALTHY';
        bannerDesc.innerHTML = `You have <strong>${metrics.daysLeft} days</strong> of inventory available. Stock is safely above the ${metrics.rop}-unit threshold.`;
        
        recommendationText.innerHTML = `No immediate purchase order required for <em>${prodName}</em>. Normal stock monitoring can continue.`;
    }

    recTotalCost.textContent = `₹${metrics.estCost.toLocaleString('en-IN')}.00`;
    recTotalRev.textContent = `₹${metrics.estRev.toLocaleString('en-IN')}.00`;
}

// Add Item from Form to Catalog
function handleAddItem(e) {
    e.preventDefault();
    const newItem = {
        id: Date.now(),
        sku: document.getElementById('skuCode').value,
        name: prodNameInput.value,
        category: document.getElementById('category').value,
        stock: parseInt(currentStockInput.value),
        dailySales: parseInt(dailySalesSlider.value),
        leadTime: parseInt(leadTimeInput.value),
        unitCost: parseFloat(unitCostInput.value),
        price: parseFloat(sellingPriceInput.value),
        supplier: supplierInput.value
    };

    catalogData.unshift(newItem);
    updateKPIs();
    renderCatalogTable();
    alert(`Success! '${newItem.name}' added to active inventory catalog.`);
}

// Update Top KPI Cards
function updateKPIs() {
    let red = 0;
    let green = 0;
    let totalStockVal = 0;

    catalogData.forEach(item => {
        const m = calculateMetrics(item.stock, item.dailySales, item.leadTime, item.unitCost, item.price);
        if (m.isCritical) red++;
        else green++;
        totalStockVal += (item.stock * item.unitCost);
    });

    kpiRedCount.textContent = red;
    kpiGreenCount.textContent = green;
    kpiTotalCount.textContent = catalogData.length;
    kpiStockValue.textContent = `₹${totalStockVal.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
}

// Render Table with Filter
function renderCatalogTable() {
    const tbody = document.getElementById('catalogTableBody');
    tbody.innerHTML = '';

    const filtered = catalogData.filter(item => {
        const m = calculateMetrics(item.stock, item.dailySales, item.leadTime, item.unitCost, item.price);
        if (activeFilter === 'all') return true;
        return m.statusCode === activeFilter;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding: 20px; color:#888;">No items match the active filter.</td></tr>`;
        return;
    }

    filtered.forEach(item => {
        const m = calculateMetrics(item.stock, item.dailySales, item.leadTime, item.unitCost, item.price);
        const tr = document.createElement('tr');
        
        tr.innerHTML = `
            <td><span class="status-pill ${m.statusCode.toLowerCase()}">${m.statusCode === 'RED' ? '🔴 RED ALERT' : '🟢 HEALTHY'}</span></td>
            <td><strong>${item.sku}</strong></td>
            <td>${item.name}</td>
            <td>${item.category}</td>
            <td>${item.stock} units</td>
            <td><strong>${m.rop}</strong></td>
            <td>${m.suggestedOrder > 0 ? `<strong>${m.suggestedOrder}</strong> units` : '-'}</td>
            <td>₹${item.unitCost.toLocaleString('en-IN')}</td>
            <td>${item.supplier}</td>
            <td>
                <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 0.75rem;" onclick="loadItemIntoForm('${item.sku}')">Inspect</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Load a clicked SKU back into the form
window.loadItemIntoForm = function(sku) {
    const found = catalogData.find(i => i.sku === sku);
    if (!found) return;

    prodNameInput.value = found.name;
    document.getElementById('skuCode').value = found.sku;
    document.getElementById('category').value = found.category;
    currentStockInput.value = found.stock;
    dailySalesSlider.value = found.dailySales;
    dailySalesVal.textContent = `${found.dailySales} units/day`;
    leadTimeInput.value = found.leadTime;
    unitCostInput.value = found.unitCost;
    sellingPriceInput.value = found.price;
    supplierInput.value = found.supplier;

    window.scrollTo({ top: 300, behavior: 'smooth' });
    computeLiveDecision();
};

// Load Sample 25 SKUs
function loadSampleData() {
    catalogData = [
        ...initialDemoProducts,
        { id: 9, sku: 'SKU-CMP-003', name: '1080p FHD Pro Webcam', category: 'Computer Peripherals', stock: 11, dailySales: 7, leadTime: 4, unitCost: 780, price: 1499, supplier: 'Alpha Peripheral Traders' },
        { id: 10, sku: 'SKU-MOB-004', name: 'MagSafe Car Mount Holder', category: 'Mobile Accessories', stock: 15, dailySales: 8, leadTime: 3, unitCost: 280, price: 699, supplier: 'Alpha Peripheral Traders' },
        { id: 11, sku: 'SKU-AUD-002', name: 'Over-Ear Wireless Headphones', category: 'Audio Devices', stock: 12, dailySales: 5, leadTime: 8, unitCost: 1450, price: 2999, supplier: 'Nexa Audio & Wearables Ltd' },
        { id: 12, sku: 'SKU-SMT-002', name: '16A Smart Wi-Fi Plug', category: 'Smart Home', stock: 140, dailySales: 9, leadTime: 12, unitCost: 380, price: 899, supplier: 'Zenith Smart Devices LLP' }
    ];
    updateKPIs();
    renderCatalogTable();
    alert('Loaded full retail sample catalog with live ROP statuses!');
}

// Download instant Purchase Order (CSV / Excel format)
function downloadCurrentPO() {
    const currentStock = parseInt(currentStockInput.value) || 0;
    const dailySales = parseInt(dailySalesSlider.value) || 1;
    const leadTime = parseInt(leadTimeInput.value) || 1;
    const unitCost = parseFloat(unitCostInput.value) || 0;
    const sellingPrice = parseFloat(sellingPriceInput.value) || 0;
    const prodName = prodNameInput.value;
    const sku = document.getElementById('skuCode').value;
    const supplier = supplierInput.value;

    const m = calculateMetrics(currentStock, dailySales, leadTime, unitCost, sellingPrice);

    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "SMART INVENTORY RESTOCK PURCHASE ORDER\n";
    csvContent += `Supplier Name,${supplier}\n`;
    csvContent += `Order Date,${new Date().toLocaleDateString()}\n`;
    csvContent += `Lead Time,${leadTime} Days\n\n`;
    csvContent += "Item,SKU,Current Stock,ROP,Recommended Order Qty,Unit Cost (INR),Total Cost (INR)\n";
    csvContent += `"${prodName}","${sku}",${currentStock},${m.rop},${m.suggestedOrder},${unitCost},${m.estCost}\n`;

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Purchase_Order_${sku}_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

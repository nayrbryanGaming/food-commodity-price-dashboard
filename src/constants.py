"""
constants.py - Application-wide constants, labels, and configuration.

This module defines all static configuration values used throughout the dashboard.
Centralizing these makes maintenance and localization easier.
"""

# =============================================================================
# DATA PATHS AND CONFIGURATION
# =============================================================================

# Default data directory (relative to project root)
DEFAULT_DATA_DIR = "data/raw"

# Expected folder name for commodity prices
COMMODITY_FOLDER = "Harga Bahan Pangan/train"

# Optional data folders
GOOGLE_TREND_FOLDER = "Google Trend"
CURRENCY_FOLDER = "Mata Uang"

# =============================================================================
# CANONICAL SCHEMA COLUMN NAMES
# =============================================================================

COL_DATE = "date"
COL_COMMODITY = "commodity"
COL_REGION = "region"
COL_PRICE = "price"

CANONICAL_COLUMNS = [COL_DATE, COL_COMMODITY, COL_REGION, COL_PRICE]

# Default region when no regional data is available
DEFAULT_REGION = "National"

# =============================================================================
# UI LABELS (Indonesian with English fallback)
# =============================================================================

LABELS = {
    # Page titles
    "app_title": "Dashboard Harga Pangan",
    "app_subtitle": "Analisis Harga Pangan Nasional",
    
    # Page names
    "page_overview": "Ringkasan",
    "page_trends": "Tren",
    "page_regions": "Wilayah",
    "page_commodities": "Komoditas",
    "page_data": "Data & Metadata",
    
    # Sidebar
    "sidebar_filters": "Filter",
    "commodity_select": "Pilih Komoditas",
    "region_select": "Pilih Wilayah (maks. 5)",
    "date_range": "Rentang Tanggal",
    "display_mode": "Mode Tampilan",
    "easy_mode": "Mode Standar",
    "analyst_mode": "Mode Analis",
    
    # KPI Cards
    "latest_price": "Harga Terkini",
    "change_7d": "Perubahan 7 Hari",
    "change_30d": "Perubahan 30 Hari",
    "trend_status": "Status Tren",
    
    # Trend status values
    "trend_rising": "Naik",
    "trend_falling": "Turun",
    "trend_stable": "Stabil",
    
    # Charts
    "price_trend": "Tren Harga",
    "ma7": "Rata-rata 7 Hari",
    "ma14": "Rata-rata 14 Hari",
    "top_movers_up": "Kenaikan Tertinggi (7 Hari)",
    "top_movers_down": "Penurunan Tertinggi (7 Hari)",
    
    # Regions page
    "highest_prices": "Harga Tertinggi",
    "lowest_prices": "Harga Terendah",
    "price_comparison": "Perbandingan Harga",
    "price_vs_volatility": "Harga vs Volatilitas",
    
    # Commodities page
    "commodity_comparison": "Perbandingan Komoditas",
    "price_heatmap": "Peta Panas Perubahan Harga",
    "summary_table": "Ringkasan",
    
    # Data page
    "data_table": "Tabel Data",
    "data_quality": "Kualitas Data",
    "download_data": "Unduh Data",
    "download_summary": "Unduh Ringkasan",
    "metadata": "Metadata",
    
    # Messages
    "no_data": "Tidak ada data untuk filter yang dipilih.",
    "no_region_data": "Data wilayah tidak tersedia untuk komoditas ini.",
    "loading": "Memuat data...",
    "last_updated": "Terakhir diperbarui",
    "data_coverage": "Cakupan data",
    
    # Units
    "price_unit": "Harga (Rp)",
    "percentage": "Persentase (%)",
}

# =============================================================================
# ANALYSIS THRESHOLDS
# =============================================================================

# Anomaly detection: daily % change threshold
ANOMALY_THRESHOLD_PCT = 10.0  # Mark as anomaly if > 10% daily change

# Trend determination threshold (7-day % change)
TREND_RISING_THRESHOLD = 2.0    # > 2% = rising
TREND_FALLING_THRESHOLD = -2.0  # < -2% = falling

# Standard deviation multiplier for anomaly detection (alternative method)
ANOMALY_STD_MULTIPLIER = 2.0

# =============================================================================
# UI CONSTRAINTS
# =============================================================================

# Maximum number of regions for multi-select (to avoid chart clutter)
MAX_REGIONS_SELECT = 5

# Maximum number of commodities for comparison
MAX_COMMODITIES_COMPARE = 9

# Default date range (days back from latest date)
DEFAULT_DATE_RANGE_DAYS = 90

# Top movers count
TOP_MOVERS_COUNT = 5

# Regional ranking count
REGIONAL_RANKING_COUNT = 10

# =============================================================================
# CHART STYLING
# =============================================================================

# Plotly color palette (accessible, high contrast)
CHART_COLORS = [
    "#1f77b4",  # Blue
    "#ff7f0e",  # Orange
    "#2ca02c",  # Green
    "#d62728",  # Red
    "#9467bd",  # Purple
    "#8c564b",  # Brown
    "#e377c2",  # Pink
    "#7f7f7f",  # Gray
    "#bcbd22",  # Yellow-green
]

# Chart layout defaults
CHART_LAYOUT = {
    "font_family": "Inter, Arial, sans-serif",
    "title_font_size": 16,
    "axis_font_size": 12,
    "legend_font_size": 11,
    "margin": {"l": 60, "r": 30, "t": 50, "b": 50},
    "height": 400,
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
}

# KPI card colors
KPI_POSITIVE_COLOR = "#28a745"  # Green for positive changes
KPI_NEGATIVE_COLOR = "#dc3545"  # Red for negative changes
KPI_NEUTRAL_COLOR = "#6c757d"   # Gray for neutral/stable

# =============================================================================
# DATE PARSING FORMATS
# =============================================================================

DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%d %B %Y",
    "%B %d, %Y",
]

# =============================================================================
# FILE PATTERNS
# =============================================================================

# File extension for data files
DATA_FILE_EXTENSION = ".csv"

# Columns that typically contain dates (case-insensitive matching)
DATE_COLUMN_PATTERNS = ["date", "tanggal", "periode", "waktu", "time"]

# Columns that should not be treated as regions (case-insensitive)
NON_REGION_COLUMNS = ["date", "tanggal", "periode", "waktu", "time", "commodity", "komoditas", "price", "harga"]

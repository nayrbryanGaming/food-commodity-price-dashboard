"""
Panel Harga Pangan - Dashboard Harga Komoditas Pangan
Titik Masuk Utama (Home.py)

Dashboard profesional dan mudah digunakan untuk harga komoditas pangan nasional.
Dibangun dengan Streamlit dan Plotly untuk eksplorasi data interaktif.

Penulis: Tim Data Engineering
Versi: 1.0.0
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.io import find_data_directory, load_all_commodities, get_data_info
from src.preprocess import process_all_commodities, validate_data, get_data_quality_stats
from src.constants import (
    LABELS,
    COL_DATE,
    COL_COMMODITY,
    COL_REGION,
    DEFAULT_DATE_RANGE_DAYS,
    MAX_REGIONS_SELECT,
)

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=LABELS["app_title"],
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CUSTOM CSS FOR PROFESSIONAL STYLING WITH DARK/LIGHT MODE
# =============================================================================

# Detect if user prefers dark mode (from browser or manual toggle)
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = 'light'

# Function to get theme-specific CSS - RESPONSIVE VERSION
def get_theme_css(is_dark: bool):
    # Common styles for both themes
    common_css = """
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        
        /* Hide Streamlit default elements */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        
        /* Toggle styling - make it more visible */
        .stToggle > label > div[data-testid="stMarkdownContainer"] > p {
            font-weight: 600 !important;
        }
        
        /* Analyst mode indicator */
        .analyst-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .analyst-badge-active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
        }
        
        .analyst-badge-inactive {
            background: #e0e0e0;
            color: #666;
        }
        
        /* Theme toggle button styling */
        .theme-toggle-container {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .theme-btn {
            flex: 1;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            border: 2px solid transparent;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s ease;
            text-align: center;
        }
    """
    
    if is_dark:
        theme_css = """
            /* ============ DARK MODE ============ */
            .stApp {
                background-color: #0E1117 !important;
            }
            
            /* All text - high contrast for dark mode */
            .stApp, .stApp p, .stApp span, .stApp label, .stApp div,
            .stMarkdown, .stMarkdown p, .stText {
                color: #FAFAFA !important;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #FFFFFF !important;
            }
            
            .main-header {
                font-size: 2.2rem;
                font-weight: 700;
                color: #4DA6FF !important;
                margin-bottom: 0.5rem;
                letter-spacing: -0.5px;
            }
            
            .sub-header {
                font-size: 1rem;
                color: #B0B0B0 !important;
                margin-bottom: 2rem;
                font-weight: 400;
            }
            
            /* Sidebar - Dark */
            section[data-testid="stSidebar"] {
                background-color: #1A1A2E !important;
                border-right: 1px solid #333 !important;
            }
            
            section[data-testid="stSidebar"] * {
                color: #FAFAFA !important;
            }
            
            section[data-testid="stSidebar"] .stSelectbox label,
            section[data-testid="stSidebar"] .stMultiSelect label {
                color: #B0B0B0 !important;
            }
            
            .sidebar-header {
                font-size: 0.85rem;
                font-weight: 600;
                color: #4DA6FF !important;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 1.5rem;
                margin-bottom: 0.8rem;
            }
            
            /* Cards - Dark */
            .nav-card {
                text-align: center;
                padding: 1.2rem;
                border-radius: 10px;
                border: 1px solid #333 !important;
                background: #1E1E2E !important;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .nav-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            
            .nav-card h3 {
                color: #FFFFFF !important;
                font-size: 1.1rem;
                margin-bottom: 0.3rem;
            }
            
            .nav-card p {
                color: #A0A0A0 !important;
                font-size: 0.85rem;
            }
            
            /* Info boxes - Dark */
            .info-box {
                background-color: rgba(33, 150, 243, 0.15) !important;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #2196f3;
                margin: 1rem 0;
            }
            
            .info-box, .info-box * {
                color: #E3F2FD !important;
            }
            
            .success-box {
                background-color: rgba(76, 175, 80, 0.15) !important;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #4caf50;
                margin: 1rem 0;
            }
            
            .success-box, .success-box * {
                color: #E8F5E9 !important;
            }
            
            .warning-box {
                background-color: rgba(255, 152, 0, 0.15) !important;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #ff9800;
                margin: 1rem 0;
            }
            
            .warning-box, .warning-box * {
                color: #FFF3E0 !important;
            }
            
            /* Metric cards - Dark */
            div[data-testid="metric-container"] {
                background-color: #1E1E2E !important;
                padding: 1.2rem;
                border-radius: 10px;
                border: 1px solid #333 !important;
            }
            
            div[data-testid="metric-container"] label {
                color: #B0B0B0 !important;
            }
            
            div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
                color: #FFFFFF !important;
            }
            
            /* Buttons - Dark */
            .stButton > button {
                background: linear-gradient(135deg, #4DA6FF 0%, #3D8BD9 100%) !important;
                color: #FFFFFF !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                border: none !important;
                transition: all 0.2s ease !important;
            }
            
            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(77, 166, 255, 0.4) !important;
            }
            
            /* Inputs - Dark */
            .stSelectbox > div > div,
            .stMultiSelect > div > div,
            .stTextInput > div > div > input,
            .stDateInput > div > div > input {
                background-color: #2D2D3D !important;
                color: #FAFAFA !important;
                border-color: #444 !important;
            }
            
            /* DataFrames - Dark */
            .stDataFrame, .stDataFrame * {
                background-color: #1E1E2E !important;
                color: #FAFAFA !important;
            }
            
            /* Expander - Dark */
            .streamlit-expanderHeader {
                background-color: #1E1E2E !important;
                color: #FAFAFA !important;
                border-radius: 8px;
            }
            
            /* Toggle - Dark mode specific styling */
            .stToggle > label > span[data-testid="stToggleSwitch"] {
                background-color: #333 !important;
            }
            
            .stToggle > label > span[data-testid="stToggleSwitch"][aria-checked="true"] {
                background-color: #4DA6FF !important;
            }
            
            /* Theme indicator */
            .theme-indicator {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #4DA6FF;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                text-align: center;
                font-weight: 600;
                border: 1px solid #333;
            }
            
            /* Analyst badge - Dark */
            .analyst-badge-inactive {
                background: #2D2D3D;
                color: #888;
            }
        """
    else:
        theme_css = """
            /* ============ LIGHT MODE ============ */
            .stApp {
                background-color: #FFFFFF !important;
            }
            
            /* All text - dark for light mode */
            .stApp, .stApp p, .stApp span, .stApp label, .stApp div,
            .stMarkdown, .stMarkdown p, .stText {
                color: #1A1A1A !important;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #1E3A5F !important;
            }
            
            .main-header {
                font-size: 2.2rem;
                font-weight: 700;
                color: #1E3A5F !important;
                margin-bottom: 0.5rem;
                letter-spacing: -0.5px;
            }
            
            .sub-header {
                font-size: 1rem;
                color: #5A5A5A !important;
                margin-bottom: 2rem;
                font-weight: 400;
            }
            
            /* Sidebar - Light */
            section[data-testid="stSidebar"] {
                background-color: #F8F9FA !important;
                border-right: 1px solid #E0E0E0 !important;
            }
            
            section[data-testid="stSidebar"] * {
                color: #1A1A1A !important;
            }
            
            section[data-testid="stSidebar"] .stSelectbox label,
            section[data-testid="stSidebar"] .stMultiSelect label {
                color: #5A5A5A !important;
            }
            
            .sidebar-header {
                font-size: 0.85rem;
                font-weight: 600;
                color: #1E3A5F !important;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 1.5rem;
                margin-bottom: 0.8rem;
            }
            
            /* Cards - Light */
            .nav-card {
                text-align: center;
                padding: 1.2rem;
                border-radius: 10px;
                border: 1px solid #E0E0E0 !important;
                background: #FFFFFF !important;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .nav-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            .nav-card h3 {
                color: #1E3A5F !important;
                font-size: 1.1rem;
                margin-bottom: 0.3rem;
            }
            
            .nav-card p {
                color: #666666 !important;
                font-size: 0.85rem;
            }
            
            /* Info boxes - Light */
            .info-box {
                background-color: #E3F2FD !important;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #2196f3;
                margin: 1rem 0;
            }
            
            .info-box, .info-box * {
                color: #0D47A1 !important;
            }
            
            .success-box {
                background-color: #E8F5E9 !important;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #4caf50;
                margin: 1rem 0;
            }
            
            .success-box, .success-box * {
                color: #1B5E20 !important;
            }
            
            .warning-box {
                background-color: #FFF3E0 !important;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #ff9800;
                margin: 1rem 0;
            }
            
            .warning-box, .warning-box * {
                color: #E65100 !important;
            }
            
            /* Metric cards - Light */
            div[data-testid="metric-container"] {
                background-color: #FFFFFF !important;
                padding: 1.2rem;
                border-radius: 10px;
                border: 1px solid #E0E0E0 !important;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            }
            
            div[data-testid="metric-container"] label {
                color: #5A5A5A !important;
            }
            
            div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
                color: #1A1A1A !important;
            }
            
            /* Buttons - Light */
            .stButton > button {
                background: linear-gradient(135deg, #1E3A5F 0%, #2D5A8C 100%) !important;
                color: #FFFFFF !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                border: none !important;
                transition: all 0.2s ease !important;
            }
            
            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3) !important;
            }
            
            /* Inputs - Light */
            .stSelectbox > div > div,
            .stMultiSelect > div > div,
            .stTextInput > div > div > input,
            .stDateInput > div > div > input {
                background-color: #FFFFFF !important;
                color: #1A1A1A !important;
                border-color: #E0E0E0 !important;
            }
            
            /* Toggle - Light mode specific styling */
            .stToggle > label > span[data-testid="stToggleSwitch"] {
                background-color: #E0E0E0 !important;
            }
            
            .stToggle > label > span[data-testid="stToggleSwitch"][aria-checked="true"] {
                background-color: #1E3A5F !important;
            }
            
            /* Theme indicator */
            .theme-indicator {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                color: #1E3A5F;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                text-align: center;
                font-weight: 600;
                border: 1px solid #E0E0E0;
            }
        """
    
    return f"<style>{common_css}{theme_css}</style>"


# Apply theme CSS based on current mode
is_dark_mode = st.session_state.theme_mode == 'dark'
st.markdown(get_theme_css(is_dark_mode), unsafe_allow_html=True)


# =============================================================================
# DATA LOADING WITH CACHING
# =============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def load_and_process_data(data_path: str):
    """
    Load and process all commodity data with caching.
    
    Args:
        data_path: Path to the data directory.
        
    Returns:
        Tuple of (processed_df, data_info, quality_stats)
    """
    # Find data directory
    data_dir = find_data_directory(data_path)
    
    if data_dir is None:
        return None, {"error": "Data directory not found"}, {}
    
    # Load raw data
    raw_data = load_all_commodities(data_dir)
    
    if not raw_data:
        return None, {"error": "No data files found"}, {}
    
    # Process to canonical format
    df = process_all_commodities(raw_data)
    
    # Validate
    is_valid, issues = validate_data(df)
    
    # Get quality stats
    quality_stats = get_data_quality_stats(df)
    
    # Get data info
    data_info = get_data_info(data_dir)
    data_info["is_valid"] = is_valid
    data_info["issues"] = issues
    
    return df, data_info, quality_stats


def get_default_data_path():
    """
    Get the default data path based on the project structure.
    
    Returns:
        Path string.
    """
    # Check common locations
    possible_paths = [
        Path(__file__).parent / "data" / "raw",
        Path(__file__).parent.parent / "data" / "raw",
        Path(__file__).parent.parent,  # If running from dashboard folder
        Path(__file__).parent.parent / "Harga Bahan Pangan" / "train",
    ]
    
    for p in possible_paths:
        if p.exists():
            return str(p)
    
    # Default to parent directory
    return str(Path(__file__).parent.parent)


# =============================================================================
# SIDEBAR - GLOBAL FILTERS
# =============================================================================

def render_sidebar(df: pd.DataFrame, quality_stats: dict):  # noqa: ARG001 - quality_stats reserved for future use
    """
    Render sidebar dengan filter global dan tema toggle.
    
    Args:
        df: DataFrame yang sudah diproses.
        quality_stats: Statistik kualitas data (reserved untuk penggunaan masa depan).
        
    Returns:
        Dictionary dari nilai filter yang dipilih.
    """
    # =========================================================================
    # TEMA TOGGLE - Toggle sederhana
    # =========================================================================
    st.sidebar.markdown("### Pengaturan Tampilan")
    
    # Dark mode toggle
    dark_mode = st.sidebar.toggle(
        "Mode Gelap",
        value=st.session_state.theme_mode == 'dark',
        help="Beralih antara tema terang dan gelap"
    )
    
    # Update session state if changed
    new_mode = 'dark' if dark_mode else 'light'
    if new_mode != st.session_state.theme_mode:
        st.session_state.theme_mode = new_mode
        st.rerun()
    
    is_dark = st.session_state.theme_mode == 'dark'
    
    st.sidebar.markdown("---")
    
    # =========================================================================
    # MODE ANALIS - Toggle visual dengan penjelasan
    # =========================================================================
    st.sidebar.markdown("### Mode Analisis")
    
    filters = {}
    
    # Initialize analyst_mode in session_state if not exists
    if 'analyst_mode' not in st.session_state:
        st.session_state.analyst_mode = False
    
    # Analyst mode toggle - use session_state to persist value
    filters['analyst_mode'] = st.sidebar.toggle(
        "Mode Analis",
        value=st.session_state.analyst_mode,
        key="analyst_mode_toggle",
        help="Aktifkan fitur analitik lanjutan"
    )
    
    # Update session_state
    st.session_state.analyst_mode = filters['analyst_mode']
    
    # Dynamic indicator based on analyst mode state
    if filters['analyst_mode']:
        st.sidebar.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;
                    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);">
            <div style="font-weight: 700; font-size: 0.9rem;">MODE ANALIS AKTIF</div>
            <div style="font-size: 0.75rem; margin-top: 0.25rem; opacity: 0.9;">
                Fitur lanjutan aktif:
                <ul style="margin: 0.25rem 0 0 1rem; padding: 0;">
                    <li>Rata-rata bergerak (MA7, MA14)</li>
                    <li>Deteksi anomali</li>
                    <li>Peta panas harga</li>
                    <li>Analisis volatilitas</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"""
        <div style="background: {'#2D2D3D' if is_dark else '#F5F5F5'};
                    color: {'#888' if is_dark else '#666'}; 
                    padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;
                    border: 1px solid {'#444' if is_dark else '#E0E0E0'};">
            <div style="font-weight: 600; font-size: 0.85rem;">MODE STANDAR</div>
            <div style="font-size: 0.75rem; margin-top: 0.25rem;">
                Tampilan dasar. Aktifkan Mode Analis untuk grafik lanjutan.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    
    st.sidebar.markdown("---")
    
    # =========================================================================
    # FILTER
    # =========================================================================
    st.sidebar.markdown("### Filter")
    
    # Commodity Selection
    commodities = sorted(df[COL_COMMODITY].unique().tolist())
    
    filters['commodity'] = st.sidebar.selectbox(
        LABELS["commodity_select"],
        options=commodities,
        index=0,
        help="Pilih komoditas untuk dianalisis"
    )
    
    # Region Selection
    regions = sorted(df[COL_REGION].unique().tolist())
    default_region = regions[0] if regions else None
    
    filters['regions'] = st.sidebar.multiselect(
        LABELS["region_select"],
        options=regions,
        default=[default_region] if default_region else [],
        max_selections=MAX_REGIONS_SELECT,
        help=f"Pilih hingga {MAX_REGIONS_SELECT} wilayah untuk perbandingan"
    )
    
    # Ensure at least one region is selected
    if not filters['regions'] and regions:
        filters['regions'] = [regions[0]]
    
    # Date Range Selection
    st.sidebar.markdown("---")
    
    min_date = df[COL_DATE].min().date()
    max_date = df[COL_DATE].max().date()
    
    # Default to last 90 days
    from datetime import timedelta
    default_start = max(min_date, max_date - timedelta(days=DEFAULT_DATE_RANGE_DAYS))
    
    date_range = st.sidebar.date_input(
        LABELS["date_range"],
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Pilih rentang tanggal untuk analisis"
    )
    
    # Handle single date selection
    if isinstance(date_range, tuple) and len(date_range) == 2:
        filters['date_start'] = date_range[0]
        filters['date_end'] = date_range[1]
    else:
        filters['date_start'] = min_date
        filters['date_end'] = max_date
    
    # =========================================================================
    # RINGKASAN DATA
    # =========================================================================
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Ringkasan Data")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.sidebar.metric("Komoditas", len(commodities))
    with col2:
        st.sidebar.metric("Wilayah", len(regions))
    
    st.sidebar.caption(f"📅 Data: {min_date} to {max_date}")
    
    return filters


# =============================================================================
# MAIN PAGE CONTENT
# =============================================================================

def main():
    """Titik masuk utama aplikasi."""
    
    # Header
    st.markdown(f'<h1 class="main-header">{LABELS["app_title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{LABELS["app_subtitle"]}</p>', unsafe_allow_html=True)
    
    # Data Path Configuration (in expander for clean UI)
    with st.expander("Konfigurasi Data", expanded=False):
        data_path = st.text_input(
            "Lokasi Data",
            value=get_default_data_path(),
            help="Masukkan lokasi folder data (berisi 'Harga Bahan Pangan/train')"
        )
    
    # Load Data
    with st.spinner(LABELS["loading"]):
        df, data_info, quality_stats = load_and_process_data(data_path)
    
    # Check if data loaded successfully
    if df is None or df.empty:
        st.error("Data tidak ditemukan!")
        st.markdown("""
        <div class="warning-box">
        <h4>Cara mengatasi:</h4>
        <ol>
            <li>Pastikan lokasi data sudah benar</li>
            <li>Struktur folder yang diharapkan: <code>Harga Bahan Pangan/train/*.csv</code></li>
            <li>Verifikasi file CSV berisi data harga komoditas</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"Lokasi yang dicoba: `{data_path}`")
        st.stop()
    
    # Store data in session state for other pages
    st.session_state['df'] = df
    st.session_state['data_info'] = data_info
    st.session_state['quality_stats'] = quality_stats
    
    # Render Sidebar Filters
    filters = render_sidebar(df, quality_stats)
    st.session_state['filters'] = filters
    
    # Main Content - Welcome/Overview
    st.markdown("---")
    
    # Success message
    st.markdown(f"""
    <div class="success-box">
        <h4>Data berhasil dimuat</h4>
        <p>
            <strong>{len(quality_stats.get('commodities', []))}</strong> komoditas • 
            <strong>{len(quality_stats.get('regions', []))}</strong> wilayah • 
            <strong>{quality_stats.get('total_rows', 0):,}</strong> titik data
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Navigation Cards
    st.markdown("### Navigasi Cepat")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Get background colors based on theme
    if st.session_state.theme_mode == 'dark':
        card_colors = ['#1E3D59', '#1E4D3D', '#4D3D1E', '#4D1E3D', '#3D1E4D']
        text_color = '#FFFFFF'
        subtext_color = '#B0B0B0'
    else:
        card_colors = ['#E3F2FD', '#E8F5E9', '#FFF3E0', '#FCE4EC', '#F3E5F5']
        text_color = '#1E3A5F'
        subtext_color = '#666666'
    
    with col1:
        st.markdown(f"""
        <div class="nav-card" style="background: {card_colors[0]};">
            <h3 style="color: {text_color};">RINGKASAN</h3>
            <p style="color: {subtext_color};">KPI & Insight Utama</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="nav-card" style="background: {card_colors[1]};">
            <h3 style="color: {text_color};">TREN</h3>
            <p style="color: {subtext_color};">Analisis deret waktu</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="nav-card" style="background: {card_colors[2]};">
            <h3 style="color: {text_color};">WILAYAH</h3>
            <p style="color: {subtext_color};">Perbandingan regional</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="nav-card" style="background: {card_colors[3]};">
            <h3 style="color: {text_color};">KOMODITAS</h3>
            <p style="color: {subtext_color};">Perbandingan harga</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="nav-card" style="background: {card_colors[4]};">
            <h3 style="color: {text_color};">DATA</h3>
            <p style="color: {subtext_color};">Tabel & metadata</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <p><strong>Tips:</strong> Gunakan menu sidebar untuk navigasi ke halaman berbeda. 
        Sesuaikan filter di sidebar untuk mengkustomisasi data yang ditampilkan.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data Coverage Summary
    st.markdown("### Cakupan Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        date_range = quality_stats.get('date_range', {})
        if date_range:
            st.metric(
                "Tanggal Mulai",
                date_range.get('min', '-'),
            )
    
    with col2:
        if date_range:
            st.metric(
                "Tanggal Akhir",
                date_range.get('max', '-'),
            )
    
    # Commodity List
    st.markdown("### Komoditas Tersedia")
    
    commodities = quality_stats.get('commodities', [])
    if commodities:
        # Display in grid
        cols = st.columns(4)
        for i, commodity in enumerate(commodities):
            with cols[i % 4]:
                st.markdown(f"• {commodity}")
    
    # Footer
    st.markdown("---")
    footer_color = '#B0B0B0' if st.session_state.theme_mode == 'dark' else '#666666'
    st.markdown(f"""
    <div style="text-align: center; color: {footer_color}; font-size: 0.85rem;">
        <p>Dashboard Harga Komoditas Pangan v1.0 | Data bersumber dari file lokal</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

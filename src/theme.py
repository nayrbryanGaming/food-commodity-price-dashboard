"""
theme.py - Centralized theme management for all pages.

This module provides theme CSS that can be applied consistently across all pages.
"""

import streamlit as st
import pandas as pd


def init_theme():
    """Initialize theme in session state if not exists."""
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'light'


def is_dark_mode() -> bool:
    """Check if dark mode is active."""
    init_theme()
    return st.session_state.theme_mode == 'dark'


def render_styled_dataframe(df: pd.DataFrame, max_height: str = "400px"):
    """
    Render a dataframe as a styled HTML table with proper contrast.
    
    Args:
        df: The dataframe to display.
        max_height: Maximum height with scroll.
    """
    if df is None or df.empty:
        st.info("Tidak ada data untuk ditampilkan.")
        return
    
    is_dark = is_dark_mode()
    
    # Pastel colors based on theme
    if is_dark:
        header_bg = "#FFE4CC"
        header_border = "#FF9F5A"
        row_even = "#FFF5EB"
        row_odd = "#FFFCF8"
        container_bg = "#FFF8F0"
        border_color = "#E8D5C4"
        text_color = "#1A1A1A"
    else:
        header_bg = "#D6E9FF"
        header_border = "#4A90D9"
        row_even = "#EDF5FF"
        row_odd = "#FAFCFF"
        container_bg = "#F0F7FF"
        border_color = "#C5DCF5"
        text_color = "#1A1A1A"
    
    # Build HTML table manually for better control
    html_parts = []
    html_parts.append(f'<div style="background-color: {container_bg}; border-radius: 12px; border: 2px solid {border_color}; padding: 8px; max-height: {max_height}; overflow-y: auto; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">')
    html_parts.append(f'<table style="width: 100%; border-collapse: collapse; font-family: Inter, Arial, sans-serif; font-size: 14px;">')
    
    # Header
    html_parts.append('<thead><tr>')
    for col in df.columns:
        html_parts.append(f'<th style="background-color: {header_bg}; color: {text_color}; font-weight: 700; padding: 14px 12px; text-align: left; border-bottom: 3px solid {header_border};">{col}</th>')
    html_parts.append('</tr></thead>')
    
    # Body
    html_parts.append('<tbody>')
    for idx, row in enumerate(df.itertuples(index=False)):
        bg_color = row_odd if idx % 2 == 0 else row_even
        html_parts.append(f'<tr style="background-color: {bg_color};">')
        for val in row:
            # Escape HTML characters in values
            val_str = str(val) if val is not None else "-"
            html_parts.append(f'<td style="padding: 12px; color: {text_color}; border-bottom: 1px solid {border_color};">{val_str}</td>')
        html_parts.append('</tr>')
    html_parts.append('</tbody>')
    
    html_parts.append('</table>')
    html_parts.append('</div>')
    
    final_html = ''.join(html_parts)
    st.markdown(final_html, unsafe_allow_html=True)


def get_chart_theme() -> dict:
    """
    Get Plotly chart theme configuration based on current theme.
    
    Returns:
        Dictionary with chart styling parameters.
    """
    if is_dark_mode():
        return {
            'paper_bgcolor': '#0E1117',
            'plot_bgcolor': '#1A1A2E',
            'font_color': '#FFFFFF',
            'grid_color': 'rgba(255,255,255,0.12)',
            'line_color': 'rgba(255,255,255,0.25)',
            'title_color': '#FFFFFF',
            'axis_color': '#E0E0E0',
            'tick_color': '#D0D0D0',
        }
    else:
        return {
            'paper_bgcolor': '#FFFFFF',
            'plot_bgcolor': '#FAFAFA',
            'font_color': '#1A1A1A',
            'grid_color': 'rgba(0,0,0,0.08)',
            'line_color': 'rgba(0,0,0,0.15)',
            'title_color': '#1E3A5F',
            'axis_color': '#333333',
            'tick_color': '#444444',
        }


def get_theme_css(is_dark: bool = None) -> str:
    """
    Get theme-specific CSS for the dashboard.
    
    Args:
        is_dark: Whether dark mode is active. If None, reads from session_state.
        
    Returns:
        CSS string wrapped in <style> tags.
    """
    if is_dark is None:
        init_theme()
        is_dark = st.session_state.theme_mode == 'dark'
    
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
        header { visibility: hidden; }
        
        /* Hide the top white header bar completely */
        [data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Also hide toolbar */
        [data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* Toggle styling */
        .stToggle > label > div[data-testid="stMarkdownContainer"] > p {
            font-weight: 600 !important;
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
                color: #D0D0D0 !important;
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
                color: #D0D0D0 !important;
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
                color: #D0D0D0 !important;
            }
            
            div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
                color: #FFFFFF !important;
                font-weight: 700 !important;
            }
            
            div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
                color: #4CAF50 !important;
            }
            
            div[data-testid="metric-container"] div[data-testid="stMetricDelta"][data-testid*="negative"] {
                color: #F44336 !important;
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
            
            /* Download buttons - Dark - FIXED */
            .stDownloadButton > button,
            .stDownloadButton button,
            [data-testid="stDownloadButton"] > button,
            [data-testid="stDownloadButton"] button {
                background: linear-gradient(135deg, #4DA6FF 0%, #3D8BD9 100%) !important;
                color: #FFFFFF !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                border: none !important;
            }
            
            .stDownloadButton > button:hover,
            [data-testid="stDownloadButton"] button:hover {
                background: linear-gradient(135deg, #5DB6FF 0%, #4D9BE9 100%) !important;
                box-shadow: 0 4px 12px rgba(77, 166, 255, 0.4) !important;
            }
            
            /* Force download button text white */
            .stDownloadButton button p,
            .stDownloadButton button span,
            [data-testid="stDownloadButton"] button p,
            [data-testid="stDownloadButton"] button span {
                color: #FFFFFF !important;
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
            
            /* Selectbox dropdown text */
            .stSelectbox [data-baseweb="select"] span,
            .stMultiSelect [data-baseweb="select"] span {
                color: #FAFAFA !important;
            }
            
            /* MultiSelect input area - FIXED white background issue */
            .stMultiSelect [data-baseweb="select"] > div,
            .stMultiSelect [data-baseweb="input"],
            .stMultiSelect input,
            [data-baseweb="select"] [data-baseweb="input"] {
                background-color: #2D2D3D !important;
                color: #FAFAFA !important;
            }
            
            /* MultiSelect dropdown list container */
            [data-baseweb="menu"],
            [data-baseweb="list"],
            ul[role="listbox"] {
                background-color: #2D2D3D !important;
            }
            
            /* MultiSelect dropdown items */
            [data-baseweb="menu"] li,
            [data-baseweb="list"] li,
            ul[role="listbox"] li {
                background-color: #2D2D3D !important;
                color: #FAFAFA !important;
            }
            
            [data-baseweb="menu"] li:hover,
            [data-baseweb="list"] li:hover,
            ul[role="listbox"] li:hover {
                background-color: #4D4D5D !important;
            }
            
            /* Dropdown menu - Dark */
            [data-baseweb="popover"] {
                background-color: #2D2D3D !important;
            }
            
            [data-baseweb="popover"] div {
                background-color: #2D2D3D !important;
            }
            
            [data-baseweb="popover"] li {
                color: #FAFAFA !important;
                background-color: #2D2D3D !important;
            }
            
            [data-baseweb="popover"] li:hover {
                background-color: #3D3D4D !important;
            }
            
            /* ============ DATAFRAME STYLING - DARK ============ */
            /* Pastel background for better readability in dark mode */
            .stDataFrame {
                background-color: #FFF8F0 !important;
                border-radius: 12px !important;
                border: 2px solid #E8D5C4 !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
            }
            
            .stDataFrame [data-testid="stDataFrameResizable"],
            .stDataFrame > div > div > div > div {
                background-color: #FFF8F0 !important;
            }
            
            .stDataFrame th,
            [data-testid="stDataFrame"] div[role="columnheader"] {
                background-color: #FFE4CC !important;
                color: #1A1A1A !important;
                font-weight: 700 !important;
                border-bottom: 3px solid #FF9F5A !important;
                padding: 12px 8px !important;
            }
            
            .stDataFrame td,
            [data-testid="stDataFrame"] div[role="gridcell"] {
                background-color: #FFFCF8 !important;
                color: #1A1A1A !important;
                border-bottom: 1px solid #F0E6DC !important;
                padding: 10px 8px !important;
            }
            
            .stDataFrame tbody tr:nth-child(even) td,
            [data-testid="stDataFrame"] div[role="row"]:nth-of-type(even) div[role="gridcell"] {
                background-color: #FFF5EB !important;
            }
            
            .stDataFrame tr:hover td,
            [data-testid="stDataFrame"] div[role="row"]:hover div[role="gridcell"] {
                background-color: #FFE8D5 !important;
            }
            
            [data-testid="stDataFrame"] > div,
            [data-testid="stDataFrame"] [data-testid="glideDataEditor"],
            .dvn-scroller {
                background-color: #FFF8F0 !important;
            }
            
            .dvn-cell, .gdg-cell {
                background-color: #FFFCF8 !important;
                color: #1A1A1A !important;
            }
            
            .dvn-header, .gdg-header {
                background-color: #FFE4CC !important;
                color: #1A1A1A !important;
                font-weight: 700 !important;
                border-bottom: 3px solid #FF9F5A !important;
            }
            
            [data-testid="stDataFrame"] canvas {
                background-color: #FFF8F0 !important;
            }
            
            /* Force all dataframe text to be dark */
            [data-testid="stDataFrame"] span,
            [data-testid="stDataFrame"] div,
            [data-testid="stDataFrame"] p {
                color: #1A1A1A !important;
            }
            
            /* Expander - Dark */
            .streamlit-expanderHeader {
                background-color: #1E1E2E !important;
                color: #FAFAFA !important;
                border-radius: 8px;
            }
            
            .streamlit-expanderContent {
                background-color: #1E1E2E !important;
                color: #FAFAFA !important;
            }
            
            /* Toggle - Dark mode specific styling */
            .stToggle > label > span[data-testid="stToggleSwitch"] {
                background-color: #333 !important;
            }
            
            .stToggle > label > span[data-testid="stToggleSwitch"][aria-checked="true"] {
                background-color: #4DA6FF !important;
            }
            
            /* Tabs - Dark */
            .stTabs [data-baseweb="tab-list"] {
                background-color: #1E1E2E !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                color: #FAFAFA !important;
            }
            
            .stTabs [aria-selected="true"] {
                color: #4DA6FF !important;
                border-bottom-color: #4DA6FF !important;
            }
            
            /* Checkbox - Dark */
            .stCheckbox label span {
                color: #FAFAFA !important;
            }
            
            .stCheckbox [data-testid="stCheckbox"] {
                color: #FAFAFA !important;
            }
            
            /* Radio buttons - Dark */
            .stRadio label {
                color: #FAFAFA !important;
            }
            
            /* Slider - Dark */
            .stSlider label {
                color: #FAFAFA !important;
            }
            
            /* Number input - Dark */
            .stNumberInput label {
                color: #FAFAFA !important;
            }
            
            .stNumberInput input {
                background-color: #2D2D3D !important;
                color: #FAFAFA !important;
                border-color: #444 !important;
            }
            
            /* Text area - Dark */
            .stTextArea textarea {
                background-color: #2D2D3D !important;
                color: #FAFAFA !important;
                border-color: #444 !important;
            }
            
            /* Alert/Info messages - Dark */
            .stAlert {
                background-color: #1E1E2E !important;
                color: #FAFAFA !important;
                border: 1px solid #333 !important;
            }
            
            [data-testid="stNotification"] {
                background-color: #1E1E2E !important;
                color: #FAFAFA !important;
            }
            
            /* Plotly charts container */
            .js-plotly-plot, .plotly {
                background-color: transparent !important;
            }
            
            /* Caption text */
            .stCaption {
                color: #B0B0B0 !important;
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
            
            /* ============ DATAFRAME STYLING - LIGHT ============ */
            /* Soft pastel blue background for light mode */
            .stDataFrame {
                background-color: #F0F7FF !important;
                border-radius: 12px !important;
                border: 2px solid #C5DCF5 !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
            }
            
            .stDataFrame th {
                background-color: #D6E9FF !important;
                color: #1A1A1A !important;
                font-weight: 700 !important;
                border-bottom: 3px solid #4A90D9 !important;
                padding: 12px 8px !important;
            }
            
            .stDataFrame td {
                background-color: #FAFCFF !important;
                color: #1A1A1A !important;
                border-bottom: 1px solid #E0ECFA !important;
                padding: 10px 8px !important;
            }
            
            .stDataFrame tbody tr:nth-child(even) td {
                background-color: #EDF5FF !important;
            }
            
            .stDataFrame tr:hover td {
                background-color: #D6E9FF !important;
            }
            
            /* Glide data grid (new Streamlit dataframe) */
            [data-testid="stDataFrame"] > div,
            .dvn-scroller {
                background-color: #F0F7FF !important;
            }
            
            .dvn-cell, .gdg-cell {
                background-color: #FAFCFF !important;
                color: #1A1A1A !important;
                border-bottom: 1px solid #E0ECFA !important;
            }
            
            [data-testid="stDataFrame"] div[role="row"]:nth-of-type(even) div[role="gridcell"] {
                background-color: #EDF5FF !important;
            }
            
            [data-testid="stDataFrame"] div[role="row"]:hover div[role="gridcell"] {
                background-color: #D6E9FF !important;
            }
            
            .dvn-header, .gdg-header,
            [data-testid="stDataFrame"] div[role="columnheader"] {
                background-color: #D6E9FF !important;
                color: #1A1A1A !important;
                font-weight: 700 !important;
                border-bottom: 3px solid #4A90D9 !important;
            }
            
            /* Force all text in dataframe to be dark */
            [data-testid="stDataFrame"] span,
            [data-testid="stDataFrame"] div,
            [data-testid="stDataFrame"] p {
                color: #1A1A1A !important;
            }
            
            /* Tabs - Light */
            .stTabs [data-baseweb="tab-list"] {
                background-color: #FFFFFF !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                color: #1A1A1A !important;
            }
            
            .stTabs [aria-selected="true"] {
                color: #1E3A5F !important;
                border-bottom-color: #1E3A5F !important;
            }
            
            /* Checkbox - Light */
            .stCheckbox label span {
                color: #1A1A1A !important;
            }
            
            /* Expander - Light */
            .streamlit-expanderHeader {
                background-color: #F8F9FA !important;
                color: #1A1A1A !important;
            }
            
            .streamlit-expanderContent {
                background-color: #FFFFFF !important;
                color: #1A1A1A !important;
            }
        """
    
    return f"<style>{common_css}{theme_css}</style>"


def apply_theme():
    """Apply theme CSS to the current page. Call this at the top of each page."""
    init_theme()
    st.markdown(get_theme_css(), unsafe_allow_html=True)

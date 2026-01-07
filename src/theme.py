"""
theme.py - Centralized theme management for all pages.

This module provides theme CSS that can be applied consistently across all pages.
"""

import streamlit as st


def init_theme():
    """Initialize theme in session state if not exists."""
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'light'


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
            
            /* Tabs - Dark */
            .stTabs [data-baseweb="tab-list"] {
                background-color: #1E1E2E !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                color: #FAFAFA !important;
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
        """
    
    return f"<style>{common_css}{theme_css}</style>"


def apply_theme():
    """Apply theme CSS to the current page. Call this at the top of each page."""
    init_theme()
    st.markdown(get_theme_css(), unsafe_allow_html=True)

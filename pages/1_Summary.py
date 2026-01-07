"""
Page 1: Summary (Overview)
Main dashboard page with KPIs, trend chart, top movers, and auto-insights.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.constants import (
    LABELS,
    COL_DATE,
    COL_COMMODITY,
    COL_REGION,
    KPI_POSITIVE_COLOR,
    KPI_NEGATIVE_COLOR,
    KPI_NEUTRAL_COLOR,
    DEFAULT_REGION,
)
from src.metrics import (
    get_kpi_summary,
    get_top_movers,
    generate_auto_insights,
)
from src.charts import (
    create_price_trend_chart,
    create_top_movers_bar,
    format_kpi_value,
    format_change_value,
)
from src.theme import apply_theme

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=f"{LABELS['page_overview']} - {LABELS['app_title']}",
    page_icon="",
    layout="wide",
)

# Apply theme
apply_theme()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_trend_display(trend_status: str) -> tuple:
    """Get display text and color for trend status."""
    if trend_status == "rising":
        return LABELS["trend_rising"], KPI_NEGATIVE_COLOR  # Rising prices = concern
    elif trend_status == "falling":
        return LABELS["trend_falling"], KPI_POSITIVE_COLOR  # Falling prices = good
    else:
        return LABELS["trend_stable"], KPI_NEUTRAL_COLOR


def render_kpi_card(label: str, value: str, delta: str = None, delta_color: str = None):
    """Render a styled KPI card."""
    delta_html = ""
    if delta:
        delta_html = f'<p style="color: {delta_color}; font-size: 1rem; margin: 0;">{delta}</p>'
    
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; 
                border: 1px solid #e9ecef; text-align: center; height: 140px;">
        <p style="color: #6c757d; font-size: 0.9rem; margin-bottom: 0.5rem;">{label}</p>
        <h2 style="color: #1E3A5F; margin: 0.5rem 0; font-size: 1.8rem;">{value}</h2>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# MAIN PAGE
# =============================================================================

def main():
    st.title("RINGKASAN")
    st.markdown("Ringkasan harga utama, tren, dan komoditas dengan performa terbaik")
    
    # Check if data is loaded
    if 'df' not in st.session_state:
        st.warning("Data belum dimuat. Silakan kembali ke Beranda untuk memuat data.")
        st.stop()
    
    df = st.session_state['df']
    filters = st.session_state.get('filters', {})
    
    # Get filter values
    commodity = filters.get('commodity', df[COL_COMMODITY].iloc[0])
    regions = filters.get('regions', [df[COL_REGION].iloc[0]])
    date_start = filters.get('date_start')
    date_end = filters.get('date_end')
    analyst_mode = filters.get('analyst_mode', False)
    
    # Ensure we have valid regions
    if not regions:
        regions = [DEFAULT_REGION] if DEFAULT_REGION in df[COL_REGION].unique() else [df[COL_REGION].iloc[0]]
    
    # Get selected region (first one for KPI display)
    selected_region = regions[0] if regions else df[COL_REGION].iloc[0]
    
    # ==========================================================================
    # KPI SECTION
    # ==========================================================================
    
    st.markdown("### Indikator Kinerja Utama")
    
    # Get KPI summary for selected commodity and region
    kpi_data = get_kpi_summary(df, commodity, selected_region)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=LABELS["latest_price"],
            value=format_kpi_value(kpi_data.get('latest_price')),
        )
    
    with col2:
        abs_7d = kpi_data.get('change_7d_abs')
        pct_7d = kpi_data.get('change_7d_pct')
        change_text, _ = format_change_value(abs_7d, pct_7d)
        st.metric(
            label=LABELS["change_7d"],
            value=change_text,
            delta=f"{pct_7d:+.1f}%" if pct_7d is not None else None,
            delta_color="inverse",  # Red for increase, green for decrease
        )
    
    with col3:
        abs_30d = kpi_data.get('change_30d_abs')
        pct_30d = kpi_data.get('change_30d_pct')
        change_text_30, _ = format_change_value(abs_30d, pct_30d)
        st.metric(
            label=LABELS["change_30d"],
            value=change_text_30,
            delta=f"{pct_30d:+.1f}%" if pct_30d is not None else None,
            delta_color="inverse",
        )
    
    with col4:
        trend_status = kpi_data.get('trend_status', 'stable')
        trend_text, _ = get_trend_display(trend_status)
        st.metric(
            label=LABELS["trend_status"],
            value=trend_text,
        )
    
    # ==========================================================================
    # PRICE TREND CHART
    # ==========================================================================
    
    st.markdown("---")
    st.markdown(f"### Tren Harga: {commodity}")
    
    # Filter data for chart
    df_filtered = df[
        (df[COL_COMMODITY] == commodity) &
        (df[COL_REGION].isin(regions))
    ].copy()
    
    if date_start and date_end:
        df_filtered = df_filtered[
            (df_filtered[COL_DATE] >= pd.Timestamp(date_start)) &
            (df_filtered[COL_DATE] <= pd.Timestamp(date_end))
        ]
    
    if not df_filtered.empty:
        date_range = None
        if date_start and date_end:
            date_range = (date_start, date_end)
        
        fig = create_price_trend_chart(
            df,
            commodity,
            regions,
            show_ma7=analyst_mode,
            show_ma14=analyst_mode,
            date_range=date_range
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(LABELS["no_data"])
    
    # ==========================================================================
    # TOP MOVERS SECTION
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("### Pergerakan Tertinggi (7 Hari)")
    
    col1, col2 = st.columns(2)
    
    # Get top movers for the selected commodity
    top_gainers, top_losers = get_top_movers(df, commodity, days=7)
    
    with col1:
        st.markdown(f"**{LABELS['top_movers_up']}**")
        if not top_gainers.empty:
            fig_movers = create_top_movers_bar(top_gainers, top_losers)
            st.plotly_chart(fig_movers, use_container_width=True)
        else:
            st.info("Data regional tidak tersedia untuk pergerakan tertinggi.")
    
    with col2:
        st.markdown(f"**{LABELS['top_movers_down']}**")
        if not top_losers.empty:
            # Show losers table
            losers_display = top_losers.copy()
            losers_display['change_pct'] = losers_display['change_pct'].apply(lambda x: f"{x:+.1f}%")
            losers_display.columns = ['Wilayah', 'Perubahan']
            st.dataframe(losers_display, use_container_width=True, hide_index=True)
        else:
            st.info("Data regional tidak tersedia untuk penurunan tertinggi.")
    
    # ==========================================================================
    # AUTO-INSIGHTS (Analyst Mode Only)
    # ==========================================================================
    
    if analyst_mode:
        st.markdown("---")
        st.markdown("### Insight Otomatis")
        
        insights = generate_auto_insights(df, commodity, selected_region)
        
        if insights:
            for i, insight in enumerate(insights, 1):
                st.markdown(f"{i}. {insight}")
        else:
            st.info("Tidak ada insight signifikan untuk pilihan saat ini.")


if __name__ == "__main__":
    main()
else:
    main()

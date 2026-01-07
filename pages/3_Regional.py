"""
Page 3: Regional Comparison
Compare prices across different regions with rankings and scatter plots.
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
    COL_PRICE,
    DEFAULT_REGION,
    REGIONAL_RANKING_COUNT,
)
from src.metrics import (
    get_regional_ranking,
    get_regional_volatility_comparison,
)
from src.charts import (
    create_price_trend_chart,
    create_regional_ranking_bar,
    create_volatility_scatter,
)
from src.theme import apply_theme

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=f"{LABELS['page_regions']} - {LABELS['app_title']}",
    page_icon="",
    layout="wide",
)

# Apply theme
apply_theme()

# =============================================================================
# MAIN PAGE
# =============================================================================

def main():
    st.title("WILAYAH")
    st.markdown("Perbandingan harga regional untuk mengidentifikasi perbedaan antar wilayah.")
    
    # Check if data is loaded
    if 'df' not in st.session_state:
        st.warning("Data belum dimuat. Silakan kembali ke Beranda untuk memuat data.")
        st.stop()
    
    df = st.session_state['df']
    filters = st.session_state.get('filters', {})
    
    # Validate data
    if df is None or df.empty:
        st.error("Tidak ada data tersedia.")
        st.stop()
    
    # Get filter values with safe defaults
    commodity = filters.get('commodity')
    if commodity is None:
        commodity = df[COL_COMMODITY].iloc[0] if not df.empty else None
    
    regions = filters.get('regions', [])
    if not regions:
        regions = [df[COL_REGION].iloc[0]] if not df.empty else []
    
    date_start = filters.get('date_start')
    date_end = filters.get('date_end')
    analyst_mode = filters.get('analyst_mode', False)
    
    if commodity is None:
        st.error("Data komoditas tidak tersedia.")
        st.stop()
    
    # Filter data by date
    df_filtered = df.copy()
    if date_start and date_end:
        try:
            df_filtered = df_filtered[
                (df_filtered[COL_DATE] >= pd.Timestamp(date_start)) &
                (df_filtered[COL_DATE] <= pd.Timestamp(date_end))
            ]
        except Exception:
            pass
    
    date_range = (date_start, date_end) if date_start and date_end else None
    
    # Check if regional data is available
    unique_regions = df_filtered[
        df_filtered[COL_COMMODITY] == commodity
    ][COL_REGION].unique()
    
    has_regional_data = len(unique_regions) > 1 and not (
        len(unique_regions) == 1 and DEFAULT_REGION in unique_regions
    )
    
    if not has_regional_data:
        st.markdown("""
        <div style="background: #fff3e0; padding: 2rem; border-radius: 12px; text-align: center;">
            <h3>Data Regional Tidak Tersedia</h3>
            <p>Data untuk komoditas ini tidak memiliki informasi regional yang cukup untuk perbandingan.</p>
            <p>Silakan pilih komoditas lain atau periksa sumber data.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # ==========================================================================
    # REGIONAL RANKING
    # ==========================================================================
    
    st.markdown(f"### Peringkat Harga Regional: {commodity}")
    st.markdown("Perbandingan harga terbaru di seluruh wilayah")
    
    try:
        highest, lowest = get_regional_ranking(
            df_filtered, 
            commodity, 
            date_range=date_range,
            top_n=REGIONAL_RANKING_COUNT
        )
        
        if not highest.empty or not lowest.empty:
            fig_ranking = create_regional_ranking_bar(highest, lowest)
            st.plotly_chart(fig_ranking, use_container_width=True)
        else:
            st.info("Data peringkat regional tidak tersedia.")
    except Exception as e:
        st.warning(f"Tidak dapat membuat peringkat regional: {str(e)}")
    
    st.markdown("---")
    
    # ==========================================================================
    # MULTI-REGION COMPARISON CHART
    # ==========================================================================
    
    st.markdown(f"### {LABELS['price_comparison']}")
    st.markdown(f"Perbandingan tren harga untuk wilayah yang dipilih: **{', '.join(regions)}**")
    
    if len(regions) > 5:
        st.warning("Terlalu banyak wilayah dipilih. Menampilkan 5 wilayah pertama.")
        regions = regions[:5]
    
    try:
        fig_comparison = create_price_trend_chart(
            df_filtered,
            commodity,
            regions,
            show_ma7=False,
            show_ma14=False,
            date_range=date_range
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
    except Exception as e:
        st.warning(f"Tidak dapat membuat grafik perbandingan: {str(e)}")
    
    # ==========================================================================
    # PRICE VS VOLATILITY SCATTER (Analyst Mode)
    # ==========================================================================
    
    if analyst_mode:
        st.markdown("---")
        st.markdown(f"### {LABELS['price_vs_volatility']}")
        st.markdown("""
        Grafik scatter menunjukkan hubungan antara harga rata-rata dan volatilitas per wilayah.
        Wilayah dengan harga tinggi dan volatilitas tinggi memerlukan perhatian khusus.
        """)
        
        try:
            volatility_data = get_regional_volatility_comparison(df_filtered, commodity, days=30)
            
            if not volatility_data.empty:
                fig_scatter = create_volatility_scatter(volatility_data)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Data tidak cukup untuk analisis volatilitas regional.")
        except Exception as e:
            st.warning(f"Tidak dapat membuat scatter volatilitas: {str(e)}")
    
    # ==========================================================================
    # REGIONAL SUMMARY TABLE
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("### Ringkasan Regional")
    
    try:
        # Calculate summary statistics per region
        mask = df_filtered[COL_COMMODITY] == commodity
        regional_data = df_filtered[mask].groupby(COL_REGION).agg({
            COL_PRICE: ['mean', 'min', 'max', 'std', 'last']
        }).round(0)
        
        regional_data.columns = ['Rata-rata', 'Minimum', 'Maksimum', 'Std Dev', 'Harga Terkini']
        regional_data = regional_data.sort_values('Harga Terkini', ascending=False)
        
        # Format as currency
        for col in regional_data.columns:
            regional_data[col] = regional_data[col].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "-")
        
        st.dataframe(
            regional_data.reset_index(),
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv_data = regional_data.reset_index().to_csv(index=False)
        st.download_button(
            label="Unduh Ringkasan Regional (CSV)",
            data=csv_data,
            file_name=f"ringkasan_regional_{commodity.replace(' ', '_')}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.warning(f"Tidak dapat membuat ringkasan regional: {str(e)}")


if __name__ == "__main__":
    main()
else:
    main()

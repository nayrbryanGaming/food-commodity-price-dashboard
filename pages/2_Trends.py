"""
Page 2: Trends (Time Series Lab)
Advanced time series analysis with resampling, moving averages, and anomaly detection.
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
)
from src.metrics import (
    detect_anomalies,
)
from src.charts import (
    create_price_trend_chart,
    create_price_trend_with_anomalies,
)
from src.theme import apply_theme

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=f"{LABELS['page_trends']} - {LABELS['app_title']}",
    page_icon="",
    layout="wide",
)

# Apply theme
apply_theme()

# =============================================================================
# MAIN PAGE
# =============================================================================

def main():
    st.title("TREN")
    st.markdown("Analisis tren harga dengan rata-rata bergerak dan deteksi anomali")
    
    # Check if data is loaded
    if 'df' not in st.session_state:
        st.warning("Data belum dimuat. Silakan kembali ke Beranda untuk memuat data.")
        st.stop()
    
    df = st.session_state['df']
    filters = st.session_state.get('filters', {})
    
    # Get filter values with safe defaults
    if df is None or df.empty:
        st.error("Tidak ada data tersedia.")
        st.stop()
    
    commodity = filters.get('commodity')
    if commodity is None:
        commodity = df[COL_COMMODITY].iloc[0] if not df.empty else None
    
    regions = filters.get('regions', [])
    if not regions:
        regions = [df[COL_REGION].iloc[0]] if not df.empty else []
    
    date_start = filters.get('date_start')
    date_end = filters.get('date_end')
    analyst_mode = filters.get('analyst_mode', False)
    
    primary_region = regions[0] if regions else None
    
    if primary_region is None or commodity is None:
        st.error("Data wilayah atau komoditas tidak tersedia.")
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
    
    # ==========================================================================
    # CONTROLS
    # ==========================================================================
    
    st.markdown("### Pengaturan")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        resample_freq = st.radio(
            "Frekuensi Data",
            options=["Harian", "Mingguan"],
            index=0,
            horizontal=True,
        )
    
    # Advanced controls for analyst mode
    show_ma7 = False
    show_ma14 = False
    show_anomalies = False
    
    if analyst_mode:
        with col2:
            show_ma7 = st.checkbox("Rata-rata Bergerak 7 Hari (MA7)", value=False)
        
        with col3:
            show_ma14 = st.checkbox("Rata-rata Bergerak 14 Hari (MA14)", value=False)
        
        with col4:
            show_anomalies = st.checkbox("Tampilkan Anomali", value=False)
    
    st.markdown("---")
    
    # ==========================================================================
    # MAIN TREND CHART
    # ==========================================================================
    
    st.markdown(f"### Tren Harga: {commodity}")
    
    # Prepare data based on resample frequency
    if resample_freq == "Mingguan":
        st.info("Data ditampilkan dalam agregasi mingguan (rata-rata)")
    
    # Create trend chart
    try:
        fig = create_price_trend_chart(
            df_filtered,
            commodity,
            regions,
            show_ma7=show_ma7,
            show_ma14=show_ma14,
            date_range=date_range
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Tidak dapat membuat grafik: {str(e)}")
    
    # ==========================================================================
    # ANOMALY DETECTION (Analyst Mode)
    # ==========================================================================
    
    if analyst_mode and show_anomalies:
        st.markdown("---")
        st.markdown("### Deteksi Anomali")
        
        from src.theme import is_dark_mode
        info_bg = "rgba(33, 150, 243, 0.15)" if is_dark_mode() else "#e3f2fd"
        info_text = "#E3F2FD" if is_dark_mode() else "#1565C0"
        
        st.markdown(f"""
        <div style="background: {info_bg}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #2196f3;">
            <span style="color: {info_text};"><strong>Metode:</strong> Anomali terdeteksi ketika perubahan harga harian melebihi 10%.
            <br>Ini membantu mengidentifikasi pergerakan harga yang tidak biasa.</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Detect anomalies for primary region
        try:
            anomaly_df = detect_anomalies(df_filtered, commodity, primary_region, method="threshold")
            
            if not anomaly_df.empty:
                # Chart with anomaly markers
                fig_anomaly = create_price_trend_with_anomalies(
                    df_filtered,
                    anomaly_df,
                    commodity,
                    primary_region,
                    date_range=date_range
                )
                st.plotly_chart(fig_anomaly, use_container_width=True)
                
                # Anomaly table
                anomalies = anomaly_df[anomaly_df['is_anomaly'] == True]
                
                if not anomalies.empty:
                    st.markdown("#### Daftar Anomali")
                    
                    anomaly_table = anomalies[[COL_DATE, COL_PRICE, 'daily_change_pct']].copy()
                    anomaly_table.columns = ['Tanggal', 'Harga', 'Perubahan (%)']
                    anomaly_table['Tanggal'] = anomaly_table['Tanggal'].dt.strftime('%d %b %Y')
                    anomaly_table['Harga'] = anomaly_table['Harga'].apply(lambda x: f"Rp {x:,.0f}")
                    anomaly_table['Perubahan (%)'] = anomaly_table['Perubahan (%)'].apply(lambda x: f"{x:+.1f}%")
                    
                    st.dataframe(
                        anomaly_table.reset_index(drop=True),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.success("Tidak ada anomali terdeteksi dalam periode ini.")
            else:
                st.info("Data tidak cukup untuk analisis anomali.")
        except Exception as e:
            st.warning(f"Tidak dapat mendeteksi anomali: {str(e)}")
    
    # ==========================================================================
    # STATISTICS PANEL
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("### Statistik Periode")
    
    try:
        mask = (df_filtered[COL_COMMODITY] == commodity) & (df_filtered[COL_REGION] == primary_region)
        period_data = df_filtered[mask].dropna(subset=[COL_PRICE])
        
        if not period_data.empty:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            prices = period_data[COL_PRICE]
            
            with col1:
                st.metric("Minimum", f"Rp {prices.min():,.0f}")
            
            with col2:
                st.metric("Maksimum", f"Rp {prices.max():,.0f}")
            
            with col3:
                st.metric("Rata-rata", f"Rp {prices.mean():,.0f}")
            
            with col4:
                st.metric("Median", f"Rp {prices.median():,.0f}")
            
            with col5:
                std_pct = (prices.std() / prices.mean()) * 100 if prices.mean() > 0 else 0
                st.metric("Volatilitas", f"{std_pct:.1f}%")
            
            # Period summary
            st.markdown(f"""
            **Ringkasan:** Dalam periode yang dipilih, harga {commodity} di {primary_region} 
            berkisar dari Rp {prices.min():,.0f} hingga Rp {prices.max():,.0f} 
            dengan rata-rata Rp {prices.mean():,.0f}.
            """)
        else:
            st.warning(LABELS["no_data"])
    except Exception as e:
        st.warning(f"Tidak dapat menghitung statistik: {str(e)}")


if __name__ == "__main__":
    main()
else:
    main()

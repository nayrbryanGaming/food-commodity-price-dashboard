"""
Page 4: Commodities (Commodity Basket)
Compare multiple commodities with charts, heatmaps, and summary tables.
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
    MAX_COMMODITIES_COMPARE,
)
from src.metrics import (
    get_commodity_summary,
)
from src.charts import (
    create_multi_commodity_chart,
    create_price_heatmap,
    create_small_multiples,
)
from src.theme import apply_theme, render_styled_dataframe

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=f"{LABELS['page_commodities']} - {LABELS['app_title']}",
    page_icon="",
    layout="wide",
)

# Apply theme
apply_theme()

# =============================================================================
# MAIN PAGE
# =============================================================================

def main():
    st.title("KOMODITAS")
    st.markdown("Bandingkan beberapa komoditas untuk melihat tren dan perubahan harga.")
    
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
    regions = filters.get('regions', [])
    if not regions:
        regions = [df[COL_REGION].iloc[0]] if not df.empty else []
    
    date_start = filters.get('date_start')
    date_end = filters.get('date_end')
    analyst_mode = filters.get('analyst_mode', False)
    
    primary_region = regions[0] if regions else None
    
    if primary_region is None:
        st.error("Data wilayah tidak tersedia.")
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
    # COMMODITY SELECTION
    # ==========================================================================
    
    st.markdown("### Pilih Komoditas untuk Perbandingan")
    
    all_commodities = sorted(df_filtered[COL_COMMODITY].unique().tolist())
    
    if not all_commodities:
        st.warning("Tidak ada komoditas tersedia dalam data yang difilter.")
        st.stop()
    
    # Default selection: first 4 commodities
    default_selection = all_commodities[:min(4, len(all_commodities))]
    
    selected_commodities = st.multiselect(
        f"Pilih komoditas (maks. {MAX_COMMODITIES_COMPARE})",
        options=all_commodities,
        default=default_selection,
        max_selections=MAX_COMMODITIES_COMPARE,
        help=f"Pilih hingga {MAX_COMMODITIES_COMPARE} komoditas untuk perbandingan"
    )
    
    if not selected_commodities:
        st.warning("Silakan pilih minimal satu komoditas untuk melanjutkan.")
        st.stop()
    
    st.markdown("---")
    
    # ==========================================================================
    # NORMALIZED COMPARISON CHART
    # ==========================================================================
    
    st.markdown("### Perbandingan Komoditas")
    st.markdown(f"""
    Grafik menunjukkan perbandingan indeks harga (harga awal = 100) untuk wilayah **{primary_region}**.
    Ini memungkinkan perbandingan tren meskipun dengan skala harga yang berbeda.
    """)
    
    try:
        fig_comparison = create_multi_commodity_chart(
            df_filtered,
            selected_commodities,
            primary_region,
            date_range=date_range
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
    except Exception as e:
        st.warning(f"Tidak dapat membuat grafik perbandingan: {str(e)}")
    
    # ==========================================================================
    # SMALL MULTIPLES
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("### Grafik Komoditas Individual")
    st.markdown("Grafik terpisah untuk setiap komoditas (harga aktual dalam Rupiah)")
    
    try:
        fig_multiples = create_small_multiples(
            df_filtered,
            selected_commodities,
            primary_region,
            date_range=date_range
        )
        st.plotly_chart(fig_multiples, use_container_width=True)
    except Exception as e:
        st.warning(f"Tidak dapat membuat grafik individual: {str(e)}")
    
    # ==========================================================================
    # HEATMAP (Analyst Mode)
    # ==========================================================================
    
    if analyst_mode:
        st.markdown("---")
        st.markdown(f"### Peta Panas Perubahan Harga")
        st.markdown("Peta perubahan harga mingguan/bulanan (dalam persen)")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            resample = st.radio("Periode", ["Mingguan", "Bulanan"], index=0)
        
        # Use 'ME' instead of deprecated 'M' for month-end
        resample_code = 'W' if resample == "Mingguan" else 'ME'
        
        # Check if we have enough data
        min_periods_needed = 2 if resample == "Mingguan" else 2
        period_text = "2 minggu" if resample == "Mingguan" else "2 bulan"
        
        try:
            fig_heatmap = create_price_heatmap(
                df_filtered,
                selected_commodities,
                primary_region,
                resample=resample_code
            )
            
            if fig_heatmap.data:
                st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.warning(f"""
                **Data tidak cukup untuk membuat peta panas.**
                
                Peta panas membutuhkan minimal **{period_text}** data untuk menghitung perubahan harga.
                
                **Solusi:**
                - Perbesar rentang tanggal di sidebar (Filter → Rentang Tanggal)
                - Coba pilih periode "Mingguan" jika data terbatas
                """)
        except Exception as e:
            st.warning(f"Gagal membuat peta panas: Pastikan rentang tanggal minimal {period_text}.")
    
    # ==========================================================================
    # SUMMARY TABLE
    # ==========================================================================
    
    st.markdown("---")
    st.markdown(f"### Statistik Ringkasan")
    st.markdown(f"Ringkasan statistik untuk wilayah **{primary_region}**")
    
    try:
        summary_df = get_commodity_summary(df_filtered, selected_commodities, primary_region)
        
        if not summary_df.empty:
            # Format the table
            display_df = summary_df.copy()
            
            # Format currency columns
            if 'Latest Price' in display_df.columns:
                display_df['Latest Price'] = display_df['Latest Price'].apply(
                    lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "-"
                )
            
            # Format percentage columns
            for col in ['7-Day Change (%)', '30-Day Change (%)', 'Volatility (%)']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(
                        lambda x: f"{x:+.1f}%" if pd.notna(x) else "-"
                    )
            
            # Format status
            if 'Status' in display_df.columns:
                status_map = {
                    'rising': 'Naik',
                    'falling': 'Turun',
                    'stable': 'Stabil'
                }
                display_df['Status'] = display_df['Status'].map(lambda x: status_map.get(x, x))
            
            # Use styled HTML table for better visibility
            render_styled_dataframe(display_df, max_height="350px")
            
            # Download button
            csv_data = summary_df.to_csv(index=False)
            st.download_button(
                label="Unduh Ringkasan Komoditas (CSV)",
                data=csv_data,
                file_name=f"ringkasan_komoditas_{primary_region.replace(' ', '_')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Data ringkasan tidak tersedia.")
    except Exception as e:
        st.info(f"Tidak dapat membuat ringkasan: {str(e)}")
    
    # ==========================================================================
    # QUICK INSIGHTS
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("### Insight Cepat")
    
    try:
        if 'summary_df' in dir() and not summary_df.empty:
            # Find highest price increase
            if '7-Day Change (%)' in summary_df.columns:
                valid_changes = summary_df[summary_df['7-Day Change (%)'].notna()]
                if not valid_changes.empty:
                    max_change_idx = valid_changes['7-Day Change (%)'].idxmax()
                    min_change_idx = valid_changes['7-Day Change (%)'].idxmin()
                    
                    max_commodity = valid_changes.loc[max_change_idx, COL_COMMODITY]
                    max_change = valid_changes.loc[max_change_idx, '7-Day Change (%)']
                    
                    min_commodity = valid_changes.loc[min_change_idx, COL_COMMODITY]
                    min_change = valid_changes.loc[min_change_idx, '7-Day Change (%)']
                    
                    st.markdown(f"""
                    - **Kenaikan tertinggi (7 hari):** {max_commodity} ({max_change:+.1f}%)
                    - **Penurunan terbesar (7 hari):** {min_commodity} ({min_change:+.1f}%)
                    """)
            
            # Find most volatile
            if 'Volatility (%)' in summary_df.columns:
                valid_vol = summary_df[summary_df['Volatility (%)'].notna()]
                if not valid_vol.empty:
                    most_volatile_idx = valid_vol['Volatility (%)'].idxmax()
                    most_volatile = valid_vol.loc[most_volatile_idx, COL_COMMODITY]
                    volatility = valid_vol.loc[most_volatile_idx, 'Volatility (%)']
                    st.markdown(f"- **Paling volatil:** {most_volatile} (volatilitas {volatility:.1f}%)")
        else:
            st.info("Tidak ada insight tersedia.")
    except Exception:
        st.info("Tidak ada insight tersedia.")


if __name__ == "__main__":
    main()
else:
    main()

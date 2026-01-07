"""
Halaman 5: Data & Metadata
Tabel data, statistik kualitas, dan fungsi ekspor.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
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
from src.theme import apply_theme

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=f"{LABELS['page_data']} - {LABELS['app_title']}",
    page_icon="",
    layout="wide",
)

# Apply theme
apply_theme()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_number(value, decimals=0):
    """Format number with thousand separators."""
    try:
        if pd.isna(value):
            return "-"
        if decimals == 0:
            return f"{int(value):,}"
        return f"{value:,.{decimals}f}"
    except Exception:
        return str(value)


def format_currency(value):
    """Format value as Indonesian Rupiah."""
    try:
        if pd.isna(value):
            return "-"
        return f"Rp {value:,.0f}"
    except Exception:
        return str(value)


def get_data_quality_stats(df):
    """Calculate data quality statistics."""
    try:
        if df is None or df.empty:
            return {}
        
        total_rows = len(df)
        missing_values = df.isnull().sum().sum()
        missing_pct = (missing_values / (total_rows * len(df.columns))) * 100 if total_rows > 0 else 0
        
        # Date range
        date_min = df[COL_DATE].min() if COL_DATE in df.columns else None
        date_max = df[COL_DATE].max() if COL_DATE in df.columns else None
        
        # Unique counts
        n_commodities = df[COL_COMMODITY].nunique() if COL_COMMODITY in df.columns else 0
        n_regions = df[COL_REGION].nunique() if COL_REGION in df.columns else 0
        
        # Price statistics
        price_min = df[COL_PRICE].min() if COL_PRICE in df.columns else 0
        price_max = df[COL_PRICE].max() if COL_PRICE in df.columns else 0
        price_mean = df[COL_PRICE].mean() if COL_PRICE in df.columns else 0
        
        return {
            'total_rows': total_rows,
            'missing_values': missing_values,
            'missing_pct': missing_pct,
            'date_min': date_min,
            'date_max': date_max,
            'n_commodities': n_commodities,
            'n_regions': n_regions,
            'price_min': price_min,
            'price_max': price_max,
            'price_mean': price_mean,
            'completeness': 100 - missing_pct,
        }
    except Exception:
        return {}


# =============================================================================
# MAIN PAGE
# =============================================================================

def main():
    st.title("DATA & METADATA")
    st.markdown("Lihat, filter, dan ekspor data dengan statistik kualitas.")
    
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
    
    # Filter data
    df_filtered = df.copy()
    
    try:
        # Apply commodity filter
        if commodity:
            df_filtered = df_filtered[df_filtered[COL_COMMODITY] == commodity]
        
        # Apply region filter
        if regions:
            df_filtered = df_filtered[df_filtered[COL_REGION].isin(regions)]
        
        # Apply date filter
        if date_start and date_end:
            df_filtered = df_filtered[
                (df_filtered[COL_DATE] >= pd.Timestamp(date_start)) &
                (df_filtered[COL_DATE] <= pd.Timestamp(date_end))
            ]
    except Exception as e:
        st.warning(f"Kesalahan menerapkan filter: {str(e)}")
        df_filtered = df.copy()
    
    # ==========================================================================
    # STATISTIK KUALITAS DATA
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("### Statistik Kualitas Data")
    
    try:
        quality_stats = get_data_quality_stats(df_filtered)
        
        if quality_stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Catatan",
                    value=format_number(quality_stats.get('total_rows', 0))
                )
            
            with col2:
                st.metric(
                    label="Kelengkapan Data",
                    value=f"{quality_stats.get('completeness', 0):.1f}%"
                )
            
            with col3:
                st.metric(
                    label="Komoditas",
                    value=format_number(quality_stats.get('n_commodities', 0))
                )
            
            with col4:
                st.metric(
                    label="Wilayah",
                    value=format_number(quality_stats.get('n_regions', 0))
                )
            
            # Date range info
            date_min = quality_stats.get('date_min')
            date_max = quality_stats.get('date_max')
            if date_min and date_max:
                st.info(f"Rentang data: {date_min.strftime('%Y-%m-%d')} sampai {date_max.strftime('%Y-%m-%d')}")
    except Exception as e:
        st.warning(f"Tidak dapat menghitung statistik kualitas: {str(e)}")
    
    # ==========================================================================
    # STATISTIK HARGA
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("### Statistik Harga")
    
    try:
        if not df_filtered.empty and COL_PRICE in df_filtered.columns:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Harga Minimum",
                    value=format_currency(df_filtered[COL_PRICE].min())
                )
            
            with col2:
                st.metric(
                    label="Harga Rata-rata",
                    value=format_currency(df_filtered[COL_PRICE].mean())
                )
            
            with col3:
                st.metric(
                    label="Harga Maksimum",
                    value=format_currency(df_filtered[COL_PRICE].max())
                )
    except Exception as e:
        st.warning(f"Tidak dapat menghitung statistik harga: {str(e)}")
    
    # ==========================================================================
    # TABEL DATA
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("### Tabel Data")
    
    # Filter controls
    col1, col2 = st.columns(2)
    
    with col1:
        show_all = st.checkbox("Tampilkan semua data (tanpa filter)", value=False)
    
    with col2:
        max_rows = st.selectbox(
            "Baris yang ditampilkan",
            options=[100, 500, 1000, 5000],
            index=0
        )
    
    try:
        display_df = df.copy() if show_all else df_filtered.copy()
        
        if not display_df.empty:
            # Sort by date descending
            if COL_DATE in display_df.columns:
                display_df = display_df.sort_values(COL_DATE, ascending=False)
            
            # Limit rows
            total_rows = len(display_df)
            display_df = display_df.head(max_rows)
            
            # Format for display
            display_formatted = display_df.copy()
            
            # Format date column
            if COL_DATE in display_formatted.columns:
                display_formatted[COL_DATE] = display_formatted[COL_DATE].dt.strftime('%Y-%m-%d')
            
            # Format price column
            if COL_PRICE in display_formatted.columns:
                display_formatted[COL_PRICE] = display_formatted[COL_PRICE].apply(format_currency)
            
            # Show info about displayed rows
            if total_rows > max_rows:
                st.info(f"Menampilkan {max_rows:,} dari {total_rows:,} catatan. Tingkatkan batas tampilan untuk melihat lebih banyak.")
            
            # Display the table
            st.dataframe(
                display_formatted,
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info("Tidak ada data untuk ditampilkan dengan filter saat ini.")
    except Exception as e:
        st.error(f"Kesalahan menampilkan data: {str(e)}")
    
    # ==========================================================================
    # EKSPOR DATA
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("### Ekspor Data")
    
    col1, col2 = st.columns(2)
    
    try:
        with col1:
            # Export filtered data
            if not df_filtered.empty:
                csv_filtered = df_filtered.to_csv(index=False)
                st.download_button(
                    label="Unduh Data Terfilter (CSV)",
                    data=csv_filtered,
                    file_name=f"data_terfilter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Unduh data yang sudah difilter sebagai CSV"
                )
            else:
                st.button("Unduh Data Terfilter (CSV)", disabled=True)
                st.caption("Tidak ada data terfilter tersedia")
        
        with col2:
            # Export all data
            if not df.empty:
                csv_all = df.to_csv(index=False)
                st.download_button(
                    label="Unduh Semua Data (CSV)",
                    data=csv_all,
                    file_name=f"semua_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Unduh seluruh dataset sebagai CSV"
                )
            else:
                st.button("Unduh Semua Data (CSV)", disabled=True)
                st.caption("Tidak ada data tersedia")
    except Exception as e:
        st.warning(f"Kesalahan menyiapkan ekspor: {str(e)}")
    
    # ==========================================================================
    # METADATA
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("### Metadata Dataset")
    
    try:
        # List all commodities
        if COL_COMMODITY in df.columns:
            with st.expander("Komoditas Tersedia", expanded=False):
                commodities = sorted(df[COL_COMMODITY].unique().tolist())
                st.write(", ".join(commodities))
        
        # List all regions
        if COL_REGION in df.columns:
            with st.expander("Wilayah Tersedia", expanded=False):
                region_list = sorted(df[COL_REGION].unique().tolist())
                st.write(", ".join(region_list))
        
        # Column information
        with st.expander("Informasi Kolom", expanded=False):
            col_info = pd.DataFrame({
                'Kolom': df.columns.tolist(),
                'Tipe': [str(dtype) for dtype in df.dtypes.tolist()],
                'Jumlah Non-Null': [df[col].notna().sum() for col in df.columns],
                'Jumlah Null': [df[col].isna().sum() for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning(f"Tidak dapat menampilkan metadata: {str(e)}")


if __name__ == "__main__":
    main()
else:
    main()

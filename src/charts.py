"""
charts.py - Plotly chart factory module.

Creates all visualization components for the dashboard.
Uses consistent styling defined in constants.
Supports dark/light theme switching.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import streamlit as st

from .constants import (
    COL_DATE,
    COL_COMMODITY,
    COL_REGION,
    COL_PRICE,
    CHART_COLORS,
    CHART_LAYOUT,
    LABELS,
    KPI_POSITIVE_COLOR,
    KPI_NEGATIVE_COLOR,
    KPI_NEUTRAL_COLOR,
)


def get_chart_colors():
    """Get theme-aware colors for charts with high contrast."""
    is_dark = st.session_state.get('theme_mode', 'light') == 'dark'
    
    if is_dark:
        return {
            'paper_bgcolor': '#0E1117',
            'plot_bgcolor': '#1A1A2E',
            'font_color': '#FFFFFF',
            'grid_color': 'rgba(255,255,255,0.12)',
            'line_color': 'rgba(255,255,255,0.25)',
            'title_color': '#FFFFFF',
            'axis_color': '#E0E0E0',  # Brighter for better readability
            'axis_title_color': '#FFFFFF',  # Full white for axis titles
            'hover_bgcolor': '#2D2D3D',
            'tick_color': '#D0D0D0',  # High contrast tick labels
        }
    else:
        return {
            'paper_bgcolor': '#FFFFFF',
            'plot_bgcolor': '#FAFAFA',
            'font_color': '#1A1A1A',
            'grid_color': 'rgba(0,0,0,0.08)',
            'line_color': 'rgba(0,0,0,0.15)',
            'title_color': '#1E3A5F',
            'axis_color': '#333333',  # Darker for better readability
            'axis_title_color': '#1E3A5F',  # Match title color
            'hover_bgcolor': '#FFFFFF',
            'tick_color': '#444444',  # High contrast tick labels
        }


def apply_default_layout(fig: go.Figure, title: str = None) -> go.Figure:
    """
    Apply consistent layout styling to a figure with theme support.
    
    Args:
        fig: Plotly figure.
        title: Optional title.
        
    Returns:
        Styled figure.
    """
    colors = get_chart_colors()
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(color=colors['title_color'], size=CHART_LAYOUT["title_font_size"])
        ) if title else None,
        font=dict(
            family=CHART_LAYOUT["font_family"],
            color=colors['font_color']
        ),
        legend=dict(
            font=dict(size=CHART_LAYOUT["legend_font_size"], color=colors['font_color']),
            bgcolor='rgba(0,0,0,0)',
        ),
        margin=CHART_LAYOUT["margin"],
        height=CHART_LAYOUT["height"],
        paper_bgcolor=colors['paper_bgcolor'],
        plot_bgcolor=colors['plot_bgcolor'],
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=colors['hover_bgcolor'],
            font_color=colors['font_color'],
        ),
    )
    
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=colors['grid_color'],
        showline=True,
        linewidth=1,
        linecolor=colors['line_color'],
        tickfont=dict(color=colors['tick_color'], size=12),
        title_font=dict(color=colors['axis_title_color'], size=13),
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=colors['grid_color'],
        showline=True,
        linewidth=1,
        linecolor=colors['line_color'],
        tickformat=",",
        tickfont=dict(color=colors['tick_color'], size=12),
        title_font=dict(color=colors['axis_title_color'], size=13),
    )
    
    return fig


def create_price_trend_chart(
    df: pd.DataFrame,
    commodity: str,
    regions: List[str],
    show_ma7: bool = False,
    show_ma14: bool = False,
    date_range: Tuple[datetime, datetime] = None
) -> go.Figure:
    """
    Create a price trend line chart for one commodity across multiple regions.
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        regions: List of regions to show.
        show_ma7: Whether to show 7-day moving average.
        show_ma14: Whether to show 14-day moving average.
        date_range: Optional (start, end) date tuple.
        
    Returns:
        Plotly figure.
    """
    fig = go.Figure()
    
    mask = df[COL_COMMODITY] == commodity
    data = df[mask].dropna(subset=[COL_PRICE])
    
    if date_range:
        data = data[
            (data[COL_DATE] >= pd.Timestamp(date_range[0])) &
            (data[COL_DATE] <= pd.Timestamp(date_range[1]))
        ]
    
    for i, region in enumerate(regions):
        region_data = data[data[COL_REGION] == region].sort_values(COL_DATE)
        
        if region_data.empty:
            continue
        
        color = CHART_COLORS[i % len(CHART_COLORS)]
        
        # Main price line
        fig.add_trace(go.Scatter(
            x=region_data[COL_DATE],
            y=region_data[COL_PRICE],
            mode='lines',
            name=region,
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{region}</b><br>" +
                         "Date: %{x|%d %b %Y}<br>" +
                         "Price: Rp %{y:,.0f}<extra></extra>"
        ))
        
        # Moving averages
        if show_ma7 and len(region_data) >= 7:
            ma7 = region_data[COL_PRICE].rolling(7).mean()
            fig.add_trace(go.Scatter(
                x=region_data[COL_DATE],
                y=ma7,
                mode='lines',
                name=f'{region} MA7',
                line=dict(color=color, width=1, dash='dot'),
                hovertemplate=f"<b>{region} MA7</b><br>" +
                             "Date: %{x|%d %b %Y}<br>" +
                             "MA7: Rp %{y:,.0f}<extra></extra>"
            ))
        
        if show_ma14 and len(region_data) >= 14:
            ma14 = region_data[COL_PRICE].rolling(14).mean()
            fig.add_trace(go.Scatter(
                x=region_data[COL_DATE],
                y=ma14,
                mode='lines',
                name=f'{region} MA14',
                line=dict(color=color, width=1, dash='dash'),
                hovertemplate=f"<b>{region} MA14</b><br>" +
                             "Date: %{x|%d %b %Y}<br>" +
                             "MA14: Rp %{y:,.0f}<extra></extra>"
            ))
    
    fig.update_layout(
        xaxis_title="Tanggal",
        yaxis_title=LABELS["price_unit"],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )
    
    return apply_default_layout(fig, f"Tren Harga: {commodity}")


def create_price_trend_with_anomalies(
    df: pd.DataFrame,
    anomalies: pd.DataFrame,
    commodity: str,
    region: str,
    date_range: Tuple[datetime, datetime] = None
) -> go.Figure:
    """
    Create price trend chart with anomaly markers.
    
    Args:
        df: Main price DataFrame.
        anomalies: DataFrame with anomaly markers.
        commodity: Commodity name.
        region: Region name.
        date_range: Optional date range.
        
    Returns:
        Plotly figure.
    """
    fig = go.Figure()
    
    data = anomalies.copy()
    
    if date_range:
        data = data[
            (data[COL_DATE] >= pd.Timestamp(date_range[0])) &
            (data[COL_DATE] <= pd.Timestamp(date_range[1]))
        ]
    
    if data.empty:
        return fig
    
    # Main price line
    fig.add_trace(go.Scatter(
        x=data[COL_DATE],
        y=data[COL_PRICE],
        mode='lines',
        name='Price',
        line=dict(color=CHART_COLORS[0], width=2),
    ))
    
    # Anomaly markers
    anomaly_points = data[data['is_anomaly'] == True]
    if not anomaly_points.empty:
        fig.add_trace(go.Scatter(
            x=anomaly_points[COL_DATE],
            y=anomaly_points[COL_PRICE],
            mode='markers',
            name='Anomaly',
            marker=dict(
                color=KPI_NEGATIVE_COLOR,
                size=12,
                symbol='circle-open',
                line=dict(width=2)
            ),
            hovertemplate="<b>Anomaly</b><br>" +
                         "Date: %{x|%d %b %Y}<br>" +
                         "Price: Rp %{y:,.0f}<br>" +
                         f"Change: %{{customdata:.1f}}%<extra></extra>",
            customdata=anomaly_points['daily_change_pct']
        ))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=LABELS["price_unit"],
    )
    
    return apply_default_layout(fig, f"Anomali Harga: {commodity} - {region}")


def create_top_movers_bar(
    gainers: pd.DataFrame,
    losers: pd.DataFrame,
) -> go.Figure:
    """
    Create horizontal bar chart for top movers.
    
    Args:
        gainers: DataFrame with top gainers.
        losers: DataFrame with top losers.
        
    Returns:
        Plotly figure with subplots.
    """
    colors = get_chart_colors()
    is_dark = st.session_state.get('theme_mode', 'light') == 'dark'
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(LABELS["top_movers_up"], LABELS["top_movers_down"]),
        horizontal_spacing=0.15
    )
    
    # Text color for bar labels
    bar_text_color = "#FFFFFF" if is_dark else "#1A1A1A"
    
    # Top gainers - bright green
    if not gainers.empty:
        fig.add_trace(go.Bar(
            y=gainers[COL_REGION],
            x=gainers['change_pct'],
            orientation='h',
            marker_color="#16A34A",
            marker_line_color="#166534",
            marker_line_width=2,
            text=gainers['change_pct'].apply(lambda x: f"+{x:.1f}%"),
            textposition='outside',
            textfont=dict(color=bar_text_color, size=12, family="Arial Black"),
            hovertemplate="<b>%{y}</b><br>Perubahan: +%{x:.1f}%<extra></extra>",
            width=0.7,
        ), row=1, col=1)
    
    # Top losers - bright red
    if not losers.empty:
        fig.add_trace(go.Bar(
            y=losers[COL_REGION],
            x=losers['change_pct'],
            orientation='h',
            marker_color="#DC2626",
            marker_line_color="#991B1B",
            marker_line_width=2,
            text=losers['change_pct'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside',
            textfont=dict(color=bar_text_color, size=12, family="Arial Black"),
            hovertemplate="<b>%{y}</b><br>Perubahan: %{x:.1f}%<extra></extra>",
            width=0.7,
        ), row=1, col=2)
    
    fig.update_layout(
        showlegend=False,
        height=400,
        bargap=0.3,
    )
    
    # Update subplot title colors
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(color=colors['title_color'], size=14, family="Arial Black")
    
    fig.update_yaxes(autorange="reversed")
    
    return apply_default_layout(fig)


def create_regional_ranking_bar(
    highest: pd.DataFrame,
    lowest: pd.DataFrame,
) -> go.Figure:
    """
    Create horizontal bar chart for regional price ranking.
    
    Args:
        highest: DataFrame with highest priced regions.
        lowest: DataFrame with lowest priced regions.
        
    Returns:
        Plotly figure with subplots.
    """
    colors = get_chart_colors()
    is_dark = st.session_state.get('theme_mode', 'light') == 'dark'
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(LABELS["highest_prices"], LABELS["lowest_prices"]),
        horizontal_spacing=0.15
    )
    
    # High contrast bar colors - always visible
    bar_color_high = "#2563EB"  # Bright Blue
    bar_color_low = "#16A34A"   # Bright Green
    
    # Text color for bar labels - always dark for readability
    bar_text_color = "#FFFFFF" if is_dark else "#1A1A1A"
    
    # Highest prices
    if not highest.empty:
        fig.add_trace(go.Bar(
            y=highest[COL_REGION],
            x=highest[COL_PRICE],
            orientation='h',
            marker_color=bar_color_high,
            marker_line_color="#1E40AF",
            marker_line_width=2,
            text=highest[COL_PRICE].apply(lambda x: f"Rp {x:,.0f}"),
            textposition='outside',
            textfont=dict(color=bar_text_color, size=12, family="Arial Black"),
            hovertemplate="<b>%{y}</b><br>Harga: Rp %{x:,.0f}<extra></extra>",
            width=0.7,
        ), row=1, col=1)
    
    # Lowest prices
    if not lowest.empty:
        fig.add_trace(go.Bar(
            y=lowest[COL_REGION],
            x=lowest[COL_PRICE],
            orientation='h',
            marker_color=bar_color_low,
            marker_line_color="#166534",
            marker_line_width=2,
            text=lowest[COL_PRICE].apply(lambda x: f"Rp {x:,.0f}"),
            textposition='outside',
            textfont=dict(color=bar_text_color, size=12, family="Arial Black"),
            hovertemplate="<b>%{y}</b><br>Harga: Rp %{x:,.0f}<extra></extra>",
            width=0.7,
        ), row=1, col=2)
    
    fig.update_layout(
        showlegend=False,
        height=450,
        bargap=0.3,
    )
    
    # Update subplot title colors
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(color=colors['title_color'], size=14, family="Arial Black")
    
    fig.update_yaxes(autorange="reversed")
    
    return apply_default_layout(fig)


def create_volatility_scatter(
    data: pd.DataFrame,
) -> go.Figure:
    """
    Create scatter plot of average price vs volatility.
    
    Args:
        data: DataFrame with region, avg_price, volatility columns.
        
    Returns:
        Plotly figure.
    """
    if data.empty:
        return go.Figure()
    
    fig = px.scatter(
        data,
        x='avg_price',
        y='volatility',
        text=COL_REGION,
        color='volatility',
        color_continuous_scale='RdYlGn_r',
    )
    
    fig.update_traces(
        textposition='top center',
        marker=dict(size=12),
        hovertemplate="<b>%{text}</b><br>" +
                     "Average Price: Rp %{x:,.0f}<br>" +
                     "Volatility: %{y:.2f}%<extra></extra>"
    )
    
    fig.update_layout(
        xaxis_title="Average Price (Rp)",
        yaxis_title="Volatility (%)",
        coloraxis_colorbar_title="Volatility",
    )
    
    return apply_default_layout(fig, LABELS["price_vs_volatility"])


def create_multi_commodity_chart(
    df: pd.DataFrame,
    commodities: List[str],
    region: str,
    date_range: Tuple[datetime, datetime] = None
) -> go.Figure:
    """
    Create multi-line chart comparing multiple commodities.
    
    Args:
        df: Canonical DataFrame.
        commodities: List of commodity names.
        region: Region to show.
        date_range: Optional date range.
        
    Returns:
        Plotly figure.
    """
    fig = go.Figure()
    
    for i, commodity in enumerate(commodities):
        mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
        data = df[mask].dropna(subset=[COL_PRICE]).sort_values(COL_DATE)
        
        if date_range:
            data = data[
                (data[COL_DATE] >= pd.Timestamp(date_range[0])) &
                (data[COL_DATE] <= pd.Timestamp(date_range[1]))
            ]
        
        if data.empty:
            continue
        
        # Normalize to percentage of first value for comparison
        first_price = data[COL_PRICE].iloc[0]
        normalized = 100 * data[COL_PRICE] / first_price
        
        color = CHART_COLORS[i % len(CHART_COLORS)]
        
        fig.add_trace(go.Scatter(
            x=data[COL_DATE],
            y=normalized,
            mode='lines',
            name=commodity,
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{commodity}</b><br>" +
                         "Date: %{x|%d %b %Y}<br>" +
                         "Index: %{y:.1f}<extra></extra>"
        ))
    
    fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price Index (start = 100)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )
    
    return apply_default_layout(fig, f"Perbandingan Komoditas - {region}")


def create_price_heatmap(
    df: pd.DataFrame,
    commodities: List[str],
    region: str,
    resample: str = 'D'
) -> go.Figure:
    """
    Create heatmap of daily/weekly price changes.
    
    Args:
        df: Canonical DataFrame.
        commodities: List of commodities.
        region: Region name.
        resample: 'D' for daily (needs 1 week), 'W' for weekly (needs 1 month).
        
    Returns:
        Plotly figure.
    """
    heatmap_data = []
    
    for commodity in commodities:
        mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
        data = df[mask].dropna(subset=[COL_PRICE]).copy()
        
        if data.empty:
            continue
        
        data = data.set_index(COL_DATE).sort_index()
        
        if resample == 'D':
            # Daily: use raw data
            resampled = data[COL_PRICE]
        else:
            # Weekly
            resampled = data[COL_PRICE].resample(resample).last()
        
        pct_changes = resampled.pct_change() * 100
        
        for date, change in pct_changes.items():
            if pd.notna(change):
                date_str = date.strftime('%m/%d')
                heatmap_data.append({
                    'Commodity': commodity,
                    'Period': date_str,
                    'Change': change
                })
    
    if not heatmap_data:
        return go.Figure()
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    # Pivot for heatmap
    pivot = heatmap_df.pivot(index='Commodity', columns='Period', values='Change')
    
    # Limit columns
    max_cols = 14 if resample == 'D' else 8
    if pivot.shape[1] > max_cols:
        pivot = pivot.iloc[:, -max_cols:]
    
    colors = get_chart_colors()
    period_label = "Harian" if resample == 'D' else "Mingguan"
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        zmid=0,
        text=np.round(pivot.values, 1),
        texttemplate="%{text}%",
        textfont={"size": 10, "color": colors['font_color']},
        hovertemplate="Komoditas: %{y}<br>" +
                     "Periode: %{x}<br>" +
                     "Perubahan: %{z:.1f}%<extra></extra>",
        colorbar=dict(
            title=dict(text="Perubahan (%)", font=dict(color=colors['font_color'])),
            tickfont=dict(color=colors['axis_color']),
        )
    ))
    
    fig.update_layout(
        xaxis_title=f"Tanggal ({period_label})",
        yaxis_title="Komoditas",
    )
    
    return apply_default_layout(fig, f"{LABELS['price_heatmap']} ({period_label})")


def create_small_multiples(
    df: pd.DataFrame,
    commodities: List[str],
    region: str,
    date_range: Tuple[datetime, datetime] = None
) -> go.Figure:
    """
    Create small multiple charts for comparing commodities.
    
    Args:
        df: Canonical DataFrame.
        commodities: List of commodities (max 9).
        region: Region name.
        date_range: Optional date range.
        
    Returns:
        Plotly figure with subplots.
    """
    n_commodities = min(len(commodities), 9)
    commodities = commodities[:n_commodities]
    
    # Calculate grid dimensions
    if n_commodities <= 3:
        rows, cols = 1, n_commodities
    elif n_commodities <= 6:
        rows, cols = 2, 3
    else:
        rows, cols = 3, 3
    
    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=commodities,
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )
    
    for i, commodity in enumerate(commodities):
        row = i // cols + 1
        col = i % cols + 1
        
        mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
        data = df[mask].dropna(subset=[COL_PRICE]).sort_values(COL_DATE)
        
        if date_range:
            data = data[
                (data[COL_DATE] >= pd.Timestamp(date_range[0])) &
                (data[COL_DATE] <= pd.Timestamp(date_range[1]))
            ]
        
        if data.empty:
            continue
        
        color = CHART_COLORS[i % len(CHART_COLORS)]
        
        fig.add_trace(go.Scatter(
            x=data[COL_DATE],
            y=data[COL_PRICE],
            mode='lines',
            line=dict(color=color, width=1.5),
            showlegend=False,
            hovertemplate=f"<b>{commodity}</b><br>" +
                         "Date: %{x|%d %b %Y}<br>" +
                         "Price: Rp %{y:,.0f}<extra></extra>"
        ), row=row, col=col)
    
    fig.update_layout(
        height=300 * rows,
    )
    
    fig.update_yaxes(tickformat=",")
    
    return apply_default_layout(fig, f"Perbandingan Komoditas - {region}")


def format_kpi_value(value: float, is_currency: bool = True) -> str:
    """
    Format a KPI value for display.
    
    Args:
        value: Numeric value.
        is_currency: Whether to format as currency.
        
    Returns:
        Formatted string.
    """
    if value is None:
        return "-"
    
    if is_currency:
        return f"Rp {value:,.0f}"
    else:
        return f"{value:,.2f}"


def format_change_value(abs_change: float, pct_change: float) -> Tuple[str, str]:
    """
    Format price change values for display.
    
    Args:
        abs_change: Absolute change value.
        pct_change: Percentage change value.
        
    Returns:
        Tuple of (formatted_string, color).
    """
    if abs_change is None or pct_change is None:
        return "-", KPI_NEUTRAL_COLOR
    
    sign = "+" if abs_change >= 0 else ""
    text = f"{sign}Rp {abs_change:,.0f} ({sign}{pct_change:.1f}%)"
    
    if pct_change > 0:
        color = KPI_NEGATIVE_COLOR  # Price increase is concerning
    elif pct_change < 0:
        color = KPI_POSITIVE_COLOR  # Price decrease is good for consumers
    else:
        color = KPI_NEUTRAL_COLOR
    
    return text, color

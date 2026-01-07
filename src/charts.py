"""
charts.py - Plotly chart factory module.

Creates all visualization components for the dashboard.
Uses consistent styling defined in constants.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Optional, Dict, Tuple
from datetime import datetime

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


def apply_default_layout(fig: go.Figure, title: str = None) -> go.Figure:
    """
    Apply consistent layout styling to a figure.
    
    Args:
        fig: Plotly figure.
        title: Optional title.
        
    Returns:
        Styled figure.
    """
    fig.update_layout(
        title=title,
        font_family=CHART_LAYOUT["font_family"],
        title_font_size=CHART_LAYOUT["title_font_size"],
        legend_font_size=CHART_LAYOUT["legend_font_size"],
        margin=CHART_LAYOUT["margin"],
        height=CHART_LAYOUT["height"],
        paper_bgcolor=CHART_LAYOUT["paper_bgcolor"],
        plot_bgcolor=CHART_LAYOUT["plot_bgcolor"],
        hovermode="x unified",
    )
    
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128,128,128,0.2)",
        showline=True,
        linewidth=1,
        linecolor="rgba(128,128,128,0.3)",
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128,128,128,0.2)",
        showline=True,
        linewidth=1,
        linecolor="rgba(128,128,128,0.3)",
        tickformat=",",
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
        xaxis_title="Date",
        yaxis_title=LABELS["price_unit"],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )
    
    return apply_default_layout(fig, f"Price Trend: {commodity}")


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
    
    return apply_default_layout(fig, f"Price Anomalies: {commodity} - {region}")


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
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(LABELS["top_movers_up"], LABELS["top_movers_down"]),
        horizontal_spacing=0.15
    )
    
    # Top gainers
    if not gainers.empty:
        fig.add_trace(go.Bar(
            y=gainers[COL_REGION],
            x=gainers['change_pct'],
            orientation='h',
            marker_color=KPI_POSITIVE_COLOR,
            text=gainers['change_pct'].apply(lambda x: f"+{x:.1f}%"),
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>Change: +%{x:.1f}%<extra></extra>"
        ), row=1, col=1)
    
    # Top losers
    if not losers.empty:
        fig.add_trace(go.Bar(
            y=losers[COL_REGION],
            x=losers['change_pct'],
            orientation='h',
            marker_color=KPI_NEGATIVE_COLOR,
            text=losers['change_pct'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>Change: %{x:.1f}%<extra></extra>"
        ), row=1, col=2)
    
    fig.update_layout(
        showlegend=False,
        height=350,
    )
    
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
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(LABELS["highest_prices"], LABELS["lowest_prices"]),
        horizontal_spacing=0.15
    )
    
    # Highest prices
    if not highest.empty:
        fig.add_trace(go.Bar(
            y=highest[COL_REGION],
            x=highest[COL_PRICE],
            orientation='h',
            marker_color=CHART_COLORS[0],
            text=highest[COL_PRICE].apply(lambda x: f"Rp {x:,.0f}"),
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>Price: Rp %{x:,.0f}<extra></extra>"
        ), row=1, col=1)
    
    # Lowest prices
    if not lowest.empty:
        fig.add_trace(go.Bar(
            y=lowest[COL_REGION],
            x=lowest[COL_PRICE],
            orientation='h',
            marker_color=CHART_COLORS[2],
            text=lowest[COL_PRICE].apply(lambda x: f"Rp {x:,.0f}"),
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>Price: Rp %{x:,.0f}<extra></extra>"
        ), row=1, col=2)
    
    fig.update_layout(
        showlegend=False,
        height=400,
    )
    
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
    
    return apply_default_layout(fig, f"Commodity Comparison - {region}")


def create_price_heatmap(
    df: pd.DataFrame,
    commodities: List[str],
    region: str,
    resample: str = 'W'
) -> go.Figure:
    """
    Create heatmap of weekly/monthly price changes.
    
    Args:
        df: Canonical DataFrame.
        commodities: List of commodities.
        region: Region name.
        resample: Resample frequency ('W' for weekly, 'M' for monthly).
        
    Returns:
        Plotly figure.
    """
    # Prepare data for heatmap
    heatmap_data = []
    
    for commodity in commodities:
        mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
        data = df[mask].dropna(subset=[COL_PRICE]).copy()
        
        if data.empty:
            continue
        
        data = data.set_index(COL_DATE).sort_index()
        resampled = data[COL_PRICE].resample(resample).last()
        pct_changes = resampled.pct_change() * 100
        
        for date, change in pct_changes.items():
            if pd.notna(change):
                heatmap_data.append({
                    'Commodity': commodity,
                    'Period': date.strftime('%Y-%m-%d'),
                    'Change': change
                })
    
    if not heatmap_data:
        return go.Figure()
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    # Pivot for heatmap
    pivot = heatmap_df.pivot(index='Commodity', columns='Period', values='Change')
    
    # Limit columns if too many
    if pivot.shape[1] > 20:
        pivot = pivot.iloc[:, -20:]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        zmid=0,
        text=np.round(pivot.values, 1),
        texttemplate="%{text}%",
        textfont={"size": 10},
        hovertemplate="Commodity: %{y}<br>" +
                     "Period: %{x}<br>" +
                     "Change: %{z:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        xaxis_title="Period",
        yaxis_title="Commodity",
    )
    
    return apply_default_layout(fig, LABELS["price_heatmap"])


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
    
    return apply_default_layout(fig, f"Commodity Comparison - {region}")


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

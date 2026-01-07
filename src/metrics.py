"""
metrics.py - Metrics and KPI computation module.

Computes all derived metrics used in the dashboard:
- Latest prices
- Rolling changes (7-day, 30-day)
- Trend status
- Volatility
- Anomaly detection
- Top movers
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from .constants import (
    COL_DATE,
    COL_COMMODITY,
    COL_REGION,
    COL_PRICE,
    CANONICAL_COLUMNS,
    ANOMALY_THRESHOLD_PCT,
    ANOMALY_STD_MULTIPLIER,
    TREND_RISING_THRESHOLD,
    TREND_FALLING_THRESHOLD,
    TOP_MOVERS_COUNT,
)


def get_latest_price(
    df: pd.DataFrame,
    commodity: str,
    region: str
) -> Optional[float]:
    """
    Get the latest available price for a commodity/region combination.
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        region: Region name.
        
    Returns:
        Latest price value, or None if not found.
    """
    mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
    subset = df[mask].dropna(subset=[COL_PRICE])
    
    if subset.empty:
        return None
    
    latest = subset.loc[subset[COL_DATE].idxmax()]
    return float(latest[COL_PRICE])


def get_price_at_date(
    df: pd.DataFrame,
    commodity: str,
    region: str,
    target_date: datetime
) -> Optional[float]:
    """
    Get the price closest to a target date.
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        region: Region name.
        target_date: Target date.
        
    Returns:
        Price value closest to target date, or None if not found.
    """
    mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
    subset = df[mask].dropna(subset=[COL_PRICE])
    
    if subset.empty:
        return None
    
    # Find closest date
    subset = subset.copy()
    subset['date_diff'] = abs(subset[COL_DATE] - pd.Timestamp(target_date))
    closest = subset.loc[subset['date_diff'].idxmin()]
    
    # Only return if within 3 days
    if closest['date_diff'] <= timedelta(days=3):
        return float(closest[COL_PRICE])
    
    return None


def calculate_price_change(
    df: pd.DataFrame,
    commodity: str,
    region: str,
    days: int = 7
) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculate price change over specified number of days.
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        region: Region name.
        days: Number of days to look back.
        
    Returns:
        Tuple of (absolute_change, percentage_change), or (None, None) if unavailable.
    """
    mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
    subset = df[mask].dropna(subset=[COL_PRICE]).sort_values(COL_DATE)
    
    if len(subset) < 2:
        return None, None
    
    latest_date = subset[COL_DATE].max()
    target_date = latest_date - timedelta(days=days)
    
    # Get latest price
    latest_price = float(subset.iloc[-1][COL_PRICE])
    
    # Get price at target date (or closest before)
    earlier = subset[subset[COL_DATE] <= target_date]
    if earlier.empty:
        # Use earliest available
        earlier = subset
    
    earlier_price = float(earlier.iloc[-1][COL_PRICE])
    
    if earlier_price == 0:
        return None, None
    
    abs_change = latest_price - earlier_price
    pct_change = 100 * abs_change / earlier_price
    
    return round(abs_change, 2), round(pct_change, 2)


def determine_trend_status(pct_change_7d: Optional[float]) -> str:
    """
    Determine trend status based on 7-day percentage change.
    
    Args:
        pct_change_7d: 7-day percentage change.
        
    Returns:
        Trend status string: "rising", "falling", or "stable".
    """
    if pct_change_7d is None:
        return "stable"
    
    if pct_change_7d > TREND_RISING_THRESHOLD:
        return "rising"
    elif pct_change_7d < TREND_FALLING_THRESHOLD:
        return "falling"
    else:
        return "stable"


def calculate_volatility(
    df: pd.DataFrame,
    commodity: str,
    region: str,
    days: int = 30
) -> Optional[float]:
    """
    Calculate price volatility (standard deviation of daily returns).
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        region: Region name.
        days: Number of days to consider.
        
    Returns:
        Volatility value (std of % changes), or None if unavailable.
    """
    mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
    subset = df[mask].dropna(subset=[COL_PRICE]).sort_values(COL_DATE)
    
    if len(subset) < 5:
        return None
    
    # Filter to recent days
    latest_date = subset[COL_DATE].max()
    cutoff = latest_date - timedelta(days=days)
    recent = subset[subset[COL_DATE] >= cutoff]
    
    if len(recent) < 5:
        return None
    
    # Calculate daily returns
    returns = recent[COL_PRICE].pct_change().dropna()
    
    if len(returns) < 3:
        return None
    
    volatility = returns.std() * 100  # Convert to percentage
    return round(volatility, 2)


def get_kpi_summary(
    df: pd.DataFrame,
    commodity: str,
    region: str
) -> Dict:
    """
    Get all KPI metrics for a commodity/region combination.
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        region: Region name.
        
    Returns:
        Dictionary with all KPI values.
    """
    latest_price = get_latest_price(df, commodity, region)
    abs_7d, pct_7d = calculate_price_change(df, commodity, region, 7)
    abs_30d, pct_30d = calculate_price_change(df, commodity, region, 30)
    trend = determine_trend_status(pct_7d)
    volatility = calculate_volatility(df, commodity, region, 30)
    
    return {
        "latest_price": latest_price,
        "change_7d_abs": abs_7d,
        "change_7d_pct": pct_7d,
        "change_30d_abs": abs_30d,
        "change_30d_pct": pct_30d,
        "trend_status": trend,
        "volatility": volatility,
    }


def calculate_moving_average(
    df: pd.DataFrame,
    commodity: str,
    region: str,
    window: int = 7
) -> pd.DataFrame:
    """
    Calculate moving average for price series.
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        region: Region name.
        window: Moving average window size.
        
    Returns:
        DataFrame with original data plus MA column.
    """
    mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
    subset = df[mask].dropna(subset=[COL_PRICE]).sort_values(COL_DATE).copy()
    
    if len(subset) < window:
        subset[f'MA{window}'] = np.nan
    else:
        subset[f'MA{window}'] = subset[COL_PRICE].rolling(window=window).mean()
    
    return subset


def detect_anomalies(
    df: pd.DataFrame,
    commodity: str,
    region: str,
    method: str = "threshold"
) -> pd.DataFrame:
    """
    Detect price anomalies (unusual daily changes).
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        region: Region name.
        method: Detection method - "threshold" (>10%) or "std" (>2 std).
        
    Returns:
        DataFrame with anomaly markers.
    """
    mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
    subset = df[mask].dropna(subset=[COL_PRICE]).sort_values(COL_DATE).copy()
    
    if len(subset) < 3:
        subset['daily_change_pct'] = np.nan
        subset['is_anomaly'] = False
        return subset
    
    # Calculate daily percentage change
    subset['daily_change_pct'] = subset[COL_PRICE].pct_change() * 100
    
    if method == "threshold":
        # Anomaly if absolute change > threshold
        subset['is_anomaly'] = abs(subset['daily_change_pct']) > ANOMALY_THRESHOLD_PCT
    else:
        # Anomaly if change > 2 standard deviations
        mean_change = subset['daily_change_pct'].mean()
        std_change = subset['daily_change_pct'].std()
        threshold = ANOMALY_STD_MULTIPLIER * std_change
        subset['is_anomaly'] = abs(subset['daily_change_pct'] - mean_change) > threshold
    
    return subset


def get_top_movers(
    df: pd.DataFrame,
    commodity: str,
    days: int = 7,
    top_n: int = TOP_MOVERS_COUNT
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Get top movers (regions with highest/lowest price changes).
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        days: Number of days to look back.
        top_n: Number of top movers to return.
        
    Returns:
        Tuple of (top_gainers_df, top_losers_df).
    """
    mask = df[COL_COMMODITY] == commodity
    subset = df[mask].dropna(subset=[COL_PRICE])
    
    if subset.empty:
        empty_df = pd.DataFrame(columns=[COL_REGION, 'change_pct'])
        return empty_df, empty_df
    
    regions = subset[COL_REGION].unique()
    changes = []
    
    for region in regions:
        _, pct_change = calculate_price_change(df, commodity, region, days)
        if pct_change is not None:
            changes.append({
                COL_REGION: region,
                'change_pct': pct_change
            })
    
    if not changes:
        empty_df = pd.DataFrame(columns=[COL_REGION, 'change_pct'])
        return empty_df, empty_df
    
    changes_df = pd.DataFrame(changes)
    
    # Top gainers (highest positive change)
    top_gainers = changes_df.nlargest(top_n, 'change_pct')
    
    # Top losers (largest negative change)
    top_losers = changes_df.nsmallest(top_n, 'change_pct')
    
    return top_gainers.reset_index(drop=True), top_losers.reset_index(drop=True)


def get_regional_ranking(
    df: pd.DataFrame,
    commodity: str,
    date_range: Tuple[datetime, datetime] = None,
    top_n: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Get regional price ranking (highest and lowest priced regions).
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        date_range: Optional (start, end) date tuple.
        top_n: Number of regions to return.
        
    Returns:
        Tuple of (highest_prices_df, lowest_prices_df).
    """
    mask = df[COL_COMMODITY] == commodity
    subset = df[mask].dropna(subset=[COL_PRICE])
    
    if date_range:
        subset = subset[
            (subset[COL_DATE] >= pd.Timestamp(date_range[0])) &
            (subset[COL_DATE] <= pd.Timestamp(date_range[1]))
        ]
    
    if subset.empty:
        empty_df = pd.DataFrame(columns=[COL_REGION, COL_PRICE])
        return empty_df, empty_df
    
    # Get latest price for each region
    latest_date = subset[COL_DATE].max()
    latest_prices = subset[subset[COL_DATE] == latest_date][[COL_REGION, COL_PRICE]]
    
    # If no data for latest date, get most recent per region
    if latest_prices.empty:
        idx = subset.groupby(COL_REGION)[COL_DATE].idxmax()
        latest_prices = subset.loc[idx][[COL_REGION, COL_PRICE]]
    
    # Remove duplicates (keep first)
    latest_prices = latest_prices.drop_duplicates(subset=[COL_REGION])
    
    # Highest prices
    highest = latest_prices.nlargest(top_n, COL_PRICE).reset_index(drop=True)
    
    # Lowest prices
    lowest = latest_prices.nsmallest(top_n, COL_PRICE).reset_index(drop=True)
    
    return highest, lowest


def get_regional_volatility_comparison(
    df: pd.DataFrame,
    commodity: str,
    days: int = 30
) -> pd.DataFrame:
    """
    Get average price vs volatility for all regions.
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        days: Number of days for volatility calculation.
        
    Returns:
        DataFrame with region, avg_price, and volatility columns.
    """
    mask = df[COL_COMMODITY] == commodity
    subset = df[mask].dropna(subset=[COL_PRICE])
    
    if subset.empty:
        return pd.DataFrame(columns=[COL_REGION, 'avg_price', 'volatility'])
    
    regions = subset[COL_REGION].unique()
    results = []
    
    for region in regions:
        region_data = subset[subset[COL_REGION] == region]
        
        # Filter to recent days
        latest_date = region_data[COL_DATE].max()
        cutoff = latest_date - timedelta(days=days)
        recent = region_data[region_data[COL_DATE] >= cutoff]
        
        if len(recent) < 5:
            continue
        
        avg_price = recent[COL_PRICE].mean()
        volatility = calculate_volatility(df, commodity, region, days)
        
        if volatility is not None:
            results.append({
                COL_REGION: region,
                'avg_price': round(avg_price, 2),
                'volatility': volatility
            })
    
    return pd.DataFrame(results)


def resample_to_weekly(
    df: pd.DataFrame,
    commodity: str,
    region: str
) -> pd.DataFrame:
    """
    Resample daily data to weekly averages.
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        region: Region name.
        
    Returns:
        DataFrame with weekly aggregated data.
    """
    mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
    subset = df[mask].dropna(subset=[COL_PRICE]).copy()
    
    if subset.empty:
        return subset
    
    subset = subset.set_index(COL_DATE)
    weekly = subset[[COL_PRICE]].resample('W').mean().reset_index()
    weekly[COL_COMMODITY] = commodity
    weekly[COL_REGION] = region
    
    return weekly[CANONICAL_COLUMNS]


def generate_auto_insights(
    df: pd.DataFrame,
    commodity: str,
    region: str
) -> List[str]:
    """
    Generate automatic text insights based on data.
    
    Args:
        df: Canonical DataFrame.
        commodity: Commodity name.
        region: Region name.
        
    Returns:
        List of insight strings.
    """
    insights = []
    
    kpi = get_kpi_summary(df, commodity, region)
    
    # Price change insight
    if kpi['change_7d_pct'] is not None:
        direction = "increased" if kpi['change_7d_pct'] > 0 else "decreased"
        insights.append(
            f"Price {direction} {abs(kpi['change_7d_pct']):.1f}% in the last 7 days."
        )
    
    # Peak price insight
    mask = (df[COL_COMMODITY] == commodity) & (df[COL_REGION] == region)
    subset = df[mask].dropna(subset=[COL_PRICE])
    
    if not subset.empty:
        peak_idx = subset[COL_PRICE].idxmax()
        peak_row = subset.loc[peak_idx]
        insights.append(
            f"Peak price Rp {peak_row[COL_PRICE]:,.0f} on {peak_row[COL_DATE].strftime('%d %b %Y')}."
        )
        
        # Latest price vs average
        avg_price = subset[COL_PRICE].mean()
        latest = kpi['latest_price']
        if latest and avg_price:
            diff_pct = 100 * (latest - avg_price) / avg_price
            position = "above" if diff_pct > 0 else "below"
            insights.append(
                f"Current price is {abs(diff_pct):.1f}% {position} average."
            )
    
    # Volatility insight
    if kpi['volatility'] is not None:
        if kpi['volatility'] > 3:
            insights.append(f"High volatility ({kpi['volatility']:.1f}%) - prices are fluctuating significantly.")
        elif kpi['volatility'] < 1:
            insights.append(f"Low volatility ({kpi['volatility']:.1f}%) - prices are relatively stable.")
    
    return insights


def get_commodity_summary(
    df: pd.DataFrame,
    commodities: List[str],
    region: str
) -> pd.DataFrame:
    """
    Get summary statistics for multiple commodities.
    
    Args:
        df: Canonical DataFrame.
        commodities: List of commodity names.
        region: Region name to analyze.
        
    Returns:
        DataFrame with summary statistics per commodity.
    """
    summaries = []
    
    for commodity in commodities:
        kpi = get_kpi_summary(df, commodity, region)
        
        summaries.append({
            COL_COMMODITY: commodity,
            'Latest Price': kpi['latest_price'],
            '7-Day Change (%)': kpi['change_7d_pct'],
            '30-Day Change (%)': kpi['change_30d_pct'],
            'Volatility (%)': kpi['volatility'],
            'Status': kpi['trend_status'],
        })
    
    return pd.DataFrame(summaries)

"""
preprocess.py - Data cleaning and transformation module.

Handles:
- Date parsing with multiple format support
- Price parsing (removes commas, currency symbols)
- Wide-to-long format conversion
- Data validation and canonicalization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
import re

from .constants import (
    COL_DATE,
    COL_COMMODITY,
    COL_REGION,
    COL_PRICE,
    CANONICAL_COLUMNS,
    DEFAULT_REGION,
    DATE_COLUMN_PATTERNS,
    NON_REGION_COLUMNS,
    DATE_FORMATS,
)


def identify_date_column(df: pd.DataFrame) -> Optional[str]:
    """
    Identify the date column in a DataFrame.
    
    Uses pattern matching on column names.
    
    Args:
        df: Input DataFrame.
        
    Returns:
        Name of the date column, or None if not found.
    """
    columns_lower = {col.lower(): col for col in df.columns}
    
    for pattern in DATE_COLUMN_PATTERNS:
        if pattern in columns_lower:
            return columns_lower[pattern]
    
    # Check if first column looks like dates
    first_col = df.columns[0]
    try:
        pd.to_datetime(df[first_col].dropna().head(10))
        return first_col
    except:
        pass
    
    return None


def parse_date_column(series: pd.Series) -> pd.Series:
    """
    Parse a series to datetime with robust format detection.
    
    Args:
        series: Input series with date values.
        
    Returns:
        Series with datetime values.
    """
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    
    # Try pandas automatic parsing first
    try:
        return pd.to_datetime(series)
    except Exception:
        pass
    
    # Try each format explicitly
    for fmt in DATE_FORMATS:
        try:
            return pd.to_datetime(series, format=fmt)
        except Exception:
            continue
    
    # Try dayfirst=True (common in Indonesian data)
    try:
        return pd.to_datetime(series, dayfirst=True)
    except Exception:
        pass
    
    # Last resort: coerce errors
    return pd.to_datetime(series, errors="coerce")


def parse_price_value(value) -> float:
    """
    Parse a single price value, handling various formats.
    
    Args:
        value: Input value (string, int, float, or None).
        
    Returns:
        Float price value, or NaN if parsing fails.
    """
    if pd.isna(value):
        return np.nan
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove common currency symbols and formatting
        cleaned = value.strip()
        cleaned = re.sub(r'[Rp$€£¥,\s]', '', cleaned)
        cleaned = cleaned.replace('.', '').replace(',', '.')  # Handle European format
        
        # Handle negative values in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return np.nan
    
    return np.nan


def parse_price_column(series: pd.Series) -> pd.Series:
    """
    Parse a series of price values.
    
    Args:
        series: Input series with price values.
        
    Returns:
        Series with float price values.
    """
    return series.apply(parse_price_value)


def is_wide_format(df: pd.DataFrame, date_col: str) -> bool:
    """
    Determine if DataFrame is in wide format (regions as columns).
    
    Args:
        df: Input DataFrame.
        date_col: Name of the date column.
        
    Returns:
        True if wide format, False if long format.
    """
    other_cols = [col for col in df.columns if col != date_col]
    
    # If there are many columns that aren't standard schema columns, likely wide format
    non_schema_cols = [
        col for col in other_cols
        if col.lower() not in NON_REGION_COLUMNS
    ]
    
    # Wide format typically has multiple region columns with numeric data
    if len(non_schema_cols) >= 3:
        # Check if these columns contain numeric data
        numeric_cols = 0
        for col in non_schema_cols[:5]:  # Check first 5
            try:
                values = df[col].dropna().head(10)
                if len(values) > 0:
                    parsed = parse_price_column(values)
                    if parsed.notna().sum() > 0:
                        numeric_cols += 1
            except:
                continue
        
        return numeric_cols >= 3
    
    return False


def convert_wide_to_long(
    df: pd.DataFrame,
    date_col: str,
    commodity_name: str
) -> pd.DataFrame:
    """
    Convert wide format DataFrame to long format.
    
    Args:
        df: Input DataFrame in wide format.
        date_col: Name of the date column.
        commodity_name: Name of the commodity for this data.
        
    Returns:
        DataFrame in canonical long format.
    """
    # Identify region columns (all columns except date)
    region_cols = [col for col in df.columns if col != date_col]
    
    # Melt the DataFrame
    df_long = pd.melt(
        df,
        id_vars=[date_col],
        value_vars=region_cols,
        var_name=COL_REGION,
        value_name=COL_PRICE
    )
    
    # Rename date column
    df_long = df_long.rename(columns={date_col: COL_DATE})
    
    # Add commodity column
    df_long[COL_COMMODITY] = commodity_name
    
    # Parse date and price
    df_long[COL_DATE] = parse_date_column(df_long[COL_DATE])
    df_long[COL_PRICE] = parse_price_column(df_long[COL_PRICE])
    
    # Reorder columns
    df_long = df_long[CANONICAL_COLUMNS]
    
    return df_long


def convert_long_format(
    df: pd.DataFrame,
    date_col: str,
    commodity_name: str
) -> pd.DataFrame:
    """
    Standardize a DataFrame already in long format.
    
    Args:
        df: Input DataFrame in long format.
        date_col: Name of the date column.
        commodity_name: Name of the commodity.
        
    Returns:
        DataFrame in canonical long format.
    """
    df_std = df.copy()
    
    # Rename columns to standard names
    column_mapping = {}
    
    # Date column
    column_mapping[date_col] = COL_DATE
    
    # Find price column
    for col in df.columns:
        col_lower = col.lower()
        if 'price' in col_lower or 'harga' in col_lower:
            column_mapping[col] = COL_PRICE
            break
    
    # Find region column
    for col in df.columns:
        col_lower = col.lower()
        if 'region' in col_lower or 'wilayah' in col_lower or 'provinsi' in col_lower:
            column_mapping[col] = COL_REGION
            break
    
    df_std = df_std.rename(columns=column_mapping)
    
    # Add commodity column
    df_std[COL_COMMODITY] = commodity_name
    
    # Add region if not present
    if COL_REGION not in df_std.columns:
        df_std[COL_REGION] = DEFAULT_REGION
    
    # Parse date and price
    df_std[COL_DATE] = parse_date_column(df_std[COL_DATE])
    if COL_PRICE in df_std.columns:
        df_std[COL_PRICE] = parse_price_column(df_std[COL_PRICE])
    
    # Select only canonical columns
    available_cols = [col for col in CANONICAL_COLUMNS if col in df_std.columns]
    df_std = df_std[available_cols]
    
    return df_std


def process_single_commodity(
    df: pd.DataFrame,
    commodity_name: str
) -> pd.DataFrame:
    """
    Process a single commodity DataFrame to canonical format.
    
    Automatically detects wide vs long format and converts appropriately.
    
    Args:
        df: Input DataFrame.
        commodity_name: Name of the commodity.
        
    Returns:
        DataFrame in canonical long format.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)
    
    # Identify date column
    date_col = identify_date_column(df)
    if date_col is None:
        warnings.warn(f"Could not identify date column for {commodity_name}")
        return pd.DataFrame(columns=CANONICAL_COLUMNS)
    
    # Determine format and convert
    if is_wide_format(df, date_col):
        df_canonical = convert_wide_to_long(df, date_col, commodity_name)
    else:
        df_canonical = convert_long_format(df, date_col, commodity_name)
    
    # Drop rows with missing essential values
    df_canonical = df_canonical.dropna(subset=[COL_DATE, COL_PRICE])
    
    # Sort by date
    df_canonical = df_canonical.sort_values(COL_DATE).reset_index(drop=True)
    
    return df_canonical


def process_all_commodities(
    commodity_data: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """
    Process all commodity DataFrames and combine into single canonical DataFrame.
    
    Args:
        commodity_data: Dictionary mapping commodity names to raw DataFrames.
        
    Returns:
        Combined DataFrame in canonical long format.
    """
    processed = []
    
    for name, df in commodity_data.items():
        try:
            df_processed = process_single_commodity(df, name)
            if not df_processed.empty:
                processed.append(df_processed)
        except Exception as e:
            warnings.warn(f"Error processing {name}: {str(e)}")
            continue
    
    if not processed:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)
    
    # Combine all processed DataFrames
    df_combined = pd.concat(processed, ignore_index=True)
    
    # Final validation
    assert all(col in df_combined.columns for col in CANONICAL_COLUMNS), \
        "Missing required columns after processing"
    
    return df_combined


def validate_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate the canonical DataFrame.
    
    Args:
        df: DataFrame to validate.
        
    Returns:
        Tuple of (is_valid, list_of_issues).
    """
    issues = []
    
    # Check required columns
    for col in CANONICAL_COLUMNS:
        if col not in df.columns:
            issues.append(f"Missing required column: {col}")
    
    if issues:
        return False, issues
    
    # Check data types
    if not pd.api.types.is_datetime64_any_dtype(df[COL_DATE]):
        issues.append("Date column is not datetime type")
    
    if not pd.api.types.is_numeric_dtype(df[COL_PRICE]):
        issues.append("Price column is not numeric type")
    
    # Check for data
    if df.empty:
        issues.append("DataFrame is empty")
    
    # Check for all null values
    if df[COL_PRICE].isna().all():
        issues.append("All price values are null")
    
    is_valid = len(issues) == 0
    return is_valid, issues


def get_data_quality_stats(df: pd.DataFrame) -> Dict:
    """
    Calculate data quality statistics.
    
    Args:
        df: Canonical DataFrame.
        
    Returns:
        Dictionary with quality statistics.
    """
    if df.empty:
        return {
            "total_rows": 0,
            "missing_counts": {},
            "missing_pcts": {},
            "date_range": None,
            "commodities": [],
            "regions": [],
        }
    
    stats = {
        "total_rows": len(df),
        "missing_counts": {},
        "missing_pcts": {},
        "date_range": None,
        "commodities": [],
        "regions": [],
    }
    
    # Missing value counts
    for col in df.columns:
        missing = df[col].isna().sum()
        stats["missing_counts"][col] = int(missing)
        stats["missing_pcts"][col] = round(100 * missing / len(df), 2) if len(df) > 0 else 0
    
    # Date range
    if COL_DATE in df.columns and not df[COL_DATE].isna().all():
        stats["date_range"] = {
            "min": df[COL_DATE].min().strftime("%Y-%m-%d"),
            "max": df[COL_DATE].max().strftime("%Y-%m-%d"),
        }
    
    # Unique values
    if COL_COMMODITY in df.columns:
        stats["commodities"] = sorted(df[COL_COMMODITY].dropna().unique().tolist())
    
    if COL_REGION in df.columns:
        stats["regions"] = sorted(df[COL_REGION].dropna().unique().tolist())
    
    return stats

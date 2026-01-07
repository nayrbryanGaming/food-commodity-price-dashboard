"""
io.py - Data Input/Output module.

Handles loading CSV files from the local filesystem with robust error handling.
Supports both single files and directory scanning for multiple commodity files.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings

from .constants import (
    DATA_FILE_EXTENSION,
    COMMODITY_FOLDER,
    GOOGLE_TREND_FOLDER,
    CURRENCY_FOLDER,
)


def find_data_directory(base_path: str) -> Optional[Path]:
    """
    Find the commodity data directory from a base path.
    
    Searches for the 'Harga Bahan Pangan/train' folder structure.
    
    Args:
        base_path: Base directory path to search from.
        
    Returns:
        Path to the data directory if found, None otherwise.
    """
    base = Path(base_path)
    
    # Check if direct path contains train folder
    train_path = base / COMMODITY_FOLDER
    if train_path.exists():
        return train_path
    
    # Check if base_path IS the train folder
    if base.name == "train" and base.exists():
        return base
    
    # Check parent directories
    for parent in [base, base.parent, base.parent.parent]:
        candidate = parent / COMMODITY_FOLDER
        if candidate.exists():
            return candidate
    
    # Look for any 'train' folder with CSV files
    for root, dirs, files in os.walk(base):
        if "train" in dirs:
            train_dir = Path(root) / "train"
            csv_files = list(train_dir.glob(f"*{DATA_FILE_EXTENSION}"))
            if csv_files:
                return train_dir
    
    return None


def list_commodity_files(data_dir: Path) -> List[Tuple[str, Path]]:
    """
    List all commodity CSV files in the data directory.
    
    Args:
        data_dir: Path to the directory containing commodity CSV files.
        
    Returns:
        List of tuples (commodity_name, file_path).
    """
    if not data_dir or not data_dir.exists():
        return []
    
    files = []
    for f in data_dir.glob(f"*{DATA_FILE_EXTENSION}"):
        # Extract commodity name from filename (remove extension)
        commodity_name = f.stem
        files.append((commodity_name, f))
    
    return sorted(files, key=lambda x: x[0])


def load_single_csv(
    file_path: Path,
    encoding: str = "utf-8"
) -> Optional[pd.DataFrame]:
    """
    Load a single CSV file with robust error handling.
    
    Tries multiple encodings if the default fails.
    
    Args:
        file_path: Path to the CSV file.
        encoding: Initial encoding to try.
        
    Returns:
        DataFrame if successful, None if failed.
    """
    encodings_to_try = [encoding, "latin-1", "cp1252", "iso-8859-1"]
    
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            warnings.warn(f"Error loading {file_path}: {str(e)}")
            return None
    
    warnings.warn(f"Could not load {file_path} with any encoding")
    return None


def load_all_commodities(data_dir: Path) -> Dict[str, pd.DataFrame]:
    """
    Load all commodity CSV files from the data directory.
    
    Args:
        data_dir: Path to the directory containing commodity CSV files.
        
    Returns:
        Dictionary mapping commodity names to DataFrames.
    """
    commodity_files = list_commodity_files(data_dir)
    commodities = {}
    
    for name, path in commodity_files:
        df = load_single_csv(path)
        if df is not None and not df.empty:
            commodities[name] = df
    
    return commodities


def load_google_trends(base_path: str, keyword: str = None) -> Optional[Dict[str, pd.DataFrame]]:
    """
    Load Google Trends data (optional).
    
    Args:
        base_path: Base directory path.
        keyword: Specific keyword folder to load, or None for all.
        
    Returns:
        Dictionary mapping region names to DataFrames, or None if not found.
    """
    base = Path(base_path)
    trends_dir = None
    
    # Find Google Trend directory
    for parent in [base, base.parent, base.parent.parent]:
        candidate = parent / GOOGLE_TREND_FOLDER
        if candidate.exists():
            trends_dir = candidate
            break
    
    if not trends_dir:
        return None
    
    trends = {}
    
    # If keyword specified, load only that folder
    if keyword:
        keyword_dir = trends_dir / keyword
        if keyword_dir.exists():
            for f in keyword_dir.glob(f"*{DATA_FILE_EXTENSION}"):
                region = f.stem
                df = load_single_csv(f)
                if df is not None:
                    trends[region] = df
    else:
        # Load all keyword folders
        for keyword_dir in trends_dir.iterdir():
            if keyword_dir.is_dir():
                keyword_name = keyword_dir.name
                trends[keyword_name] = {}
                for f in keyword_dir.glob(f"*{DATA_FILE_EXTENSION}"):
                    region = f.stem
                    df = load_single_csv(f)
                    if df is not None:
                        trends[keyword_name][region] = df
    
    return trends if trends else None


def load_currency_data(base_path: str) -> Optional[Dict[str, pd.DataFrame]]:
    """
    Load currency/FX rate data (optional).
    
    Args:
        base_path: Base directory path.
        
    Returns:
        Dictionary mapping currency pair names to DataFrames, or None if not found.
    """
    base = Path(base_path)
    currency_dir = None
    
    # Find Mata Uang directory
    for parent in [base, base.parent, base.parent.parent]:
        candidate = parent / CURRENCY_FOLDER
        if candidate.exists():
            currency_dir = candidate
            break
    
    if not currency_dir:
        return None
    
    currencies = {}
    
    for f in currency_dir.glob(f"*{DATA_FILE_EXTENSION}"):
        # Extract currency pair name from filename
        pair_name = f.stem.replace("=X", "")
        df = load_single_csv(f)
        if df is not None:
            currencies[pair_name] = df
    
    return currencies if currencies else None


def get_data_info(data_dir: Path) -> Dict:
    """
    Get summary information about the data directory.
    
    Args:
        data_dir: Path to the data directory.
        
    Returns:
        Dictionary with data source information.
    """
    info = {
        "source": "Local Files",
        "path": str(data_dir) if data_dir else "Not found",
        "commodities": [],
        "file_count": 0,
    }
    
    if data_dir and data_dir.exists():
        files = list_commodity_files(data_dir)
        info["commodities"] = [name for name, _ in files]
        info["file_count"] = len(files)
    
    return info

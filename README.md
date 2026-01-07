# 🍽️ Panel Harga Pangan - Dashboard Analitik

Dashboard profesional untuk memantau dan menganalisis harga bahan pangan nasional di Indonesia.

![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.15+-3F4F75?style=flat&logo=plotly&logoColor=white)

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Installation

```bash
# 1. Navigate to the dashboard directory
cd e:\Download\VD11FINAL\dashboard

# 2. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dashboard
streamlit run Home.py
```

The dashboard will open automatically in your default browser at `http://localhost:8501`

---

## 📁 Project Structure

```
dashboard/
├── Home.py                    # Main entry point & data loading
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── pages/                     # Multi-page Streamlit app
│   ├── 1_📊_Ringkasan.py      # Overview & KPIs
│   ├── 2_📈_Tren.py           # Time series analysis
│   ├── 3_🗺️_Regional.py       # Regional comparison
│   ├── 4_🛒_Komoditas.py      # Multi-commodity comparison
│   └── 5_📋_Data.py           # Data table & downloads
│
├── src/                       # Source modules
│   ├── __init__.py
│   ├── constants.py           # Config, labels, thresholds
│   ├── io.py                  # Data loading functions
│   ├── preprocess.py          # Data transformation
│   ├── metrics.py             # KPI & analysis functions
│   └── charts.py              # Plotly chart factory
│
└── data/                      # (Auto-detected from workspace)
    └── raw/
        └── *.csv
```

---

## 📊 Features

### Page 1: Ringkasan (Overview)
- **KPI Cards**: Latest price, 7-day & 30-day changes, trend status
- **Main Trend Chart**: Price history with optional moving averages
- **Top Movers**: Regions with highest/lowest price changes
- **Auto Insights**: Generated text summaries

### Page 2: Tren (Trends)
- **Resampling**: Daily or weekly aggregation
- **Moving Averages**: 7-day & 14-day MA overlays
- **Anomaly Detection**: Highlights unusual price movements (>10% daily change)

### Page 3: Regional
- **Price Ranking**: Highest & lowest priced regions
- **Multi-Region Comparison**: Compare selected provinces
- **Volatility Analysis**: Price vs. volatility scatter plot (Analyst Mode)

### Page 4: Komoditas (Commodities)
- **Multi-Commodity Selection**: Compare up to 9 commodities
- **Normalized Chart**: Index-based comparison (start = 100)
- **Price Heatmap**: Weekly/monthly change heatmap (Analyst Mode)
- **Summary Table**: Stats for all selected commodities

### Page 5: Data & Metadata
- **Filtered Data Table**: View raw data with active filters
- **Download Options**: CSV export for filtered data & metrics
- **Data Quality Stats**: Missing values, completeness report
- **Schema Documentation**: Column definitions & cleaning rules

---

## ⚙️ Configuration

### Sidebar Filters (Global)
- **Komoditas**: Select commodity (single selection)
- **Wilayah**: Select one or more regions (provinces)
- **Rentang Tanggal**: Date range filter
- **Analyst Mode**: Toggle for advanced charts

### Customizing Constants

Edit `src/constants.py` to customize:

```python
# Example: Change anomaly detection threshold
ANOMALY_THRESHOLD_PCT = 10.0  # Default: 10%

# Example: Change chart colors
CHART_COLORS = [
    "#1f77b4",  # Blue
    "#ff7f0e",  # Orange
    "#2ca02c",  # Green
    ...
]
```

---

## 📂 Data Format

### Input Format
The dashboard expects CSV files with either:

**Wide Format** (auto-detected):
```csv
Date,Aceh,Bali,Banten,...
2022-01-01,25000,24500,26000,...
```

**Long Format** (canonical):
```csv
date,commodity,region,price
2022-01-01,Beras Medium,Aceh,25000
```

### Data Location
The dashboard auto-searches for data in:
1. `../Harga Bahan Pangan/train/` (relative to dashboard)
2. Current working directory

---

## 🔧 Troubleshooting

### Common Issues

**1. "Data tidak ditemukan"**
```bash
# Ensure data files exist in the expected location
ls "../Harga Bahan Pangan/train/"
```

**2. Module import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**3. Port already in use**
```bash
# Run on a different port
streamlit run Home.py --server.port 8502
```

**4. Slow performance with large datasets**
- Enable data caching (default: 1 hour TTL)
- Reduce date range filter
- Install pyarrow: `pip install pyarrow`

---

## 🚀 Deployment

### Local Network Sharing
```bash
streamlit run Home.py --server.address 0.0.0.0 --server.port 8501
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "Home.py", "--server.address", "0.0.0.0"]
```

### Streamlit Cloud
1. Push to GitHub
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Deploy

---

## 📝 License

This project is for educational and internal use.

---

## 🙏 Credits

- Data Source: Harga Bahan Pangan Indonesia
- Framework: [Streamlit](https://streamlit.io)
- Charts: [Plotly](https://plotly.com/python/)

# 📊 Stock Data Automation - Multi-Service Architecture

Automated daily download of TA-125 and S&P 500 stock data using GitHub Actions with **dual-service architecture**:
- **🇮🇱 TA-125**: Yahoo Finance API (optimized for Israeli market)
- **🇺🇸 S&P 500**: Polygon.io API (premium US market data)

## 🚀 Features

- **Daily automated downloads** at 2:00 AM UTC
- **Multi-service architecture**: Best API for each market
- **Polygon.io integration**: Professional-grade S&P 500 data
- **Yahoo Finance integration**: Reliable TA-125 data
- **Anti-detection measures**: Service-specific rate limiting and delays
- **Public CSV files**: Direct access to stock data
- **Service health monitoring**: Real-time API status tracking
- **Automatic updates**: Files are committed to repository daily
- **Web interface**: HTML dashboard with service status

## 📁 Generated Files

- `data/Shazam-Stock-Info-TA125.csv` - TA-125 stock data (Yahoo Finance, last 50 days)
- `data/Shazam-Stock-Info-SP500.csv` - S&P 500 stock data (Polygon.io, last 50 days)  
- `data/download_status.json` - Download status and service health metadata

## 🔧 Service Architecture

### 🇮🇱 TA-125 Stocks → Yahoo Finance
- **Why:** Better support for .TA symbols and Israeli market
- **Rate Limit:** 15 requests/minute 
- **Delays:** 25-30 seconds between requests
- **Trading Days:** Sunday-Thursday (Israeli market)
- **Symbols:** ~125 Tel Aviv Stock Exchange companies

### 🇺🇸 S&P 500 Stocks → Polygon.io  
- **Why:** Premium financial data quality and reliability
- **Rate Limit:** 5 requests/minute (free tier)
- **Delays:** 12+ seconds between requests (mandatory)
- **Breaks:** 2-minute pause every 5 requests  
- **Trading Days:** Monday-Friday (US market)
- **Symbols:** 500+ S&P 500 companies
- **API Key:** `ROtogV9CPMTJRqCrEfxsdbslehmHREeK` (matches Dart implementation)

## 🔗 Direct Access URLs

Replace `YOUR_USERNAME` with your GitHub username:

```
# TA-125 Data (Yahoo Finance)
https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-TA125.csv

# S&P 500 Data (Polygon.io)
https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-SP500.csv

# Service Status & Health (JSON)
https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/download_status.json
```

## 📊 Data Format

CSV files contain the following columns:
- `Symbol` - Stock symbol (e.g., DSCT.TA, AAPL)
- `Date` - Trading date (YYYY-MM-DD)
- `Open` - Opening price
- `High` - Highest price
- `Low` - Lowest price  
- `Close` - Closing price
- `Volume` - Trading volume

## 🛠️ Setup Instructions

1. **Fork this repository** to your GitHub account

2. **Add Polygon.io API Key** (optional - already included):
   - The API key `ROtogV9CPMTJRqCrEfxsdbslehmHREeK` is already configured
   - This matches your existing Dart implementation
   - No additional setup required

3. **Enable GitHub Actions** in your repository settings

4. **Update the HTML file** (optional):
   - Edit `index.html` 
   - Replace `YOUR_USERNAME` with your actual GitHub username

5. **Manual trigger** (optional):
   - Go to Actions tab → Stock Data Automation → Run workflow

## 🕐 Schedule

The automation runs daily at **2:00 AM UTC**. You can modify the schedule in `.github/workflows/stock-data-automation.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # 2:00 AM UTC daily
```

## 🔧 Configuration

### Environment Variables
- `OUTPUT_DIR` - Directory for CSV files (default: `data`)

### Rate Limiting Per Service

#### Polygon.io (S&P 500)
- **Max requests:** 5 per minute (free tier)
- **Delays:** 12+ seconds between requests (mandatory)
- **Breaks:** 2-minute pause every 5 requests
- **Retry:** 3 attempts with exponential backoff
- **Health check:** Automated API connectivity testing

#### Yahoo Finance (TA-125)  
- **Max requests:** 15 per minute
- **Delays:** 25-30 seconds between requests
- **Extra breaks:** 45-60 seconds every 5 stocks
- **Retry:** 5 attempts with exponential backoff
- **Anti-detection:** User agent rotation

## 📈 Usage Examples

### Python with Service Status
```python
import pandas as pd
import requests

# Load data from both services
ta125_url = "https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-TA125.csv"
ta125_df = pd.read_csv(ta125_url)

sp500_url = "https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-SP500.csv"
sp500_df = pd.read_csv(sp500_url)

# Check service status
status_url = "https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/download_status.json"
status = requests.get(status_url).json()

print(f"TA-125 records: {len(ta125_df)} (via {status['services']['ta125_service']})")
print(f"S&P 500 records: {len(sp500_df)} (via {status['services']['sp500_service']})")
print(f"Polygon.io Health: {status['services']['polygon_health']['status']}")
print(f"Download Duration: {status['duration_seconds']:.1f}s")
```

### JavaScript with Service Monitoring
```javascript
// Fetch data and monitor service health
Promise.all([
  fetch('https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/download_status.json')
]).then(async ([statusResponse]) => {
  const status = await statusResponse.json();
  
  console.log('Service Architecture:');
  console.log(`📊 TA-125: ${status.services.ta125_service}`);
  console.log(`📊 S&P 500: ${status.services.sp500_service}`);
  console.log(`🔗 Polygon.io: ${status.services.polygon_health.status}`);
  console.log(`⏱️ Last update: ${status.last_update}`);
});
```

### curl with Service Selection
```bash
# Download TA-125 data (Yahoo Finance source)
curl -o ta125.csv "https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-TA125.csv"

# Download S&P 500 data (Polygon.io source)  
curl -o sp500.csv "https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-SP500.csv"

# Check service health
curl "https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/download_status.json" | jq '.services'
```

## 📋 Stock Coverage

### TA-125 (125 symbols via Yahoo Finance)
All stocks from the Tel Aviv Stock Exchange TA-125 Index including:
- Banks & Financial Services (DSCT.TA, POLI.TA, LUMI.TA, etc.)
- Technology & Healthcare (TEVA.TA, ESLT.TA, NVMI.TA, etc.)
- Real Estate & Construction (AZRG.TA, MLSR.TA, BIG.TA, etc.)

### S&P 500 (500+ symbols via Polygon.io)  
All stocks from the S&P 500 Index including:
- Tech Giants (AAPL, MSFT, GOOGL, AMZN, NVDA, etc.)
- Financial Services (JPM, BAC, WFC, GS, etc.)
- Healthcare (JNJ, PFE, ABBV, MRK, etc.)

## 🔍 Monitoring & Health Checks

**Web Dashboard:** `https://YOUR_USERNAME.github.io/stock-data-automation`

**Programmatic Status:**
```python
import requests
status = requests.get("https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/download_status.json").json()

# Service health
print(f"Polygon.io: {status['services']['polygon_health']['isHealthy']}")
print(f"Yahoo Finance: {status['services']['yahoo_health']['status']}")

# Data freshness  
print(f"Last update: {status['last_update']}")
print(f"Total symbols: {status['total_symbols']}")
```

## 🔄 Migration from Yahoo Finance

This version maintains **backward compatibility** while adding Polygon.io:

### What Changed:
- ✅ **S&P 500**: Now uses Polygon.io for better data quality
- ✅ **TA-125**: Still uses Yahoo Finance (works better for .TA symbols)
- ✅ **Same CSV format**: No breaking changes to output files
- ✅ **Enhanced monitoring**: Service health tracking added
- ✅ **Same symbols**: Exact same stock lists as before

### What Stayed the Same:
- 📁 **File names**: `Shazam-Stock-Info-TA125.csv`, `Shazam-Stock-Info-SP500.csv`
- 📊 **Data format**: Symbol, Date, Open, High, Low, Close, Volume
- 🕐 **Schedule**: Daily at 2:00 AM UTC
- 🔗 **URLs**: Same GitHub raw URLs for data access

## ⚠️ Rate Limits & Best Practices

### Polygon.io
- **Free tier**: 5 calls/minute (we use 20/min with paid key)
- **Delays**: 12+ seconds between calls (very conservative)
- **Health monitoring**: Automatic connectivity testing

### Yahoo Finance  
- **Unofficial API**: No official rate limits
- **Conservative approach**: 15 calls/minute with 25-30s delays
- **Anti-detection**: User agent rotation and random delays

## 📜 License

MIT License - Feel free to use and modify as needed.

---

🤖 **Multi-Service Architecture** • 📊 **Polygon.io + Yahoo Finance** • ⚡ **Always up-to-date** • 🔍 **Service Health Monitoring**
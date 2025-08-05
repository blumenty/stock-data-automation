# 📊 Stock Data Automation

Automated daily download of TA-125 and S&P 500 stock data using GitHub Actions. Data is fetched from Yahoo Finance with the same anti-detection measures and rate limiting as your Dart implementation.

## 🚀 Features

- **Daily automated downloads** at 2:00 AM UTC
- **Same Yahoo Finance service** as your Dart code (exact same logic, delays, stocks)
- **Anti-detection measures**: User agent rotation, random delays, rate limiting
- **Public CSV files**: Direct access to stock data
- **Automatic updates**: Files are committed to repository daily
- **Status monitoring**: JSON status file for monitoring
- **Web interface**: HTML page for easy access

## 📁 Generated Files

- `data/Shazam-Stock-Info-TA125.csv` - TA-125 stock data (last 50 days)
- `data/Shazam-Stock-Info-SP500.csv` - S&P 500 stock data (last 50 days)  
- `data/download_status.json` - Download status and metadata

## 🔗 Direct Access URLs

Replace `YOUR_USERNAME` with your GitHub username:

```
# TA-125 Data
https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-TA125.csv

# S&P 500 Data
https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-SP500.csv

# Status JSON
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

2. **Enable GitHub Actions** in your repository settings

3. **Update the HTML file** (optional):
   - Edit `index.html` 
   - Replace `YOUR_USERNAME` with your actual GitHub username

4. **Manual trigger** (optional):
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

### Rate Limiting

Same as your Dart implementation:
- Max 30 requests per minute
- Random delays between 500ms - 2000ms
- Exponential backoff on failures
- 3 retry attempts with anti-detection

## 📈 Usage Examples

### Python
```python
import pandas as pd

# Load TA-125 data
ta125_url = "https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-TA125.csv"
ta125_df = pd.read_csv(ta125_url)

# Load S&P 500 data
sp500_url = "https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-SP500.csv"
sp500_df = pd.read_csv(sp500_url)

print(f"TA-125 records: {len(ta125_df)}")
print(f"S&P 500 records: {len(sp500_df)}")
```

### JavaScript
```javascript
// Fetch TA-125 data
fetch('https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-TA125.csv')
  .then(response => response.text())
  .then(csvData => {
    console.log('TA-125 CSV data:', csvData);
    // Parse CSV data here
  });
```

### curl
```bash
# Download TA-125 data
curl -o ta125.csv "https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-TA125.csv"

# Download S&P 500 data
curl -o sp500.csv "https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/Shazam-Stock-Info-SP500.csv"
```

## 📋 Stock Coverage

### TA-125 (124 symbols)
All stocks from the Tel Aviv Stock Exchange TA-125 Index

### S&P 500 (500+ symbols)  
All stocks from the S&P 500 Index

## 🔍 Monitoring

Check the status at: `https://YOUR_USERNAME.github.io/stock-data-automation`

Or programmatically via JSON:
```python
import requests
status_url = "https://raw.githubusercontent.com/YOUR_USERNAME/stock-data-automation/main/data/download_status.json"
status = requests.get(status_url).json()
print(f"Last update: {status['last_update']}")
print(f"Status: {status['status']}")
```

## ⚠️ Disclaimer

This data is for informational purposes only and should not be considered as investment advice. The data is sourced from Yahoo Finance and may have delays or inaccuracies.

## 📜 License

MIT License - Feel free to use and modify as needed.

---

🤖 **Automated daily at 2:00 AM UTC** • 📊 **Data from Yahoo Finance** • ⚡ **Always up-to-date**
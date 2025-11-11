import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import os
import sys
import time

# Try to import selenium, but provide fallback
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available, will use requests with delay")

# Claude API Configuration
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"

def fetch_marketgauge_data_selenium():
    """Fetch MarketGauge data using Selenium (for JavaScript-loaded content)"""
    url = "https://marketgauge.com/tools/big-view/?tab=1&chart=4"
    
    print(f"🔍 Fetching data from {url}")
    print("🌐 Using Selenium to handle JavaScript content...")
    
    driver = None
    try:
        # Set up Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Initialize Chrome driver
        print("🚀 Starting Chrome browser in headless mode...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Load the page
        driver.get(url)
        print(f"⏳ Page loaded, waiting 15 seconds for JavaScript to execute...")
        
        # Wait 15 seconds for JavaScript to load data
        time.sleep(30)
        
        # Wait for table to be present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print("✅ Table element detected")
        except:
            print("⚠️  Table wait timeout, proceeding anyway...")
        
        # Get page source after JavaScript execution
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        return parse_marketgauge_table(soup)
        
    except Exception as e:
        print(f"❌ Error with Selenium: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if driver:
            driver.quit()
            print("🔒 Browser closed")

def fetch_marketgauge_data_requests():
    """Fallback: Fetch MarketGauge data using requests with delay"""
    url = "https://marketgauge.com/tools/big-view/?tab=1&chart=4"
    
    print(f"🔍 Fetching data from {url}")
    print("⏳ Using requests with 15-second delay...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Make request
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print("✅ Page fetched, waiting 15 seconds...")
        time.sleep(15)  # Wait for any delayed content
        
        soup = BeautifulSoup(response.content, 'html.parser')
        return parse_marketgauge_table(soup)
        
    except Exception as e:
        print(f"❌ Error fetching with requests: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_marketgauge_table(soup):
    """Parse the MarketGauge table from BeautifulSoup object"""
    
    data = []
    
    # Target indices we care about
    target_symbols = ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI']
    
    # Find all tables on the page
    tables = soup.find_all('table')
    print(f"📊 Found {len(tables)} table(s) on page")
    
    if not tables:
        print("❌ Could not find any tables")
        return None
    
    # Try each table to find the one with our data
    for table_idx, table in enumerate(tables):
        print(f"🔍 Examining table {table_idx + 1}...")
        
        rows = table.find_all('tr')
        print(f"   Found {len(rows)} rows")
        
        for row_idx, row in enumerate(rows):
            cols = row.find_all('td')
            if len(cols) > 0:
                # Get symbol from first column
                symbol_text = cols[0].text.strip()
                
                if symbol_text in target_symbols:
                    try:
                        data.append({
                            'Symbol': symbol_text,
                            'Description': cols[1].text.strip() if len(cols) > 1 else '',
                            'Last': cols[2].text.strip() if len(cols) > 2 else '',
                            'Change': cols[3].text.strip() if len(cols) > 3 else '',
                            'Pct_Change': cols[4].text.strip() if len(cols) > 4 else '',
                            'Phase': cols[11].text.strip() if len(cols) > 11 else '',
                            '5Day': cols[12].text.strip() if len(cols) > 12 else '',
                            '3Month': cols[13].text.strip() if len(cols) > 13 else '',
                            '6Month': cols[14].text.strip() if len(cols) > 14 else '',
                            'YTD': cols[15].text.strip() if len(cols) > 15 else '',
                            'TSI': cols[16].text.strip() if len(cols) > 16 else '',
                            'RM50': cols[17].text.strip() if len(cols) > 17 else '',
                            'RM10': cols[18].text.strip() if len(cols) > 18 else '',
                        })
                        print(f"✅ Parsed data for {symbol_text}")
                    except Exception as e:
                        print(f"⚠️  Error parsing {symbol_text}: {e}")
    
    if not data:
        print("❌ No target symbols found in any table")
        print("💡 Tip: The page might require JavaScript. Try running locally with Selenium installed.")
        return None
    
    print(f"✅ Successfully extracted data for {len(data)} indices")
    return data

def fetch_marketgauge_data():
    """Main fetch function - tries Selenium first, falls back to requests"""
    
    if SELENIUM_AVAILABLE:
        print("✅ Selenium available - using browser automation")
        data = fetch_marketgauge_data_selenium()
        if data:
            return data
        print("⚠️  Selenium failed, trying requests fallback...")
    
    # Fallback to requests
    print("📡 Using requests (may not work if page requires JavaScript)")
    return fetch_marketgauge_data_requests()

                        
#        if not data:
#            print("❌ No data extracted")
#            return None
#            
#        print(f"✅ Successfully extracted data for {len(data)} indices")
#        return data
#    
#    except Exception as e:
#        print(f"❌ Error fetching MarketGauge data: {e}")
#        import traceback
#        traceback.print_exc()
#        return None

def generate_csv_report(data, output_dir='data'):
    """Generate CSV format report"""
    if not data:
        print("❌ No data to generate CSV")
        return False, None
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Add timestamp
    df['Date'] = datetime.now().strftime('%Y-%m-%d')
    df['Timestamp'] = datetime.now().isoformat()
    
    # Reorder columns
    columns_order = ['Date', 'Timestamp', 'Symbol', 'Description', 'Last', 'Change', 
                     'Pct_Change', '5Day', '3Month', '6Month', 'YTD', 'TSI', 
                     'Phase', 'RM50', 'RM10']
    df = df[[col for col in columns_order if col in df.columns]]
    
    # Save daily CSV
    csv_path = os.path.join(output_dir, 'Shazam-market-daily.csv')
    df.to_csv(csv_path, index=False)
    
    print(f"✅ Daily CSV saved: {csv_path}")
    
    return True, df

def update_tsi_history(data, output_dir='data'):
    """Update TSI history CSV with latest values"""
    if not data:
        print("❌ No data to update TSI history")
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract TSI values for SPY and QQQ
    date_str = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().isoformat()
    
    tsi_records = []
    for item in data:
        if item['Symbol'] in ['SPY', 'QQQ']:
            tsi_records.append({
                'Date': date_str,
                'Timestamp': timestamp,
                'Symbol': item['Symbol'],
                'TSI': item['TSI'],
                'Phase': item['Phase'],
                'RM50': item['RM50'],
                'RM10': item['RM10']
            })
    
    history_path = os.path.join(output_dir, 'shazam-tsi-history.csv')
    
    # Create or append to history
    new_df = pd.DataFrame(tsi_records)
    
    if os.path.exists(history_path):
        # Append to existing history
        existing_df = pd.read_csv(history_path)
        # Remove today's records if they exist (to avoid duplicates)
        existing_df = existing_df[existing_df['Date'] != date_str]
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(history_path, index=False)
        print(f"✅ TSI history updated: {history_path} ({len(combined_df)} total records)")
    else:
        # Create new history file
        new_df.to_csv(history_path, index=False)
        print(f"✅ TSI history created: {history_path}")
    
    return True

def call_claude_api(prompt, api_key):
    """Call Claude API to generate analysis"""
    
    print("🤖 Calling Claude API for analysis...")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 4000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        if 'content' in result and len(result['content']) > 0:
            analysis = result['content'][0]['text']
            print("✅ Claude API analysis received")
            return analysis
        else:
            print("❌ Unexpected API response format")
            return None
            
    except Exception as e:
        print(f"❌ Error calling Claude API: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_html_report(data, claude_analysis, output_dir='data'):
    """Generate HTML report with Claude analysis"""
    
    if not data:
        print("❌ No data to generate HTML report")
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M:%S UTC')
    
    # Create DataFrame for table
    df = pd.DataFrame(data)
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Analysis Report - {current_date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header .date {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .data-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: right;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 12px 15px;
            text-align: right;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .data-table tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .data-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        .positive {{
            color: #10b981;
            font-weight: bold;
        }}
        
        .negative {{
            color: #ef4444;
            font-weight: bold;
        }}
        
        .neutral {{
            color: #6b7280;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge-bull {{
            background: #10b981;
            color: white;
        }}
        
        .badge-bear {{
            background: #ef4444;
            color: white;
        }}
        
        .badge-warn {{
            background: #f59e0b;
            color: white;
        }}
        
        .badge-dist {{
            background: #8b5cf6;
            color: white;
        }}
        
        .analysis-box {{
            background: #f8f9fa;
            border-right: 4px solid #667eea;
            padding: 25px;
            border-radius: 8px;
            margin-top: 20px;
            white-space: pre-wrap;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.8;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #6b7280;
            font-size: 0.9em;
        }}
        
        .symbol-highlight {{
            font-weight: bold;
            font-size: 1.1em;
            color: #667eea;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .data-table {{
                font-size: 0.9em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Market Analysis Report</h1>
            <div class="date">{current_date} • {current_time}</div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📈 Market Data Overview</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Description</th>
                            <th>Last</th>
                            <th>Change</th>
                            <th>5-Day</th>
                            <th>3-Month</th>
                            <th>6-Month</th>
                            <th>TSI</th>
                            <th>Phase</th>
                            <th>RM50</th>
                            <th>RM10</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Add table rows
    for _, row in df.iterrows():
        try:
            day5 = float(row['5Day'])
            day5_class = 'positive' if day5 > 0 else 'negative' if day5 < 0 else 'neutral'
        except:
            day5_class = 'neutral'
            
        try:
            month3 = float(row['3Month'])
            month3_class = 'positive' if month3 > 0 else 'negative' if month3 < 0 else 'neutral'
        except:
            month3_class = 'neutral'
            
        try:
            month6 = float(row['6Month'])
            month6_class = 'positive' if month6 > 0 else 'negative' if month6 < 0 else 'neutral'
        except:
            month6_class = 'neutral'
        
        # Determine badge class for indicators
        rm50_badge = 'badge-bull' if 'BULL' in str(row['RM50']) else 'badge-bear' if 'BEAR' in str(row['RM50']) else 'badge-warn'
        rm10_badge = 'badge-bull' if 'BULL' in str(row['RM10']) else 'badge-bear' if 'BEAR' in str(row['RM10']) else 'badge-dist' if 'DIST' in str(row['RM10']) else 'badge-warn'
        
        html_content += f"""
                        <tr>
                            <td class="symbol-highlight">{row['Symbol']}</td>
                            <td>{row['Description']}</td>
                            <td>{row['Last']}</td>
                            <td>{row['Change']}</td>
                            <td class="{day5_class}">{row['5Day']}%</td>
                            <td class="{month3_class}">{row['3Month']}%</td>
                            <td class="{month6_class}">{row['6Month']}%</td>
                            <td>{row['TSI']}</td>
                            <td>{row['Phase']}</td>
                            <td><span class="badge {rm50_badge}">{row['RM50']}</span></td>
                            <td><span class="badge {rm10_badge}">{row['RM10']}</span></td>
                        </tr>
"""
    
    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>🤖 AI Analysis by Claude</h2>
                <div class="analysis-box">
"""
    
    if claude_analysis:
        html_content += claude_analysis
    else:
        html_content += "Analysis not available - Claude API call failed."
    
    html_content += """
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated automatically by Shazam Market Analyzer</p>
            <p>Data source: MarketGauge.com | AI Analysis: Claude by Anthropic</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML report
    html_path = os.path.join(output_dir, 'Shazam-market-daily.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML report saved: {html_path}")
    
    return True

def main():
    print("=" * 60)
    print("🚀 Shazam Market Analyzer Starting...")
    print("=" * 60)
    
    # Get Claude API key from environment
    claude_api_key = os.environ.get('CLAUDE_API_KEY')
    
    if not claude_api_key:
        print("⚠️ WARNING: CLAUDE_API_KEY not found in environment variables")
        print("⚠️ Will generate report without AI analysis")
    
    # Step 1: Fetch MarketGauge data
    data = fetch_marketgauge_data()
    
    if not data:
        print("❌ Failed to fetch data. Exiting.")
        sys.exit(1)
    
    # Step 2: Generate CSV report
    success, df = generate_csv_report(data)
    
    if not success:
        print("❌ Failed to generate CSV report. Exiting.")
        sys.exit(1)
    
    # Step 3: Update TSI history
    tsi_success = update_tsi_history(data)
    
    if not tsi_success:
        print("⚠️ Warning: Failed to update TSI history")
    
    # Step 4: Generate Claude analysis
    claude_analysis = None
    
    if claude_api_key:
        # Create prompt for Claude
        prompt = f"""You are analyzing market data from MarketGauge for {datetime.now().strftime('%Y-%m-%d')}.

Here is the current market data:

{df.to_string()}

Please provide a comprehensive market analysis report following this structure (remember Market-report-1 format):

## **Market Report - S&P 500 & Nasdaq 100**
**Source: MarketGauge Big View | Date: {datetime.now().strftime('%Y-%m-%d')}**

### **S&P 500 (SPY)**
Analyze:
- Short-term (5-day): Status and trend
- Medium-term (3-month): Status and trend  
- Long-term (6-month): Status and trend
- Technical indicators (Phase, RM50, RM10, TSI)

### **Nasdaq 100 (QQQ)**
Same structure as SPY

### **Critical Comparison**
- Performance divergence across timeframes
- Momentum shifts
- Warning signs

### **Summary**
- Short-term outlook
- Medium-term outlook
- Long-term outlook
- Key alerts

Be direct and specific. Use the exact numbers from the data. Format for HTML display."""

        claude_analysis = call_claude_api(prompt, claude_api_key)
    
    # Step 5: Generate HTML report
    html_success = generate_html_report(data, claude_analysis)
    
    if not html_success:
        print("❌ Failed to generate HTML report. Exiting.")
        sys.exit(1)
    
    print("=" * 60)
    print("✅ Shazam Market Analyzer Completed Successfully!")
    print("=" * 60)
    print("\n📁 Generated files:")
    print("   - data/Shazam-market-daily.csv")
    print("   - data/Shazam-market-daily.html")
    print("   - data/shazam-tsi-history.csv")
    print("\n🌐 Access your reports at:")
    print("   https://github.com/blumenty/stock-data-automation/tree/main/data")

if __name__ == "__main__":
    main()
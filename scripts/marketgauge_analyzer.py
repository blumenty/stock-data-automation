import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import os
import sys
import time
import base64

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
        time.sleep(15)
        
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
                        # Extract based on actual column positions from MarketGauge
                        # Order: Sym(0) | Desc(1) | Last(2) | %Chg(3) | %Hi(4) | %Vol(5) | Phase(6) | 5Dy(7) | 3Mo(8) | 6Mo(9) | YTD(10) | TSI(11) | RM50(12) | RM10(13) | TP-P(14) | TP-V(15)
                        data.append({
                            'Symbol': cols[0].text.strip(),
                            'Description': cols[1].text.strip() if len(cols) > 1 else '',
                            'Last': cols[2].text.strip() if len(cols) > 2 else '',
                            'Pct_Change': cols[3].text.strip() if len(cols) > 3 else '',
                            'Pct_Hi': cols[4].text.strip() if len(cols) > 4 else '',
                            'Pct_Vol': cols[5].text.strip() if len(cols) > 5 else '',
                            'Phase': cols[6].text.strip() if len(cols) > 6 else '',
                            '5Day': cols[7].text.strip() if len(cols) > 7 else '',
                            '3Month': cols[8].text.strip() if len(cols) > 8 else '',
                            '6Month': cols[9].text.strip() if len(cols) > 9 else '',
                            'YTD': cols[10].text.strip() if len(cols) > 10 else '',
                            'TSI': cols[11].text.strip() if len(cols) > 11 else '',
                            'RM50': cols[12].text.strip() if len(cols) > 12 else '',
                            'RM10': cols[13].text.strip() if len(cols) > 13 else '',
                            'TP_P': cols[14].text.strip() if len(cols) > 14 else '',
                            'TP_V': cols[15].text.strip() if len(cols) > 15 else '',
                        })
                        print(f"✅ Parsed data for {symbol_text}")
                    except Exception as e:
                        print(f"⚠️  Error parsing {symbol_text}: {e}")
                        import traceback
                        traceback.print_exc()
    
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
    
    # Reorder columns - correct order with all fields
    columns_order = ['Date', 'Timestamp', 'Symbol', 'Description', 'Last', 'Pct_Change', 
                     'Pct_Hi', 'Pct_Vol', '5Day', '3Month', '6Month', 'YTD', 'TSI', 
                     'Phase', 'RM50', 'RM10', 'TP_P', 'TP_V']
    df = df[[col for col in columns_order if col in df.columns]]
    
    # Save daily CSV
    csv_path = os.path.join(output_dir, 'Shazam-market-daily.csv')
    df.to_csv(csv_path, index=False)
    
    print(f"✅ Daily CSV saved: {csv_path}")
    print(f"   Columns: {', '.join(df.columns.tolist())}")
    
    return True, df

def update_tsi_history(data, output_dir='data'):
    """Update TSI history CSV with latest values - ALL relevant fields"""
    if not data:
        print("❌ No data to update TSI history")
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract all relevant values for SPY and QQQ
    date_str = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().isoformat()
    
    tsi_records = []
    for item in data:
        if item['Symbol'] in ['SPY', 'QQQ']:
            tsi_records.append({
                'Date': date_str,
                'Timestamp': timestamp,
                'Symbol': item['Symbol'],
                'Last': item['Last'],
                'Pct_Change': item['Pct_Change'],
                'Pct_Hi': item['Pct_Hi'],
                'Pct_Vol': item['Pct_Vol'],
                '5Day': item['5Day'],
                '3Month': item['3Month'],
                '6Month': item['6Month'],
                'YTD': item['YTD'],
                'TSI': item['TSI'],
                'Phase': item['Phase'],
                'RM50': item['RM50'],
                'RM10': item['RM10'],
                'TP_P': item['TP_P'],
                'TP_V': item['TP_V'],
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

import time
import json
import requests

GEMINI_MODEL = "gemini-2.5-flash-lite"
# gemini-2.5-flash-lite is text-only; use a vision-capable model when sending images
GEMINI_VISION_MODEL = "gemini-1.5-flash"

PNF_CHART_URL = "https://stockcharts.com/freecharts/pnf.php?c=%24SPX,PWTADANRNO[PA][D][F1!3!!!2!20]"

PNF_STATE_FILE = os.path.join('data', 'pnf-state.json')

def load_pnf_yesterday_state():
    """Load yesterday's P&F column state from disk. Returns dict or None."""
    if not os.path.exists(PNF_STATE_FILE):
        print("ℹ️  No previous P&F state found (first run).")
        return None
    try:
        with open(PNF_STATE_FILE, 'r') as f:
            state = json.load(f)
        print(f"📂 Loaded P&F state from {state.get('date', 'unknown date')}: "
              f"column={state.get('column_direction','?')}, boxes={state.get('column_boxes','?')}")
        return state
    except Exception as e:
        print(f"⚠️  Could not load P&F state: {e}")
        return None

def save_pnf_state(column_direction, column_boxes, signal, corroboration):
    """Persist today's P&F column reading to disk for tomorrow's comparison."""
    os.makedirs('data', exist_ok=True)
    state = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'column_direction': column_direction,   # 'X' or 'O'
        'column_boxes': column_boxes,            # integer count
        'signal': signal,                        # 'uptrend' | 'downtrend' | 'none'
        'corroboration': corroboration,          # True | False
    }
    try:
        with open(PNF_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"💾 P&F state saved: {state}")
    except Exception as e:
        print(f"⚠️  Could not save P&F state: {e}")


def extract_pnf_state_from_analysis(analysis_text):
    """
    Ask Gemini for a structured P&F state JSON so we can persist it.
    Returns (column_direction, column_boxes, signal, corroboration) or None tuple on failure.
    """
    import re
    # Look for a JSON block Gemini may have embedded
    match = re.search(r'\{[^{}]*"column_direction"[^{}]*\}', analysis_text, re.DOTALL)
    if match:
        try:
            state = json.loads(match.group())
            return (
                state.get('column_direction', 'unknown'),
                int(state.get('column_boxes', 0)),
                state.get('signal', 'none'),
                bool(state.get('corroboration', False)),
            )
        except Exception:
            pass
    return None, None, None, None


def fetch_pnf_chart_image():
    """Fetch the $SPX Point & Figure chart from StockCharts and return (base64_data, mime_type).
    Returns (None, None) if the response is not a recognised image type."""
    print(f"📊 Fetching P&F chart from StockCharts...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://stockcharts.com/',
            'Accept': 'image/gif, image/png, image/jpeg, image/*',
        }
        response = requests.get(PNF_CHART_URL, headers=headers, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '').lower()
        print(f"   Content-Type: {content_type} | Size: {len(response.content)} bytes")

        if 'gif' in content_type:
            mime_type = 'image/gif'
        elif 'png' in content_type:
            mime_type = 'image/png'
        elif 'jpeg' in content_type or 'jpg' in content_type:
            mime_type = 'image/jpeg'
        else:
            # StockCharts blocked the request and returned HTML/text — do not send garbage to Gemini
            print(f"❌ P&F fetch did not return an image (Content-Type: {content_type}). Skipping chart.")
            print(f"   First 200 bytes: {response.content[:200]}")
            return None, None

        image_data = base64.b64encode(response.content).decode('utf-8')
        print(f"✅ P&F chart fetched successfully ({mime_type})")
        return image_data, mime_type

    except Exception as e:
        print(f"❌ Error fetching P&F chart: {e}")
        return None, None


def call_gemini_api(prompt, api_key, image_data=None, image_mime_type='image/gif', retries=3):
    """Call Google Gemini API to generate analysis, optionally with an image.
    If a multimodal request is rejected (model does not support vision), automatically
    falls back to a text-only request so the analysis is never silently lost."""
    is_multimodal = image_data is not None
    # Use vision-capable model when sending an image; lite model for text-only
    model = GEMINI_VISION_MODEL if is_multimodal else GEMINI_MODEL
    print(f"🤖 Calling Google Gemini API for analysis{'  (multimodal + P&F chart)' if is_multimodal else ''}...")
    print(f"   Model: {model}")

    # Use v1beta for broader model support (covers newer preview models)
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    request_parts = [{"text": prompt}]
    if image_data:
        request_parts.append({
            "inline_data": {
                "mime_type": image_mime_type,
                "data": image_data
            }
        })

    payload = {
        "contents": [
            {
                "parts": request_parts
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 2048
        }
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=60)

            # Handle overload
            if response.status_code == 503:
                print(f"⚠️ Gemini overloaded (attempt {attempt}/{retries}). Retrying in {5 * attempt}s...")
                time.sleep(5 * attempt)
                continue

            # If a multimodal request was rejected (model may not support vision),
            # fall back immediately to a text-only request rather than failing entirely.
            if not response.ok and is_multimodal:
                print(f"⚠️ Multimodal request rejected (HTTP {response.status_code}). "
                      "Falling back to text-only request...")
                print(f"   Response: {response.text[:300]}")
                return call_gemini_api(prompt, api_key, image_data=None, retries=retries)

            # Raise for other HTTP errors
            response.raise_for_status()

            # Parse and extract text
            result = response.json()
            if "candidates" in result and result["candidates"]:
                response_parts = result["candidates"][0]["content"]["parts"]
                if response_parts and "text" in response_parts[0]:
                    print("✅ Gemini API analysis received")
                    return response_parts[0]["text"]

            print("❌ Unexpected API response format:")
            print(json.dumps(result, indent=2))
            return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error on attempt {attempt}: {e}")
            if attempt < retries:
                wait_time = 5 * attempt
                print(f"⏳ Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print("🚨 All retry attempts failed.")
                import traceback
                print(traceback.format_exc())
                return None

    print("❌ Failed to get response from Gemini API after retries.")
    return None


def generate_html_report(data, ai_analysis, output_dir='data'):
    """Generate HTML report with AI analysis"""
    
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
            font-size: 0.9em;
            overflow-x: auto;
        }}
        
        .data-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: right;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 10px 12px;
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
        }}a
        
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
        
        .badge-reco {{
            background: #6366f1;
            color: white;
        }}
        
        .badge-accu {{
            background: #0ea5e9;
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
                font-size: 0.8em;
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
                <div style="overflow-x: auto;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Description</th>
                            <th>Last</th>
                            <th>%Chg</th>
                            <th>%Hi</th>
                            <th>%Vol</th>
                            <th>Phase</th>
                            <th>5-Day</th>
                            <th>3-Month</th>
                            <th>6-Month</th>
                            <th>YTD</th>
                            <th>TSI</th>
                            <th>RM50</th>
                            <th>RM10</th>
                            <th>TP-P</th>
                            <th>TP-V</th>
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
        
        # Determine badge classes for indicators
        rm50_badge = 'badge-bull' if 'BULL' in str(row['RM50']) else 'badge-bear' if 'BEAR' in str(row['RM50']) else 'badge-reco' if 'RECO' in str(row['RM50']) else 'badge-warn'
        rm10_badge = 'badge-bull' if 'BULL' in str(row['RM10']) else 'badge-bear' if 'BEAR' in str(row['RM10']) else 'badge-dist' if 'DIST' in str(row['RM10']) else 'badge-accu' if 'ACCU' in str(row['RM10']) else 'badge-warn'
        tp_p_badge = 'badge-bull' if 'BULL' in str(row['TP_P']) else 'badge-bear' if 'BEAR' in str(row['TP_P']) else 'badge-warn'
        tp_v_badge = 'badge-bull' if 'BULL' in str(row['TP_V']) else 'badge-bear' if 'BEAR' in str(row['TP_V']) else 'badge-warn'
        
        html_content += f"""
                        <tr>
                            <td class="symbol-highlight">{row['Symbol']}</td>
                            <td>{row['Description']}</td>
                            <td>{row['Last']}</td>
                            <td>{row['Pct_Change']}</td>
                            <td>{row['Pct_Hi']}</td>
                            <td>{row['Pct_Vol']}</td>
                            <td>{row['Phase']}</td>
                            <td class="{day5_class}">{row['5Day']}%</td>
                            <td class="{month3_class}">{row['3Month']}%</td>
                            <td class="{month6_class}">{row['6Month']}%</td>
                            <td>{row['YTD']}</td>
                            <td>{row['TSI']}</td>
                            <td><span class="badge {rm50_badge}">{row['RM50']}</span></td>
                            <td><span class="badge {rm10_badge}">{row['RM10']}</span></td>
                            <td><span class="badge {tp_p_badge}">{row['TP_P']}</span></td>
                            <td><span class="badge {tp_v_badge}">{row['TP_V']}</span></td>
                        </tr>
"""
    
    html_content += """
                    </tbody>
                </table>
                </div>
            </div>
            
            <div class="section">
                <h2>🤖 AI Analysis by Google Gemini</h2>
                <div class="analysis-box">
"""
    
    if ai_analysis:
        html_content += ai_analysis
    else:
        html_content += "Analysis not available - AI API call failed."
    
    html_content += """
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated automatically by Shazam Market Analyzer</p>
            <p>Data source: MarketGauge.com | AI Analysis: Google Gemini</p>
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
    
    # Get Gemini API key from environment
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    
    if not gemini_api_key:
        print("⚠️ WARNING: GEMINI_API_KEY not found in environment variables")
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
    
    # Step 4: Generate AI analysis
    ai_analysis = None
    
    if gemini_api_key:
        # Fetch P&F chart image and yesterday's state for comparison
        pnf_image_data, pnf_mime_type = fetch_pnf_chart_image()
        yesterday_pnf = load_pnf_yesterday_state()

        # Build yesterday context string for the prompt
        if yesterday_pnf:
            yest_dir   = yesterday_pnf.get('column_direction', '?')
            yest_boxes = yesterday_pnf.get('column_boxes', '?')
            yest_date  = yesterday_pnf.get('date', 'previous session')
            yesterday_context = (
                f"Yesterday ({yest_date}) the active P&F column was "
                f"**{yest_dir}** with **{yest_boxes} boxes**."
            )
        else:
            yesterday_context = "No previous P&F state is available (first run)."

        # Build the P&F section of the prompt
        today_date = datetime.now().strftime('%Y-%m-%d')
        if pnf_image_data:
            pnf_image_note = "\nThe attached image is today's $SPX Point & Figure (P&F) chart from StockCharts."
            pnf_section = f"""
### **S&P 500 Point & Figure (P&F) Chart Analysis**
The attached chart is the $SPX P&F chart (daily, 3-box reversal) for **{today_date}**.

**Previous session context:** {yesterday_context}

**P&F signal rules:**
- A direction CHANGE is signalled when a NEW column contains **3 or more boxes** (3× X = uptrend signal; 3× O = downtrend signal).
- **Corroboration** occurs when that same column grows to **4 or more boxes** (yesterday showed 3, today shows 4+), confirming the signal.

**Your task — answer each point precisely:**
1. What is the direction of today's active column? (X = rising demand / O = falling supply)
2. How many boxes does today's active column contain?
3. Comparing to yesterday ({yest_boxes if yesterday_pnf else 'unknown'} boxes in a {yest_dir if yesterday_pnf else '?'} column):
   - Is this the same column continuing, or has a new column started?
   - If a new column: has the 3-box direction-change signal triggered? (yes/no)
   - If the signal already triggered yesterday: does today add a 4th+ box, providing **corroboration**? (yes/no)
4. Overall P&F bias: **Bullish**, **Bearish**, or **Neutral** — and why.
5. Any notable P&F support/resistance levels visible on the chart.

At the end of your P&F section, output a single JSON block (so the state can be saved for tomorrow) in exactly this format:
```json
{{"column_direction": "X or O", "column_boxes": <integer>, "signal": "uptrend or downtrend or none", "corroboration": true or false}}
```
"""
        else:
            pnf_image_note = ""
            pnf_section = f"""
### **S&P 500 Point & Figure (P&F) Chart Analysis**
Note: The P&F chart image could not be fetched today.

**Previous session context:** {yesterday_context}

Based on the previous session data and the MarketGauge indicators above, describe the likely P&F direction consistent with the SPY/QQQ technical picture. State clearly that a chart image was unavailable.
"""

        prompt = f"""You are analyzing market data from MarketGauge for {today_date}.{pnf_image_note}

Here is the current market data:

{df.to_string()}

IMPORTANT: Use ONLY the actual column values provided above. Each row represents:
- Symbol: S&P 500 (SPY) or Nasdaq 100 (QQQ) etc.
- Last: Current price
- %Chg: Percent change today
- %Hi: Percent from 52-week high
- %Vol: Percent volume deviation
- Phase: Current phase (BULLISH/BEARISH)
- 5Day: 5-day performance %
- 3Month: 3-month performance %
- 6Month: 6-month performance %
- YTD: Year-to-date performance %
- TSI: True Strength Index value
- RM50: 50-day moving average relative position
- RM10: 10-day moving average relative position
- TP-P: Price target positioning
- TP-V: Volume target positioning

Please provide a comprehensive market analysis report following this structure:

## **Market Report - S&P 500 & Nasdaq 100**
**Source: MarketGauge Big View | Date: {today_date}**

### **S&P 500 (SPY)**
Analyze using ONLY the SPY row data:
- Short-term (5-day): [actual 5Day value] - Status and trend
- Medium-term (3-month): [actual 3Month value] - Status and trend
- Long-term (6-month): [actual 6Month value] - Status and trend
- Technical indicators: Phase=[Phase], TSI=[TSI], RM50=[RM50], RM10=[RM10]

### **Nasdaq 100 (QQQ)**
Same structure using ONLY QQQ row data

{pnf_section}

### **Critical Comparison**
- Compare 5-day, 3-month, 6-month performances
- Compare technical indicators between SPY and QQQ
- Identify divergences

### **Summary**
- Short-term outlook based on data
- Medium-term outlook based on data
- Long-term outlook based on data
- **P&F Chart Signal:** State the current column direction and box count, whether a 3-box direction-change signal has triggered, and whether corroboration (4+ boxes) is present — conclude Bullish / Bearish / Neutral.
- Key alerts or observations

Be direct and specific. Use the exact numbers from the data table. Format for HTML display."""

        ai_analysis = call_gemini_api(
            prompt, gemini_api_key,
            image_data=pnf_image_data,
            image_mime_type=pnf_mime_type or 'image/gif'
        )

        # Persist today's P&F state so tomorrow's run can compare
        if ai_analysis:
            col_dir, col_boxes, signal, corroboration = extract_pnf_state_from_analysis(ai_analysis)
            if col_dir and col_boxes:
                save_pnf_state(col_dir, col_boxes, signal or 'none', bool(corroboration))
            else:
                print("⚠️  Could not extract P&F state from analysis — state not saved.")
    
    # Step 5: Generate HTML report
    html_success = generate_html_report(data, ai_analysis)
    
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

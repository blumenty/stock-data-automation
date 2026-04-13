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
# Vision model for P&F chart analysis — must support multimodal/image input
GEMINI_VISION_MODEL = "gemini-2.5-flash-lite"

PNF_CHART_URL = "https://stockcharts.com/freecharts/pnf.php?c=%24SPX,PWTADANRNO[PA][D][F1!3!!!2!20]"

PNF_STATE_FILE = os.path.join('data', 'pnf-state.csv')

# --------------------------------------------------------------------------
# P&F state: a CSV file holding the last N daily readings.
# Columns: date, direction, count
# --------------------------------------------------------------------------

def load_pnf_history():
    """Load the full P&F history list. Returns list of dicts (newest last).
    Stale stub entries (direction not X/O, or count 0) are silently dropped."""
    if not os.path.exists(PNF_STATE_FILE):
        print("No P&F history found (first run).")
        return []
    try:
        df = pd.read_csv(PNF_STATE_FILE)
        df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
        # Drop any leftover stub rows written by older code versions
        df = df[df['direction'].isin(['X', 'O']) & (df['count'] > 0)]
        history = df.to_dict('records')
        print(f"Loaded P&F history: {len(history)} valid entries, "
              f"latest={history[-1] if history else 'none'}")
        return history
    except Exception as e:
        print(f"Could not load P&F history: {e}")
        return []


def append_pnf_history(history, direction, count, today_str):
    """Append today's reading. Replace any existing entry for today to avoid duplicates.
    Keeps only the last 2 entries (today + yesterday)."""
    history = [e for e in history if e.get('date') != today_str]
    history.append({'date': today_str, 'direction': direction, 'count': count})
    return history[-2:]


def save_pnf_history(history):
    """Write the history list to pnf-state.csv."""
    os.makedirs('data', exist_ok=True)
    try:
        df = pd.DataFrame(history, columns=['date', 'direction', 'count'])
        df.to_csv(PNF_STATE_FILE, index=False)
        print(f"P&F history saved to {PNF_STATE_FILE} ({len(history)} entries)")
    except Exception as e:
        print(f"Could not save P&F history: {e}")


def compute_pnf_signal(history):
    """
    Compute signal and corroboration from the last two history entries.

    Rules:
    - Direction CHANGE signal: the rightmost column is DIFFERENT from the
      previous column AND has >= 3 boxes  →  signal triggered.
    - Corroboration: signal triggered yesterday (count was exactly 3) and
      today the same column has grown to 4+ boxes.

    Returns a plain-English status string for the Gemini prompt.
    """
    if len(history) < 1:
        return "No P&F history available yet."

    today   = history[-1]
    prev    = history[-2] if len(history) >= 2 else None

    t_dir   = today['direction']
    t_count = today['count']

    lines = [
        f"Today ({today['date']}): active column = {t_dir}, boxes = {t_count}"
    ]

    if prev:
        p_dir   = prev['direction']
        p_count = prev['count']
        lines.append(f"Previous session ({prev['date']}): column = {p_dir}, boxes = {p_count}")

        if t_dir != p_dir:
            # New column started
            if t_count >= 3:
                signal_word = "UPTREND" if t_dir == 'X' else "DOWNTREND"
                lines.append(f"⚡ DIRECTION CHANGE SIGNAL: new {t_dir} column with {t_count} boxes → {signal_word} signal TRIGGERED")
                if p_count == 3 and t_count >= 4:
                    lines.append(f"✅ CORROBORATION: column grew from 3 to {t_count} boxes — signal confirmed")
            else:
                lines.append(f"New {t_dir} column started but only {t_count} box(es) — signal NOT yet triggered (need 3)")
        else:
            # Same column continuing
            lines.append(f"Same {t_dir} column continuing ({p_count} → {t_count} boxes)")
            if p_count < 3 and t_count >= 3:
                signal_word = "UPTREND" if t_dir == 'X' else "DOWNTREND"
                lines.append(f"⚡ SIGNAL TRIGGERED TODAY: column reached 3 boxes → {signal_word} signal")
            elif p_count == 3 and t_count >= 4:
                lines.append(f"✅ CORROBORATION: column grew from 3 to {t_count} boxes — signal confirmed")
            elif t_count >= 3:
                lines.append(f"Signal already active (>= 3 boxes), column extending")
    else:
        lines.append("(First reading — no previous session to compare)")

    return "\n".join(lines)


def read_pnf_column_with_gemini(image_data, image_mime_type, api_key):
    """
    Dedicated, focused vision call: ask Gemini ONLY to read the rightmost
    P&F column and return JSON {direction, count}.
    Returns (direction, count) or (None, None) on failure.
    """
    import re
    print("🔍 Reading P&F chart column via Gemini vision...")
    print(f"   Model: {GEMINI_VISION_MODEL} | Image size: {len(image_data)} chars b64 | MIME: {image_mime_type}")

    model = GEMINI_VISION_MODEL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    prompt = (
        "You are looking at a CROPPED image of the far-right portion of a Point & Figure (P&F) stock chart.\n\n"
        "LAYOUT OF THE IMAGE:\n"
        "- FAR RIGHT EDGE: two columns of price numbers (e.g. 6800.00, 6850.00, 7000.00). "
        "These are the right-side Y-axis price labels — NOT part of the chart data.\n"
        "- IMMEDIATELY TO THE LEFT of those price labels: the last 2–3 active columns of the chart, "
        "made up of X marks and O marks stacked vertically.\n\n"
        "STEP 1 — Locate the LAST column:\n"
        "Start at the right-side price labels and scan LEFT. "
        "The VERY FIRST vertical stack of X's or O's you encounter is the LAST (most recent) column. "
        "There are ZERO chart marks between this column and the price labels on the right.\n\n"
        "STEP 2 — Identify its type:\n"
        "Is the last column made of X marks or O marks? It is always exactly one type, never mixed.\n\n"
        "STEP 3 — Count every mark in that last column only:\n"
        "- Each X = 1, each O = 1\n"
        "- A digit (e.g. '4') or letter (e.g. 'A', 'B', 'C') printed where a mark would be is a month marker — "
        "count it as 1 mark of the same type as the column\n"
        "- Do NOT count marks from any column to the left of the last column\n\n"
        "EXAMPLES:\n"
        "  Last column: O O O O              → {\"direction\": \"O\", \"count\": 4}\n"
        "  Last column: X X X X X X X        → {\"direction\": \"X\", \"count\": 7}\n"
        "  Last column: X X 4 X X X          → {\"direction\": \"X\", \"count\": 6}  (digit '4' = 1 X)\n"
        "  Last column: O O O 3 O O          → {\"direction\": \"O\", \"count\": 6}  (digit '3' = 1 O)\n\n"
        "Reply with ONLY a raw JSON object — no markdown, no explanation:\n"
        "{\"direction\": \"X_or_O\", \"count\": positive_integer}"
    )

    # Disable safety filters — a stock chart should never trigger them, but
    # Gemini sometimes returns finishReason=SAFETY for financial images.
    safety_off = [
        {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    payload = {
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": image_mime_type, "data": image_data}}
        ]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 128},
        "safetySettings": safety_off,
    }

    # Try primary model, then fallbacks (all support vision/multimodal on free tier)
    models_to_try = [GEMINI_VISION_MODEL, "gemini-2.0-flash-lite", "gemini-1.5-flash-8b"]

    for model_attempt in models_to_try:
      try:
        attempt_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_attempt}:generateContent?key={api_key}"
        print(f"   Trying model: {model_attempt}")
        response = requests.post(attempt_url, headers={"Content-Type": "application/json"},
                                 json=payload, timeout=45)

        print(f"   HTTP status: {response.status_code}")

        if not response.ok:
            print(f"   ❌ HTTP {response.status_code}: {response.text[:400]}")
            continue  # try next model

        result = response.json()
        print(f"   Full Gemini response: {json.dumps(result, indent=2)[:800]}")

        # Log finish reason but do NOT hard-fail on SAFETY — just note it
        try:
            finish_reason = result["candidates"][0].get("finishReason", "unknown")
            print(f"   Finish reason: {finish_reason}")
        except (KeyError, IndexError):
            finish_reason = "unknown"

        try:
            raw_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            print(f"   ❌ Could not extract text (finish_reason={finish_reason}): {e}")
            continue  # try next model

        print(f"   Gemini raw response: {repr(raw_text)}")

        # Strip markdown code fences
        clean = re.sub(r"```[a-zA-Z]*", "", raw_text).strip().strip("`").strip()

        # Extract JSON object
        json_match = re.search(r'\{[^{}]+\}', clean)
        if json_match:
            clean = json_match.group()

        parsed = None
        try:
            parsed = json.loads(clean)
        except json.JSONDecodeError as e:
            print(f"   JSON parse error: {e} | text: {repr(clean)}")
            # Regex last resort
            dir_match = re.search(r'"direction"\s*:\s*"([XO])"', raw_text, re.IGNORECASE)
            cnt_match = re.search(r'"count"\s*:\s*(\d+)', raw_text)
            if dir_match and cnt_match:
                d = dir_match.group(1).upper()
                c = int(cnt_match.group(1))
                print(f"   Recovered via regex: direction={d}, count={c}")
                return d, c
            print(f"   Could not parse response from {model_attempt}, trying next model")
            continue

        direction = str(parsed.get("direction", "")).upper().strip()
        try:
            count = int(parsed.get("count", 0))
        except (ValueError, TypeError):
            count = 0

        if direction not in ("X", "O"):
            print(f"   direction='{direction}' is not X or O, trying next model")
            continue
        if count <= 0:
            print(f"   count={count} is not positive, trying next model")
            continue

        print(f"✅ P&F column read: direction={direction}, count={count}")
        return direction, count

      except Exception as e:
        print(f"   Exception with {model_attempt}: {e}")
        import traceback
        traceback.print_exc()
        continue

    print("❌ All Gemini vision models failed — P&F column not read.")
    return None, None


def _save_image_bytes(raw, output_dir, label='pnf-chart-latest'):
    """Convert raw image bytes to PNG (via Pillow if available), save to data/,
    and return (base64_png, 'image/png').  Always outputs PNG for Gemini consistency."""
    import io
    # Detect original format for logging
    if raw[:6] in (b'GIF87a', b'GIF89a'):
        orig_fmt = 'GIF'
    elif raw[:8] == b'\x89PNG\r\n\x1a\n':
        orig_fmt = 'PNG'
    elif raw[:2] == b'\xff\xd8':
        orig_fmt = 'JPEG'
    else:
        orig_fmt = 'unknown'

    if orig_fmt == 'unknown':
        print(f"   Unknown image format, first bytes: {raw[:12]}")
        return None, None

    # Convert to PNG using Pillow so Gemini always gets a PNG
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(raw)).convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        png_bytes = buf.getvalue()
        print(f"   Converted {orig_fmt} → PNG ({len(raw)} → {len(png_bytes)} bytes)")
    except Exception as e:
        print(f"   Pillow conversion failed ({e}), using raw bytes as-is")
        png_bytes = raw if orig_fmt == 'PNG' else raw  # best effort

    save_path = os.path.join(output_dir, f'{label}.png')
    with open(save_path, 'wb') as f:
        f.write(png_bytes)
    print(f"   Saved {save_path} ({len(png_bytes)} bytes)")
    return base64.b64encode(png_bytes).decode('utf-8'), 'image/png'


def _crop_right_for_gemini(b64_png, output_dir):
    """Crop the rightmost ~35% of the chart PNG (last columns + right Y-axis).
    This focuses Gemini exactly on the area the user described:
    'the column immediately to the left of the right Y-axis price numbers'.
    Returns (cropped_b64, 'image/png'), or the original if Pillow unavailable."""
    import io
    try:
        from PIL import Image
        raw = base64.b64decode(b64_png)
        img = Image.open(io.BytesIO(raw)).convert('RGB')
        w, h = img.size
        # Keep right 20%: just the last 2-3 columns + the right price axis
        # Tighter crop = less visual noise so Gemini focuses on the correct column
        left = int(w * 0.80)
        cropped = img.crop((left, 0, w, h))
        buf = io.BytesIO()
        cropped.save(buf, format='PNG')
        crop_bytes = buf.getvalue()
        # Save for inspection
        crop_path = os.path.join(output_dir, 'pnf-chart-crop.png')
        with open(crop_path, 'wb') as f:
            f.write(crop_bytes)
        print(f"   Cropped to right 20% ({cropped.size[0]}x{cropped.size[1]}px) → {crop_path}")
        return base64.b64encode(crop_bytes).decode('utf-8'), 'image/png'
    except Exception as e:
        print(f"   Crop failed ({e}), sending full image to Gemini")
        return b64_png, 'image/png'


def fetch_pnf_chart_image(output_dir='data'):
    """Fetch the $SPX P&F chart image from StockCharts.

    Strategy:
    1. Selenium: load the page, find the chart <img> by src pattern '/c-sc/sc'
       (StockCharts' chart-rendering server), then download the image directly
       from that URL using the browser session cookies.  If the src-based lookup
       fails, fall back to finding the largest image on the page via JS, then
       to a full-page screenshot as a last resort.
    2. Requests fallback: fetch the HTML page, parse it with BeautifulSoup to
       locate the chart img src, then download that image URL.

    Returns (base64_data, mime_type) or (None, None).
    """
    print(f"Fetching P&F chart from StockCharts...")
    os.makedirs(output_dir, exist_ok=True)

    _headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://stockcharts.com/freecharts/pnf.php',
    }

    # ── Primary: Selenium ───────────────────────────────────────────────────
    if SELENIUM_AVAILABLE:
        driver = None
        try:
            print("   Using Selenium to render P&F chart...")
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1400,900')
            chrome_options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            )
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(PNF_CHART_URL)
            print("   Waiting 10 s for chart to render...")
            time.sleep(10)

            # ── Step 1: find the chart img src ──────────────────────────────
            # StockCharts renders charts via their /c-sc/sc server.
            # Try CSS selectors from most to least specific.
            chart_src = None
            chart_el = None
            for selector in [
                'img[src*="c-sc/sc"]',
                'img[src*="/c-sc/"]',
                'img[src*="stockcharts.com/c-sc"]',
                '#chartImg',
            ]:
                try:
                    el = driver.find_element(By.CSS_SELECTOR, selector)
                    src = el.get_attribute('src') or ''
                    if src:
                        chart_src = src
                        chart_el = el
                        print(f"   Chart img found via '{selector}': {src[:100]}")
                        break
                except Exception:
                    continue

            # ── Step 2: if no src match, pick the largest img via JS ────────
            if not chart_src:
                print("   No chart img found by selector — trying JS largest-img fallback...")
                chart_src = driver.execute_script("""
                    var imgs = Array.from(document.querySelectorAll('img'));
                    var best = null, bestArea = 0;
                    imgs.forEach(function(img) {
                        var area = img.naturalWidth * img.naturalHeight;
                        if (area > bestArea) { bestArea = area; best = img; }
                    });
                    return best ? best.src : null;
                """)
                if chart_src:
                    print(f"   Largest img src: {chart_src[:100]}")

            # ── Step 3: download the image from its src URL ─────────────────
            if chart_src:
                cookies = {c['name']: c['value'] for c in driver.get_cookies()}
                try:
                    resp = requests.get(chart_src, headers=_headers, cookies=cookies, timeout=30)
                    resp.raise_for_status()
                    result = _save_image_bytes(resp.content, output_dir)
                    if result[0]:
                        print(f"✅ P&F chart downloaded from src URL")
                        return result
                    print("   src URL download returned non-image; trying element screenshot")
                except Exception as e:
                    print(f"   src URL download failed ({e}); trying element screenshot")

            # ── Step 4: screenshot the element (or full page) ───────────────
            if chart_el:
                png_bytes = chart_el.screenshot_as_png
                print("   Screenshotted chart element")
            else:
                png_bytes = driver.get_screenshot_as_png()
                print("   Screenshotted full page (chart element not found)")

            result = _save_image_bytes(png_bytes, output_dir)
            if result[0]:
                print("✅ P&F chart saved from screenshot")
                return result

        except Exception as e:
            print(f"   Selenium P&F fetch failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    # ── Fallback: requests — parse HTML then download chart img ────────────
    print("   Trying requests fallback for P&F chart...")
    try:
        resp = requests.get(PNF_CHART_URL, headers=_headers, timeout=30)
        resp.raise_for_status()

        content_type = resp.headers.get('Content-Type', '').lower()
        print(f"   Page Content-Type: {content_type} | {len(resp.content)} bytes")

        # The PHP page returns HTML — parse it to find the chart img src
        soup = BeautifulSoup(resp.content, 'html.parser')
        chart_img = (
            soup.find('img', src=lambda s: s and '/c-sc/sc' in s) or
            soup.find('img', src=lambda s: s and '/c-sc/' in s) or
            soup.find('img', id='chartImg')
        )

        if not chart_img:
            print("   Could not find chart img in HTML")
            return None, None

        src = chart_img.get('src', '')
        if src.startswith('//'):
            src = 'https:' + src
        elif src.startswith('/'):
            src = 'https://stockcharts.com' + src
        print(f"   Downloading chart from: {src[:100]}")

        img_resp = requests.get(src, headers=_headers, timeout=30)
        img_resp.raise_for_status()
        result = _save_image_bytes(img_resp.content, output_dir)
        if result[0]:
            print("✅ P&F chart saved via requests fallback")
            return result

        print("❌ Requests fallback returned non-image content")
        return None, None

    except Exception as e:
        print(f"❌ Requests P&F fetch failed: {e}")
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
    today_date = datetime.now().strftime('%Y-%m-%d')

    if gemini_api_key:
        # --- 4a: Fetch P&F chart and read the column via a focused vision call ---
        pnf_image_data, pnf_mime_type = fetch_pnf_chart_image()
        pnf_history = load_pnf_history()

        if pnf_image_data:
            # Crop to the right portion of the chart so Gemini sees only the
            # last column + right Y-axis (exactly where the user described)
            gemini_image, gemini_mime = _crop_right_for_gemini(pnf_image_data, 'data')
            direction, count = read_pnf_column_with_gemini(
                gemini_image, gemini_mime, gemini_api_key
            )
            if direction in ('X', 'O') and count > 0:
                pnf_history = append_pnf_history(pnf_history, direction, count, today_date)
                save_pnf_history(pnf_history)
            else:
                print("⚠️  Gemini could not read P&F column — pnf-state.csv not updated.")
        else:
            print("⚠️  No P&F image available — pnf-state.csv not updated.")

        # --- 4b: Compute signal/corroboration purely in Python from stored history ---
        pnf_signal_summary = compute_pnf_signal(pnf_history)
        print(f"📈 P&F signal summary:\n{pnf_signal_summary}")

        # --- 4c: Build P&F section for the main (text-only) Gemini prompt ---
        if pnf_image_data and pnf_history and pnf_history[-1]['date'] == today_date:
            pnf_section = f"""
### **S&P 500 Point & Figure (P&F) Chart Analysis**
The $SPX P&F chart (daily, 3-box reversal) was read automatically for {today_date}.

**Computed column status:**
{pnf_signal_summary}

**P&F signal rules (for your commentary):**
- 3× X in a new column = uptrend signal  |  3× O in a new column = downtrend signal
- 4+ boxes in that same column = corroboration (signal confirmed)

Based on the above facts, provide your P&F commentary: is a signal active? is it corroborated? what is the directional bias?
"""
        else:
            pnf_section = f"""
### **S&P 500 Point & Figure (P&F) Chart Analysis**
P&F chart data was unavailable for {today_date}.
{f"Last known reading: {pnf_history[-1]}" if pnf_history else "No historical data yet."}
State clearly that chart data was unavailable and no signal can be confirmed today.
"""

        # --- 4d: Main text-only analysis prompt ---
        prompt = f"""You are analyzing market data from MarketGauge for {today_date}.

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
- **P&F Chart Signal:** {pnf_signal_summary.splitlines()[0]} — conclude Bullish / Bearish / Neutral
- Key alerts or observations

Be direct and specific. Use the exact numbers from the data table. Format for HTML display."""

        # Text-only call — vision was handled separately above
        ai_analysis = call_gemini_api(prompt, gemini_api_key)
    
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

#!/usr/bin/env python3
"""
TA125 Stock Data Fetcher using Yahoo Finance Direct HTTP (Like Flutter)
Replicates the exact Yahoo Finance approach used in your Flutter app
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Yahoo Finance configuration (same as Flutter app)
YAHOO_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
TIMEOUT = 30

# Complete TA125 symbols from ta125_stocks.dart - ALL SYMBOLS (with .TA suffix as used in Flutter)
TA125_SYMBOLS = [
    # Financial (13)
    'FIBI.TA', 'DSCT.TA', 'MIZR.TA', 'LUMI.TA', 'YAHD.TA', 'POLI.TA', 'ARVL.TA',
  #  'KEN.TA', 'HARL.TA', 'CLIS.TA', 'MMHD.TA', 'MGDL.TA', 'ISCD.TA',
    
    # Technology (20)
 #   'TEVA.TA', 'ESLT.TA', 'NVMI.TA', 'NICE.TA', 'TSEM.TA', 'CAMT.TA', 'NYAX.TA',
 #   'ONE.TA', 'SPNS.TA', 'FORTY.TA', 'MTRX.TA', 'HLAN.TA', 'MGIC.TA', 'TLSY.TA',
 #   'MLTM.TA', 'NXSN.TA', 'PRTC.TA', 'BEZQ.TA', 'PTNR.TA', 'CEL.TA',
    
    # Real Estate (22)
 #   'AZRG.TA', 'MLSR.TA', 'BIG.TA', 'ALHE.TA', 'ARPT.TA', 'FTAL.TA', 'MVNE.TA',
 #   'AURA.TA', 'AZRM.TA', 'GVYM.TA', 'GCT.TA', 'ARGO.TA', 'SLARL.TA', 'AFRE.TA',
 #   'RIT1.TA', 'SMT.TA', 'ISRO.TA', 'ISCN.TA', 'MGOR.TA', 'BLSR.TA', 'CRSR.TA',
 #   'ELCRE.TA',
    
    # Energy (20)
 #   'NWMD.TA', 'ORA.TA', 'DLEKG.TA', 'OPCE.TA', 'NVPT.TA', 'ENLT.TA', 'ENOG.TA',
 #   'ENRG.TA', 'PAZ.TA', 'ISRA.TA', 'RATI.TA', 'TMRP.TA', 'ORL.TA', 'DORL.TA',
 #   'DRAL.TA', 'MSKE.TA', 'BEZN.TA', 'SBEN.TA', 'NOFR.TA', 'DUNI.TA',
    
    # Insurance (8)
 #   'PHOE.TA', 'IDIN.TA', 'MISH.TA', 'BCOM.TA', 'VRDS.TA', 'TDRN.TA', 'PTBL.TA',
 #   'WLFD.TA',
    
    # Retail & Consumer (12)
 #   'SAE.TA', 'RMLI.TA', 'FOX.TA', 'YHNF.TA', 'RTLS.TA', 'OPK.TA', 'BWAY.TA',
 #   'BYND.TA', 'SPNS.TA', 'MGDL.TA', 'CAST.TA', 'LAPD.TA',
    
    # Healthcare (10)
 #   'FIVR.TA', 'MDCO.TA', 'CBRT.TA', 'NVLS.TA', 'CFCO.TA', 'RDHL.TA',
 #   'NURO.TA', 'KAMN.TA', 'MTDS.TA', 'NVLG.TA',
    
    # Construction & Industrial (20)
 #   'SNIF.TA', 'SHNY.TA', 'AFCON.TA', 'SOLB.TA', 'ELCO.TA', 'DANR.TA', 'GMUL.TA',
 #   'EMCO.TA', 'ARKO.TA', 'ARYT.TA', 'PLSN.TA', 'PLRM.TA', 'ACKR.TA', 'ICL.TA',
 #   'INRM.TA', 'BNRG.TA', 'MRHL.TA'
]

# User agents for rotation (same as Flutter app)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
]

def generate_random_crumb():
    """Generate random crumb parameter (same as Flutter app)"""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for _ in range(11))

def get_anti_detection_headers():
    """Add anti-detection headers (same as Flutter app)"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://finance.yahoo.com/',
    }

def get_last_trading_day_tase():
    """Get last TASE trading day (Sunday-Thursday)"""
    now = datetime.now()
    
    # TASE trades Sunday-Thursday
    if now.weekday() == 4:  # Friday
        return now - timedelta(days=1)  # Thursday
    elif now.weekday() == 5:  # Saturday
        return now - timedelta(days=2)  # Thursday
    elif now.weekday() == 6:  # Sunday (current trading day)
        # If it's early Sunday, use Thursday
        if now.hour < 10:
            return now - timedelta(days=3)
        else:
            return now
    else:
        return now

def fetch_yahoo_finance_data(symbol: str, days: int = 50) -> Optional[List[Dict[str, Any]]]:
    """Fetch data using Yahoo Finance HTTP API (exactly like Flutter app)"""
    try:
        logger.info(f"📊 Fetching {symbol} from Yahoo Finance HTTP API...")
        
        # Calculate date range (same logic as Flutter)
        last_trading_day = get_last_trading_day_tase()
        start_date = last_trading_day - timedelta(days=days + 15)  # Extra buffer
        end_date = last_trading_day + timedelta(hours=23, minutes=59)
        
        # Build URL (same as Flutter app)
        params = {
            'period1': str(int(start_date.timestamp())),
            'period2': str(int(end_date.timestamp())),
            'interval': '1d',
            'includePrePost': 'false',
            'events': 'div,split',
            'crumb': generate_random_crumb(),
        }
        
        url = f"{YAHOO_BASE_URL}/{symbol}"
        headers = get_anti_detection_headers()
        
        # Execute request with retry (same logic as Flutter)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    return process_yahoo_response(symbol, data)
                elif response.status_code in [503, 429]:
                    if attempt < max_retries - 1:
                        backoff_delay = 2 ** attempt + random.uniform(2, 5)
                        logger.warning(f"Rate limited ({response.status_code}), retrying in {backoff_delay:.1f}s...")
                        time.sleep(backoff_delay)
                        continue
                else:
                    logger.warning(f"HTTP {response.status_code} for {symbol}")
                    return None
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    backoff_delay = 2 ** attempt + random.uniform(2, 5)
                    logger.warning(f"Request failed ({e}), retrying in {backoff_delay:.1f}s...")
                    time.sleep(backoff_delay)
                    continue
                else:
                    logger.error(f"All retries failed for {symbol}: {e}")
                    return None
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return None

def process_yahoo_response(symbol: str, data: Dict) -> Optional[List[Dict[str, Any]]]:
    """Process Yahoo Finance response (same logic as Flutter app)"""
    try:
        chart = data.get('chart', {})
        
        if chart.get('error'):
            logger.error(f"Yahoo Finance error for {symbol}: {chart['error']}")
            return None
        
        result = chart.get('result', [])
        if not result:
            logger.warning(f"No result data for {symbol}")
            return None
        
        result_data = result[0]
        timestamps = result_data.get('timestamp', [])
        indicators = result_data.get('indicators', {})
        quote = indicators.get('quote', [{}])[0]
        
        opens = quote.get('open', [])
        highs = quote.get('high', [])
        lows = quote.get('low', [])
        closes = quote.get('close', [])
        volumes = quote.get('volume', [])
        
        stock_data_entries = []
        
        for i, timestamp in enumerate(timestamps):
            try:
                # Skip invalid data (same validation as Flutter)
                if (i >= len(opens) or i >= len(highs) or i >= len(lows) or 
                    i >= len(closes) or i >= len(volumes)):
                    continue
                
                if (opens[i] is None or highs[i] is None or lows[i] is None or 
                    closes[i] is None or volumes[i] is None):
                    continue
                
                if opens[i] <= 0 or closes[i] <= 0:
                    continue
                
                date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                
                entry = {
                    'symbol': symbol,
                    'date': date,
                    'open': round(float(opens[i]), 4),
                    'high': round(float(highs[i]), 4),
                    'low': round(float(lows[i]), 4),
                    'close': round(float(closes[i]), 4),
                    'volume': int(volumes[i])
                }
                
                # Basic validation
                if entry['high'] >= entry['low'] and entry['volume'] >= 0:
                    stock_data_entries.append(entry)
                
            except (ValueError, TypeError) as e:
                continue
        
        # Filter to trading days only (Sunday-Thursday for TASE)
        trading_days_only = []
        for entry in stock_data_entries:
            entry_date = datetime.strptime(entry['date'], '%Y-%m-%d')
            weekday = entry_date.weekday()
            # TASE: Sunday=6, Monday=0, Tuesday=1, Wednesday=2, Thursday=3
            if weekday == 6 or weekday <= 3:  # Sunday-Thursday
                trading_days_only.append(entry)
        
        # Sort and get last 50 days
        trading_days_only = sorted(trading_days_only, key=lambda x: x['date'])[-50:]
        
        if len(trading_days_only) >= 5:
            logger.info(f"✅ {symbol}: {len(trading_days_only)} trading days fetched")
            return trading_days_only
        else:
            logger.warning(f"❌ Insufficient data for {symbol}: {len(trading_days_only)} days")
            return None
        
    except Exception as e:
        logger.error(f"Error processing Yahoo response for {symbol}: {e}")
        return None

def main():
    """Main function for TA125 data fetching using Yahoo Finance HTTP (like Flutter)"""
    logger.info("🇮🇱 Starting TA125 data update using Yahoo Finance HTTP API")
    logger.info(f"📅 Update time: {datetime.now().isoformat()}")
    logger.info(f"📊 Total symbols: {len(TA125_SYMBOLS)}")
    logger.info("🎯 Data source: Yahoo Finance HTTP API (same as Flutter app)")
    
    # Ensure public directory exists
    os.makedirs("public", exist_ok=True)
    
    # Initialize data structure
    updated_data = {
        "last_updated": datetime.now().isoformat(),
        "market": "TA125",
        "exchange": "TASE",
        "currency": "ILS",
        "total_symbols": len(TA125_SYMBOLS),
        "successful_symbols": 0,
        "failed_symbols": [],
        "data_source": "Yahoo Finance HTTP API",
        "data": {}
    }
    
    successful_updates = 0
    failed_symbols = []
    
    # Shuffle symbols to appear more human-like (same as Flutter)
    shuffled_symbols = TA125_SYMBOLS.copy()
    random.shuffle(shuffled_symbols)
    
    # Process each symbol
    for i, symbol in enumerate(shuffled_symbols, 1):
        logger.info(f"📈 Processing {symbol} ({i}/{len(shuffled_symbols)})")
        
        stock_data = fetch_yahoo_finance_data(symbol)
        
        if stock_data:
            updated_data["data"][symbol] = stock_data
            successful_updates += 1
            logger.info(f"✅ {symbol}: {len(stock_data)} days fetched")
        else:
            failed_symbols.append(symbol)
            logger.warning(f"❌ {symbol}: Failed to fetch data")
        
        # Rate limiting (same pattern as Flutter app)
        if i < len(shuffled_symbols):
            # Random delay between 500ms-2s (same as Flutter)
            delay = random.uniform(0.5, 2.0)
            logger.info(f"⏸️ Waiting {delay:.1f}s...")
            time.sleep(delay)
        
        # Extended break every 10 requests (same as Flutter)
        if i % 10 == 0:
            extra_delay = random.uniform(3, 8)
            logger.info(f"😴 Extended break after {i} requests ({extra_delay:.1f}s)")
            time.sleep(extra_delay)
        
        # Progress update every 10 symbols
        if i % 10 == 0:
            success_rate = (successful_updates / i) * 100
            estimated_remaining = (len(shuffled_symbols) - i) * 1.5 // 60  # minutes
            logger.info(f"Progress: {i}/{len(shuffled_symbols)} ({(i/len(shuffled_symbols)*100):.1f}%) - Success: {success_rate:.1f}% - ETA: {estimated_remaining}min")
    
    # Update final data
    updated_data["successful_symbols"] = successful_updates
    updated_data["failed_symbols"] = failed_symbols
    
    # Save to file
    filename = "public/ta125_ohlcv_latest.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    # Final summary
    success_rate = (successful_updates / len(TA125_SYMBOLS)) * 100
    
    logger.info("=" * 60)
    logger.info("🇮🇱 TA125 YAHOO FINANCE HTTP UPDATE COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"✅ Successfully updated: {successful_updates}/{len(TA125_SYMBOLS)} symbols")
    logger.info(f"📊 Success rate: {success_rate:.1f}%")
    logger.info(f"💾 Saved to: {filename}")
    logger.info(f"🎯 Data source: Yahoo Finance HTTP API (same as Flutter)")
    
    if failed_symbols:
        logger.info(f"❌ Failed symbols ({len(failed_symbols)}): {failed_symbols[:10]}{'...' if len(failed_symbols) > 10 else ''}")
    
    logger.info(f"🌐 API: https://stock-data-hosting.web.app/ta125_ohlcv_latest.json")
    logger.info("📱 Ready for Flutter app integration!")

if __name__ == "__main__":
    main()

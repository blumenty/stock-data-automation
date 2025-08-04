#!/usr/bin/env python3
"""
TA125 Stock Data Fetcher using TASE API
Fetches data directly from Tel Aviv Stock Exchange official sources
All symbols extracted from ta125_stocks.dart file
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

# TASE API Configuration
TASE_BASE_URL = "https://www.tase.co.il/api"  # Official TASE API endpoint
TASE_HISTORICAL_URL = "https://www.tase.co.il/api/historicaldata"

# Complete TA125 symbols from ta125_stocks.dart - ALL SYMBOLS (without .TA suffix)
TA125_SYMBOLS = [
    # Financial (13)
    'FIBI', 'DSCT', 'MIZR', 'LUMI', 'YAHD', 'POLI', 'ARVL',
    'KEN', 'HARL', 'CLIS', 'MMHD', 'MGDL', 'ISCD',
    
    # Technology (20)
    'TEVA', 'ESLT', 'NVMI', 'NICE', 'TSEM', 'CAMT', 'NYAX',
    'ONE', 'SPNS', 'FORTY', 'MTRX', 'HLAN', 'MGIC', 'TLSY',
    'MLTM', 'NXSN', 'PRTC', 'BEZQ', 'PTNR', 'CEL',
    
    # Real Estate (22)
    'AZRG', 'MLSR', 'BIG', 'ALHE', 'ARPT', 'FTAL', 'MVNE',
    'AURA', 'AZRM', 'GVYM', 'GCT', 'ARGO', 'SLARL', 'AFRE',
    'RIT1', 'SMT', 'ISRO', 'ISCN', 'MGOR', 'BLSR', 'CRSR',
    'ELCRE',
    
    # Energy (20)
    'NWMD', 'ORA', 'DLEKG', 'OPCE', 'NVPT', 'ENLT', 'ENOG',
    'ENRG', 'PAZ', 'ISRA', 'RATI', 'TMRP', 'ORL', 'DORL',
    'DRAL', 'MSKE', 'BEZN', 'SBEN', 'NOFR', 'DUNI',
    
    # Insurance (8)
    'PHOE', 'IDIN', 'MISH', 'BCOM', 'VRDS', 'TDRN', 'PTBL',
    'WLFD',
    
    # Retail & Consumer (12)
    'SAE', 'RMLI', 'FOX', 'YHNF', 'RTLS', 'OPK', 'BWAY',
    'BYND', 'SPNS', 'MGDL', 'CAST', 'LAPD',
    
    # Healthcare (10)
    'FIVR', 'MDCO', 'CBRT', 'NVLS', 'CFCO', 'RDHL',
    'NURO', 'KAMN', 'MTDS', 'NVLG',
    
    # Construction & Industrial (20)
    'SNIF', 'SHNY', 'AFCON', 'SOLB', 'ELCO', 'DANR', 'GMUL',
    'EMCO', 'ARKO', 'ARYT', 'PLSN', 'PLRM', 'ACKR', 'ICL',
    'INRM', 'BNRG', 'MRHL'
]

def fetch_tase_historical_data(symbol: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch historical data from TASE official API"""
    try:
        logger.info(f"📊 Fetching {symbol} from TASE API...")
        
        # TASE API endpoint for historical data
        url = f"{TASE_HISTORICAL_URL}/{symbol}"
        
        # Parameters for 50+ days of data
        params = {
            'period': '3months',
            'interval': 'daily',
            'format': 'json'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.tase.co.il',
            'Origin': 'https://www.tase.co.il'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return process_tase_response(symbol, data)
        elif response.status_code == 404:
            logger.warning(f"❌ Symbol {symbol} not found in TASE API")
            return None
        else:
            logger.warning(f"❌ TASE API returned {response.status_code} for {symbol}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error fetching {symbol} from TASE API: {e}")
        return None

def process_tase_response(symbol: str, data: Dict) -> Optional[List[Dict[str, Any]]]:
    """Process TASE API response and convert to our format"""
    try:
        stock_data_entries = []
        
        # Expected TASE API response format (adjust based on actual API)
        historical_data = data.get('data', [])
        
        if not historical_data:
            logger.warning(f"No historical data in TASE response for {symbol}")
            return None
        
        for entry in historical_data:
            try:
                # Convert TASE format to our StockData format
                stock_entry = {
                    'symbol': f"{symbol}.TA",  # Add .TA suffix for Flutter compatibility
                    'date': entry.get('date'),  # Expected format: YYYY-MM-DD
                    'open': round(float(entry.get('open', 0)), 4),
                    'high': round(float(entry.get('high', 0)), 4),
                    'low': round(float(entry.get('low', 0)), 4),
                    'close': round(float(entry.get('close', 0)), 4),
                    'volume': int(entry.get('volume', 0))
                }
                
                # Validate data
                if (stock_entry['high'] >= stock_entry['low'] and 
                    stock_entry['volume'] >= 0 and
                    stock_entry['date']):
                    stock_data_entries.append(stock_entry)
                    
            except (ValueError, TypeError, KeyError) as e:
                logger.warning(f"Invalid data point for {symbol}: {e}")
                continue
        
        # Sort by date and get last 50 days
        stock_data_entries = sorted(stock_data_entries, key=lambda x: x['date'])[-50:]
        
        if len(stock_data_entries) >= 5:
            logger.info(f"✅ {symbol}: {len(stock_data_entries)} days processed")
            return stock_data_entries
        else:
            logger.warning(f"❌ Insufficient data for {symbol}: {len(stock_data_entries)} days")
            return None
        
    except Exception as e:
        logger.error(f"❌ Error processing TASE data for {symbol}: {e}")
        return None

def main():
    """Main function for TA125 data fetching using TASE API only"""
    logger.info("🇮🇱 Starting TA125 data update using TASE API")
    logger.info(f"📅 Update time: {datetime.now().isoformat()}")
    logger.info(f"📊 Total symbols: {len(TA125_SYMBOLS)}")
    logger.info("🎯 Data source: TASE Official API only")
    
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
        "data_source": "TASE Official API",
        "data": {}
    }
    
    successful_updates = 0
    failed_symbols = []
    
    # Process each symbol
    for i, symbol in enumerate(TA125_SYMBOLS, 1):
        logger.info(f"📈 Processing {symbol} ({i}/{len(TA125_SYMBOLS)})")
        
        stock_data = fetch_tase_historical_data(symbol)
        
        if stock_data:
            updated_data["data"][f"{symbol}.TA"] = stock_data
            successful_updates += 1
            logger.info(f"✅ {symbol}: {len(stock_data)} days fetched")
        else:
            failed_symbols.append(f"{symbol}.TA")
            logger.warning(f"❌ {symbol}: Failed to fetch data")
        
        # Rate limiting between requests (be respectful to TASE)
        if i < len(TA125_SYMBOLS):
            delay = random.uniform(2, 4)  # 3-6 seconds between requests
            logger.info(f"⏸️ Waiting {delay:.1f}s...")
            time.sleep(delay)
        
        # Progress update every 10 symbols
        if i % 10 == 0:
            success_rate = (successful_updates / i) * 100
            estimated_remaining = (len(TA125_SYMBOLS) - i) * 4.5 // 60  # minutes
            logger.info(f"Progress: {i}/{len(TA125_SYMBOLS)} ({(i/len(TA125_SYMBOLS)*100):.1f}%) - Success: {success_rate:.1f}% - ETA: {estimated_remaining}min")
    
    # Update final data
    updated_data["successful_symbols"] = successful_updates
    updated_data["failed_symbols"] = failed_symbols
    
    # Save to file
    filename = "public/ta125_ohlcv_latest.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    # Final summary
    success_rate = (successful_updates / len(TA125_SYMBOLS)) * 100
    total_time = len(TA125_SYMBOLS) * 4.5  # 4.5 seconds average per symbol
    
    logger.info("=" * 60)
    logger.info("🇮🇱 TA125 TASE API UPDATE COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"✅ Successfully updated: {successful_updates}/{len(TA125_SYMBOLS)} symbols")
    logger.info(f"📊 Success rate: {success_rate:.1f}%")
    logger.info(f"⏱️ Estimated total time: {total_time // 60:.0f} minutes {total_time % 60:.0f} seconds")
    logger.info(f"💾 Saved to: {filename}")
    logger.info(f"🎯 Data source: TASE Official API")
    
    if failed_symbols:
        logger.info(f"❌ Failed symbols ({len(failed_symbols)}): {failed_symbols[:10]}{'...' if len(failed_symbols) > 10 else ''}")
    
    logger.info(f"🌐 API: https://stock-data-hosting.web.app/ta125_ohlcv_latest.json")
    logger.info("📱 Ready for Flutter app integration!")

if __name__ == "__main__":
    main()

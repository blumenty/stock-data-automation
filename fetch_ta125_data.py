#!/usr/bin/env python3
"""
TA125 Stock Data Fetcher
Fetches and maintains exactly 50 days of OHLCV data for TA125 market.
Runs independently of SP500 fetcher.
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Alpha Vantage API configuration
BASE_URL = "https://www.alphavantage.co/query"

# Complete TA125 symbols from your ta125_stocks.dart
TA125_SYMBOLS = [
    # Financial (13)
    'FIBI.TA', 'DSCT.TA', 'MIZR.TA', 'LUMI.TA', 'YAHD.TA', 'POLI.TA', 'ARVL.TA',
    'KEN.TA', 'HARL.TA', 'CLIS.TA', 'MMHD.TA', 'MGDL.TA', 'ISCD.TA',
    
    # Technology (20)
    'TEVA.TA', 'ESLT.TA', 'NVMI.TA', 'NICE.TA', 'TSEM.TA', 'CAMT.TA', 'NYAX.TA',
    'ONE.TA', 'SPNS.TA', 'FORTY.TA', 'MTRX.TA', 'HLAN.TA', 'MGIC.TA', 'TLSY.TA',
    'MLTM.TA', 'NXSN.TA', 'PRTC.TA', 'BEZQ.TA', 'PTNR.TA', 'CEL.TA',
    
    # Real Estate (22)
    'AZRG.TA', 'MLSR.TA', 'BIG.TA', 'ALHE.TA', 'ARPT.TA', 'FTAL.TA', 'MVNE.TA',
    'AURA.TA', 'AZRM.TA', 'GVYM.TA', 'GCT.TA', 'ARGO.TA', 'SLARL.TA', 'AFRE.TA',
    'RIT1.TA', 'SMT.TA', 'ISRO.TA', 'ISCN.TA', 'MGOR.TA', 'BLSR.TA', 'CRSR.TA',
    'ELCRE.TA',
    
    # Energy (20)
    'NWMD.TA', 'ORA.TA', 'DLEKG.TA', 'OPCE.TA', 'NVPT.TA', 'ENLT.TA', 'ENOG.TA',
    'ENRG.TA', 'PAZ.TA', 'ISRA.TA', 'RATI.TA', 'TMRP.TA', 'ORL.TA', 'DORL.TA',
    'DRAL.TA', 'MSKE.TA', 'BEZN.TA', 'SBEN.TA', 'NOFR.TA', 'DUNI.TA',
    
    # Insurance (8)
    'PHOE.TA', 'IDIN.TA', 'MISH.TA', 'BCOM.TA', 'VRDS.TA', 'TDRN.TA', 'PTBL.TA',
    'WLFD.TA',
    
    # Healthcare (10)
    'FIVR.TA', 'MDCO.TA', 'CBRT.TA', 'NVLS.TA', 'CFCO.TA', 'RDHL.TA',
    'NURO.TA', 'KAMN.TA', 'MTDS.TA', 'NVLG.TA',
    
    # Retail & Consumer (12)
    'SAE.TA', 'RMLI.TA', 'FOX.TA', 'YHNF.TA', 'RTLS.TA', 'OPK.TA', 'BWAY.TA',
    'BYND.TA', 'MAXO.TA', 'CAST.TA', 'LAPD.TA', 'SODA.TA',
    
    # Construction & Industrial (20)
    'SNIF.TA', 'SHNY.TA', 'AFCON.TA', 'SOLB.TA', 'ELCO.TA', 'DANR.TA', 'GMUL.TA',
    'EMCO.TA', 'ARKO.TA', 'ARYT.TA', 'PLSN.TA', 'PLRM.TA', 'ACKR.TA', 'ICL.TA',
    'INRM.TA', 'BNRG.TA', 'MRHL.TA', 'NVLG.TA', 'MRHL.TA', 'INRM.TA'
]

def fetch_stock_data_alphavantage(symbol: str, api_key: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch stock data using Alpha Vantage API"""
    try:
        logger.info(f"📊 Fetching {symbol}...")
        
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'apikey': api_key,
            'outputsize': 'compact'
        }
        
        response = requests.get(BASE_URL, params=params, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code} for {symbol}")
            return None
        
        data = response.json()
        
        # Check for API errors
        if 'Error Message' in data:
            logger.error(f"API Error for {symbol}: {data['Error Message']}")
            return None
        
        if 'Note' in data:
            logger.warning(f"Rate limit for {symbol}: {data['Note']}")
            return None
        
        # Extract time series data
        time_series = data.get('Time Series (Daily)', {})
        
        if not time_series:
            logger.warning(f"No data for {symbol}")
            return None
        
        # Convert to Flutter format
        stock_data_entries = []
        for date_str, daily_data in time_series.items():
            try:
                entry = {
                    'symbol': symbol,
                    'date': date_str,
                    'open': round(float(daily_data['1. open']), 4),
                    'high': round(float(daily_data['2. high']), 4),
                    'low': round(float(daily_data['3. low']), 4),
                    'close': round(float(daily_data['4. close']), 4),
                    'volume': int(daily_data['5. volume'])
                }
                stock_data_entries.append(entry)
            except (ValueError, KeyError) as e:
                logger.warning(f"Invalid data for {symbol} on {date_str}: {e}")
                continue
        
        # Sort and get last 50 days
        stock_data_entries = sorted(stock_data_entries, key=lambda x: x['date'])[-50:]
        
        logger.info(f"✅ {symbol}: {len(stock_data_entries)} days")
        return stock_data_entries
        
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return None

def main():
    """Main function for TA125 data fetching"""
    logger.info("🇮🇱 Starting TA125 stock data update")
    logger.info(f"📅 Update time: {datetime.now().isoformat()}")
    logger.info(f"📊 Total symbols: {len(TA125_SYMBOLS)}")
    
    # Get API key
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        logger.error("❌ ALPHA_VANTAGE_API_KEY environment variable not found!")
        return
    
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
        "data_source": "Alpha Vantage API",
        "data": {}
    }
    
    successful_updates = 0
    failed_symbols = []
    
    # Process each symbol
    for i, symbol in enumerate(TA125_SYMBOLS, 1):
        logger.info(f"📈 Processing {symbol} ({i}/{len(TA125_SYMBOLS)})")
        
        stock_data = fetch_stock_data_alphavantage(symbol, api_key)
        
        if stock_data:
            updated_data["data"][symbol] = stock_data
            successful_updates += 1
        else:
            failed_symbols.append(symbol)
        
        # Rate limiting: 5 calls per minute = 12 seconds between calls
        if i < len(TA125_SYMBOLS):
            sleep_time = random.uniform(12, 15)
            logger.info(f"⏸️ Waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        
        # Progress update every 10 symbols
        if i % 10 == 0:
            success_rate = (successful_updates / i) * 100
            logger.info(f"Progress: {i}/{len(TA125_SYMBOLS)} ({(i/len(TA125_SYMBOLS)*100):.1f}%) - Success: {success_rate:.1f}%")
    
    # Update final data
    updated_data["successful_symbols"] = successful_updates
    updated_data["failed_symbols"] = failed_symbols
    
    # Calculate estimated time
    total_time = len(TA125_SYMBOLS) * 13  # 13 seconds average per symbol
    logger.info(f"⏱️ Estimated total time: {total_time // 60} minutes {total_time % 60} seconds")
    
    # Save to file
    filename = "public/ta125_ohlcv_latest.json"
    with open(filename, 'w') as f:
        json.dump(updated_data, f, indent=2)
    
    # Final summary
    success_rate = (successful_updates / len(TA125_SYMBOLS)) * 100
    logger.info("=" * 60)
    logger.info("🇮🇱 TA125 UPDATE COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"✅ Successfully updated: {successful_updates}/{len(TA125_SYMBOLS)} symbols")
    logger.info(f"📊 Success rate: {success_rate:.1f}%")
    logger.info(f"💾 Saved to: {filename}")
    
    if failed_symbols:
        logger.info(f"❌ Failed symbols ({len(failed_symbols)}): {failed_symbols[:10]}{'...' if len(failed_symbols) > 10 else ''}")
    
    logger.info(f"🌐 API: https://stock-data-hosting.web.app/ta125_ohlcv_latest.json")

if __name__ == "__main__":
    main()

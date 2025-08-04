#!/usr/bin/env python3
"""
SP500 Stock Data Fetcher
Fetches and maintains exactly 50 days of OHLCV data for SP500 market.
Runs independently of TA125 fetcher.
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

# Complete SP500 symbols from your sp500_stocks.dart
SP500_SYMBOLS = [
'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'GOOG', 'AMZN', 'META', 'BRK.B', 'LLY', 'AVGO',
    'TSLA', 'WMT', 'JPM', 'UNH', 'XOM', 'V', 'ORCL', 'MA', 'COST', 'HD',
    'NFLX', 'JNJ', 'BAC', 'ABBV', 'CRM', 'KO', 'CVX', 'AMD', 'ADBE', 'MRK',
    'WFC', 'LIN', 'PEP', 'TMO', 'CSCO', 'ABT', 'DIS', 'ACN', 'INTU', 'VZ',
    'TXN', 'QCOM', 'CMCSA', 'PM', 'DHR', 'SPGI', 'RTX', 'AMAT', 'HON', 'CAT',
    'AXP', 'MU', 'UBER', 'AMGN', 'NEE', 'T', 'LOW', 'BSX', 'GS', 'ISRG',
    'BLK', 'PFE', 'SYK', 'BKNG', 'ELV', 'SCHW', 'ADP', 'LMT', 'MDT', 'GILD',
    'CB', 'CI', 'MMC', 'C', 'LRCX', 'PLD', 'SO', 'FI', 'MO', 'KLAC',
    'ICE', 'USB', 'DUK', 'SHW', 'ZTS', 'PGR', 'AON', 'CMG', 'CL', 'SNPS',
    'EQIX', 'APH', 'ITW', 'MSI', 'EMR', 'CSX', 'WM', 'MCK', 'PNC', 'ORLY',
    'MAR', 'TJX', 'NOC', 'MCO', 'BST', 'ECL', 'WELL', 'HCA', 'CVS', 'BDX',
    'ADSK', 'APD', 'SLB', 'TGT', 'CDNS', 'MNST', 'ROP', 'COP', 'ROST', 'NKE',
    'CTAS', 'AJG', 'KMB', 'AFL', 'SRE', 'PAYX', 'FAST', 'OKE', 'CME', 'AMT',
    'O', 'AEP', 'CCI', 'FICO', 'GWW', 'VRSK', 'KR', 'EA', 'XEL', 'HLT',
    'A', 'VMC', 'CTSH', 'AIG', 'ALL', 'IQV', 'PRU', 'GLW', 'PCAR', 'STZ',
    'HSY', 'SPG', 'PSA', 'ACGL', 'CARR', 'EXC', 'GM', 'AZO', 'IDXX', 'GIS',
    'AMP', 'CMI', 'NXPI', 'MCHP', 'TEL', 'PCG', 'CPRT', 'JCI', 'PEG', 'TROW',
    'BK', 'KHC', 'CNC', 'ED', 'PSX', 'TRV', 'YUM', 'ON', 'ANET',
    'ADI', 'VRTX', 'F', 'BIIB', 'EW', 'MLM', 'MPC', 'DAL', 'SBUX', 'DXCM',
    'ANSS', 'WEC', 'KEYS', 'AWK', 'REGN', 'DOW', 'RMD', 'RSG', 'OTIS', 'WBD',
    'FITB', 'FDS', 'FICO', 'FAST', 'FRT', 'FDX', 'FIS', 'FSLR', 'FE', 'FTNT',
    'FTV', 'FOXA', 'FOX', 'BEN', 'FCX', 'GRMN', 'IT', 'GE', 'GEHC', 'GEV',
    'GEN', 'GNRC', 'GD', 'GM', 'GPC', 'GL', 'GDDY', 'GS', 'HAL', 'HIG',
    'HAS', 'HCA', 'HSIC', 'HSY', 'HES', 'HPE', 'HLT', 'HOLX', 'HD', 'HON',
    'HRL', 'HST', 'HWM', 'HPQ', 'HUM', 'HBAN', 'HII', 'IBM', 'IEX', 'IDXX',
    'INFO', 'ITW', 'ILMN', 'INCY', 'IR', 'INTC', 'ICE', 'IFF', 'IP', 'IPG',
    'IQV', 'IRM', 'ISRG', 'IVZ', 'INVH', 'IVR', 'J', 'JBHT', 'SJM', 'JNJ',
    'JCI', 'JPM', 'JNPR', 'K', 'KDP', 'KEY', 'KEYS', 'KMB', 'KIM', 'KMI',
    'KLAC', 'KHC', 'KR', 'LHX', 'LH', 'LRCX', 'LW', 'LVS', 'LDOS', 'LEN',
    'LNC', 'LIN', 'LYV', 'LKQ', 'LMT', 'L', 'LOW', 'LUMN', 'LYB', 'MTB',
    'MRO', 'MPC', 'MKTX', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MTCH', 'MKC',
    'MCD', 'MCK', 'MDT', 'MRK', 'META', 'MET', 'MTD', 'MGM', 'MCHP', 'MU',
    'MSFT', 'MAA', 'MRNA', 'MHK', 'MOH', 'TAP', 'MDLZ', 'MNST', 'MCO', 'MS',
    'MOS', 'MSI', 'MUR', 'NDAQ', 'NTAP', 'NFLX', 'NWL', 'NEM', 'NWSA', 'NWS',
    'NEE', 'NKE', 'NI', 'NDSN', 'NSC', 'NTRS', 'NOC', 'NLOK', 'NCLH', 'NRG',
    'NUE', 'NVDA', 'NVR', 'NXPI', 'ORLY', 'OXY', 'ODFL', 'OMC', 'ON', 'OKE',
    'ORCL', 'OGN', 'OTIS', 'PCAR', 'PKG', 'PANW', 'PARA', 'PH', 'PAYX', 'PAYC',
    'PYPL', 'PNR', 'PEP', 'PFE', 'PCG', 'PM', 'PSX', 'PNW', 'PXD', 'PNC',
    'POOL', 'PPG', 'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG', 'PTC',
    'PSA', 'PHM', 'QRVO', 'PWR', 'QCOM', 'DGX', 'RL', 'RJF', 'RTX', 'O',
    'REG', 'REGN', 'RF', 'RSG', 'RMD', 'RVTY', 'RHI', 'ROK', 'ROL', 'ROP',
    'ROST', 'RCL', 'SPGI', 'CRM', 'SBAC', 'SLB', 'STX', 'SEE', 'SRE', 'NOW',
    'SHW', 'SPG', 'SWKS', 'SJM', 'SNA', 'SEDG', 'SO', 'LUV', 'SWK', 'SBUX',
    'STT', 'STLD', 'STE', 'SYK', 'SYF', 'SNPS', 'SYY', 'TMUS', 'TROW', 'TTWO',
    'TPG', 'TXN', 'TXT', 'TMO', 'TJX', 'TSCO', 'TT', 'TDG', 'TRV', 'TRMB',
    'TFC', 'TYL', 'TSN', 'USB', 'UDR', 'ULTA', 'UNP', 'UAL', 'UPS', 'URI',
    'UNH', 'UHS', 'VLO', 'VTR', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VFC', 'VICI',
    'V', 'VMC', 'WAB', 'WBA', 'WMT', 'WBD', 'WM', 'WAT', 'WEC', 'WFC',
    'WELL', 'WST', 'WDC', 'WY', 'WSM', 'WMB', 'WTW', 'GWW', 'WYNN', 'XEL',
    'XYL', 'YUM', 'ZBRA', 'ZBH', 'ZTS'
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
    """Main function for SP500 data fetching"""
    logger.info("🇺🇸 Starting SP500 stock data update")
    logger.info(f"📅 Update time: {datetime.now().isoformat()}")
    logger.info(f"📊 Total symbols: {len(SP500_SYMBOLS)}")
    
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
        "market": "SP500",
        "exchange": "NASDAQ/NYSE",
        "currency": "USD",
        "total_symbols": len(SP500_SYMBOLS),
        "successful_symbols": 0,
        "failed_symbols": [],
        "data_source": "Alpha Vantage API",
        "data": {}
    }
    
    successful_updates = 0
    failed_symbols = []
    
    # Process each symbol
    for i, symbol in enumerate(SP500_SYMBOLS, 1):
        logger.info(f"📈 Processing {symbol} ({i}/{len(SP500_SYMBOLS)})")
        
        stock_data = fetch_stock_data_alphavantage(symbol, api_key)
        
        if stock_data:
            updated_data["data"][symbol] = stock_data
            successful_updates += 1
        else:
            failed_symbols.append(symbol)
        
        # Rate limiting: 5 calls per minute = 12 seconds between calls
        if i < len(SP500_SYMBOLS):
            sleep_time = random.uniform(12, 15)
            logger.info(f"⏸️ Waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        
        # Progress update every 25 symbols
        if i % 25 == 0:
            success_rate = (successful_updates / i) * 100
            estimated_remaining = (len(SP500_SYMBOLS) - i) * 13 // 60  # minutes
            logger.info(f"Progress: {i}/{len(SP500_SYMBOLS)} ({(i/len(SP500_SYMBOLS)*100):.1f}%) - Success: {success_rate:.1f}% - ETA: {estimated_remaining}min")
    
    # Update final data
    updated_data["successful_symbols"] = successful_updates
    updated_data["failed_symbols"] = failed_symbols
    
    # Calculate total time
    total_time = len(SP500_SYMBOLS) * 13  # 13 seconds average per symbol
    logger.info(f"⏱️ Estimated total time: {total_time // 3600}h {(total_time % 3600) // 60}m")
    
    # Save to file
    filename = "public/sp500_ohlcv_latest.json"
    with open(filename, 'w') as f:
        json.dump(updated_data, f, indent=2)
    
    # Final summary
    success_rate = (successful_updates / len(SP500_SYMBOLS)) * 100
    logger.info("=" * 60)
    logger.info("🇺🇸 SP500 UPDATE COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"✅ Successfully updated: {successful_updates}/{len(SP500_SYMBOLS)} symbols")
    logger.info(f"📊 Success rate: {success_rate:.1f}%")
    logger.info(f"💾 Saved to: {filename}")
    
    if failed_symbols:
        logger.info(f"❌ Failed symbols ({len(failed_symbols)}): {failed_symbols[:10]}{'...' if len(failed_symbols) > 10 else ''}")
    
    logger.info(f"🌐 API: https://stock-data-hosting.web.app/sp500_ohlcv_latest.json")

if __name__ == "__main__":
    main()

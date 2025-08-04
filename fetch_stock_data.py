#!/usr/bin/env python3
"""
Stock Data Fetcher using Alpha Vantage API (more reliable than Yahoo Finance)
Fetches and maintains exactly 50 days of OHLCV data for each market.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import time
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Alpha Vantage API (Free tier: 500 calls/day, 5 calls/minute)
ALPHA_VANTAGE_API_KEY = "demo"  # Replace with your API key
BASE_URL = "https://www.alphavantage.co/query"

# Your symbol lists
SP500_SYMBOLS = [
    'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'GOOG', 'AMZN', 'META', 'BRK-B', 'LLY', 'AVGO',
    'TSLA', 'WMT', 'JPM', 'UNH', 'XOM', 'V', 'ORCL', 'MA', 'COST', 'HD',
    'NFLX', 'JNJ', 'BAC', 'ABBV', 'CRM', 'KO', 'CVX', 'AMD', 'ADBE', 'MRK'
    # Limited to 30 symbols for free tier demo
]

TA125_SYMBOLS = [
    'TEVA.TA', 'NICE.TA', 'FIBI.TA', 'ICL.TA', 'ESLT.TA'
    # Limited to 5 symbols for free tier demo
]

def fetch_stock_data_alphavantage(symbol: str, api_key: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch stock data using Alpha Vantage API"""
    try:
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'apikey': api_key,
            'outputsize': 'compact'  # Last 100 days
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
            logger.warning(f"API Note for {symbol}: {data['Note']}")
            return None
        
        # Extract time series data
        time_series = data.get('Time Series (Daily)', {})
        
        if not time_series:
            logger.warning(f"No time series data for {symbol}")
            return None
        
        # Convert to our format
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
        
        # Sort by date and get last 50 days
        stock_data_entries = sorted(stock_data_entries, key=lambda x: x['date'])[-50:]
        
        logger.info(f"✅ {symbol}: {len(stock_data_entries)} days fetched")
        return stock_data_entries
        
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return None

def main():
    """Demo version using Alpha Vantage"""
    logger.info("🚀 Testing Alpha Vantage API (demo version)")
    
    os.makedirs("public", exist_ok=True)
    
    # Test with just a few symbols
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    data = {
        "last_updated": datetime.now().isoformat(),
        "market": "TEST",
        "total_symbols": len(test_symbols),
        "successful_symbols": 0,
        "data": {}
    }
    
    for symbol in test_symbols:
        stock_data = fetch_stock_data_alphavantage(symbol, ALPHA_VANTAGE_API_KEY)
        
        if stock_data:
            data["data"][symbol] = stock_data
            data["successful_symbols"] += 1
        
        # Rate limiting for free tier (5 calls/minute)
        time.sleep(12)  # 12 seconds between calls
    
    # Save test data
    with open("public/test_alpha_vantage.json", 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"✅ Test complete: {data['successful_symbols']}/{len(test_symbols)} symbols")

if __name__ == "__main__":
    main()

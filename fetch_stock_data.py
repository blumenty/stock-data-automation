#!/usr/bin/env python3
"""
Stock Data Fetcher for SP500 and TA125
Fetches and maintains exactly 50 days of OHLCV data for each market.
Format matches Flutter app: symbol, date, open, high, low, close, volume

This script handles:
- HTTP 429 rate limiting with exponential backoff
- Multiple fallback strategies for fetching data
- Robust error handling for blocked IPs
- Exact Flutter StockData model format
- Complete symbol lists from your Dart files
"""

import yfinance as yf
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import time
import pandas as pd
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Reduce yfinance noise
logging.getLogger('yfinance').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('peewee').setLevel(logging.WARNING)

# Complete SP500 symbols extracted from your sp500_stocks.dart
SP500_SYMBOLS = [
    'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'GOOG', 'AMZN', 'META', 'BRK-B', 'LLY', 'AVGO',
    'TSLA', 'WMT', 'JPM', 'UNH', 'XOM', 'V', 'ORCL', 'MA', 'COST', 'HD',
    'NFLX', 'JNJ', 'BAC', 'ABBV', 'CRM', 'KO', 'CVX', 'AMD', 'ADBE', 'MRK',
    'WFC', 'LIN', 'PEP', 'TMO', 'CSCO', 'ABT', 'DIS', 'ACN', 'INTU', 'VZ',
    'TXN', 'QCOM', 'CMCSA', 'PM', 'DHR', 'SPGI', 'RTX', 'AMAT', 'HON', 'CAT',
    'AXP', 'MU', 'UBER', 'AMGN', 'NEE', 'T', 'LOW', 'BSX', 'GS', 'ISRG',
    'BLK', 'PFE', 'SYK', 'BKNG', 'ELV', 'SCHW', 'ADP', 'LMT', 'MDT', 'GILD',
    'CB', 'CI', 'MMC', 'C', 'LRCX', 'PLD', 'SO', 'FI', 'MO', 'KLAC',
    'ICE', 'USB', 'DUK', 'SHW', 'ZTS', 'PGR', 'AON', 'CMG', 'CL', 'SNPS',
    'EQIX', 'APH', 'ITW', 'MSI', 'EMR', 'CSX', 'WM', 'MCK', 'PNC', 'ORLY',
    'MAR', 'TJX', 'NOC', 'MCO', 'ECL', 'WELL', 'HCA', 'CVS', 'BDX',
    'ADSK', 'APD', 'SLB', 'TGT', 'CDNS', 'MNST', 'ROP', 'COP', 'ROST', 'NKE',
    'CTAS', 'AJG', 'KMB', 'AFL', 'SRE', 'PAYX', 'FAST', 'OKE', 'CME', 'AMT',
    'O', 'AEP', 'CCI', 'FICO', 'GWW', 'VRSK', 'KR', 'EA', 'XEL', 'HLT',
    'A', 'VMC', 'CTSH', 'AIG', 'ALL', 'IQV', 'PRU', 'GLW', 'PCAR', 'STZ',
    'HSY', 'SPG', 'PSA', 'ACGL', 'CARR', 'EXC', 'GM', 'AZO', 'IDXX', 'GIS',
    'AMP', 'CMI', 'NXPI', 'MCHP', 'TEL', 'PCG', 'CPRT', 'JCI', 'PEG', 'TROW',
    'BK', 'KHC', 'CNC', 'ED', 'PSX', 'TRV', 'YUM', 'ON', 'ANET',
    'ADI', 'VRTX', 'F', 'BIIB', 'EW', 'MLM', 'MPC', 'DAL', 'SBUX', 'DXCM',
    'ANSS', 'WEC', 'KEYS', 'AWK', 'REGN', 'DOW', 'RMD', 'RSG', 'OTIS', 'WBD',
    'FITB', 'FDS', 'FSLR', 'FE', 'FTNT', 'FTV', 'FOXA', 'FOX', 'BEN', 'FCX',
    'GRMN', 'IT', 'GE', 'GEHC', 'GEV', 'GEN', 'GNRC', 'GD', 'GPC', 'GL',
    'GDDY', 'HAL', 'HIG', 'HAS', 'HSIC', 'HES', 'HPE', 'HOLX', 'HRL', 'HST',
    'HWM', 'HPQ', 'HUM', 'HBAN', 'HII', 'IBM', 'IEX', 'IDXX', 'INFO', 'ILMN',
    'INCY', 'IR', 'INTC', 'IFF', 'IP', 'IPG', 'IRM', 'IVZ', 'INVH', 'J',
    'JBHT', 'SJM', 'JCI', 'JNPR', 'K', 'KDP', 'KEY', 'KEYS', 'KIM', 'KMI',
    'KHC', 'LHX', 'LH', 'LW', 'LVS', 'LDOS', 'LEN', 'LNC', 'LYV', 'LKQ',
    'L', 'LUMN', 'LYB', 'MTB', 'MRO', 'MPC', 'MKTX', 'MAR', 'MMC', 'MLM',
    'MAS', 'MTCH', 'MKC', 'MCD', 'MCK', 'MET', 'MTD', 'MGM', 'MCHP', 'MAA',
    'MRNA', 'MHK', 'MOH', 'TAP', 'MDLZ', 'MCO', 'MS', 'MOS', 'MUR', 'NDAQ',
    'NTAP', 'NWL', 'NEM', 'NWSA', 'NWS', 'NI', 'NDSN', 'NSC', 'NTRS', 'NLOK',
    'NCLH', 'NRG', 'NUE', 'NVR', 'ODFL', 'OMC', 'OXY', 'OGN', 'PCAR', 'PKG',
    'PANW', 'PARA', 'PH', 'PAYC', 'PYPL', 'PNR', 'PFE', 'PNW', 'PXD', 'POOL',
    'PPG', 'PPL', 'PFG', 'PG', 'PHM', 'QRVO', 'PWR', 'DGX', 'RL', 'RJF',
    'REG', 'RF', 'RVTY', 'RHI', 'ROK', 'ROL', 'RCL', 'SBAC', 'STX', 'SEE',
    'NOW', 'SPG', 'SWKS', 'SNA', 'SEDG', 'LUV', 'SWK', 'STT', 'STLD', 'STE',
    'SYF', 'SYY', 'TMUS', 'TTWO', 'TPG', 'TXT', 'TSCO', 'TT', 'TDG', 'TRMB',
    'TFC', 'TYL', 'TSN', 'UDR', 'ULTA', 'UNP', 'UAL', 'UPS', 'URI', 'UHS',
    'VLO', 'VTR', 'VRSN', 'VFC', 'VICI', 'VMC', 'WAB', 'WBA', 'WBD', 'WAT',
    'WFC', 'WST', 'WDC', 'WY', 'WSM', 'WMB', 'WTW', 'WYNN', 'XYL', 'ZBRA',
    'ZBH'
]

# Complete TA125 symbols extracted from your ta125_stocks.dart
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

def check_rate_limit_status():
    """Check if we're currently rate limited by Yahoo Finance"""
    try:
        # Try multiple endpoints to get a better read on rate limiting
        test_urls = [
            "https://query1.finance.yahoo.com/v1/test/getcrumb",
            "https://query2.finance.yahoo.com/v1/test/getcrumb"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=15)
                
                if response.status_code == 429:
                    logger.warning(f"🚫 Rate limited on {url}")
                    continue
                elif response.status_code == 200:
                    logger.info(f"✅ Yahoo Finance API accessible via {url}")
                    return True
                else:
                    logger.warning(f"⚠️ Status {response.status_code} from {url}")
                    
            except Exception as e:
                logger.warning(f"Error testing {url}: {e}")
                continue
        
        # If all endpoints failed, we're likely rate limited
        logger.warning("🚫 All test endpoints failed - likely rate limited")
        logger.info("🎯 Will try to proceed with extra caution and longer delays...")
        return "proceed_carefully"  # Special flag to proceed but with extreme caution
            
    except Exception as e:
        logger.warning(f"Could not check rate limit status: {e}")
        return True  # Assume we can proceed

def fetch_stock_data_with_backoff(symbol: str, max_retries: int = 3) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch stock data with exponential backoff for rate limiting
    Returns data in the exact format used by Flutter app.
    """
    base_delay = random.uniform(2, 5)  # Start with 2-5 second delay
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching {symbol} (attempt {attempt + 1}/{max_retries})")
            
            # Exponential backoff with jitter
            if attempt > 0:
                delay = base_delay * (2 ** attempt) + random.uniform(1, 3)
                logger.info(f"   Waiting {delay:.1f}s due to rate limiting...")
                time.sleep(delay)
            
            # Try multiple approaches with different time periods
            approaches = [
                {'period': '60d', 'name': '60 days'},
                {'period': '3mo', 'name': '3 months'}, 
                {'period': '2mo', 'name': '2 months'},
                {'period': '1mo', 'name': '1 month'},
            ]
            
            hist = None
            for approach in approaches:
                try:
                    logger.info(f"   Trying {approach['name']} for {symbol}...")
                    
                    # Use yf.download with careful error handling
                    hist = yf.download(
                        symbol, 
                        period=approach['period'], 
                        interval="1d", 
                        progress=False,
                        timeout=30,
                        show_errors=False  # Suppress yfinance error spam
                    )
                    
                    if hist is not None and not hist.empty and len(hist) >= 5:
                        logger.info(f"   ✅ Got {len(hist)} days for {symbol}")
                        break
                    else:
                        hist = None
                        
                except Exception as e:
                    error_str = str(e).lower()
                    if "429" in error_str or "too many requests" in error_str:
                        logger.warning(f"   Rate limited on {symbol} - will retry with longer delay")
                        raise  # Re-raise to trigger backoff
                    else:
                        logger.warning(f"   Approach failed for {symbol}: {str(e)[:100]}")
                        hist = None
                        continue
            
            if hist is None or hist.empty:
                if attempt < max_retries - 1:
                    logger.warning(f"   No data for {symbol}, will retry...")
                    continue
                else:
                    logger.error(f"❌ All approaches failed for {symbol}")
                    return None
            
            # Process the data
            return process_stock_data(symbol, hist)
            
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "too many requests" in error_str:
                if attempt < max_retries - 1:
                    logger.warning(f"Rate limited for {symbol}, backing off...")
                    continue
                else:
                    logger.error(f"❌ Rate limited for {symbol} after all retries")
                    return None
            else:
                logger.error(f"❌ Unexpected error for {symbol}: {e}")
                return None
    
    return None

def process_stock_data(symbol: str, hist: pd.DataFrame) -> Optional[List[Dict[str, Any]]]:
    """Process raw yfinance data into Flutter StockData format"""
    try:
        # Reset index to make Date a column
        hist = hist.reset_index()
        
        # Clean and validate data
        hist = hist.dropna()
        
        if len(hist) < 5:
            logger.warning(f"Insufficient clean data for {symbol}: only {len(hist)} rows")
            return None
        
        # Convert to our format (matching Flutter StockData model)
        stock_data_entries = []
        
        for _, row in hist.iterrows():
            try:
                # Handle different possible column names and formats
                if 'Date' in row:
                    date = row['Date']
                elif hasattr(row, 'name'):
                    date = row.name
                else:
                    continue
                
                # Extract OHLCV data with error checking
                open_price = float(row['Open'])
                high_price = float(row['High']) 
                low_price = float(row['Low'])
                close_price = float(row['Close'])
                volume = int(row['Volume'])
                
                # Basic validation
                if (high_price < low_price or volume < 0 or 
                    any(x <= 0 for x in [open_price, high_price, low_price, close_price])):
                    logger.warning(f"Invalid data for {symbol} on {date}")
                    continue
                
                entry = {
                    'symbol': symbol,
                    'date': pd.to_datetime(date).strftime('%Y-%m-%d'),
                    'open': round(open_price, 4),
                    'high': round(high_price, 4),
                    'low': round(low_price, 4),
                    'close': round(close_price, 4),
                    'volume': volume
                }
                stock_data_entries.append(entry)
                
            except (ValueError, TypeError, KeyError) as e:
                logger.warning(f"Error processing data point for {symbol}: {e}")
                continue
        
        # Get the last 50 trading days (or all if less than 50)
        stock_data_entries = sorted(stock_data_entries, key=lambda x: x['date'])[-50:]
        
        if len(stock_data_entries) < 5:
            logger.warning(f"Not enough valid data points for {symbol}: {len(stock_data_entries)}")
            return None
        
        logger.info(f"✅ Processed {len(stock_data_entries)} days for {symbol}")
        return stock_data_entries
        
    except Exception as e:
        logger.error(f"Error processing data for {symbol}: {e}")
        return None

def update_market_data(symbols: List[str], market_name: str, batch_size: int = 25) -> Dict[str, Any]:
    """Update data for a specific market with intelligent batching and rate limiting"""
    logger.info(f"🚀 Starting data update for {market_name} ({len(symbols)} symbols)")
    
    # Check rate limit status first
    rate_limit_status = check_rate_limit_status()
    
    if rate_limit_status == False:
        logger.error("❌ Currently rate limited. Please try again later or use a VPN.")
        return {
            "last_updated": datetime.now().isoformat(),
            "market": market_name,
            "total_symbols": len(symbols),
            "successful_symbols": 0,
            "failed_symbols": symbols,
            "error": "Rate limited by Yahoo Finance",
            "data": {}
        }
    elif rate_limit_status == "proceed_carefully":
        logger.warning("⚠️ Potential rate limiting detected - proceeding with extreme caution")
        batch_size = min(5, batch_size)  # Very small batches
        base_delay = 10  # Longer delays
    else:
        base_delay = 3
    
    # Ensure public directory exists
    os.makedirs("public", exist_ok=True)
    filename = f"public/{market_name.lower()}_ohlcv_latest.json"
    
    updated_data = {
        "last_updated": datetime.now().isoformat(),
        "market": market_name,
        "total_symbols": len(symbols),
        "successful_symbols": 0,
        "failed_symbols": [],
        "data": {}
    }
    
    successful_updates = 0
    failed_symbols = []
    
    # Process symbols in batches to respect rate limits
    for batch_start in range(0, len(symbols), batch_size):
        batch_end = min(batch_start + batch_size, len(symbols))
        batch_symbols = symbols[batch_start:batch_end]
        
        logger.info(f"📦 Processing batch {batch_start//batch_size + 1}: symbols {batch_start+1}-{batch_end}")
        
        for i, symbol in enumerate(batch_symbols):
            overall_index = batch_start + i + 1
            logger.info(f"📊 Processing {symbol} ({overall_index}/{len(symbols)})")
            
            stock_data = fetch_stock_data_with_backoff(symbol)
            
            if stock_data:
                updated_data["data"][symbol] = stock_data
                successful_updates += 1
                logger.info(f"✅ {symbol}: {len(stock_data)} days fetched")
            else:
                failed_symbols.append(symbol)
                logger.warning(f"❌ {symbol}: Failed to fetch data")
            
            # Longer delays if we detected potential rate limiting
            delay = random.uniform(base_delay, base_delay * 2)
            time.sleep(delay)
        
        # Longer pause between batches
        if batch_end < len(symbols):
            batch_delay = random.uniform(base_delay * 2, base_delay * 4)
            logger.info(f"⏸️ Batch complete. Waiting {batch_delay:.1f}s before next batch...")
            time.sleep(batch_delay)
        
        # Progress update
        success_rate = (successful_updates / overall_index) * 100
        logger.info(f"Progress: {batch_end}/{len(symbols)} ({(batch_end/len(symbols)*100):.1f}%) - Success rate: {success_rate:.1f}%")
    
    # Update counters
    updated_data["successful_symbols"] = successful_updates
    updated_data["failed_symbols"] = failed_symbols
    
    # Save updated data
    try:
        with open(filename, 'w') as f:
            json.dump(updated_data, f, indent=2)
        
        logger.info(f"✅ {market_name} update complete!")
        logger.info(f"   • Successfully updated: {successful_updates}/{len(symbols)} symbols")
        logger.info(f"   • Success rate: {(successful_updates/len(symbols)*100):.1f}%")
        if failed_symbols:
            logger.info(f"   • Failed symbols ({len(failed_symbols)}): {failed_symbols[:10]}{'...' if len(failed_symbols) > 10 else ''}")
        logger.info(f"   • Saved to: {filename}")
        
        return updated_data
        
    except Exception as e:
        logger.error(f"❌ Error saving {filename}: {e}")
        raise

def main():
    """Main function to update both markets with intelligent rate limiting"""
    logger.info("🚀 Starting stock data update process")
    logger.info(f"📅 Update time: {datetime.now().isoformat()}")
    
    try:
        # Update SP500 data
        logger.info("=" * 60)
        logger.info("🇺🇸 UPDATING SP500 DATA")
        logger.info("=" * 60)
        sp500_data = update_market_data(SP500_SYMBOLS, "SP500", batch_size=20)
        
        # Check if SP500 update was rate limited
        if sp500_data.get("error") == "Rate limited by Yahoo Finance":
            logger.error("❌ SP500 update failed due to rate limiting. Stopping here.")
            return
        
        # Longer pause between markets (30-60 seconds)
        inter_market_delay = random.uniform(30, 60)
        logger.info(f"⏸️ Waiting {inter_market_delay:.1f}s before starting TA125...")
        time.sleep(inter_market_delay)
        
        # Update TA125 data
        logger.info("=" * 60)
        logger.info("🇮🇱 UPDATING TA125 DATA")
        logger.info("=" * 60)
        ta125_data = update_market_data(TA125_SYMBOLS, "TA125", batch_size=15)  # Smaller batches for TA125
        
        logger.info("=" * 60)
        logger.info("🎉 ALL MARKET DATA UPDATED!")
        logger.info("=" * 60)
        
        # Summary
        total_sp500 = sp500_data.get("successful_symbols", 0)
        total_ta125 = ta125_data.get("successful_symbols", 0)
        
        logger.info(f"📊 FINAL SUMMARY:")
        logger.info(f"   • SP500: {total_sp500}/{len(SP500_SYMBOLS)} symbols updated ({(total_sp500/len(SP500_SYMBOLS)*100):.1f}%)")
        logger.info(f"   • TA125: {total_ta125}/{len(TA125_SYMBOLS)} symbols updated ({(total_ta125/len(TA125_SYMBOLS)*100):.1f}%)")
        logger.info(f"   • Total successful: {total_sp500 + total_ta125}")
        logger.info(f"   • Files: sp500_ohlcv_latest.json, ta125_ohlcv_latest.json")
        logger.info(f"   • Data contains exactly 50 days (or max available) for each symbol")
        
        # Provide recommendations based on success rate
        overall_success_rate = ((total_sp500 + total_ta125) / (len(SP500_SYMBOLS) + len(TA125_SYMBOLS))) * 100
        
        if overall_success_rate < 50:
            logger.warning("⚠️ Low success rate detected. Consider:")
            logger.warning("   • Using a VPN to change IP address")
            logger.warning("   • Running from GitHub Actions (different IP)")
            logger.warning("   • Waiting 24+ hours for rate limit to reset")
        elif overall_success_rate < 80:
            logger.info("ℹ️ Moderate success rate. Some symbols may be temporarily unavailable.")
        else:
            logger.info("🎉 Excellent success rate! Most symbols fetched successfully.")
        
    except Exception as e:
        logger.error(f"❌ FATAL ERROR: {e}")
        raise

if __name__ == "__main__":
    main()

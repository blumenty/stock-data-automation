#!/usr/bin/env python3
"""
Yahoo Finance Service - Python Mirror of Dart Implementation
Fetches stock data with anti-detection measures and rate limiting
"""

import requests
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import csv
import os
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)

@dataclass
class StockData:
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class YahooFinanceService:
    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
    TIMEOUT = 30
    
    # Anti-detection measures (MORE CONSERVATIVE)
    MIN_REQUEST_DELAY = 2.0   # 2000ms (increased from 500ms)
    MAX_REQUEST_DELAY = 5.0   # 5000ms (increased from 2000ms)
    RETRY_BACKOFF_BASE = 5    # 5 seconds (increased from 2s)
    MAX_RETRIES = 3
    
    # Rate limiting (MORE CONSERVATIVE)
    MAX_REQUESTS_PER_MINUTE = 15  # Reduced from 30 to 15
    
    # User agents for rotation (exact same as Dart)
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    ]
    
    def __init__(self):
        self.last_request_time = None
        self.request_count = 0
        self.session = requests.Session()
    
    def _apply_rate_limit(self):
        """Apply intelligent rate limiting (EXACT same as Dart)"""
        now = datetime.now()
        
        # Reset counter every minute (exact same as Dart)
        if (self.last_request_time is None or 
            (now - self.last_request_time).total_seconds() >= 60):
            self.request_count = 0
        
        # Check if we're hitting rate limits (exact same as Dart)
        if self.request_count >= self.MAX_REQUESTS_PER_MINUTE:
            wait_time = 60 - now.second
            log.info(f'🐌 Rate limit reached, waiting {wait_time}s')
            time.sleep(wait_time)
            self.request_count = 0
        
        # Add random delay between requests (EXACT same as Dart)
        delay_ms = self.MIN_REQUEST_DELAY * 1000 + random.randint(0, int((self.MAX_REQUEST_DELAY - self.MIN_REQUEST_DELAY) * 1000))
        delay_seconds = delay_ms / 1000.0
        time.sleep(delay_seconds)
        
        self.last_request_time = now
        self.request_count += 1
    
    def _get_anti_detection_headers(self) -> Dict[str, str]:
        """Generate anti-detection headers (exact same as Dart)"""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
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
    
    def _generate_random_crumb(self) -> str:
        """Generate random crumb parameter (exact same as Dart)"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(chars) for _ in range(11))
    
    def _is_us_market_symbol(self, symbol: str) -> bool:
        """Check if symbol is from US market (exact same as Dart)"""
        return not (symbol.endswith('.TA') or symbol.endswith('.TLV'))
    
    def _is_trading_day(self, date: datetime, is_us_market: bool) -> bool:
        """Check if date is a trading day (exact same logic as Dart)"""
        weekday = date.weekday()  # 0=Monday, 6=Sunday
        
        if is_us_market:
            # US markets: Monday-Friday (0-4)
            return 0 <= weekday <= 4
        else:
            # TASE markets: Sunday-Thursday (6, 0-3)
            return weekday == 6 or 0 <= weekday <= 3
    
    def _get_last_trading_day(self, symbol: str) -> datetime:
        """Get last complete trading day (exact same logic as Dart)"""
        now = datetime.now()
        is_us_market = self._is_us_market_symbol(symbol)
        
        current = now
        while True:
            if self._is_trading_day(current, is_us_market):
                # Check if market has closed
                if is_us_market:
                    # US market closes at 4:00 PM ET (simplified)
                    market_close_hour = 16
                else:
                    # TASE closes at 5:25 PM Israel time (simplified)
                    market_close_hour = 17
                
                if current.hour >= market_close_hour or current.date() < now.date():
                    return current.replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    # Market still open, use previous trading day
                    current -= timedelta(days=1)
            else:
                current -= timedelta(days=1)
    
    def _handle_rate_limiting(self):
        """Handle rate limiting response (exact same as Dart)"""
        # Increase delays for subsequent requests
        self.request_count += 10  # Penalty (exact same as Dart)
        log.info('🛡️ Applied rate limiting penalty')
    
    def fetch_stock_data(self, symbol: str, days: int = 50) -> Optional[List[StockData]]:
        """Fetch stock data with enhanced caching and anti-detection (exact same as Dart)"""
        try:
            log.info(f'📊 Fetching {days} days of data for {symbol}')
            
            # Apply rate limiting and anti-detection delay
            self._apply_rate_limit()
            
            last_trading_day = self._get_last_trading_day(symbol)
            start_date = last_trading_day - timedelta(days=days + 15)
            end_date = last_trading_day + timedelta(hours=23, minutes=59)
            
            # Build URL (exact same as Dart)
            params = {
                'period1': str(int(start_date.timestamp())),
                'period2': str(int(end_date.timestamp())),
                'interval': '1d',
                'includePrePost': 'false',
                'events': 'div,split',
                'crumb': self._generate_random_crumb(),
            }
            
            url = f"{self.BASE_URL}/{symbol}"
            
            log.info(f'Fetching {symbol} from {start_date.strftime("%d/%m/%Y")} to {end_date.strftime("%d/%m/%Y")}')
            
            # Execute request with retry and exponential backoff
            response = self._execute_with_retry(url, params)
            
            if response is None:
                log.error(f'❌ Failed to fetch {symbol} after all retries')
                return None
            
            if response.status_code != 200:
                log.error(f'❌ Error fetching {symbol}: HTTP {response.status_code}')
                if response.status_code in [503, 429]:
                    log.info('🛡️ Detected rate limiting - will increase delays')
                    self._handle_rate_limiting()
                return None
            
            data = response.json()
            
            if 'chart' not in data or not data['chart']['result']:
                log.error(f'❌ Yahoo Finance API error for {symbol}')
                return None
            
            stock_data_list = self._parse_yahoo_response(data, symbol)
            
            # Filter trading days only (exact same as Dart)
            is_us_market = self._is_us_market_symbol(symbol)
            trading_days_only = [
                data for data in stock_data_list 
                if self._is_trading_day(data.date, is_us_market)
            ]
            
            # Sort and take last N days (exact same as Dart)
            trading_days_only.sort(key=lambda x: x.date)
            result = trading_days_only[-days:] if len(trading_days_only) > days else trading_days_only
            
            log.info(f'✅ Successfully fetched {len(result)} trading days for {symbol}')
            return result
            
        except Exception as e:
            log.error(f'❌ Exception fetching data for {symbol}: {e}')
            return None
    
    def _execute_with_retry(self, url: str, params: Dict) -> Optional[requests.Response]:
        """Execute request with retry and exponential backoff (EXACT same as Dart)"""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                headers = self._get_anti_detection_headers()
                response = self.session.get(
                    url, 
                    params=params, 
                    headers=headers, 
                    timeout=self.TIMEOUT
                )
                
                if response.status_code == 200:
                    return response
                
                if response.status_code in [503, 429]:
                    if attempt < self.MAX_RETRIES:
                        # EXACT same backoff calculation as Dart
                        backoff_delay = self.RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                        log.warning(f'🔄 Rate limited, retrying in {backoff_delay}s (attempt {attempt}/{self.MAX_RETRIES})')
                        time.sleep(backoff_delay)
                        continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < self.MAX_RETRIES:
                    # EXACT same backoff calculation as Dart
                    backoff_delay = self.RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                    log.warning(f'🔄 Request failed, retrying in {backoff_delay}s: {e}')
                    time.sleep(backoff_delay)
                else:
                    log.error(f'❌ Max retries exceeded for {url}')
                    return None
        
        return None
    
    def _parse_yahoo_response(self, data: Dict, symbol: str) -> List[StockData]:
        """Parse Yahoo Finance response (exact same as Dart)"""
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        quotes = result['indicators']['quote'][0]
        
        opens = quotes.get('open', [])
        highs = quotes.get('high', [])
        lows = quotes.get('low', [])
        closes = quotes.get('close', [])
        volumes = quotes.get('volume', [])
        
        stock_data_list = []
        
        for i in range(len(timestamps)):
            # Skip days with null/invalid data (exact same as Dart)
            if (opens[i] is None or highs[i] is None or 
                lows[i] is None or closes[i] is None or volumes[i] is None or
                opens[i] <= 0 or closes[i] <= 0):
                continue
            
            stock_data_list.append(StockData(
                symbol=symbol,
                date=datetime.fromtimestamp(timestamps[i]),
                open=float(opens[i]),
                high=float(highs[i]),
                low=float(lows[i]),
                close=float(closes[i]),
                volume=int(volumes[i]),
            ))
        
        return stock_data_list
    
    def fetch_multiple_stocks_with_breaks(self, symbols: List[str], days: int = 50) -> Dict[str, List[StockData]]:
        """Fetch multiple stocks with extended breaks (EXTRA CONSERVATIVE)"""
        results = {}
        
        log.info(f'📊 Fetching data for {len(symbols)} stocks with conservative rate limiting...')
        
        # Shuffle symbols to appear more human-like (same as Dart)
        shuffled_symbols = symbols.copy()
        random.shuffle(shuffled_symbols)
        
        for i, symbol in enumerate(shuffled_symbols):
            log.info(f'📊 Downloading {symbol} ({i+1}/{len(symbols)})')
            
            data = self.fetch_stock_data(symbol, days=days)
            if data and len(data) > 0:
                results[symbol] = data
                log.info(f'✅ Downloaded {len(data)} days for {symbol}')
            else:
                log.warning(f'⚠️ No data received for {symbol}')
            
            # Add extra delay every 5 requests instead of 10 (MORE CONSERVATIVE)
            if (i + 1) % 5 == 0:
                extra_delay = 10 + random.randint(0, 10)  # 10-20 seconds
                log.info(f'😴 Taking extended break ({extra_delay}s) after {i + 1} requests')
                time.sleep(extra_delay)
            
            # Add small delay between every request (EXTRA SAFETY)
            elif i < len(shuffled_symbols) - 1:  # Don't delay after last symbol
                small_delay = 3 + random.randint(0, 3)  # 3-6 seconds
                log.info(f'⏱️ Brief pause ({small_delay}s) before next symbol')
                time.sleep(small_delay)
        
        log.info(f'✅ Successfully fetched data for {len(results)}/{len(symbols)} stocks')
        return results
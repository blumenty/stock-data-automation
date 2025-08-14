#!/usr/bin/env python3
"""
Polygon.io Service - Python Mirror of Dart Implementation
Fetches stock data with anti-detection measures and rate limiting
"""

import requests
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
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

class PolygonIOService:
    BASE_URL = "https://api.polygon.io"
    API_KEY = "ROtogV9CPMTJRqCrEfxsdbslehmHREeK"  # Same as your Dart implementation
    TIMEOUT = 30
    
    # Anti-detection measures (STRICT - exact same as Dart)
    MIN_REQUEST_DELAY = 12.0   # 12 seconds minimum = 5 requests per minute MAX
    RETRY_BACKOFF_BASE = 5     # 5 seconds base
    MAX_RETRIES = 3
    
    # Rate limiting (5 REQUESTS PER MINUTE MAX - Polygon.io free tier)
    MAX_REQUESTS_PER_MINUTE = 5  # Free tier limit
    request_count = 0
    last_request_time = None
    
    def __init__(self):
        self.session = requests.Session()
    
    def _weekday_name(self, weekday: int) -> str:
        """Get weekday name (exact same as Dart)"""
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return days[weekday]  # Python weekday: 0=Monday, 6=Sunday
    
    def _apply_rate_limit(self):
        """Apply intelligent rate limiting - 5 REQUESTS PER MINUTE MAX (Polygon.io free tier)"""
        now = datetime.now()
        
        # Reset counter every minute
        if self.last_request_time is None or (now - self.last_request_time).total_seconds() >= 60:
            self.request_count = 0
        
        # Check if we're hitting the 5 requests per minute limit
        if self.request_count >= self.MAX_REQUESTS_PER_MINUTE:
            wait_time = 60 - now.second
            log.info(f'🐌 Rate limit reached (5/min), waiting {wait_time}s')
            time.sleep(wait_time)
            self.request_count = 0
        
        # MANDATORY 12+ second delay between requests (ensures max 5 per minute)
        if self.last_request_time is not None:
            time_since_last = (now - self.last_request_time).total_seconds()
            if time_since_last < 12:
                wait_time = 12 - time_since_last
                log.info(f'⏳ Waiting {wait_time:.1f}s (12s minimum delay)...')
                time.sleep(wait_time)
        
        self.request_count += 1
        self.last_request_time = datetime.now()
        
        # After every 5 stocks, wait extra 2 minutes (since we hit the limit)
        if self.request_count >= 5:
            log.info('🛌 Hit 5 request limit, waiting 2 minutes before continuing...')
            time.sleep(15)  # 2 minutes
            self.request_count = 0
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for requests (exact same as Dart)"""
        return {
            'Accept': 'application/json',
            'User-Agent': 'StockShazam/1.0',
            'Connection': 'keep-alive',
        }
    
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
    
    def _get_last_complete_trading_day(self, symbol: str) -> datetime:
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
    
    def _calculate_start_date(self, end_date: datetime, required_days: int) -> datetime:
        """Calculate appropriate start date based on market and required days (exact same as Dart)"""
        # For S&P 500, account for weekends (5 trading days per week)
        # Add extra buffer to ensure we get enough trading days
        calendar_days = int(required_days * 1.5) + 10  # Extra buffer
        return end_date - timedelta(days=calendar_days)
    
    def _format_date_for_api(self, date: datetime) -> str:
        """Format date for Polygon.io API (YYYY-MM-DD) (exact same as Dart)"""
        return f"{date.year}-{date.month:02d}-{date.day:02d}"
    
    def fetch_stock_data(self, symbol: str, days: int = 30) -> Optional[List[StockData]]:
        """Fetch stock data with enhanced caching and anti-detection (exact same as Dart)"""
        try:
            log.info(f'📊 Fetching {days} days of data for {symbol} from Polygon.io...')
            
            # Apply rate limiting and anti-detection delay
            self._apply_rate_limit()
            
            # Calculate date range
            end_date = self._get_last_complete_trading_day(symbol)
            start_date = self._calculate_start_date(end_date, days)
            
            formatted_start_date = self._format_date_for_api(start_date)
            formatted_end_date = self._format_date_for_api(end_date)
            
            log.info(f'📅 Date range: {formatted_start_date} to {formatted_end_date}')
            
            # Build Polygon.io URL for aggregated bars (daily data)
            url = f"{self.BASE_URL}/v2/aggs/ticker/{symbol}/range/1/day/{formatted_start_date}/{formatted_end_date}"
            params = {
                'adjusted': 'true',
                'sort': 'asc',
                'limit': '50000',
                'apikey': self.API_KEY
            }
            
            # Execute request with retry and exponential backoff
            response = self._execute_with_retry(url, params)
            
            if response is None:
                log.error(f'❌ Failed to fetch {symbol} after all retries')
                return None
            
            if response.status_code != 200:
                log.error(f'❌ Error fetching {symbol}: HTTP {response.status_code}')
                if response.status_code in [503, 429]:
                    log.info('🛡️ Detected rate limiting - will increase delays')
                return None
            
            data = response.json()
            
            if data.get('status') != 'OK' or not data.get('results'):
                log.error(f'❌ Polygon.io API error for {symbol}: {data.get("status", "Unknown")}')
                return None
            
            stock_data_list = self._parse_polygon_response(data, symbol)
            
            # Filter trading days only (exact same as Dart)
            is_us_market = self._is_us_market_symbol(symbol)
            trading_days_only = [
                data for data in stock_data_list 
                if self._is_trading_day(data.date, is_us_market)
            ]
            
            # Sort and take last N days (exact same as Dart)
            trading_days_only.sort(key=lambda x: x.date)
            result = trading_days_only[-days:] if len(trading_days_only) > days else trading_days_only
            
            log.info(f'✅ Successfully fetched {len(result)} trading days for {symbol} from Polygon.io')
            return result
            
        except Exception as e:
            log.error(f'❌ Exception fetching data for {symbol} from Polygon.io: {e}')
            return None
    
    def _execute_with_retry(self, url: str, params: Dict) -> Optional[requests.Response]:
        """Execute request with retry and exponential backoff (exact same as Dart)"""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                headers = self._get_headers()
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
                        # Exact same backoff calculation as Dart
                        backoff_delay = self.RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                        log.warning(f'🔄 Rate limited, retrying in {backoff_delay}s (attempt {attempt}/{self.MAX_RETRIES})')
                        time.sleep(backoff_delay)
                        continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < self.MAX_RETRIES:
                    # Exact same backoff calculation as Dart
                    backoff_delay = self.RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                    log.warning(f'🔄 Request failed, retrying in {backoff_delay}s: {e}')
                    time.sleep(backoff_delay)
                else:
                    log.error(f'❌ Max retries exceeded for {url}')
                    return None
        
        return None
    
    def _parse_polygon_response(self, data: Dict, symbol: str) -> List[StockData]:
        """Parse Polygon.io response (exact same as Dart)"""
        if data['status'] != 'OK' or data['results'] is None:
            log.error(f'❌ Polygon.io API returned error status: {data["status"]}')
            return []
        
        results = data['results']
        stock_data_list = []
        
        log.info(f'🔍 RAW POLYGON.IO DATA for {symbol}:')
        
        for i, result in enumerate(results):
            try:
                # Polygon.io timestamp is in milliseconds
                timestamp = result['t']
                date = datetime.fromtimestamp(timestamp / 1000)
                
                open_price = float(result['o'])
                high = float(result['h'])
                low = float(result['l'])
                close = float(result['c'])
                volume = int(result['v'])
                
                weekday = date.weekday()
                weekday_name = self._weekday_name(weekday)
                log.info(f'📅 Raw data[{i}]: {date.strftime("%d/%m/%Y")} ({weekday_name}) - O:{open_price} H:{high} L:{low} C:{close} V:{volume}')
                
                # Skip days with invalid data (exact same as Dart)
                if open_price <= 0 or high <= 0 or low <= 0 or close <= 0 or volume <= 0:
                    log.warning(f'⚠️ SKIPPING invalid data for {date.strftime("%d/%m/%Y")}: O:{open_price} C:{close} V:{volume}')
                    continue
                
                stock_data_list.append(StockData(
                    symbol=symbol,
                    date=date,
                    open=open_price,
                    high=high,
                    low=low,
                    close=close,
                    volume=volume,
                ))
                
            except Exception as e:
                log.warning(f'⚠️ Error parsing result {i}: {e}')
                continue
        
        log.info(f'🔍 Parsed {len(stock_data_list)} valid records from {len(results)} raw results')
        return stock_data_list
    
    def fetch_multiple_stocks_with_breaks(self, symbols: List[str], days: int = 30) -> Dict[str, List[StockData]]:
        """Fetch multiple stocks with STRICT 5-per-minute rate limiting"""
        results = {}
        
        log.info(f'📊 Fetching data for {len(symbols)} stocks with STRICT 5-per-minute rate limiting...')
        log.info(f'⏱️ Estimated time: {len(symbols) * 12 / 60:.1f} minutes (12s per stock minimum)')
        
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
            
            # Every 5 requests = 2 minute mandatory break (free tier limit)
            if (i + 1) % 5 == 0 and i < len(shuffled_symbols) - 1:
                log.info(f'😴 Mandatory 2-minute break after 5 requests (free tier limit)')
                time.sleep(120)  # 2 minutes
            
            # Log progress
            if (i + 1) % 10 == 0:
                elapsed_time = (i + 1) * 12 / 60  # Minimum time elapsed
                remaining_time = (len(shuffled_symbols) - (i + 1)) * 12 / 60
                log.info(f'📈 Progress: {i+1}/{len(shuffled_symbols)} ({elapsed_time:.1f}m elapsed, {remaining_time:.1f}m remaining)')
        
        log.info(f'✅ Successfully fetched data for {len(results)}/{len(symbols)} stocks')
        return results
    
    def check_service_health(self) -> Dict[str, any]:
        """Check service health and connectivity (exact same as Dart)"""
        try:
            # Test with a simple S&P 500 stock
            test_symbol = 'AAPL'
            start_time = datetime.now()
            
            url = f"{self.BASE_URL}/v2/aggs/ticker/{test_symbol}/range/1/day/2025-08-01/2025-08-01"
            params = {'apikey': self.API_KEY}
            
            response = self.session.get(url, params=params, timeout=self.TIMEOUT)
            response_time = datetime.now() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'isHealthy': True,
                    'responseTime': response_time.total_seconds() * 1000,  # milliseconds
                    'status': 'Connected',
                    'apiLimitRemaining': response.headers.get('x-ratelimit-remaining'),
                    'testSymbol': test_symbol,
                }
            else:
                return {
                    'isHealthy': False,
                    'error': f'HTTP {response.status_code}',
                    'status': 'API Error',
                    'responseTime': response_time.total_seconds() * 1000,
                }
        except Exception as e:
            return {
                'isHealthy': False,
                'error': str(e),
                'status': 'Disconnected',
            }
#!/usr/bin/env python3
"""
Earnings & Dividends Service - Fetches upcoming dividend and earnings dates
"""

import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)

@dataclass
class DividendEarningsData:
    symbol: str
    date: datetime
    next_div_date: Optional[str]
    next_earn_date: Optional[str]

class EarningsDividendsService:
    BASE_URL = "https://api.polygon.io"
    API_KEY = "ROtogV9CPMTJRqCrEfxsdbslehmHREeK"
    TIMEOUT = 30
    MIN_REQUEST_DELAY = 12.0  # 5 requests per minute max
    
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = None
    
    def _apply_rate_limit(self):
        """Apply rate limiting - 5 requests per minute"""
        if self.last_request_time is not None:
            time_since_last = (datetime.now() - self.last_request_time).total_seconds()
            if time_since_last < self.MIN_REQUEST_DELAY:
                wait_time = self.MIN_REQUEST_DELAY - time_since_last
                log.info(f'⏳ Waiting {wait_time:.1f}s (12s minimum delay)...')
                time.sleep(wait_time)
        
        self.last_request_time = datetime.now()
    
    def _get_next_saturday(self) -> datetime:
        """Get the next Saturday date"""
        today = datetime.now()
        days_ahead = 5 - today.weekday()  # Saturday is 5
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days=days_ahead)
    
    def fetch_next_dividend(self, symbol: str, from_date: str) -> Optional[str]:
        """Fetch next dividend date for a symbol"""
        try:
            self._apply_rate_limit()
            
            url = f"{self.BASE_URL}/v3/reference/dividends"
            params = {
                'ticker': symbol,
                'ex_dividend_date.gte': from_date,
                'order': 'asc',
                'limit': 1,
                'sort': 'ex_dividend_date',
                'apiKey': self.API_KEY
            }
            
            response = self.session.get(url, params=params, timeout=self.TIMEOUT)
            
            if response.status_code != 200:
                log.warning(f'⚠️ Dividend API error for {symbol}: HTTP {response.status_code}')
                return None
            
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('results'):
                next_div = data['results'][0]
                div_date = next_div.get('ex_dividend_date')
                log.info(f'✅ {symbol}: Next dividend {div_date}')
                return div_date
            
            log.info(f'ℹ️ {symbol}: No upcoming dividends')
            return None
            
        except Exception as e:
            log.error(f'❌ Error fetching dividend for {symbol}: {e}')
            return None
    
    def fetch_dividend_earnings_data(self, symbols: list) -> Dict[str, DividendEarningsData]:
        """Fetch dividend and earnings data for all symbols"""
        results = {}
        saturday = self._get_next_saturday()
        from_date = saturday.strftime('%Y-%m-%d')
        
        log.info(f'📊 Fetching dividend data for {len(symbols)} symbols from {from_date}')
        
        for i, symbol in enumerate(symbols):
            log.info(f'📊 Processing {symbol} ({i+1}/{len(symbols)})')
            
            next_div = self.fetch_next_dividend(symbol, from_date)
            
            results[symbol] = DividendEarningsData(
                symbol=symbol,
                date=datetime.now(),
                next_div_date=next_div,
                next_earn_date=None  # Earnings will be added later
            )
            
            # Break every 5 requests (free tier limit)
            if (i + 1) % 5 == 0 and i < len(symbols) - 1:
                log.info('😴 Mandatory 2-minute break after 5 requests')
                time.sleep(120)
        
        log.info(f'✅ Completed dividend data fetch for {len(results)} symbols')

        return results


#!/usr/bin/env python3
"""
Interactive Brokers (IBKR) Service - Python Service for TASE (Tel Aviv Stock Exchange) Stocks
Similar logic to Polygon.io Service but adapted for IBKR API

REQUIREMENTS:
1. TWS (Trader Workstation) or IB Gateway must be running
2. API must be enabled in TWS/Gateway settings (default port: 7497 for TWS, 4001 for Gateway)
3. Market data subscription for TASE (or use delayed data)
4. Install: pip install ib_insync pandas

RATE LIMITS (IBKR is MORE GENEROUS than Polygon.io):
- No identical historical data requests within 15 seconds
- No more than 6 requests for same contract within 2 seconds  
- No more than 60 requests in any 10-minute period
- No more than 50 outstanding requests at a time

COMPARISON WITH POLYGON.IO:
- Polygon.io free tier: 5 requests per minute (very restrictive)
- IBKR: ~6 requests per minute sustained (60 per 10 min), more generous
- IBKR requires running TWS/Gateway, Polygon.io is pure REST API
"""

import time
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)

@dataclass
class StockData:
    """Stock data class matching Polygon.io service structure"""
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class IBKRService:
    """
    Interactive Brokers Service for TASE (Tel Aviv Stock Exchange) Stocks
    
    This service connects to TWS or IB Gateway to fetch historical stock data
    for Israeli stocks listed on the Tel Aviv Stock Exchange.
    """
    
    # Connection settings
    DEFAULT_HOST = '127.0.0.1'
    DEFAULT_TWS_PORT = 7497      # TWS default port
    DEFAULT_GATEWAY_PORT = 4001  # IB Gateway default port
    DEFAULT_CLIENT_ID = 1
    TIMEOUT = 30
    
    # Rate limiting (IBKR is more generous than Polygon.io)
    # Polygon.io free tier: 5 requests/minute = 12s minimum delay
    # IBKR: 60 requests/10 minutes = 10s average, but we use 15s for safety
    MIN_REQUEST_DELAY = 10.0      # 10 seconds minimum (vs 12s for Polygon)
    IDENTICAL_REQUEST_DELAY = 15  # Must wait 15s for identical requests
    MAX_REQUESTS_PER_10MIN = 60   # IBKR limit
    MAX_RETRIES = 4
    RETRY_BACKOFF_BASE = 5
    
    # Track requests for rate limiting
    request_timestamps: List[datetime] = []
    last_request_time: Optional[datetime] = None
    
    def __init__(self, host: str = None, port: int = None, client_id: int = None, use_gateway: bool = False):
        """
        Initialize IBKR Service
        
        Args:
            host: TWS/Gateway host (default: 127.0.0.1)
            port: TWS/Gateway port (default: 7497 for TWS, 4001 for Gateway)
            client_id: Unique client ID for this connection
            use_gateway: If True, use IB Gateway port instead of TWS
        """
        self.host = host or self.DEFAULT_HOST
        self.port = port or (self.DEFAULT_GATEWAY_PORT if use_gateway else self.DEFAULT_TWS_PORT)
        self.client_id = client_id or self.DEFAULT_CLIENT_ID
        self.ib = None
        self._connected = False
        
    def _weekday_name(self, weekday: int) -> str:
        """Get weekday name (exact same as Dart/Polygon service)"""
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return days[weekday]
    
    def _is_tase_trading_day(self, date: datetime) -> bool:
        """
        Check if date is a TASE trading day
        TASE markets: Sunday-Thursday (weekday 6, 0-3 in Python where 0=Monday)
        
        Note: Python weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday
        """
        weekday = date.weekday()
        # Sunday=6, Monday=0, Tuesday=1, Wednesday=2, Thursday=3
        return weekday == 6 or 0 <= weekday <= 3
    
    def _convert_symbol_for_ibkr(self, yahoo_symbol: str) -> str:
        """
        Convert Yahoo Finance symbol format to IBKR format
        Yahoo: TEVA.TA -> IBKR: TEVA
        """
        if yahoo_symbol.endswith('.TA') or yahoo_symbol.endswith('.TLV'):
            return yahoo_symbol.replace('.TA', '').replace('.TLV', '')
        return yahoo_symbol
    
    def _convert_symbol_to_yahoo(self, ibkr_symbol: str) -> str:
        """
        Convert IBKR symbol format back to Yahoo Finance format
        IBKR: TEVA -> Yahoo: TEVA.TA
        """
        if not ibkr_symbol.endswith('.TA'):
            return f"{ibkr_symbol}.TA"
        return ibkr_symbol
    
    def _apply_rate_limit(self):
        """
        Apply intelligent rate limiting for IBKR
        
        IBKR limits:
        - 60 requests per 10 minutes
        - 15 second minimum between identical requests
        - 10 second safe delay between any requests
        """
        now = datetime.now()
        
        # Clean old timestamps (older than 10 minutes)
        cutoff = now - timedelta(minutes=10)
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > cutoff]
        
        # Check if we're approaching the 60 requests per 10 minutes limit
        if len(self.request_timestamps) >= self.MAX_REQUESTS_PER_10MIN - 5:
            # Calculate time until oldest request falls off
            oldest = min(self.request_timestamps)
            wait_time = (oldest + timedelta(minutes=10) - now).total_seconds()
            if wait_time > 0:
                log.info(f'🐌 Approaching rate limit ({len(self.request_timestamps)}/60 in 10min), waiting {wait_time:.1f}s')
                time.sleep(wait_time + 1)  # +1 for safety
        
        # Minimum delay between requests (10 seconds for IBKR vs 12 for Polygon)
        if self.last_request_time is not None:
            time_since_last = (now - self.last_request_time).total_seconds()
            if time_since_last < self.MIN_REQUEST_DELAY:
                wait_time = self.MIN_REQUEST_DELAY - time_since_last
                log.info(f'⏳ Waiting {wait_time:.1f}s (10s minimum delay for IBKR)...')
                time.sleep(wait_time)
        
        self.request_timestamps.append(datetime.now())
        self.last_request_time = datetime.now()
    
    def _get_last_complete_trading_day(self) -> datetime:
        """
        Get last complete TASE trading day
        TASE closes at 5:25 PM Israel time
        """
        now = datetime.now()
        current = now
        
        while True:
            if self._is_tase_trading_day(current):
                # TASE closes at 17:25 Israel time
                market_close_hour = 17
                market_close_minute = 25
                
                if current.date() < now.date():
                    # Previous days are always complete
                    return current.replace(hour=0, minute=0, second=0, microsecond=0)
                elif current.hour > market_close_hour or (current.hour == market_close_hour and current.minute >= market_close_minute):
                    # Today's market has closed
                    return current.replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    # Market still open, use previous trading day
                    current -= timedelta(days=1)
            else:
                current -= timedelta(days=1)
    
    def _calculate_duration_string(self, days: int) -> str:
        """
        Calculate IBKR duration string for historical data request
        Format: "X D" for days, "X W" for weeks, "X M" for months, "X Y" for years
        """
        if days <= 365:
            return f"{days} D"
        else:
            # Convert to months for longer periods
            months = days // 30
            return f"{months} M"
    
    def connect(self) -> bool:
        """
        Connect to TWS or IB Gateway
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            from ib_insync import IB, util
            
            log.info(f'🔌 Connecting to IBKR at {self.host}:{self.port} (clientId={self.client_id})...')
            
            self.ib = IB()
            self.ib.connect(self.host, self.port, clientId=self.client_id, timeout=self.TIMEOUT)
            
            self._connected = True
            log.info(f'✅ Connected to IBKR successfully')
            return True
            
        except ImportError:
            log.error('❌ ib_insync not installed. Run: pip install ib_insync')
            return False
        except Exception as e:
            log.error(f'❌ Failed to connect to IBKR: {e}')
            log.error('Make sure TWS or IB Gateway is running and API is enabled')
            return False
    
    def disconnect(self):
        """Disconnect from TWS/Gateway"""
        if self.ib and self._connected:
            self.ib.disconnect()
            self._connected = False
            log.info('🔌 Disconnected from IBKR')
    
    def _create_tase_contract(self, symbol: str):
        """
        Create a contract for TASE stocks
        
        Args:
            symbol: Stock symbol (can be Yahoo format like TEVA.TA or plain like TEVA)
        
        Returns:
            ib_insync Stock contract
        """
        from ib_insync import Stock
        
        # Convert Yahoo symbol to IBKR format
        ibkr_symbol = self._convert_symbol_for_ibkr(symbol)
        
        # Create contract for TASE
        contract = Stock(
            symbol=ibkr_symbol,
            exchange='TASE',      # Tel Aviv Stock Exchange
            currency='ILS'        # Israeli Shekel
        )
        
        return contract
    
    def fetch_stock_data(self, symbol: str, days: int = 30) -> Optional[List[StockData]]:
        """
        Fetch stock data from IBKR (same interface as Polygon.io service)
        
        Args:
            symbol: Stock symbol (Yahoo format like TEVA.TA or plain like TEVA)
            days: Number of trading days to fetch
            
        Returns:
            List of StockData objects, or None if failed
        """
        if not self._connected:
            if not self.connect():
                return None
        
        try:
            from ib_insync import util
            
            log.info(f'📊 Fetching {days} days of data for {symbol} from IBKR...')
            
            # Apply rate limiting
            self._apply_rate_limit()
            
            # Create contract
            contract = self._create_tase_contract(symbol)
            
            # Qualify contract to get full details
            try:
                qualified = self.ib.qualifyContracts(contract)
                if not qualified:
                    log.error(f'❌ Could not qualify contract for {symbol}')
                    return None
                contract = qualified[0]
                log.info(f'✅ Qualified contract: {contract}')
            except Exception as e:
                log.warning(f'⚠️ Could not qualify contract for {symbol}: {e}')
                # Try to proceed anyway
            
            # Calculate date range
            end_date = self._get_last_complete_trading_day()
            duration = self._calculate_duration_string(int(days * 1.5) + 10)  # Extra buffer
            
            log.info(f'📅 Requesting {duration} of data ending at {end_date.strftime("%Y%m%d")}')
            
            # Request historical data
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime=end_date.strftime('%Y%m%d %H:%M:%S'),
                durationStr=duration,
                barSizeSetting='1 day',
                whatToShow='TRADES',
                useRTH=True,           # Regular trading hours only
                formatDate=1,          # Format as YYYYMMDD
                keepUpToDate=False
            )
            
            if not bars:
                log.error(f'❌ No data received for {symbol}')
                return None
            
            # Parse response
            stock_data_list = self._parse_ibkr_response(bars, symbol)
            
            # Filter trading days only
            trading_days_only = [
                data for data in stock_data_list 
                if self._is_tase_trading_day(data.date)
            ]
            
            # Sort and take last N days
            trading_days_only.sort(key=lambda x: x.date)
            result = trading_days_only[-days:] if len(trading_days_only) > days else trading_days_only
            
            log.info(f'✅ Successfully fetched {len(result)} trading days for {symbol} from IBKR')
            return result
            
        except Exception as e:
            log.error(f'❌ Exception fetching data for {symbol} from IBKR: {e}')
            return None
    
    def _parse_ibkr_response(self, bars, symbol: str) -> List[StockData]:
        """
        Parse IBKR historical data response
        
        Args:
            bars: List of BarData objects from IBKR
            symbol: Original symbol (for logging)
            
        Returns:
            List of StockData objects
        """
        stock_data_list = []
        
        # Keep Yahoo format for symbol in output
        yahoo_symbol = self._convert_symbol_to_yahoo(self._convert_symbol_for_ibkr(symbol))
        
        log.info(f'🔍 RAW IBKR DATA for {symbol}:')
        
        for i, bar in enumerate(bars):
            try:
                # IBKR date format depends on formatDate parameter
                if hasattr(bar.date, 'date'):
                    # datetime object
                    date = bar.date
                else:
                    # String format YYYYMMDD
                    date = datetime.strptime(str(bar.date), '%Y%m%d')
                
                open_price = float(bar.open)
                high = float(bar.high)
                low = float(bar.low)
                close = float(bar.close)
                volume = int(bar.volume) if bar.volume >= 0 else 0
                
                weekday = date.weekday()
                weekday_name = self._weekday_name(weekday)
                log.info(f'📅 Raw data[{i}]: {date.strftime("%d/%m/%Y")} ({weekday_name}) - O:{open_price:.2f} H:{high:.2f} L:{low:.2f} C:{close:.2f} V:{volume}')
                
                # Skip days with invalid data
                if open_price <= 0 or high <= 0 or low <= 0 or close <= 0:
                    log.warning(f'⚠️ SKIPPING invalid data for {date.strftime("%d/%m/%Y")}: O:{open_price} C:{close}')
                    continue
                
                stock_data_list.append(StockData(
                    symbol=yahoo_symbol,
                    date=date,
                    open=open_price,
                    high=high,
                    low=low,
                    close=close,
                    volume=volume,
                ))
                
            except Exception as e:
                log.warning(f'⚠️ Error parsing bar {i}: {e}')
                continue
        
        log.info(f'🔍 Parsed {len(stock_data_list)} valid records from {len(bars)} raw results')
        return stock_data_list
    
    def fetch_multiple_stocks_with_breaks(self, symbols: List[str], days: int = 30) -> Dict[str, List[StockData]]:
        """
        Fetch multiple stocks with rate limiting (same interface as Polygon.io service)
        
        IBKR is more generous: 60 requests per 10 minutes vs Polygon's 5 per minute
        
        Args:
            symbols: List of stock symbols
            days: Number of trading days to fetch
            
        Returns:
            Dictionary mapping symbol to list of StockData
        """
        results = {}
        
        # Estimated time: IBKR allows ~6 requests/minute vs Polygon's 5/minute
        est_time = len(symbols) * self.MIN_REQUEST_DELAY / 60
        
        log.info(f'📊 Fetching data for {len(symbols)} TASE stocks with IBKR rate limiting...')
        log.info(f'⏱️ Estimated time: {est_time:.1f} minutes (10s per stock for IBKR)')
        
        # Shuffle symbols to appear more human-like
        shuffled_symbols = symbols.copy()
        random.shuffle(shuffled_symbols)
        
        # Connect once for all requests
        if not self._connected:
            if not self.connect():
                return results
        
        try:
            for i, symbol in enumerate(shuffled_symbols):
                log.info(f'📊 Downloading {symbol} ({i+1}/{len(symbols)})')
                
                data = self.fetch_stock_data(symbol, days=days)
                if data and len(data) > 0:
                    results[symbol] = data
                    log.info(f'✅ Downloaded {len(data)} days for {symbol}')
                else:
                    log.warning(f'⚠️ No data received for {symbol}')
                
                # Log progress every 10 stocks
                if (i + 1) % 10 == 0:
                    elapsed_time = (i + 1) * self.MIN_REQUEST_DELAY / 60
                    remaining_time = (len(shuffled_symbols) - (i + 1)) * self.MIN_REQUEST_DELAY / 60
                    log.info(f'📈 Progress: {i+1}/{len(shuffled_symbols)} ({elapsed_time:.1f}m elapsed, {remaining_time:.1f}m remaining)')
                
                # Take a longer break every 50 stocks to be safe
                if (i + 1) % 50 == 0 and i < len(shuffled_symbols) - 1:
                    log.info(f'😴 Taking 30s break after 50 requests...')
                    time.sleep(30)
                    
        finally:
            # Disconnect when done
            self.disconnect()
        
        log.info(f'✅ Successfully fetched data for {len(results)}/{len(symbols)} stocks')
        return results
    
    def check_service_health(self) -> Dict[str, any]:
        """
        Check service health and connectivity
        
        Returns:
            Dictionary with health status
        """
        try:
            start_time = datetime.now()
            
            if not self._connected:
                if not self.connect():
                    return {
                        'isHealthy': False,
                        'error': 'Could not connect to TWS/Gateway',
                        'status': 'Disconnected',
                    }
            
            # Test with a simple request
            accounts = self.ib.managedAccounts()
            response_time = datetime.now() - start_time
            
            return {
                'isHealthy': True,
                'responseTime': response_time.total_seconds() * 1000,  # milliseconds
                'status': 'Connected',
                'accounts': accounts,
                'host': self.host,
                'port': self.port,
            }
            
        except Exception as e:
            return {
                'isHealthy': False,
                'error': str(e),
                'status': 'Error',
            }
    
    def request_delayed_data(self):
        """
        Request delayed market data (15-minute delay)
        Use this if you don't have a market data subscription for TASE
        """
        if self.ib:
            self.ib.reqMarketDataType(3)  # 3 = Delayed data
            log.info('📡 Switched to delayed market data (15-minute delay)')
    
    def request_live_data(self):
        """
        Request live market data
        Requires market data subscription for TASE
        """
        if self.ib:
            self.ib.reqMarketDataType(1)  # 1 = Live data
            log.info('📡 Switched to live market data')


# TA-125 Stocks for IBKR (same list, converted to IBKR format)
TA125_STOCKS_IBKR = [
    # These are the same stocks from your Dart implementation
    # Comment/uncomment as needed
    
    # Banks & Financial Services
    # 'DSCT', 'POLI', 'LUMI', 'MZTF', 'FIBI', 'IBI',
    # 'AMOT', 'EQTL', 'MTAV', 'ISRS', 'MNIF', 'TASE',
    # 'KEN', 'HARL', 'CLIS', 'MMHD', 'MGDL', 'ISCD',
    
    # Technology & Healthcare
    # 'TEVA', 'ESLT', 'NVMI', 'NICE', 'TSEM', 'CAMT',
    # 'NYAX', 'ONE', 'SPNS', 'FORTY', 'MTRX', 'HLAN',
    # 'MGIC', 'TLSY', 'MLTM', 'NXSN', 'PRTC',
    
    # ... add more as needed
]


def main():
    """Example usage of IBKR Service"""
    
    # Create service (will connect to TWS on default port 7497)
    service = IBKRService()
    
    # Check health
    print("\n=== Checking Service Health ===")
    health = service.check_service_health()
    print(f"Health: {health}")
    
    if not health['isHealthy']:
        print("\n❌ Service is not healthy. Make sure:")
        print("   1. TWS or IB Gateway is running")
        print("   2. API is enabled in TWS/Gateway settings")
        print("   3. Port 7497 (TWS) or 4001 (Gateway) is correct")
        return
    
    # Request delayed data if you don't have a subscription
    service.request_delayed_data()
    
    # Fetch single stock
    print("\n=== Fetching Single Stock ===")
    data = service.fetch_stock_data('TEVA.TA', days=30)
    if data:
        print(f"Got {len(data)} days of data for TEVA")
        for d in data[-5:]:  # Print last 5 days
            print(f"  {d.date.strftime('%Y-%m-%d')}: O={d.open:.2f} H={d.high:.2f} L={d.low:.2f} C={d.close:.2f} V={d.volume}")
    
    # Fetch multiple stocks
    print("\n=== Fetching Multiple Stocks ===")
    test_symbols = ['TEVA.TA', 'NICE.TA', 'ESLT.TA']  # Small test batch
    results = service.fetch_multiple_stocks_with_breaks(test_symbols, days=30)
    print(f"Successfully fetched: {list(results.keys())}")
    
    # Disconnect
    service.disconnect()


if __name__ == '__main__':
    main()

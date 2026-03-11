#!/usr/bin/env python3
"""
Yahoo Finance Service - Python mirror of Dart implementation.
Fetches TASE / IL stock data with anti-detection, IP rotation,
real crumb/cookie session management, and correct UTC date parsing.
"""

import requests
import json
import time
import random
import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# TASE trading-day schedule
#   Before 05 Jan 2026 : Sun–Thu  (weekday 6, 0-3 in Python)
#   From   05 Jan 2026 : Mon–Fri  (weekday 0-4 in Python)
# ---------------------------------------------------------------------------
TASE_SCHEDULE_CHANGE = date(2026, 1, 5)


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
    BASE_URL  = 'https://query1.finance.yahoo.com/v8/finance/chart'
    CRUMB_URL = 'https://query1.finance.yahoo.com/v1/test/getcrumb'
    CONSENT_URL = 'https://finance.yahoo.com/'
    TIMEOUT = 30

    # Delays (seconds) — kept conservative for a server/CI context
    MIN_DELAY      = 2.0
    MAX_DELAY      = 6.0
    BATCH_BREAK    = 12.0   # extra pause every BATCH_SIZE requests
    BATCH_SIZE     = 10
    RETRY_BASE     = 5      # seconds, doubles per attempt
    MAX_RETRIES    = 5

    MAX_REQ_PER_MIN = 20

    # Modern user-agents (Chrome 131 / Firefox 133 / Safari 17 — early 2025)
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    ]

    # Random IP pools for X-Forwarded-For spoofing
    _IP_RANGES = [
        # Residential-looking ranges
        ('82.80.0.0',   '82.80.255.255'),
        ('84.94.0.0',   '84.94.255.255'),
        ('93.172.0.0',  '93.172.255.255'),
        ('109.64.0.0',  '109.64.255.255'),
        ('151.200.0.0', '151.200.255.255'),
        ('176.12.0.0',  '176.12.255.255'),
        ('188.120.0.0', '188.120.255.255'),
        ('212.143.0.0', '212.143.255.255'),
        ('5.100.0.0',   '5.100.255.255'),
        ('37.26.0.0',   '37.26.255.255'),
    ]

    def __init__(self):
        self._session = requests.Session()
        self._crumb: Optional[str] = None
        self._last_req_time: Optional[datetime] = None
        self._req_count = 0

    # -----------------------------------------------------------------------
    # Session / crumb bootstrap
    # -----------------------------------------------------------------------

    def _bootstrap_session(self) -> bool:
        """
        Visit Yahoo Finance to pick up cookies, then fetch a real crumb.
        This is required since Yahoo deprecated the fake-crumb approach.
        Returns True on success.
        """
        try:
            log.info('🔑 Bootstrapping Yahoo Finance session (cookie + crumb)…')
            headers = self._base_headers()
            # Step 1 – land on the home page to get consent cookie
            r = self._session.get(
                self.CONSENT_URL,
                headers=headers,
                timeout=self.TIMEOUT,
                allow_redirects=True,
            )
            if r.status_code not in (200, 301, 302):
                log.warning(f'⚠️ Consent page returned {r.status_code}')

            time.sleep(random.uniform(1.0, 2.5))

            # Step 2 – fetch a real crumb
            crumb_headers = self._base_headers()
            crumb_headers['Referer'] = 'https://finance.yahoo.com/'
            r2 = self._session.get(
                self.CRUMB_URL,
                headers=crumb_headers,
                timeout=self.TIMEOUT,
            )
            if r2.status_code == 200 and r2.text.strip():
                self._crumb = r2.text.strip()
                log.info(f'✅ Got real crumb: {self._crumb[:6]}…')
                return True
            else:
                log.warning(f'⚠️ Crumb fetch returned {r2.status_code}, falling back to random crumb')
                self._crumb = self._random_crumb()
                return False
        except Exception as e:
            log.warning(f'⚠️ Session bootstrap failed: {e}  — using random crumb')
            self._crumb = self._random_crumb()
            return False

    def _ensure_crumb(self):
        if self._crumb is None:
            self._bootstrap_session()

    # -----------------------------------------------------------------------
    # Header / IP helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _random_ip() -> str:
        start_ip, end_ip = random.choice(YahooFinanceService._IP_RANGES)
        parts_s = [int(p) for p in start_ip.split('.')]
        parts_e = [int(p) for p in end_ip.split('.')]
        ip = '.'.join(
            str(random.randint(parts_s[i], parts_e[i])) for i in range(4)
        )
        return ip

    def _base_headers(self) -> Dict[str, str]:
        ua = random.choice(self.USER_AGENTS)
        ip = self._random_ip()
        # Pick a realistic sec-ch-ua for Chrome or skip for Firefox/Safari
        is_chrome = 'Chrome' in ua
        headers: Dict[str, str] = {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
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
            # Fake-IP headers (some CDNs/proxies forward these; Yahoo may respect them)
            'X-Forwarded-For': ip,
            'X-Real-IP': ip,
            'Via': f'1.1 {ip}',
        }
        if is_chrome:
            chrome_ver = ua.split('Chrome/')[1].split('.')[0]
            headers['sec-ch-ua'] = f'"Google Chrome";v="{chrome_ver}", "Chromium";v="{chrome_ver}", "Not-A.Brand";v="99"'
            headers['sec-ch-ua-mobile'] = '?1' if 'Mobile' in ua else '?0'
            headers['sec-ch-ua-platform'] = '"Android"' if 'Android' in ua else ('"macOS"' if 'Mac' in ua else '"Windows"')
        return headers

    @staticmethod
    def _random_crumb() -> str:
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(chars) for _ in range(11))

    # -----------------------------------------------------------------------
    # Rate limiting
    # -----------------------------------------------------------------------

    def _rate_limit(self):
        now = datetime.now()
        if (self._last_req_time is None or
                (now - self._last_req_time).total_seconds() >= 60):
            self._req_count = 0

        if self._req_count >= self.MAX_REQ_PER_MIN:
            wait = max(1, 60 - now.second)
            log.info(f'🐌 Rate limit reached, waiting {wait}s')
            time.sleep(wait)
            self._req_count = 0

        delay = self.MIN_DELAY + random.uniform(0, self.MAX_DELAY - self.MIN_DELAY)
        time.sleep(delay)
        self._last_req_time = now
        self._req_count += 1

    # -----------------------------------------------------------------------
    # Trading-day logic (TASE + US)
    # -----------------------------------------------------------------------

    @staticmethod
    def _is_il_symbol(symbol: str) -> bool:
        return symbol.endswith('.TA') or symbol.endswith('.TLV')

    @staticmethod
    def _is_tase_trading_day(d: date) -> bool:
        wd = d.weekday()  # Mon=0 … Sun=6
        if d >= TASE_SCHEDULE_CHANGE:
            return 0 <= wd <= 4   # Mon–Fri
        else:
            return wd == 6 or 0 <= wd <= 3  # Sun–Thu

    @staticmethod
    def _is_us_trading_day(d: date) -> bool:
        return 0 <= d.weekday() <= 4   # Mon–Fri

    def _is_trading_day(self, d: date, is_il: bool) -> bool:
        return self._is_tase_trading_day(d) if is_il else self._is_us_trading_day(d)

    def _get_last_trading_day(self, symbol: str) -> date:
        """Return the last *completed* trading day (market already closed)."""
        now = datetime.utcnow()
        is_il = self._is_il_symbol(symbol)
        # TASE closes ~15:25 UTC (18:25 IST); US closes ~21:00 UTC
        market_close_utc = 16 if is_il else 21
        current = now.date()

        while True:
            if self._is_trading_day(current, is_il):
                if current < now.date() or now.hour >= market_close_utc:
                    return current
                else:
                    current -= timedelta(days=1)
            else:
                current -= timedelta(days=1)

    # -----------------------------------------------------------------------
    # HTTP execution
    # -----------------------------------------------------------------------

    def _execute_with_retry(self, url: str, params: Dict) -> Optional[requests.Response]:
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                headers = self._base_headers()
                resp = self._session.get(url, params=params, headers=headers, timeout=self.TIMEOUT)
                if resp.status_code == 200:
                    return resp
                if resp.status_code in (429, 503):
                    if attempt < self.MAX_RETRIES:
                        backoff = self.RETRY_BASE * (2 ** (attempt - 1))
                        log.warning(f'🔄 Rate limited ({resp.status_code}), retry {attempt}/{self.MAX_RETRIES} in {backoff}s')
                        time.sleep(backoff)
                        continue
                return resp
            except requests.exceptions.RequestException as e:
                if attempt < self.MAX_RETRIES:
                    backoff = self.RETRY_BASE * (2 ** (attempt - 1))
                    log.warning(f'🔄 Request error ({e}), retry {attempt}/{self.MAX_RETRIES} in {backoff}s')
                    time.sleep(backoff)
                else:
                    log.error(f'❌ Max retries exceeded for {url}')
                    return None
        return None

    # -----------------------------------------------------------------------
    # Response parsing  (UTC-safe — mirrors Dart implementation)
    # -----------------------------------------------------------------------

    def _parse_response(self, data: Dict, symbol: str) -> List[StockData]:
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        quotes = result['indicators']['quote'][0]

        opens   = quotes.get('open',   [])
        highs   = quotes.get('high',   [])
        lows    = quotes.get('low',    [])
        closes  = quotes.get('close',  [])
        volumes = quotes.get('volume', [])

        out: List[StockData] = []
        for i in range(len(timestamps)):
            if (opens[i] is None or highs[i] is None or
                    lows[i] is None or closes[i] is None or volumes[i] is None or
                    opens[i] <= 0 or closes[i] <= 0):
                continue
            # Parse timestamp as UTC then build a naive calendar date
            # (mirrors Dart: DateTime.fromMillisecondsSinceEpoch(..., isUtc: true))
            raw_utc = datetime.utcfromtimestamp(timestamps[i])
            calendar_date = datetime(raw_utc.year, raw_utc.month, raw_utc.day)

            out.append(StockData(
                symbol=symbol,
                date=calendar_date,
                open=float(opens[i]),
                high=float(highs[i]),
                low=float(lows[i]),
                close=float(closes[i]),
                volume=int(volumes[i]),
            ))

        log.info(f'🔍 Parsed {len(out)} valid records from {len(timestamps)} raw timestamps for {symbol}')
        return out

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def fetch_stock_data(self, symbol: str, days: int = 50) -> Optional[List[StockData]]:
        self._ensure_crumb()
        self._rate_limit()

        last_day = self._get_last_trading_day(symbol)
        is_il = self._is_il_symbol(symbol)
        # Same buffer formula as Polygon.io: int(days * 1.5) + 10 calendar days back
        # ensures at least `days` trading days are returned even with holidays/gaps
        calendar_days = int(days * 1.5) + 10
        start_dt = datetime.combine(last_day - timedelta(days=calendar_days), datetime.min.time())
        end_dt   = datetime.combine(last_day, datetime.min.time()) + timedelta(hours=12)

        params = {
            'period1': str(int(start_dt.timestamp())),
            'period2': str(int(end_dt.timestamp())),
            'interval': '1d',
            'includePrePost': 'false',
            'events': 'div,split',
            'crumb': self._crumb or self._random_crumb(),
        }
        url = f'{self.BASE_URL}/{symbol}'

        log.info(f'📊 Fetching {symbol}  {start_dt.strftime("%d/%m/%Y")} → {end_dt.strftime("%d/%m/%Y")}')
        resp = self._execute_with_retry(url, params)

        if resp is None:
            log.error(f'❌ Failed to fetch {symbol} after all retries')
            return None
        if resp.status_code != 200:
            log.error(f'❌ HTTP {resp.status_code} for {symbol}')
            if resp.status_code in (429, 503):
                self._req_count += 10  # penalty
            return None

        data = resp.json()
        if 'chart' not in data or not data['chart'].get('result'):
            log.error(f'❌ Empty/error response for {symbol}')
            return None

        records = self._parse_response(data, symbol)
        trading = [r for r in records if self._is_trading_day(r.date.date(), is_il)]
        trading.sort(key=lambda x: x.date)
        result = trading[-days:] if len(trading) > days else trading

        log.info(f'✅ {symbol}: {len(result)} trading days fetched')
        return result

    def fetch_multiple_stocks_with_breaks(
        self,
        symbols: List[str],
        days: int = 50,
    ) -> Dict[str, List[StockData]]:
        """Fetch a list of symbols with human-like batching and breaks."""
        self._ensure_crumb()

        results: Dict[str, List[StockData]] = {}
        shuffled = symbols.copy()
        random.shuffle(shuffled)

        log.info(f'📊 Fetching {len(shuffled)} symbols (conservative rate-limiting + IP rotation)…')

        for i, symbol in enumerate(shuffled):
            log.info(f'⬇️  {symbol}  ({i + 1}/{len(shuffled)})')
            data = self.fetch_stock_data(symbol, days=days)
            if data:
                results[symbol] = data
            else:
                log.warning(f'⚠️  No data for {symbol}')

            # Extended break every BATCH_SIZE requests (mirrors Dart every-10 logic)
            if (i + 1) % self.BATCH_SIZE == 0 and i + 1 < len(shuffled):
                pause = self.BATCH_BREAK + random.uniform(0, 8)
                log.info(f'😴 Batch break ({pause:.1f}s) after {i + 1} requests')
                time.sleep(pause)

        log.info(f'✅ Done: {len(results)}/{len(shuffled)} symbols fetched successfully')
        return results

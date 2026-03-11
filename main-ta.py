#!/usr/bin/env python3
"""
Stock Data Automation - Main-TA Script
Downloads TA125, SME60, TA-Others, TA-Remainings and Top ETFs IL data
at 5 PM UTC daily and saves to public CSV files using Yahoo Finance.
"""

import os
import csv
import json
import logging
from datetime import datetime
from typing import Dict, List
from yahoo_finance_service import YahooFinanceService, StockData
from stock_symbols_ta import get_all_symbols

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)


class StockDataAutomation:
    def __init__(self):
        self.yahoo_service = YahooFinanceService()
        self.output_dir = os.environ.get('OUTPUT_DIR', 'data')
        os.makedirs(self.output_dir, exist_ok=True)

    def save_to_csv(self, stock_data: Dict[str, List[StockData]], filename: str, market_name: str):
        """Save stock data to CSV file"""
        filepath = os.path.join(self.output_dir, filename)
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
                for symbol, data_list in stock_data.items():
                    for item in data_list:
                        writer.writerow([
                            item.symbol,
                            item.date.strftime('%Y-%m-%d'),
                            item.open,
                            item.high,
                            item.low,
                            item.close,
                            item.volume,
                        ])
            log.info(f'💾 Saved {market_name} data to: {filepath}')
        except Exception as e:
            log.error(f'❌ Error saving {market_name} data to {filepath}: {e}')
            raise

    def download_market_data(self, symbols: List[str], market_name: str) -> Dict[str, List[StockData]]:
        """Download data for all symbols using Yahoo Finance"""
        log.info(f'🚀 Starting {market_name} download for {len(symbols)} symbols...')
        market_data = self.yahoo_service.fetch_multiple_stocks_with_breaks(symbols, days=50)
        log.info(f'✅ {market_name} complete: {len(market_data)}/{len(symbols)} symbols successful')
        return market_data

    def run_daily_download(self):
        """Run the daily download process"""
        start_time = datetime.now()
        log.info(f'🚀 Starting daily TA stock data download at {start_time.strftime("%Y-%m-%d %H:%M:%S")}')

        try:
            all_symbols = get_all_symbols()

            # --- TA Stocks: TA125 + SME60 + TA-Others + TA-Remainings ---
            ta_symbols = (
                all_symbols['TA125'] +
                all_symbols['TA-SME60'] +
                all_symbols['TA-Others'] +
                all_symbols['TA-Remainings']
            )
            # Deduplicate while preserving order
            seen = set()
            ta_symbols_unique = []
            for s in ta_symbols:
                if s not in seen:
                    seen.add(s)
                    ta_symbols_unique.append(s)

            log.info(f'🇮🇱 Total TA symbols to download: {len(ta_symbols_unique)} (after dedup)')
            ta_data = self.download_market_data(ta_symbols_unique, 'TA Stocks (TA125+SME60+Others+Remainings)')
            if ta_data:
                self.save_to_csv(ta_data, 'Shazam-Stock-Info-TA125.csv', 'TA Stocks')

            # --- Top ETFs IL ---
            etf_symbols = all_symbols['Top ETFs IL']
            log.info(f'📊 Total ETF IL symbols to download: {len(etf_symbols)}')
            etf_data = self.download_market_data(etf_symbols, 'Top ETFs IL')
            if etf_data:
                self.save_to_csv(etf_data, 'Shazam-Stock-Info-ETFIL.csv', 'Top ETFs IL')

            end_time = datetime.now()
            duration = end_time - start_time

            log.info(f'🎉 Daily download completed successfully!')
            log.info(f'📊 TA Stocks (Yahoo Finance): {len(ta_data)} symbols')
            log.info(f'📊 Top ETFs IL (Yahoo Finance): {len(etf_data)} symbols')
            log.info(f'⏱️ Total duration: {duration}')

            self.create_status_file(ta_data, etf_data, start_time, end_time)

        except Exception as e:
            log.error(f'❌ Daily download failed: {e}')
            raise

    def create_status_file(self, ta_data: Dict, etf_data: Dict, start_time: datetime, end_time: datetime):
        """Create a status file for monitoring"""
        status_file = os.path.join(self.output_dir, 'download_status.json')
        status = {
            'last_update': end_time.isoformat(),
            'start_time': start_time.isoformat(),
            'duration_seconds': (end_time - start_time).total_seconds(),
            'ta_symbols': len(ta_data),
            'etf_il_symbols': len(etf_data),
            'total_symbols': len(ta_data) + len(etf_data),
            'status': 'success',
            'services': {
                'ta_service': 'Yahoo Finance',
                'etf_il_service': 'Yahoo Finance',
            },
        }
        try:
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
            log.info(f'📄 Status file created: {status_file}')
        except Exception as e:
            log.error(f'❌ Error creating status file: {e}')


def main():
    """Main entry point"""
    log.info('🚀 Stock Data Automation (TA) Starting...')
    log.info('📊 TA Stocks (TA125 + SME60 + Others + Remainings): Yahoo Finance')
    log.info('📊 Top ETFs IL: Yahoo Finance')

    automation = StockDataAutomation()
    automation.run_daily_download()


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Weekly Earnings & Dividends - Main Script
Downloads dividend and earnings dates every Sunday at 12pm
"""

import os
import csv
import logging
from datetime import datetime
from earnings_dividends_service import EarningsDividendsService
from stock_symbols import get_all_symbols

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)

class WeeklyEarningsDividends:
    def __init__(self):
        self.service = EarningsDividendsService()
        self.output_dir = os.environ.get('OUTPUT_DIR', 'data')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_to_csv(self, data: dict, filename: str):
        """Save earnings/dividends data to CSV"""
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(['Symbol', 'Date', 'Next_Div_Date', 'Next_Earn_Date'])
                
                for symbol, item in data.items():
                    writer.writerow([
                        item.symbol,
                        item.date.strftime('%Y-%m-%d'),
                        item.next_div_date or '',
                        item.next_earn_date or ''
                    ])
            
            log.info(f'💾 Saved earnings/dividends data to: {filepath}')
            
        except Exception as e:
            log.error(f'❌ Error saving data to {filepath}: {e}')
            raise
    
    def run_weekly_update(self):
        """Run the weekly earnings/dividends update"""
        start_time = datetime.now()
        log.info(f'🚀 Starting weekly earnings/dividends update at {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
        
        try:
            all_symbols = get_all_symbols()
            all_stock_symbols = all_symbols['ETFs']
            
            log.info(f'📊 Processing {len(all_stock_symbols)} symbols')
            log.info(f'📋 First 10 symbols: {all_stock_symbols[:10]}')
            log.info(f'📋 Last 10 symbols: {all_stock_symbols[-10:]}')
            
            data = self.service.fetch_dividend_earnings_data(all_stock_symbols)
            
            if data:
                self.save_to_csv(data, 'Shazam-Stock-Earn-Div.csv')
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            log.info(f'🎉 Weekly update completed successfully!')
            log.info(f'📊 Processed {len(data)} symbols')
            log.info(f'⏱️ Total duration: {duration}')
            
        except Exception as e:
            log.error(f'❌ Weekly update failed: {e}')
            raise

def main():
    log.info('🚀 Weekly Earnings & Dividends Starting...')
    automation = WeeklyEarningsDividends()
    automation.run_weekly_update()

if __name__ == '__main__':

    main()






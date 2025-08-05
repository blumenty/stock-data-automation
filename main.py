#!/usr/bin/env python3
"""
Stock Data Automation - Main Script
Downloads TA125 and SP500 data at 2 AM daily and saves to public CSV files
"""

import os
import csv
import logging
from datetime import datetime
from typing import Dict, List
from yahoo_finance_service import YahooFinanceService, StockData
from stock_symbols import get_all_symbols

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
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_to_csv(self, stock_data: Dict[str, List[StockData]], filename: str, market_name: str):
        """Save stock data to CSV file (same format as your Dart code)"""
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header (same as Dart)
                writer.writerow(['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
                
                # Write all stock data for this market
                for symbol, data_list in stock_data.items():
                    for stock_data_item in data_list:
                        writer.writerow([
                            stock_data_item.symbol,
                            stock_data_item.date.strftime('%Y-%m-%d'),
                            stock_data_item.open,
                            stock_data_item.high,
                            stock_data_item.low,
                            stock_data_item.close,
                            stock_data_item.volume,
                        ])
            
            log.info(f'💾 Saved {market_name} data to: {filepath}')
            
        except Exception as e:
            log.error(f'❌ Error saving {market_name} data to {filepath}: {e}')
            raise
    
    def download_market_data(self, symbols: List[str], market_name: str) -> Dict[str, List[StockData]]:
        """Download data for all symbols in a market"""
        log.info(f'🚀 Starting {market_name} download for {len(symbols)} symbols...')
        
        market_data = {}
        successful_downloads = 0
        
        for i, symbol in enumerate(symbols):
            try:
                log.info(f'📊 Downloading {symbol} ({i+1}/{len(symbols)})')
                
                # Fetch last 50 days of data (same as your requirement)
                stock_data = self.yahoo_service.fetch_stock_data(symbol, days=50)
                
                if stock_data and len(stock_data) > 0:
                    market_data[symbol] = stock_data
                    successful_downloads += 1
                    log.info(f'✅ Downloaded {len(stock_data)} days for {symbol}')
                else:
                    log.warning(f'⚠️ No data received for {symbol}')
                
            except Exception as e:
                log.error(f'❌ Error downloading data for {symbol}: {e}')
        
        log.info(f'✅ {market_name} download complete: {successful_downloads}/{len(symbols)} symbols successful')
        return market_data
    
    def run_daily_download(self):
        """Run the daily download process"""
        start_time = datetime.now()
        log.info(f'🚀 Starting daily stock data download at {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
        
        try:
            # Get all symbols (same as your Dart code)
            all_symbols = get_all_symbols()
            
            # Download TA125 data
            ta125_data = self.download_market_data(all_symbols['TA125'], 'TA-125')
            if ta125_data:
                self.save_to_csv(ta125_data, 'Shazam-Stock-Info-TA125.csv', 'TA-125')
            
            # Download SP500 data
            sp500_data = self.download_market_data(all_symbols['SP500'], 'S&P 500')
            if sp500_data:
                self.save_to_csv(sp500_data, 'Shazam-Stock-Info-SP500.csv', 'S&P 500')
            
            # Summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            log.info(f'🎉 Daily download completed successfully!')
            log.info(f'📊 TA-125: {len(ta125_data)} symbols')
            log.info(f'📊 S&P 500: {len(sp500_data)} symbols')
            log.info(f'⏱️ Total duration: {duration}')
            
            # Create status file for monitoring
            self.create_status_file(ta125_data, sp500_data, start_time, end_time)
            
        except Exception as e:
            log.error(f'❌ Daily download failed: {e}')
            raise
    
    def create_status_file(self, ta125_data: Dict, sp500_data: Dict, start_time: datetime, end_time: datetime):
        """Create a status file for monitoring"""
        status_file = os.path.join(self.output_dir, 'download_status.json')
        
        import json
        status = {
            'last_update': end_time.isoformat(),
            'start_time': start_time.isoformat(),
            'duration_seconds': (end_time - start_time).total_seconds(),
            'ta125_symbols': len(ta125_data),
            'sp500_symbols': len(sp500_data),
            'total_symbols': len(ta125_data) + len(sp500_data),
            'status': 'success'
        }
        
        try:
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
            log.info(f'📄 Status file created: {status_file}')
        except Exception as e:
            log.error(f'❌ Error creating status file: {e}')

def main():
    """Main entry point"""
    automation = StockDataAutomation()
    automation.run_daily_download()

if __name__ == '__main__':
    main()
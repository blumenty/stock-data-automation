#!/usr/bin/env python3
"""
Stock Data Automation - Main Script
Downloads TA125 and SP500 data at 2 AM daily and saves to public CSV files
NOW USING POLYGON.IO for S&P 500 and Yahoo Finance for TA125
"""

import os
import csv
import logging
from datetime import datetime
from typing import Dict, List
from polygon_io_service import PolygonIOService, StockData  # Updated import
from yahoo_finance_service import YahooFinanceService  # Keep for TA125
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
        self.polygon_service = PolygonIOService()  # For S&P 500
        self.yahoo_service = YahooFinanceService()  # For TA125
        self.output_dir = os.environ.get('OUTPUT_DIR', 'data')
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_to_csv(self, stock_data: Dict[str, List[StockData]], filename: str, market_name: str):
        """Save stock data to CSV file (same format as before)"""
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header (same as before)
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
    
    def download_market_data(self, symbols: List[str], market_name: str, service_type: str = 'polygon') -> Dict[str, List[StockData]]:
        """Download data for all symbols in a market using the appropriate service"""
        log.info(f'🚀 Starting {market_name} download for {len(symbols)} symbols using {service_type}...')
        
        # Choose the appropriate service based on market
        if service_type == 'polygon':
            log.info(f'🇺🇸 Using Polygon.io for {market_name} (S&P 500)')
            market_data = self.polygon_service.fetch_multiple_stocks_with_breaks(symbols, days=50)
        else:
            log.info(f'🇮🇱 Using Yahoo Finance for {market_name} (TA-125)')
            market_data = self.yahoo_service.fetch_multiple_stocks_with_breaks(symbols, days=50)
        
        successful_downloads = len(market_data)
        log.info(f'✅ {market_name} download complete: {successful_downloads}/{len(symbols)} symbols successful')
        
        return market_data
    
    def check_services_health(self):
        """Check health of both services"""
        log.info('🔍 Checking service health...')
        
        # Check Polygon.io health
        polygon_health = self.polygon_service.check_service_health()
        log.info(f'📊 Polygon.io Health: {polygon_health["status"]} (Response: {polygon_health.get("responseTime", "N/A")}ms)')
        
        # For Yahoo Finance, we don't have a health check, so we'll just log that it's available
        log.info('📊 Yahoo Finance: Available for TA-125 symbols')
        
        return {
            'polygon': polygon_health,
            'yahoo': {'status': 'Available', 'service': 'Yahoo Finance'}
        }
    
    def run_daily_download(self):
        """Run the daily download process with multi-service support"""
        start_time = datetime.now()
        log.info(f'🚀 Starting daily stock data download at {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
        
        try:
            # Check service health first
            health_status = self.check_services_health()
            
            # Get all symbols (same as before)
            all_symbols = get_all_symbols()
            
            # Download TA125 data using Yahoo Finance (TA symbols work better with Yahoo)
#            log.info('🇮🇱 Starting TA-125 download with Yahoo Finance...')
#            ta125_data = self.download_market_data(
#                all_symbols['TA125'], 
#                'TA-125', 
#                service_type='yahoo'
#            )
#            if ta125_data:
#                self.save_to_csv(ta125_data, 'Shazam-Stock-Info-TA125.csv', 'TA-125')
            
            # Download SP500 data using Polygon.io (better for US stocks)
            log.info('🇺🇸 Starting S&P 500 download with Polygon.io...')
            sp500_data = self.download_market_data(
                all_symbols['SP500'], 
                'S&P 500', 
                service_type='polygon'
            )
            if sp500_data:
                self.save_to_csv(sp500_data, 'Shazam-Stock-Info-SP500.csv', 'S&P 500')
            
            # Summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            log.info(f'🎉 Daily download completed successfully!')
            log.info(f'📊 TA-125 (Yahoo Finance): {len(ta125_data)} symbols')
            log.info(f'📊 S&P 500 (Polygon.io): {len(sp500_data)} symbols')
            log.info(f'⏱️ Total duration: {duration}')
            
            # Create status file for monitoring
            self.create_status_file(ta125_data, sp500_data, start_time, end_time, health_status)
            
        except Exception as e:
            log.error(f'❌ Daily download failed: {e}')
            raise
    
    def create_status_file(self, ta125_data: Dict, sp500_data: Dict, start_time: datetime, end_time: datetime, health_status: Dict):
        """Create a status file for monitoring with service information"""
        status_file = os.path.join(self.output_dir, 'download_status.json')
        
        import json
        status = {
            'last_update': end_time.isoformat(),
            'start_time': start_time.isoformat(),
            'duration_seconds': (end_time - start_time).total_seconds(),
            'ta125_symbols': len(ta125_data),
            'sp500_symbols': len(sp500_data),
            'total_symbols': len(ta125_data) + len(sp500_data),
            'status': 'success',
            'services': {
                'ta125_service': 'Yahoo Finance',
                'sp500_service': 'Polygon.io',
                'polygon_health': health_status.get('polygon', {}),
                'yahoo_health': health_status.get('yahoo', {})
            },
            'api_info': {
                'polygon_api_key_present': bool(self.polygon_service.API_KEY),
                'polygon_rate_limit': '5 requests/minute (free tier) with 12s minimum delays',
                'yahoo_rate_limit': '15 requests/minute with 25-30s delays'
            }
        }
        
        try:
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
            log.info(f'📄 Status file created: {status_file}')
        except Exception as e:
            log.error(f'❌ Error creating status file: {e}')

def main():
    """Main entry point"""
    log.info('🚀 Stock Data Automation Starting...')
    log.info('📊 TA-125: Yahoo Finance Service')
    log.info('📊 S&P 500: Polygon.io Service')
    
    automation = StockDataAutomation()
    automation.run_daily_download()

if __name__ == '__main__':
    main()
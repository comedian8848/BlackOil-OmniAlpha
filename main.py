import argparse
import sys
from core.data_provider import data_provider
from core.engine import AnalysisEngine
from strategies import get_strategy, get_all_strategy_keys
from utils.file_io import load_stock_pool_from_csv, save_results_to_csv
from utils.date_utils import get_today_str

def main():
    parser = argparse.ArgumentParser(description="OmniAlpha Stock Selector CLI")
    
    # Date argument
    parser.add_argument('--date', type=str, 
                        help='Target date YYYY-MM-DD. Defaults to the latest trading day.')
    
    # Strategy selection
    available_keys = get_all_strategy_keys()
    parser.add_argument('--strategies', type=str, default='ma',
                        help=f'Comma-separated list of strategies. Available: {", ".join(available_keys)}')
    
    # Stock pool source
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--file', type=str, 
                       help='Path to a CSV file containing a "code" column to use as the stock pool.')
    group.add_argument('--quick', action='store_true', 
                       help='Quick mode: Scan only the first 20 stocks of HS300 for testing.')
    
    args = parser.parse_args()
    
    # 1. Initialize Data Provider (Login)
    try:
        data_provider.login()
        
        # 2. Determine Date
        target_date = args.date
        if not target_date:
            target_date = data_provider.get_latest_trading_date()
            print(f"Auto-detected latest trading date: {target_date}")
            
        # 3. Prepare Stock Pool
        stock_pool = []
        if args.file:
            print(f"Loading stock pool from file: {args.file}")
            try:
                stock_pool = load_stock_pool_from_csv(args.file)
            except Exception as e:
                print(f"Error loading file: {e}")
                sys.exit(1)
        else:
            # Default to HS300
            stock_pool = data_provider.get_hs300_stocks(target_date)
            if args.quick:
                print("Quick mode enabled: limiting to first 20 stocks.")
                stock_pool = stock_pool[:20]
                
        if not stock_pool:
            print("Stock pool is empty. Exiting.")
            sys.exit(0)
            
        # 4. Initialize Strategies
        selected_keys = args.strategies.split(',')
        active_strategies = []
        for key in selected_keys:
            strat = get_strategy(key.strip())
            if strat:
                active_strategies.append(strat)
            else:
                print(f"Warning: Strategy '{key}' not found.")
        
        if not active_strategies:
            print("No valid strategies selected. Exiting.")
            sys.exit(1)
            
        print(f"Active Strategies: {[s.name for s in active_strategies]}")
            
        # 5. Run Analysis
        engine = AnalysisEngine(active_strategies)
        results = engine.run(stock_pool, target_date)
        
        # 6. Save Results
        if results:
            filename = f"selection_{target_date}_{'_'.join([k.strip() for k in selected_keys])}.csv"
            save_results_to_csv(results, filename)
        else:
            print("No stocks matched the selected strategies.")
            
    finally:
        data_provider.logout()

if __name__ == "__main__":
    main()

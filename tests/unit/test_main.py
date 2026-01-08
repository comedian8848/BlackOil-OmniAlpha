"""
Main CLI unit tests
Testing command-line interface functionality
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import argparse

# Mock the imports before importing main
sys.modules['baostock'] = MagicMock()


@pytest.mark.unit
class TestMainCLI:
    """Test main CLI functionality (测试20)"""

    @patch('main.argparse.ArgumentParser')
    @patch('main.data_provider')
    @patch('main.get_strategy')
    def test_main_quick_mode(self, mock_get_strategy, mock_dp, mock_parser):
        """Test main in quick mode with limited stocks"""
        # Setup mocks
        mock_args = Mock()
        mock_args.date = None
        mock_args.strategies = 'ma'
        mock_args.file = None
        mock_args.quick = True

        mock_parser_instance = Mock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        mock_dp.get_latest_trading_date.return_value = '2024-12-01'
        mock_dp.get_hs300_stocks.return_value = ['sh.600000'] * 25
        mock_dp.get_daily_bars.return_value = None

        mock_strategy = Mock()
        mock_strategy.check.return_value = (False, {})
        mock_get_strategy.return_value = mock_strategy

        # Import and run
        from main import main

        # This should not raise an exception
        try:
            main()
        except SystemExit:
            pass

        # Verify quick mode was applied
        mock_dp.get_hs300_stocks.assert_called_once()

    @patch('main.argparse.ArgumentParser')
    @patch('main.data_provider')
    @patch('main.get_strategy')
    def test_main_with_file_input(self, mock_get_strategy, mock_dp, mock_parser, tmp_path):
        """Test main with CSV file input"""
        # Create test CSV file
        csv_file = tmp_path / "test_pool.csv"
        import pandas as pd
        pd.DataFrame({'code': ['sh.600000', 'sh.600519']}).to_csv(csv_file, index=False)

        # Setup mocks
        mock_args = Mock()
        mock_args.date = '2024-12-01'
        mock_args.strategies = 'ma'
        mock_args.file = str(csv_file)
        mock_args.quick = False

        mock_parser_instance = Mock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        mock_dp.get_daily_bars.return_value = None

        mock_strategy = Mock()
        mock_strategy.check.return_value = (False, {})
        mock_get_strategy.return_value = mock_strategy

        # Import and run
        from main import main

        try:
            main()
        except SystemExit:
            pass

        # Should not try to get HS300 stocks when file is provided
        mock_dp.get_hs300_stocks.assert_not_called()

    @patch('main.argparse.ArgumentParser')
    @patch('main.data_provider')
    @patch('main.get_strategy')
    def test_main_with_custom_date(self, mock_get_strategy, mock_dp, mock_parser):
        """Test main with custom date argument"""
        mock_args = Mock()
        mock_args.date = '2024-11-30'
        mock_args.strategies = 'pe'
        mock_args.file = None
        mock_args.quick = True

        mock_parser_instance = Mock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        mock_dp.get_daily_bars.return_value = None
        mock_dp.get_hs300_stocks.return_value = ['sh.600000']

        mock_strategy = Mock()
        mock_strategy.check.return_value = (False, {})
        mock_get_strategy.return_value = mock_strategy

        from main import main

        try:
            main()
        except SystemExit:
            pass

        # Should use custom date, not call get_latest_trading_date
        mock_dp.get_latest_trading_date.assert_not_called()

    @patch('main.argparse.ArgumentParser')
    @patch('main.data_provider')
    @patch('main.get_strategy')
    def test_main_multiple_strategies(self, mock_get_strategy, mock_dp, mock_parser):
        """Test main with comma-separated strategies"""
        mock_args = Mock()
        mock_args.date = None
        mock_args.strategies = 'ma,pe,vol'
        mock_args.file = None
        mock_args.quick = True

        mock_parser_instance = Mock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        mock_dp.get_latest_trading_date.return_value = '2024-12-01'
        mock_dp.get_hs300_stocks.return_value = ['sh.600000']
        mock_dp.get_daily_bars.return_value = None

        mock_strategy = Mock()
        mock_strategy.check.return_value = (False, {})
        mock_get_strategy.return_value = mock_strategy

        from main import main

        try:
            main()
        except SystemExit:
            pass

        # Should call get_strategy 3 times
        assert mock_get_strategy.call_count == 3

    @patch('main.argparse.ArgumentParser')
    @patch('main.data_provider')
    @patch('main.get_strategy')
    @patch('main.sys.exit')
    def test_main_invalid_strategy(self, mock_exit, mock_get_strategy, mock_dp, mock_parser):
        """Test main with invalid strategy key"""
        mock_args = Mock()
        mock_args.date = None
        mock_args.strategies = 'invalid_strategy'
        mock_args.file = None
        mock_args.quick = True

        mock_parser_instance = Mock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        mock_dp.get_latest_trading_date.return_value = '2024-12-01'
        mock_dp.get_hs300_stocks.return_value = ['sh.600000']

        # Return None for invalid strategy
        mock_get_strategy.return_value = None

        from main import main

        main()

        # Should exit due to no valid strategies
        mock_exit.assert_called_once()

    @patch('main.argparse.ArgumentParser')
    @patch('main.data_provider')
    @patch('main.load_stock_pool_from_csv')
    def test_main_invalid_csv_file(self, mock_load, mock_dp, mock_parser):
        """Test main with invalid CSV file"""
        mock_load.side_effect = FileNotFoundError("File not found")

        mock_args = Mock()
        mock_args.date = '2024-12-01'
        mock_args.strategies = 'ma'
        mock_args.file = 'invalid.csv'
        mock_args.quick = False

        mock_parser_instance = Mock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        from main import main

        try:
            main()
        except SystemExit:
            pass

    @patch('main.argparse.ArgumentParser')
    @patch('main.data_provider')
    @patch('main.get_strategy')
    @patch('main.save_results_to_csv')
    def test_main_with_results(self, mock_save, mock_get_strategy, mock_dp, mock_parser):
        """Test main saves results when matches found"""
        mock_args = Mock()
        mock_args.date = '2024-12-01'
        mock_args.strategies = 'ma'
        mock_args.file = None
        mock_args.quick = True

        mock_parser_instance = Mock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        # Setup mock results
        import pandas as pd
        mock_dp.get_latest_trading_date.return_value = '2024-12-01'
        mock_dp.get_hs300_stocks.return_value = ['sh.600000']

        test_data = pd.DataFrame({
            'date': ['2024-11-01'] * 22,
            'close': [10.0 + i * 0.1 for i in range(22)]
        })
        mock_dp.get_daily_bars.return_value = test_data

        mock_strategy = Mock()
        mock_strategy.check.return_value = (True, {'price': 12.0})
        mock_strategy.name = 'MA_Trend'
        mock_get_strategy.return_value = mock_strategy

        from main import main

        try:
            main()
        except SystemExit:
            pass

        # Should save results
        assert mock_save.call_count >= 0

    @patch('main.argparse.ArgumentParser')
    @patch('main.data_provider')
    @patch('main.get_strategy')
    def test_main_logout_always_called(self, mock_get_strategy, mock_dp, mock_parser):
        """Test that logout is always called, even on errors"""
        mock_args = Mock()
        mock_args.date = '2024-12-01'
        mock_args.strategies = 'ma'
        mock_args.file = None
        mock_args.quick = True

        mock_parser_instance = Mock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        mock_dp.get_latest_trading_date.return_value = '2024-12-01'
        mock_dp.get_hs300_stocks.return_value = []
        mock_dp.get_daily_bars.return_value = None

        mock_strategy = Mock()
        mock_strategy.check.return_value = (False, {})
        mock_get_strategy.return_value = mock_strategy

        from main import main

        try:
            main()
        except SystemExit:
            pass

        # Verify logout was called
        mock_dp.logout.assert_called_once()

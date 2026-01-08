"""
Utils unit tests
Testing utility functions in utils/
"""
import pytest
import pandas as pd
import os
from datetime import datetime
from utils.file_io import load_stock_pool_from_csv, save_results_to_csv
from utils.date_utils import get_today_str, format_date


@pytest.mark.unit
class TestDateUtils:
    """Test date utility functions (测试15)"""

    def test_get_today_str_format(self):
        """Test that get_today_str returns correct format"""
        today = get_today_str()
        assert isinstance(today, str)
        # Check YYYY-MM-DD format
        datetime.strptime(today, "%Y-%m-%d")

    def test_get_today_str_is_current_date(self):
        """Test that get_today_str returns current date"""
        today_str = get_today_str()
        today_date = datetime.now()
        expected = today_date.strftime("%Y-%m-%d")
        assert today_str == expected

    def test_format_date_valid_input(self):
        """Test format_date with valid datetime object"""
        dt = datetime(2024, 12, 1)
        result = format_date(dt)
        assert result == "2024-12-01"

    def test_format_date_different_dates(self):
        """Test format_date with various dates"""
        test_cases = [
            (datetime(2024, 1, 1), "2024-01-01"),
            (datetime(2024, 12, 31), "2024-12-31"),
            (datetime(2023, 6, 15), "2023-06-15"),
        ]

        for dt, expected in test_cases:
            assert format_date(dt) == expected


@pytest.mark.unit
class TestFileIO:
    """Test file I/O utility functions (测试16)"""

    def test_load_stock_pool_from_csv(self, tmp_path):
        """Test loading stock pool from valid CSV file"""
        csv_file = tmp_path / "test_pool.csv"
        test_data = pd.DataFrame({
            'code': ['sh.600000', 'sh.600519', 'sz.000001', 'sz.000002']
        })
        test_data.to_csv(csv_file, index=False)

        result = load_stock_pool_from_csv(str(csv_file))

        assert isinstance(result, list)
        assert len(result) == 4
        assert 'sh.600000' in result
        assert 'sh.600519' in result

    def test_load_stock_pool_file_not_found(self):
        """Test loading from non-existent file"""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_stock_pool_from_csv("nonexistent.csv")

        assert "File not found" in str(exc_info.value)

    def test_load_stock_pool_missing_code_column(self, tmp_path):
        """Test loading CSV without 'code' column"""
        csv_file = tmp_path / "invalid_pool.csv"
        test_data = pd.DataFrame({
            'stock_id': ['sh.600000', 'sh.600519']
        })
        test_data.to_csv(csv_file, index=False)

        with pytest.raises(ValueError) as exc_info:
            load_stock_pool_from_csv(str(csv_file))

        assert "code" in str(exc_info.value)

    def test_load_stock_pool_empty_file(self, tmp_path):
        """Test loading empty CSV file"""
        csv_file = tmp_path / "empty_pool.csv"
        pd.DataFrame({'code': []}).to_csv(csv_file, index=False)

        result = load_stock_pool_from_csv(str(csv_file))

        assert isinstance(result, list)
        assert len(result) == 0

    def test_load_stock_pool_with_extra_columns(self, tmp_path):
        """Test loading CSV with extra columns"""
        csv_file = tmp_path / "pool_with_extra.csv"
        test_data = pd.DataFrame({
            'code': ['sh.600000', 'sh.600519'],
            'name': ['浦发银行', '贵州茅台'],
            'price': [10.5, 1800.0]
        })
        test_data.to_csv(csv_file, index=False)

        result = load_stock_pool_from_csv(str(csv_file))

        assert len(result) == 2
        assert 'sh.600000' in result
        assert 'sh.600519' in result

    def test_save_results_to_csv(self, tmp_path):
        """Test saving results to CSV"""
        results = [
            {
                'date': '2024-12-01',
                'code': 'sh.600000',
                'strategy': 'MA_Trend',
                'price': 10.5,
                'MA5': 10.2,
                'MA20': 9.8
            },
            {
                'date': '2024-12-01',
                'code': 'sz.000001',
                'strategy': 'MA_Trend',
                'price': 15.3,
                'MA5': 15.0,
                'MA20': 14.5
            }
        ]

        csv_file = tmp_path / "test_results.csv"
        save_results_to_csv(results, str(csv_file))

        # Verify file was created
        assert os.path.exists(csv_file)

        # Verify content
        df = pd.read_csv(csv_file)
        assert len(df) == 2
        assert 'date' in df.columns
        assert 'code' in df.columns
        assert 'strategy' in df.columns
        assert list(df.columns)[:3] == ['date', 'code', 'strategy']

    def test_save_results_empty_list(self, tmp_path, capsys):
        """Test saving empty results list"""
        csv_file = tmp_path / "empty_results.csv"

        save_results_to_csv([], str(csv_file))

        # Check for print message
        captured = capsys.readouterr()
        assert "No results to save" in captured.out

    def test_save_results_column_order(self, tmp_path):
        """Test that columns are reordered correctly"""
        results = [
            {
                'MA5': 10.2,
                'date': '2024-12-01',
                'price': 10.5,
                'MA20': 9.8,
                'code': 'sh.600000',
                'strategy': 'MA_Trend'
            }
        ]

        csv_file = tmp_path / "column_order.csv"
        save_results_to_csv(results, str(csv_file))

        df = pd.read_csv(csv_file)
        # First three columns should be date, code, strategy
        assert list(df.columns)[:3] == ['date', 'code', 'strategy']

    def test_save_results_multiple_strategies(self, tmp_path):
        """Test saving results from multiple strategies"""
        results = [
            {
                'date': '2024-12-01',
                'code': 'sh.600000',
                'strategy': 'MA_Trend',
                'price': 10.5
            },
            {
                'date': '2024-12-01',
                'code': 'sh.600000',
                'strategy': 'Volume_Breakout',
                'price': 10.5,
                'vol_ratio': 2.5
            }
        ]

        csv_file = tmp_path / "multi_strategy.csv"
        save_results_to_csv(results, str(csv_file))

        df = pd.read_csv(csv_file)
        assert len(df) == 2
        assert set(df['strategy']) == {'MA_Trend', 'Volume_Breakout'}

    def test_save_results_with_special_characters(self, tmp_path):
        """Test saving results with special characters in data"""
        results = [
            {
                'date': '2024-12-01',
                'code': 'sh.600519',
                'strategy': 'High_Turnover',
                'price': 1800.0,
                'note': 'Test "quote" and comma, value'
            }
        ]

        csv_file = tmp_path / "special_chars.csv"
        save_results_to_csv(results, str(csv_file))

        # Verify file can be read back
        df = pd.read_csv(csv_file)
        assert len(df) == 1
        assert df.iloc[0]['code'] == 'sh.600519'

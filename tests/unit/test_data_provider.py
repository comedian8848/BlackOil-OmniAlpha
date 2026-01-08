"""
数据提供层单元测试
测试范围：
- 登录/登出功能
- 交易日获取
- 沪深300成分股获取
- 日线数据获取
- 财报数据获取
- 边界和异常情况
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta

from core.data_provider import BaostockProvider


@pytest.mark.unit
class TestBaostockProviderLogin:
    """测试登录/登出功能 (测试1)"""

    @patch('core.data_provider.bs.login')
    def test_login_success(self, mock_login):
        provider = BaostockProvider()
        provider.login()

        assert provider.is_logged_in is True
        mock_login.assert_called_once()

    @patch('core.data_provider.bs.logout')
    def test_logout_success(self, mock_logout):
        provider = BaostockProvider()
        provider.is_logged_in = True
        provider.logout()

        assert provider.is_logged_in is False
        mock_logout.assert_called_once()

    @patch('core.data_provider.bs.login')
    def test_login_already_logged_in(self, mock_login):
        provider = BaostockProvider()
        provider.is_logged_in = True
        provider.login()

        mock_login.assert_not_called()

    @patch('core.data_provider.bs.logout')
    def test_logout_already_logged_out(self, mock_logout):
        provider = BaostockProvider()
        provider.logout()

        mock_logout.assert_not_called()


@pytest.mark.unit
class TestBaostockProviderTradingDates:
    """测试交易日获取 (测试2)"""

    @patch('core.data_provider.bs.query_trade_dates')
    def test_get_latest_trading_date(self, mock_query):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = ['calendar_date', 'is_trading_day']
        mock_result.get_row_data.side_effect = [
            ['2024-12-01', '1'],
            ['2024-11-30', '1'],
            ['2024-11-29', '0'],
            None
        ]
        mock_result.next.side_effect = [True, True, True, False]
        mock_query.return_value = mock_result

        result = provider.get_latest_trading_date()

        assert result == '2024-12-01'
        mock_query.assert_called_once()

    @patch('core.data_provider.bs.query_trade_dates')
    def test_get_latest_trading_date_no_trading_days(self, mock_query):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = ['calendar_date', 'is_trading_day']
        mock_result.get_row_data.return_value = None
        mock_result.next.return_value = False
        mock_query.return_value = mock_result

        result = provider.get_latest_trading_date()

        assert isinstance(result, str)
        assert len(result) == 10  # YYYY-MM-DD格式


@pytest.mark.unit
class TestBaostockProviderHS300:
    """测试沪深300成分股获取 (测试3)"""

    @patch('core.data_provider.bs.query_hs300_stocks')
    def test_get_hs300_stocks(self, mock_query):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = ['date', 'code', 'code_name']
        mock_result.get_row_data.side_effect = [
            ['2024-12-01', 'sh.600000', '浦发银行'],
            ['2024-12-01', 'sh.600519', '贵州茅台'],
            ['2024-12-01', 'sz.000001', '平安银行'],
            None
        ]
        mock_result.next.side_effect = [True, True, True, False]
        mock_query.return_value = mock_result

        result = provider.get_hs300_stocks('2024-12-01')

        assert len(result) == 3
        assert 'sh.600000' in result
        assert 'sh.600519' in result
        assert 'sz.000001' in result
        mock_query.assert_called_once_with(date='2024-12-01')

    @patch('core.data_provider.bs.query_hs300_stocks')
    def test_get_hs300_stocks_empty(self, mock_query):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.next.return_value = False
        mock_query.return_value = mock_result

        result = provider.get_hs300_stocks('2024-12-01')

        assert result == []


@pytest.mark.unit
class TestBaostockProviderDailyBars:
    """测试日线数据获取 (测试4)"""

    @patch('core.data_provider.bs.query_history_k_data_plus')
    def test_get_daily_bars_success(self, mock_query, sample_daily_data):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = list(sample_daily_data.columns)

        rows = [list(row) for row in sample_daily_data.values]
        mock_result.get_row_data.side_effect = rows + [None]
        mock_result.next.side_effect = [True] * len(rows) + [False]
        mock_query.return_value = mock_result

        result = provider.get_daily_bars('sh.600000', '2024-12-01', lookback_days=60)

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'close' in result.columns
        assert 'peTTM' in result.columns
        assert 'pbMRQ' in result.columns
        assert 'turn' in result.columns

    @patch('core.data_provider.bs.query_history_k_data_plus')
    def test_get_daily_bars_empty(self, mock_query):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.get_row_data.return_value = None
        mock_result.next.return_value = False
        mock_query.return_value = mock_result

        result = provider.get_daily_bars('sh.600000', '2024-12-01')

        assert result is None

    @patch('core.data_provider.bs.query_history_k_data_plus')
    def test_get_daily_bars_data_type_conversion(self, mock_query):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = ['date', 'code', 'open', 'high', 'low', 'close',
                            'volume', 'amount', 'pctChg', 'peTTM', 'pbMRQ', 'turn', 'isST']
        mock_result.get_row_data.side_effect = [
            ['2024-12-01', 'sh.600000', '10.5', '10.8', '10.3', '10.7',
             '1000000', '10700000', '2.5', '15.3', '2.1', '5.5', '0'],
            None
        ]
        mock_result.next.side_effect = [True, False]
        mock_query.return_value = mock_result

        result = provider.get_daily_bars('sh.600000', '2024-12-01')

        assert result is not None
        assert result['close'].dtype in ['float64', 'float32']
        assert result['volume'].dtype in ['int64', 'int32']

    @patch('core.data_provider.bs.query_history_k_data_plus')
    def test_get_daily_bars_lookback_days(self, mock_query, test_date):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.next.return_value = False
        mock_query.return_value = mock_result

        provider.get_daily_bars('sh.600000', test_date, lookback_days=90)

        call_args = mock_query.call_args
        assert call_args is not None
        start_date = call_args[1]['start_date']
        expected_start = (datetime.strptime(test_date, "%Y-%m-%d") - timedelta(days=90)).strftime("%Y-%m-%d")
        assert start_date == expected_start


@pytest.mark.unit
class TestBaostockProviderFinancialData:
    """测试财报数据获取 (测试5)"""

    @patch('core.data_provider.bs.query_profit_data')
    def test_get_profit_data(self, mock_query, sample_profit_data):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = list(sample_profit_data.columns)

        rows = [list(row) for row in sample_profit_data.values]
        mock_result.get_row_data.side_effect = rows + [None]
        mock_result.next.side_effect = [True, False]
        mock_query.return_value = mock_result

        result = provider.get_profit_data('sh.600519', '2024', '3')

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert 'roeAvg' in result.columns
        assert len(result) == 1

    @patch('core.data_provider.bs.query_operation_data')
    def test_get_operation_data(self, mock_query):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = ['code', 'pubDate', 'NRTurnRatio']
        mock_result.get_row_data.side_effect = [
            ['sh.600519', '2024-10-31', '5.2'],
            None
        ]
        mock_result.next.side_effect = [True, False]
        mock_query.return_value = mock_result

        result = provider.get_operation_data('sh.600519', '2024', '3')

        assert result is not None
        assert 'NRTurnRatio' in result.columns

    @patch('core.data_provider.bs.query_growth_data')
    def test_get_growth_data(self, mock_query, sample_growth_data):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = list(sample_growth_data.columns)

        rows = [list(row) for row in sample_growth_data.values]
        mock_result.get_row_data.side_effect = rows + [None]
        mock_result.next.side_effect = [True, False]
        mock_query.return_value = mock_result

        result = provider.get_growth_data('sh.600519', '2024', '3')

        assert result is not None
        assert 'YOYNI' in result.columns

    @patch('core.data_provider.bs.query_balance_data')
    def test_get_balance_data(self, mock_query, sample_balance_data):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = list(sample_balance_data.columns)

        rows = [list(row) for row in sample_balance_data.values]
        mock_result.get_row_data.side_effect = rows + [None]
        mock_result.next.side_effect = [True, False]
        mock_query.return_value = mock_result

        result = provider.get_balance_data('sh.600519', '2024', '3')

        assert result is not None
        assert 'liabilityToAsset' in result.columns


@pytest.mark.unit
class TestBaostockProviderExceptions:
    """测试边界和异常情况 (测试6)"""

    @patch('core.data_provider.bs.query_history_k_data_plus')
    def test_invalid_stock_code(self, mock_query):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '1'
        mock_result.next.return_value = False
        mock_query.return_value = mock_result

        result = provider.get_daily_bars('invalid.code', '2024-12-01')

        assert result is None

    @patch('core.data_provider.bs.query_history_k_data_plus')
    def test_invalid_date_format(self, mock_query):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.next.return_value = False
        mock_query.return_value = mock_result

        result = provider.get_daily_bars('sh.600000', 'invalid-date')

        assert result is None

    @patch('core.data_provider.bs.query_profit_data')
    def test_empty_financial_data(self, mock_query):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.get_row_data.return_value = None
        mock_result.next.return_value = False
        mock_query.return_value = mock_result

        result = provider.get_profit_data('sh.600000', '2024', '3')

        assert result is None

    @patch('core.data_provider.bs.query_profit_data')
    def test_financial_data_query_exception(self, mock_query):
        provider = BaostockProvider()

        mock_query.side_effect = Exception("Network error")

        result = provider.get_profit_data('sh.600000', '2024', '3')

        assert result is None

    @patch('core.data_provider.bs.query_history_k_data_plus')
    def test_suspended_stock(self, mock_query):
        provider = BaostockProvider()

        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.get_row_data.return_value = None
        mock_result.next.return_value = False
        mock_query.return_value = mock_result

        result = provider.get_daily_bars('sh.600000', '2024-12-01')

        assert result is None

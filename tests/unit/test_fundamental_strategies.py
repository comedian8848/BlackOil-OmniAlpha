"""
基本面策略单元测试
测试范围：
- LowPeStrategy
- HighGrowthStrategy
- HighRoeStrategy
- LowDebtStrategy
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch

from strategies.fundamental import LowPeStrategy, HighGrowthStrategy, HighRoeStrategy, LowDebtStrategy
from strategies.technical import MovingAverageStrategy


@pytest.mark.unit
class TestLowPeStrategy:
    """测试低PE策略 (测试10)"""

    def test_strategy_properties(self):
        strategy = LowPeStrategy()
        assert strategy.name == "Value_LowPE"
        assert strategy.description == "Low Valuation: 0 < PE_TTM < 30"

    def test_low_pe_match(self):
        strategy = LowPeStrategy()
        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'peTTM': [15.5],
            'pbMRQ': [2.1]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is True
        assert 'price' in details
        assert 'peTTM' in details
        assert 'pbMRQ' in details
        assert 0 < details['peTTM'] < 30

    def test_negative_pe_no_match(self):
        strategy = LowPeStrategy()
        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'peTTM': [-5.5],
            'pbMRQ': [2.1]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False
        assert details == {}

    def test_high_pe_no_match(self):
        strategy = LowPeStrategy()
        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'peTTM': [45.0],
            'pbMRQ': [2.1]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False
        assert details == {}

    def test_boundary_pe_values(self):
        strategy = LowPeStrategy()

        data_low = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'peTTM': [0.01],
            'pbMRQ': [2.0]
        })
        is_match_low, _ = strategy.check('sh.600000', data_low)
        assert is_match_low is True

        data_boundary = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'peTTM': [30.0],
            'pbMRQ': [2.0]
        })
        is_match_boundary, _ = strategy.check('sh.600000', data_boundary)
        assert is_match_boundary is True

        data_above = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'peTTM': [30.01],
            'pbMRQ': [2.0]
        })
        is_match_above, _ = strategy.check('sh.600000', data_above)
        assert is_match_above is False

    def test_missing_pe_column(self):
        strategy = LowPeStrategy()
        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False


@pytest.mark.unit
class TestHighGrowthStrategy:
    """测试高成长策略 (测试11)"""

    @patch('strategies.fundamental.data_provider')
    def test_high_growth_match(self, mock_dp, sample_growth_data):
        strategy = HighGrowthStrategy()

        mock_dp.get_growth_data.return_value = sample_growth_data

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [1800.0]
        })

        is_match, details = strategy.check('sh.600519', data)

        assert is_match is True
        assert 'price' in details
        assert 'YOY_NetProfit' in details
        assert 'Period' in details
        mock_dp.get_growth_data.assert_called_once_with('sh.600519', '2024', '3')

    @patch('strategies.fundamental.data_provider')
    def test_low_growth_no_match(self, mock_dp):
        strategy = HighGrowthStrategy()

        low_growth_data = pd.DataFrame({
            'YOYNI': [15.5]
        })
        mock_dp.get_growth_data.return_value = low_growth_data

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False
        assert details == {}

    @patch('strategies.fundamental.data_provider')
    def test_empty_growth_data(self, mock_dp):
        strategy = HighGrowthStrategy()

        mock_dp.get_growth_data.return_value = None

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False

    @patch('strategies.fundamental.data_provider')
    def test_boundary_growth_value(self, mock_dp):
        strategy = HighGrowthStrategy()

        boundary_data = pd.DataFrame({
            'YOYNI': [20.0]
        })
        mock_dp.get_growth_data.return_value = boundary_data

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is True

    @patch('strategies.fundamental.data_provider')
    def test_growth_exception_handling(self, mock_dp):
        strategy = HighGrowthStrategy()

        mock_dp.get_growth_data.side_effect = Exception("Database error")

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False


@pytest.mark.unit
class TestHighRoeStrategy:
    """测试高ROE策略 (测试12)"""

    @patch('strategies.fundamental.data_provider')
    def test_high_roe_decimal_match(self, mock_dp, sample_profit_data):
        strategy = HighRoeStrategy()

        mock_dp.get_profit_data.return_value = sample_profit_data

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [1800.0]
        })

        is_match, details = strategy.check('sh.600519', data)

        assert is_match is True
        assert 'price' in details
        assert 'ROE' in details
        assert 'Period' in details
        assert float(details['ROE'].rstrip('%')) > 15

    @patch('strategies.fundamental.data_provider')
    def test_low_roe_no_match(self, mock_dp):
        strategy = HighRoeStrategy()

        low_roe_data = pd.DataFrame({
            'roeAvg': [0.10]
        })
        mock_dp.get_profit_data.return_value = low_roe_data

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False

    @patch('strategies.fundamental.data_provider')
    def test_roe_percentage_format(self, mock_dp):
        strategy = HighRoeStrategy()

        roe_data = pd.DataFrame({
            'roeAvg': [18.5]
        })
        mock_dp.get_profit_data.return_value = roe_data

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is True
        assert '%' in details['ROE']

    @patch('strategies.fundamental.data_provider')
    def test_roe_boundary_value(self, mock_dp):
        strategy = HighRoeStrategy()

        boundary_data = pd.DataFrame({
            'roeAvg': [0.15]
        })
        mock_dp.get_profit_data.return_value = boundary_data

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is True

    @patch('strategies.fundamental.data_provider')
    def test_empty_profit_data(self, mock_dp):
        strategy = HighRoeStrategy()

        mock_dp.get_profit_data.return_value = None

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False


@pytest.mark.unit
class TestLowDebtStrategy:
    """测试低负债策略 (测试13)"""

    @patch('strategies.fundamental.data_provider')
    def test_low_debt_match(self, mock_dp, sample_balance_data):
        strategy = LowDebtStrategy()

        mock_dp.get_balance_data.return_value = sample_balance_data

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [1800.0]
        })

        is_match, details = strategy.check('sh.600519', data)

        assert is_match is True
        assert 'price' in details
        assert 'DebtRatio' in details
        assert 'Period' in details
        debt_ratio = float(details['DebtRatio'].rstrip('%'))
        assert debt_ratio < 50

    @patch('strategies.fundamental.data_provider')
    def test_high_debt_no_match(self, mock_dp):
        strategy = LowDebtStrategy()

        high_debt_data = pd.DataFrame({
            'liabilityToAsset': [0.65]
        })
        mock_dp.get_balance_data.return_value = high_debt_data

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False

    @patch('strategies.fundamental.data_provider')
    def test_boundary_debt_ratio(self, mock_dp):
        strategy = LowDebtStrategy()

        boundary_data = pd.DataFrame({
            'liabilityToAsset': [0.50]
        })
        mock_dp.get_balance_data.return_value = boundary_data

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is True

    @patch('strategies.fundamental.data_provider')
    def test_debt_ratio_percentage_format(self, mock_dp, sample_balance_data):
        strategy = LowDebtStrategy()

        mock_dp.get_balance_data.return_value = sample_balance_data

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is True
        assert '%' in details['DebtRatio']

    @patch('strategies.fundamental.data_provider')
    def test_empty_balance_data(self, mock_dp):
        strategy = LowDebtStrategy()

        mock_dp.get_balance_data.return_value = None

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False


@pytest.mark.unit
class TestFundamentalStrategiesIntegration:
    """测试基本面策略集成"""

    @patch('strategies.fundamental.data_provider')
    def test_multiple_fundamental_strategies(self, mock_dp, sample_uptrend_data):
        ma_strategy = MovingAverageStrategy()
        pe_strategy = LowPeStrategy()

        # 使用足够的历史数据以满足MA策略要求
        data = sample_uptrend_data.copy()
        data['peTTM'] = 15.5
        data['pbMRQ'] = 2.1

        ma_is_match, ma_details = ma_strategy.check('sh.600000', data)
        pe_is_match, pe_details = pe_strategy.check('sh.600000', data)

        assert ma_is_match is True
        assert pe_is_match is True

    @patch('strategies.fundamental.data_provider')
    def test_fundamental_data_query_efficiency(self, mock_dp):
        strategy = HighGrowthStrategy()

        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        strategy.check('sh.600000', data)
        strategy.check('sh.600000', data)

        assert mock_dp.get_growth_data.call_count == 2

"""
技术面策略单元测试
测试范围：
- MovingAverageStrategy
- VolumeRiseStrategy
- HighTurnoverStrategy
"""
import pytest
import pandas as pd
import numpy as np

from strategies.technical import MovingAverageStrategy, VolumeRiseStrategy, HighTurnoverStrategy


@pytest.mark.unit
class TestMovingAverageStrategy:
    """测试均线趋势策略 (测试7)"""

    def test_strategy_properties(self):
        strategy = MovingAverageStrategy()
        assert strategy.name == "MA_Trend"
        assert strategy.description == "Moving Average Trend: Close > MA20 & MA5 > MA20"

    def test_uptrend_match(self, sample_uptrend_data):
        strategy = MovingAverageStrategy()
        is_match, details = strategy.check('sh.600519', sample_uptrend_data)

        assert is_match is True
        assert 'price' in details
        assert 'MA5' in details
        assert 'MA20' in details
        assert details['MA5'] > details['MA20']

    def test_downtrend_no_match(self, sample_downtrend_data):
        strategy = MovingAverageStrategy()
        is_match, details = strategy.check('sz.000001', sample_downtrend_data)

        assert is_match is False
        assert details == {}

    def test_insufficient_data(self):
        strategy = MovingAverageStrategy()
        short_data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0]
        })

        is_match, details = strategy.check('sh.600000', short_data)

        assert is_match is False
        assert details == {}

    def test_moving_average_calculation(self):
        strategy = MovingAverageStrategy()
        dates = pd.date_range(start='2024-10-01', end='2024-12-01', freq='D')
        close_prices = 10 + np.linspace(0, 5, len(dates))

        data = pd.DataFrame({
            'date': dates,
            'close': close_prices
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is True
        ma5 = details['MA5']
        ma20 = details['MA20']
        assert ma5 > ma20

    def test_details_accuracy(self, sample_uptrend_data):
        strategy = MovingAverageStrategy()
        is_match, details = strategy.check('sh.600519', sample_uptrend_data)

        last_close = sample_uptrend_data.iloc[-1]['close']
        assert abs(details['price'] - last_close) < 0.01


@pytest.mark.unit
class TestVolumeRiseStrategy:
    """测试放量突破策略 (测试8)"""

    def test_strategy_properties(self):
        strategy = VolumeRiseStrategy()
        assert strategy.name == "Volume_Breakout"
        assert strategy.description == "Volume Breakout: Rise > 2% & Volume > 1.5 * MA_VOL5"

    def test_volume_breakout_match(self, sample_volume_breakout_data):
        strategy = VolumeRiseStrategy()
        is_match, details = strategy.check('sh.600519', sample_volume_breakout_data)

        assert is_match is True
        assert 'price' in details
        assert 'pctChg' in details
        assert 'vol_ratio' in details
        assert details['pctChg'] > 2.0
        assert details['vol_ratio'] > 1.5

    def test_normal_volume_no_match(self, sample_daily_data):
        strategy = VolumeRiseStrategy()
        is_match, details = strategy.check('sh.600000', sample_daily_data)

        assert is_match is False
        assert details == {}

    def test_price_up_volume_normal(self):
        strategy = VolumeRiseStrategy()
        dates = pd.date_range(start='2024-10-15', end='2024-12-01', freq='D')
        n = len(dates)

        data = pd.DataFrame({
            'date': dates,
            'close': [10 + i * 0.01 for i in range(n)],
            'volume': [1000000] * n,
            'pctChg': [3.0 if i == n-1 else 0.5 for i in range(n)]
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False

    def test_volume_up_price_normal(self):
        strategy = VolumeRiseStrategy()
        dates = pd.date_range(start='2024-10-15', end='2024-12-01', freq='D')
        n = len(dates)

        data = pd.DataFrame({
            'date': dates,
            'close': [10 + i * 0.01 for i in range(n)],
            'volume': [1000000 if i < n-1 else 5000000 for i in range(n)],
            'pctChg': [0.5] * n
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False

    def test_insufficient_data(self):
        strategy = VolumeRiseStrategy()
        short_data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'volume': [1000000],
            'pctChg': [5.0]
        })

        is_match, details = strategy.check('sh.600000', short_data)

        assert is_match is False

    def test_details_accuracy(self, sample_volume_breakout_data):
        strategy = VolumeRiseStrategy()
        is_match, details = strategy.check('sh.600519', sample_volume_breakout_data)

        last_row = sample_volume_breakout_data.iloc[-1]
        ma_vol5 = sample_volume_breakout_data['volume'].rolling(window=5).mean().iloc[-1]
        expected_vol_ratio = last_row['volume'] / ma_vol5

        assert abs(details['vol_ratio'] - expected_vol_ratio) < 0.01


@pytest.mark.unit
class TestHighTurnoverStrategy:
    """测试高换手率策略 (测试9)"""

    def test_strategy_properties(self):
        strategy = HighTurnoverStrategy()
        assert strategy.name == "High_Turnover"
        assert strategy.description == "High Turnover: Turnover > 5% & Not ST"

    def test_high_turnover_match(self, sample_high_turnover_data):
        strategy = HighTurnoverStrategy()
        is_match, details = strategy.check('sh.600519', sample_high_turnover_data)

        assert is_match is True
        assert 'price' in details
        assert 'turn' in details
        assert 'pctChg' in details
        assert details['turn'] > 5

    def test_st_stock_no_match(self, sample_st_stock_data):
        strategy = HighTurnoverStrategy()
        is_match, details = strategy.check('sh.600000', sample_st_stock_data)

        assert is_match is False
        assert details == {}

    def test_low_turnover_no_match(self):
        strategy = HighTurnoverStrategy()
        # 使用确定的低换手率数据（<5%）
        low_turn_data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'turn': [3.5],
            'pctChg': [0.5],
            'isST': ['0']
        })
        is_match, details = strategy.check('sh.600000', low_turn_data)

        assert is_match is False
        assert details == {}

    def test_missing_turn_column(self):
        strategy = HighTurnoverStrategy()
        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'isST': ['0']
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False

    def test_boundary_turnover_value(self):
        strategy = HighTurnoverStrategy()
        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'turn': [5.0],
            'pctChg': [0.5],
            'isST': ['0']
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is True

    def test_boundary_turnover_below_threshold(self):
        strategy = HighTurnoverStrategy()
        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'turn': [4.99],
            'pctChg': [0.5],
            'isST': ['0']
        })

        is_match, details = strategy.check('sh.600000', data)

        assert is_match is False

    def test_details_accuracy(self, sample_high_turnover_data):
        strategy = HighTurnoverStrategy()
        is_match, details = strategy.check('sh.600519', sample_high_turnover_data)

        last_turn = sample_high_turnover_data.iloc[-1]['turn']
        assert abs(details['turn'] - last_turn) < 0.01


@pytest.mark.unit
class TestTechnicalStrategiesEdgeCases:
    """测试策略边界情况"""

    def test_null_values_handling(self):
        data = pd.DataFrame({
            'date': ['2024-11-01', '2024-11-02', '2024-11-03'],
            'close': [10.0, None, 12.0],
            'volume': [1000000, 1500000, 2000000],
            'pctChg': [1.0, None, 2.0]
        })

        ma_strategy = MovingAverageStrategy()
        is_match, details = ma_strategy.check('sh.600000', data)

        assert isinstance(is_match, bool)

    def test_empty_dataframe(self):
        data = pd.DataFrame()

        ma_strategy = MovingAverageStrategy()
        is_match, details = ma_strategy.check('sh.600000', data)

        assert is_match is False

    def test_single_row_dataframe(self):
        data = pd.DataFrame({
            'date': ['2024-12-01'],
            'close': [10.0],
            'volume': [1000000],
            'pctChg': [5.0],
            'turn': [6.0],
            'isST': ['0']
        })

        vol_strategy = VolumeRiseStrategy()
        is_match, details = vol_strategy.check('sh.600000', data)

        assert is_match is False

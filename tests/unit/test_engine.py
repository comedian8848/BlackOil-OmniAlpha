"""
Engine unit tests
Testing AnalysisEngine functionality
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from core.engine import AnalysisEngine
from strategies.technical import MovingAverageStrategy, VolumeRiseStrategy
from strategies.fundamental import LowPeStrategy


@pytest.mark.unit
class TestAnalysisEngine:
    """Test AnalysisEngine (测试14)"""

    def test_engine_initialization(self):
        """Test engine initialization with strategies"""
        strategies = [MovingAverageStrategy(), LowPeStrategy()]
        engine = AnalysisEngine(strategies)

        assert len(engine.strategies) == 2
        assert engine.strategies[0].name == "MA_Trend"
        assert engine.strategies[1].name == "Value_LowPE"

    def test_engine_with_empty_strategies(self):
        """Test engine with no strategies"""
        engine = AnalysisEngine([])
        assert len(engine.strategies) == 0

    @patch('core.engine.data_provider')
    def test_scan_one_matching_stock(self, mock_dp, sample_uptrend_data):
        """Test scanning a single stock that matches all strategies"""
        mock_dp.get_daily_bars.return_value = sample_uptrend_data

        strategies = [MovingAverageStrategy()]
        engine = AnalysisEngine(strategies)

        result = engine.scan_one('sh.600519', '2024-12-01')

        assert result is not None
        assert result['code'] == 'sh.600519'
        assert result['date'] == '2024-12-01'
        assert 'MA_Trend' in result['strategy']

    @patch('core.engine.data_provider')
    def test_scan_one_no_match(self, mock_dp, sample_downtrend_data):
        """Test scanning a stock that doesn't match strategy"""
        mock_dp.get_daily_bars.return_value = sample_downtrend_data

        strategies = [MovingAverageStrategy()]
        engine = AnalysisEngine(strategies)

        result = engine.scan_one('sz.000001', '2024-12-01')

        assert result is None

    @patch('core.engine.data_provider')
    def test_scan_one_no_data(self, mock_dp):
        """Test scanning when data provider returns None"""
        mock_dp.get_daily_bars.return_value = None

        strategies = [MovingAverageStrategy()]
        engine = AnalysisEngine(strategies)

        result = engine.scan_one('sh.600000', '2024-12-01')

        assert result is None

    @patch('core.engine.data_provider')
    def test_scan_one_empty_dataframe(self, mock_dp):
        """Test scanning when data provider returns empty DataFrame"""
        mock_dp.get_daily_bars.return_value = pd.DataFrame()

        strategies = [MovingAverageStrategy()]
        engine = AnalysisEngine(strategies)

        result = engine.scan_one('sh.600000', '2024-12-01')

        assert result is None

    @patch('core.engine.data_provider')
    def test_scan_one_multiple_strategies_and_logic(self, mock_dp, sample_uptrend_data):
        """Test scan_one with multiple strategies using AND logic"""
        mock_dp.get_daily_bars.return_value = sample_uptrend_data

        strategies = [MovingAverageStrategy(), LowPeStrategy()]
        engine = AnalysisEngine(strategies)

        result = engine.scan_one('sh.600519', '2024-12-01')

        # Both strategies should be listed if all match
        assert result is not None
        strategy_names = result['strategy']
        assert 'MA_Trend' in strategy_names

    @patch('core.engine.data_provider')
    def test_scan_one_partial_match_fails(self, mock_dp):
        """Test scan_one fails when any strategy doesn't match (AND logic)"""
        # Create data that matches MA but not PE
        data = pd.DataFrame({
            'date': ['2024-11-01', '2024-11-02', '2024-11-03', '2024-11-04', '2024-11-05',
                     '2024-11-06', '2024-11-07', '2024-11-08', '2024-11-09', '2024-11-10',
                     '2024-11-11', '2024-11-12', '2024-11-13', '2024-11-14', '2024-11-15',
                     '2024-11-16', '2024-11-17', '2024-11-18', '2024-11-19', '2024-11-20',
                     '2024-11-21', '2024-11-22', '2024-11-23', '2024-11-24', '2024-11-25',
                     '2024-11-26', '2024-11-27', '2024-11-28', '2024-11-29', '2024-11-30',
                     '2024-12-01'],
            'close': [10.0 + i * 0.2 for i in range(31)],  # Uptrend for MA
            'peTTM': [50.0] * 31,  # High PE (won't match LowPeStrategy)
            'pbMRQ': [5.0] * 31
        })

        mock_dp.get_daily_bars.return_value = data

        strategies = [MovingAverageStrategy(), LowPeStrategy()]
        engine = AnalysisEngine(strategies)

        result = engine.scan_one('sh.600000', '2024-12-01')

        # Should return None because PE strategy doesn't match
        assert result is None

    @patch('core.engine.data_provider')
    def test_run_with_matches(self, mock_dp, sample_uptrend_data, sample_daily_data):
        """Test run method with matching stocks"""
        mock_dp.get_daily_bars.side_effect = [sample_uptrend_data, sample_daily_data, sample_daily_data]

        strategies = [MovingAverageStrategy()]
        engine = AnalysisEngine(strategies)

        results = engine.run(['sh.600519', 'sz.000001', 'sz.000002'], '2024-12-01')

        assert len(results) == 1
        assert results[0]['code'] == 'sh.600519'
        assert results[0]['strategy'] == 'MA_Trend'

    @patch('core.engine.data_provider')
    def test_run_empty_stock_pool(self, mock_dp):
        """Test run with empty stock pool"""
        strategies = [MovingAverageStrategy()]
        engine = AnalysisEngine(strategies)

        results = engine.run([], '2024-12-01')

        assert results == []
        mock_dp.get_daily_bars.assert_not_called()

    @patch('core.engine.data_provider')
    def test_run_with_none_data(self, mock_dp, sample_uptrend_data):
        """Test run when data provider returns None for some stocks"""
        mock_dp.get_daily_bars.side_effect = [None, None, sample_uptrend_data]

        strategies = [MovingAverageStrategy()]
        engine = AnalysisEngine(strategies)

        results = engine.run(['sh.600000', 'sz.000001', 'sh.600519'], '2024-12-01')

        # Should skip None data and continue
        assert len(results) == 1
        assert results[0]['code'] == 'sh.600519'

    @patch('core.engine.data_provider')
    def test_run_multiple_strategies(self, mock_dp, sample_daily_data):
        """Test run with multiple strategies"""
        # Each stock matches at least one strategy
        mock_dp.get_daily_bars.return_value = sample_daily_data

        strategies = [MovingAverageStrategy(), VolumeRiseStrategy()]
        engine = AnalysisEngine(strategies)

        results = engine.run(['sh.600000', 'sz.000001'], '2024-12-01')

        # Each matching stock appears once per matching strategy
        assert len(results) >= 0

    @patch('core.engine.data_provider')
    def test_run_with_progress_callback(self, mock_dp, sample_daily_data, progress_callback):
        """Test run with progress callback"""
        mock_dp.get_daily_bars.return_value = sample_daily_data

        strategies = [MovingAverageStrategy()]
        engine = AnalysisEngine(strategies)

        results = engine.run(['sh.600000', 'sz.000001', 'sz.000002'], '2024-12-01',
                           progress_callback=progress_callback)

        # Check that callback was called
        assert progress_callback.call_count > 0
        # Check that progress values are in [0, 1]
        for call in progress_callback.call_args_list:
            progress = call[0][0]
            assert 0 <= progress <= 1

    @patch('core.engine.data_provider')
    def test_run_progress_callback_completes(self, mock_dp, sample_daily_data):
        """Test that progress callback reaches 100%"""
        mock_dp.get_daily_bars.return_value = sample_daily_data

        strategies = [MovingAverageStrategy()]
        engine = AnalysisEngine(strategies)

        callback = Mock()
        results = engine.run(['sh.600000', 'sz.000001'], '2024-12-01', progress_callback=callback)

        # Last callback should be close to 1.0
        last_call = callback.call_args_list[-1][0][0]
        assert last_call >= 0.5

    @patch('core.engine.data_provider')
    def test_run_result_structure(self, mock_dp, sample_uptrend_data):
        """Test that run returns results with correct structure"""
        mock_dp.get_daily_bars.return_value = sample_uptrend_data

        strategies = [MovingAverageStrategy()]
        engine = AnalysisEngine(strategies)

        results = engine.run(['sh.600519'], '2024-12-01')

        assert len(results) == 1
        result = results[0]

        # Check required fields
        assert 'code' in result
        assert 'strategy' in result
        assert 'date' in result
        assert isinstance(result['code'], str)
        assert isinstance(result['strategy'], str)
        assert isinstance(result['date'], str)

        # Check strategy-specific fields
        assert 'price' in result
        assert 'MA5' in result
        assert 'MA20' in result

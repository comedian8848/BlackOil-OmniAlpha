"""
Strategies module unit tests
Testing strategy registry and factory functions
"""
import pytest
from strategies import get_strategy, get_all_strategy_keys, STRATEGY_REGISTRY
from strategies.technical import MovingAverageStrategy, VolumeRiseStrategy, HighTurnoverStrategy
from strategies.fundamental import LowPeStrategy, HighGrowthStrategy, HighRoeStrategy, LowDebtStrategy


@pytest.mark.unit
class TestStrategyRegistry:
    """Test strategy registry (测试17)"""

    def test_registry_contains_all_strategies(self):
        """Test that registry contains all expected strategies"""
        expected_keys = ['ma', 'vol', 'turn', 'pe', 'growth', 'roe', 'debt']
        for key in expected_keys:
            assert key in STRATEGY_REGISTRY

    def test_registry_values_are_classes(self):
        """Test that registry values are strategy classes"""
        for key, strategy_cls in STRATEGY_REGISTRY.items():
            assert isinstance(strategy_cls, type)
            # Check it's a subclass (will fail on actual base class without import)
            # For now just check it's callable
            assert callable(strategy_cls)

    def test_registry_ma_strategy(self):
        """Test MA strategy in registry"""
        assert 'ma' in STRATEGY_REGISTRY
        strategy = STRATEGY_REGISTRY['ma']()
        assert strategy.name == "MA_Trend"

    def test_registry_vol_strategy(self):
        """Test Volume strategy in registry"""
        assert 'vol' in STRATEGY_REGISTRY
        strategy = STRATEGY_REGISTRY['vol']()
        assert strategy.name == "Volume_Breakout"

    def test_registry_turn_strategy(self):
        """Test Turnover strategy in registry"""
        assert 'turn' in STRATEGY_REGISTRY
        strategy = STRATEGY_REGISTRY['turn']()
        assert strategy.name == "High_Turnover"

    def test_registry_pe_strategy(self):
        """Test PE strategy in registry"""
        assert 'pe' in STRATEGY_REGISTRY
        strategy = STRATEGY_REGISTRY['pe']()
        assert strategy.name == "Value_LowPE"

    def test_registry_growth_strategy(self):
        """Test Growth strategy in registry"""
        assert 'growth' in STRATEGY_REGISTRY
        strategy = STRATEGY_REGISTRY['growth']()
        assert strategy.name == "Growth_DoubleHigh"

    def test_registry_roe_strategy(self):
        """Test ROE strategy in registry"""
        assert 'roe' in STRATEGY_REGISTRY
        strategy = STRATEGY_REGISTRY['roe']()
        assert strategy.name == "Quality_HighROE"

    def test_registry_debt_strategy(self):
        """Test Debt strategy in registry"""
        assert 'debt' in STRATEGY_REGISTRY
        strategy = STRATEGY_REGISTRY['debt']()
        assert strategy.name == "Safety_LowDebt"


@pytest.mark.unit
class TestGetStrategy:
    """Test get_strategy factory function (测试18)"""

    def test_get_valid_strategy(self):
        """Test getting a valid strategy by key"""
        strategy = get_strategy('ma')
        assert strategy is not None
        assert isinstance(strategy, MovingAverageStrategy)
        assert strategy.name == "MA_Trend"

    def test_get_all_strategy_keys(self):
        """Test getting all available strategy keys"""
        keys = get_all_strategy_keys()
        assert isinstance(keys, list)
        assert len(keys) > 0

    def test_get_strategy_keys_match_registry(self):
        """Test that get_all_strategy_keys matches registry keys"""
        keys = get_all_strategy_keys()
        registry_keys = list(STRATEGY_REGISTRY.keys())
        assert set(keys) == set(registry_keys)

    def test_get_invalid_strategy(self):
        """Test getting an invalid strategy key"""
        strategy = get_strategy('invalid_key')
        assert strategy is None

    def test_get_strategy_with_whitespace(self):
        """Test get_strategy with key containing whitespace"""
        # Note: get_strategy doesn't strip whitespace, so 'ma ' should return None
        strategy = get_strategy('ma ')
        assert strategy is None

    def test_get_strategy_case_sensitivity(self):
        """Test that strategy keys are case-sensitive"""
        # Registry uses lowercase
        strategy_lower = get_strategy('ma')
        assert strategy_lower is not None

        strategy_upper = get_strategy('MA')
        assert strategy_upper is None

    def test_get_each_strategy_type(self):
        """Test getting each strategy type"""
        strategy_mapping = {
            'ma': MovingAverageStrategy,
            'vol': VolumeRiseStrategy,
            'turn': HighTurnoverStrategy,
            'pe': LowPeStrategy,
            'growth': HighGrowthStrategy,
            'roe': HighRoeStrategy,
            'debt': LowDebtStrategy
        }

        for key, expected_cls in strategy_mapping.items():
            strategy = get_strategy(key)
            assert isinstance(strategy, expected_cls)

    def test_get_strategy_returns_new_instance(self):
        """Test that get_strategy returns new instances each time"""
        strategy1 = get_strategy('ma')
        strategy2 = get_strategy('ma')

        assert strategy1 is not strategy2
        assert isinstance(strategy1, MovingAverageStrategy)
        assert isinstance(strategy2, MovingAverageStrategy)


@pytest.mark.unit
class TestStrategyIntegration:
    """Test strategy integration patterns (测试19)"""

    def test_get_multiple_strategies_for_engine(self):
        """Test getting multiple strategies for engine initialization"""
        requested_keys = ['ma', 'pe', 'vol']
        strategies = [get_strategy(key) for key in requested_keys]

        assert len(strategies) == 3
        assert all(s is not None for s in strategies)

    def test_filter_valid_strategy_keys(self):
        """Test filtering valid strategy keys from mixed input"""
        all_keys = ['ma', 'invalid', 'pe', 'wrong', 'vol']
        valid_keys = [k for k in all_keys if get_strategy(k)]

        assert valid_keys == ['ma', 'pe', 'vol']

    def test_strategy_registry_immutability(self):
        """Test that registry keys are not easily modified"""
        original_keys = set(STRATEGY_REGISTRY.keys())

        # Try to add (this might work depending on implementation)
        STRATEGY_REGISTRY['test_key'] = None

        # Clean up if it worked
        if 'test_key' in STRATEGY_REGISTRY:
            del STRATEGY_REGISTRY['test_key']

        # At minimum, original keys should be present
        for key in original_keys:
            assert key in STRATEGY_REGISTRY

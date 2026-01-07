from .technical import MovingAverageStrategy, VolumeRiseStrategy, HighTurnoverStrategy
from .fundamental import LowPeStrategy

# Registry of available strategies
STRATEGY_REGISTRY = {
    'ma': MovingAverageStrategy,
    'vol': VolumeRiseStrategy,
    'turn': HighTurnoverStrategy,
    'pe': LowPeStrategy
}

def get_strategy(key):
    strategy_cls = STRATEGY_REGISTRY.get(key)
    if strategy_cls:
        return strategy_cls()
    return None

def get_all_strategy_keys():
    return list(STRATEGY_REGISTRY.keys())

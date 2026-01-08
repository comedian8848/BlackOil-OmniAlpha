# OmniAlpha Developer Guide

This guide helps AI agents work effectively in the OmniAlpha codebase.

## Build, Test, and Development Commands

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage (generates htmlcov/ and coverage.xml)
pytest

# Run a single test
pytest tests/unit/test_technical_strategies.py::TestMovingAverageStrategy::test_uptrend_match

# Run tests by marker
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m "not slow"   # Skip slow tests
pytest -m slow         # Run only slow tests
```

### Running the Application
```bash
# Web UI (Streamlit)
streamlit run web_ui.py

# CLI Mode
python main.py --quick --strategies ma,pe
python main.py --date 2024-12-01 --strategies ma,vol,turn
python main.py --file my_stocks.csv --strategies pe
```

### Dependency Management
```bash
pip install -r requirements.txt
```

## Code Style Guidelines

### Import Organization
```python
# Standard library imports
import sys
import os
from datetime import datetime

# Third-party imports
import pandas as pd
import baostock as bs

# Local imports - absolute from project root
from core.data_provider import data_provider
from core.engine import AnalysisEngine

# Local imports - relative within packages
from .base import StockStrategy
```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `MovingAverageStrategy`, `AnalysisEngine`, `BaostockProvider`)
- **Functions/Methods**: `snake_case` (e.g., `check`, `get_profit_data`, `get_hs300_stocks`)
- **Variables**: `snake_case` (e.g., `stock_pool`, `last_row`, `target_date`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `STRATEGY_REGISTRY`)
- **Private methods**: prefix with underscore (e.g., `_query_quarterly_data`)
- **Test classes**: `Test<ClassName>` (e.g., `TestMovingAverageStrategy`)
- **Test methods**: `test_<scenario>` (e.g., `test_uptrend_match`)

### File Organization
- `core/` - Core business logic (engine, data provider)
- `strategies/` - Strategy implementations, grouped by type
  - `base.py` - Abstract base class for all strategies
  - `technical.py` - Technical analysis strategies
  - `fundamental.py` - Fundamental analysis strategies
  - `__init__.py` - Strategy registry and factory functions
- `tests/` - Test suite mirroring source structure
  - `unit/` - Unit tests
  - `integration/` - Integration tests
  - `conftest.py` - Shared pytest fixtures
- `utils/` - Utility functions (file I/O, date helpers)
- `main.py` - CLI entry point
- `web_ui.py` - Streamlit web interface

### Class Design Patterns
**Strategies must extend `StockStrategy`:**
```python
from .base import StockStrategy

class CustomStrategy(StockStrategy):
    @property
    def name(self):
        return "Strategy_Name"

    @property
    def description(self):
        return "Brief description of what this does"

    def check(self, code, df):
        """
        Check if stock meets criteria.

        Args:
            code: Stock code (e.g., 'sh.600519')
            df: DataFrame with OHLCV data

        Returns:
            tuple: (is_match: bool, details: dict)
        """
        if df is None or df.empty:
            return False, {}

        # Your logic here
        return True, {'price': price, 'metric': value}
```

**Register new strategies in `strategies/__init__.py`:**
```python
from .your_strategy import CustomStrategy

STRATEGY_REGISTRY = {
    'short_name': CustomStrategy,
    # ... existing strategies
}
```

### Error Handling
- Data fetch failures: Return `None` for DataFrame results
- Strategy failures: Return `(False, {})` tuple
- Input validation: Raise `ValueError` or `FileNotFoundError` with descriptive messages
- API errors: Log with `print()` statements (project uses basic logging)

### Data Provider Pattern
The `data_provider` is a singleton instance of `BaostockProvider`. Key methods:
- `get_hs300_stocks(date)` - Returns list of stock codes
- `get_daily_bars(code, date, lookback_days=60)` - Returns DataFrame with OHLCV
- `get_profit_data(code, year, quarter)` - Returns ROE and profit metrics
- `get_growth_data(code, year, quarter)` - Returns YOY growth metrics
- `get_balance_data(code, year, quarter)` - Returns debt ratio and balance metrics

DataFrame columns include: `date, open, high, low, close, volume, amount, pctChg, peTTM, pbMRQ, turn, isST`

### Testing Patterns
- Use fixtures from `conftest.py` for test data
- Mock external dependencies (baostock) using `unittest.mock`
- Test both positive and negative cases
- Test edge cases (empty data, None values, insufficient data)
- Use descriptive test method names: `test_<condition>_<result>`

Example test structure:
```python
@pytest.mark.unit
class TestCustomStrategy:
    def test_strategy_properties(self):
        strategy = CustomStrategy()
        assert strategy.name == "Expected_Name"
        assert strategy.description == "Expected description"

    def test_matching_conditions(self, sample_matching_data):
        strategy = CustomStrategy()
        is_match, details = strategy.check('sh.600519', sample_matching_data)
        assert is_match is True
        assert 'price' in details
```

### Coverage Configuration
- Branch and line coverage enabled
- Excludes: `tests/`, `venv/`, `__pycache__/`, `*/test_*.py`, `alpha/` directories
- Generate coverage reports: `htmlcov/` (HTML), `coverage.xml` (XML)
- Target: Check coverage reports after running tests

### Language and Comments
- Code comments and docstrings in English preferred
- Chinese comments present in legacy code (mixed English/Chinese acceptable)
- Add docstrings to all public methods and classes

### DataFrame Handling
- Always check for `None` or empty: `if df is None or df.empty: return False, {}`
- Make copies to avoid SettingWithCopyWarning: `df = df.copy()`
- Convert string columns to numeric: `pd.to_numeric(df[col], errors='coerce')`
- Access last row: `last_row = df.iloc[-1]`
- Round floating point values: `round(value, 2)`

### Constants and Magic Numbers
Avoid magic numbers. Define constants at module level:
```python
DEFAULT_LOOKBACK_DAYS = 60
MIN_TURNOVER_THRESHOLD = 5.0
MAX_PE_THRESHOLD = 30.0
VOLUME_MULTIPLIER = 1.5
```

### Progress Reporting
Engine accepts optional `progress_callback`:
```python
def run(self, stock_pool, date, progress_callback=None):
    for i, code in enumerate(stock_pool):
        if progress_callback:
            progress_callback(i / len(stock_pool))
```

### CSV File Format
Stock pool CSV must have a 'code' column:
```csv
code
sh.600519
sz.000001
```

### Logging
- Use `print()` statements for progress and error reporting
- CI logs show detailed pytest output with `log_cli = true`
- Log format: `%(asctime)s [%(levelname)8s] %(message)s`

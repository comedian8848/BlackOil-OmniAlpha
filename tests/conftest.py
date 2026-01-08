"""
Pytest共享fixtures和配置
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def project_root():
    """项目根目录"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def sample_stock_codes():
    """测试用股票代码列表"""
    return ['sh.600000', 'sh.600519', 'sz.000001', 'sz.000002', 'sh.600036']


@pytest.fixture
def test_date():
    """测试日期"""
    return "2024-12-01"


@pytest.fixture
def test_date_obj():
    """测试日期对象"""
    return datetime(2024, 12, 1)


@pytest.fixture
def sample_daily_data():
    """生成示例日线数据"""
    dates = pd.date_range(start='2024-10-01', end='2024-12-01', freq='D')
    n = len(dates)

    # 生成模拟价格数据（上涨趋势）
    base_price = 10.0
    trend = np.linspace(0, 2, n)
    noise = np.random.normal(0, 0.5, n)
    close_prices = base_price + trend + noise

    data = {
        'date': dates,
        'code': ['sh.600000'] * n,
        'open': close_prices * (1 + np.random.uniform(-0.02, 0.02, n)),
        'high': close_prices * (1 + np.random.uniform(0, 0.03, n)),
        'low': close_prices * (1 - np.random.uniform(0, 0.03, n)),
        'close': close_prices,
        'volume': np.random.randint(1000000, 5000000, n),
        'amount': close_prices * np.random.randint(1000000, 5000000, n),
        'pctChg': np.random.uniform(-5, 5, n),
        'peTTM': np.random.uniform(10, 50, n),
        'pbMRQ': np.random.uniform(1, 10, n),
        'turn': np.random.uniform(1, 15, n),
        'isST': ['0'] * n
    }

    df = pd.DataFrame(data)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df


@pytest.fixture
def sample_uptrend_data():
    """上涨趋势数据（用于测试均线策略）"""
    dates = pd.date_range(start='2024-09-01', end='2024-12-01', freq='D')
    n = len(dates)

    # 确保MA5 > MA20
    base_price = 10.0
    close_prices = base_price + np.linspace(0, 5, n)

    data = {
        'date': dates,
        'code': ['sh.600519'] * n,
        'open': close_prices * (1 + np.random.uniform(-0.01, 0.01, n)),
        'high': close_prices * (1 + np.random.uniform(0, 0.02, n)),
        'low': close_prices * (1 - np.random.uniform(0, 0.02, n)),
        'close': close_prices,
        'volume': np.random.randint(2000000, 8000000, n),
        'amount': close_prices * np.random.randint(2000000, 8000000, n),
        'pctChg': np.random.uniform(0, 3, n),  # 正涨幅
        'peTTM': np.random.uniform(15, 25, n),
        'pbMRQ': np.random.uniform(2, 5, n),
        'turn': np.random.uniform(3, 10, n),
        'isST': ['0'] * n
    }

    df = pd.DataFrame(data)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df


@pytest.fixture
def sample_downtrend_data():
    """下跌趋势数据"""
    dates = pd.date_range(start='2024-09-01', end='2024-12-01', freq='D')
    n = len(dates)

    base_price = 20.0
    close_prices = base_price - np.linspace(0, 8, n)

    data = {
        'date': dates,
        'code': ['sz.000001'] * n,
        'open': close_prices * (1 + np.random.uniform(-0.01, 0.01, n)),
        'high': close_prices * (1 + np.random.uniform(0, 0.02, n)),
        'low': close_prices * (1 - np.random.uniform(0, 0.02, n)),
        'close': close_prices,
        'volume': np.random.randint(1000000, 3000000, n),
        'amount': close_prices * np.random.randint(1000000, 3000000, n),
        'pctChg': np.random.uniform(-3, 0, n),  # 负涨幅
        'peTTM': np.random.uniform(30, 60, n),
        'pbMRQ': np.random.uniform(3, 8, n),
        'turn': np.random.uniform(1, 5, n),
        'isST': ['0'] * n
    }

    df = pd.DataFrame(data)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df


@pytest.fixture
def sample_sideways_data():
    """震荡行情数据"""
    dates = pd.date_range(start='2024-09-01', end='2024-12-01', freq='D')
    n = len(dates)

    base_price = 15.0
    close_prices = base_price + np.sin(np.linspace(0, 4*np.pi, n)) * 2

    data = {
        'date': dates,
        'code': ['sh.600036'] * n,
        'open': close_prices * (1 + np.random.uniform(-0.01, 0.01, n)),
        'high': close_prices * (1 + np.random.uniform(0, 0.02, n)),
        'low': close_prices * (1 - np.random.uniform(0, 0.02, n)),
        'close': close_prices,
        'volume': np.random.randint(1500000, 4000000, n),
        'amount': close_prices * np.random.randint(1500000, 4000000, n),
        'pctChg': np.random.uniform(-2, 2, n),
        'peTTM': np.random.uniform(10, 30, n),
        'pbMRQ': np.random.uniform(1, 4, n),
        'turn': np.random.uniform(2, 8, n),
        'isST': ['0'] * n
    }

    df = pd.DataFrame(data)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df


@pytest.fixture
def sample_volume_breakout_data():
    """放量突破数据"""
    dates = pd.date_range(start='2024-10-15', end='2024-12-01', freq='D')
    n = len(dates)

    base_price = 12.0
    close_prices = base_price + np.linspace(0, 1, n)

    # 最后一天放量上涨
    volumes = np.random.randint(1000000, 2000000, n)
    volumes[-1] = 5000000  # 放量
    pct_changes = np.random.uniform(-1, 1, n)
    pct_changes[-1] = 3.5  # 涨幅>2%

    data = {
        'date': dates,
        'code': ['sh.600519'] * n,
        'open': close_prices * (1 + np.random.uniform(-0.01, 0.01, n)),
        'high': close_prices * (1 + np.random.uniform(0, 0.02, n)),
        'low': close_prices * (1 - np.random.uniform(0, 0.02, n)),
        'close': close_prices,
        'volume': volumes,
        'amount': close_prices * volumes,
        'pctChg': pct_changes,
        'peTTM': np.random.uniform(15, 25, n),
        'pbMRQ': np.random.uniform(2, 5, n),
        'turn': np.random.uniform(3, 10, n),
        'isST': ['0'] * n
    }

    df = pd.DataFrame(data)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df


@pytest.fixture
def sample_high_turnover_data():
    """高换手率数据"""
    dates = pd.date_range(start='2024-11-15', end='2024-12-01', freq='D')
    n = len(dates)

    data = {
        'date': dates,
        'code': ['sh.600519'] * n,
        'open': np.random.uniform(180, 185, n),
        'high': np.random.uniform(185, 190, n),
        'low': np.random.uniform(178, 183, n),
        'close': np.random.uniform(180, 188, n),
        'volume': np.random.randint(3000000, 6000000, n),
        'amount': np.random.uniform(500000000, 1000000000, n),
        'pctChg': np.random.uniform(-2, 2, n),
        'peTTM': np.random.uniform(20, 30, n),
        'pbMRQ': np.random.uniform(5, 7, n),
        'turn': np.random.uniform(6, 12, n),  # 换手率>5%
        'isST': ['0'] * n
    }

    df = pd.DataFrame(data)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df


@pytest.fixture
def sample_st_stock_data():
    """ST股票数据"""
    dates = pd.date_range(start='2024-11-01', end='2024-12-01', freq='D')
    n = len(dates)

    data = {
        'date': dates,
        'code': ['sh.600000'] * n,
        'open': np.random.uniform(5, 6, n),
        'high': np.random.uniform(5.5, 6.5, n),
        'low': np.random.uniform(4.5, 5.5, n),
        'close': np.random.uniform(5, 6, n),
        'volume': np.random.randint(1000000, 2000000, n),
        'amount': np.random.uniform(5000000, 12000000, n),
        'pctChg': np.random.uniform(-5, 5, n),
        'peTTM': np.random.uniform(10, 30, n),
        'pbMRQ': np.random.uniform(1, 3, n),
        'turn': np.random.uniform(6, 12, n),  # 换手率>5%但它是ST
        'isST': ['1'] * n  # ST股票
    }

    df = pd.DataFrame(data)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df


@pytest.fixture
def sample_profit_data():
    """示例盈利能力数据（ROE等）"""
    return pd.DataFrame({
        'code': ['sh.600519'],
        'pubDate': '2024-10-31',
        'statDate': '2024-09-30',
        'roeAvg': [0.22],  # ROE 22%
        'npMargin': [0.35],
        'gpMargin': [0.60],
        'netProfit': [50000000000],
        'EPSBasic': [25.5]
    })


@pytest.fixture
def sample_growth_data():
    """示例成长能力数据"""
    return pd.DataFrame({
        'code': ['sh.600519'],
        'pubDate': '2024-10-31',
        'statDate': '2024-09-30',
        'YOYEquity': [15.5],
        'YOYAsset': [12.3],
        'YOYNI': [25.8],  # 净利润同比>20%
        'YOYEPSBasic': [23.4]
    })


@pytest.fixture
def sample_balance_data():
    """示例偿债能力数据"""
    return pd.DataFrame({
        'code': ['sh.600519'],
        'pubDate': '2024-10-31',
        'statDate': '2024-09-30',
        'currentRatio': [3.5],
        'quickRatio': [2.8],
        'cashRatio': [1.5],
        'liabilityToAsset': [0.25],  # 资产负债率25% < 50%
        'assetToLiab': [4.0]
    })


@pytest.fixture
def mock_baostock():
    """Mock Baostock模块"""
    with patch('baostock.bs') as mock_bs:
        # Mock login/logout
        mock_bs.login.return_value = None
        mock_bs.logout.return_value = None

        # Mock query结果对象
        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.next.side_effect = [True] * 10 + [False]

        # Mock query_trade_dates
        mock_result.fields = ['calendar_date', 'is_trading_day']
        mock_result.get_row_data.side_effect = [
            ['2024-12-01', '1'],
            ['2024-11-30', '1'],
            ['2024-11-29', '1'],
        ]

        # Mock query_hs300_stocks
        def mock_get_row_data_hs300():
            mock_result.fields = ['date', 'code', 'code_name']
            codes = ['sh.600000', 'sh.600519', 'sz.000001', 'sz.000002']
            for i, code in enumerate(codes):
                yield ['2024-12-01', code, f'股票{i+1}']

        def mock_query_hs300_stocks(date):
            mock_result_hs300 = Mock()
            mock_result_hs300.error_code = '0'
            mock_result_hs300.fields = ['date', 'code', 'code_name']
            mock_result_hs300.get_row_data.side_effect = list(mock_get_row_data_hs300()) + [None]
            mock_result_hs300.next.side_effect = [True] * 4 + [False]
            return mock_result_hs300

        mock_bs.query_hs300_stocks.side_effect = mock_query_hs300_stocks
        mock_bs.query_trade_dates.return_value = mock_result

        yield mock_bs


@pytest.fixture
def mock_data_provider():
    """Mock Data Provider实例"""
    provider = Mock()
    provider.is_logged_in = False
    provider.login.return_value = None
    provider.logout.return_value = None

    def mock_get_latest_trading_date():
        return '2024-12-01'

    def mock_get_hs300_stocks(date):
        return ['sh.600000', 'sh.600519', 'sz.000001', 'sz.000002', 'sh.600036']

    provider.get_latest_trading_date.side_effect = mock_get_latest_trading_date
    provider.get_hs300_stocks.side_effect = mock_get_hs300_stocks

    yield provider


@pytest.fixture
def sample_csv_file(tmp_path, sample_stock_codes):
    """创建测试用CSV文件"""
    csv_file = tmp_path / "test_stock_pool.csv"
    df = pd.DataFrame({'code': sample_stock_codes})
    df.to_csv(csv_file, index=False)
    return csv_file


@pytest.fixture
def sample_invalid_csv_file(tmp_path):
    """创建无效的CSV文件（缺少code列）"""
    csv_file = tmp_path / "invalid_stock_pool.csv"
    df = pd.DataFrame({'stock_id': ['sh.600000', 'sh.600519']})
    df.to_csv(csv_file, index=False)
    return csv_file


@pytest.fixture
def progress_callback():
    """进度回调函数mock"""
    callback = Mock()
    return callback


@pytest.fixture(scope="function", autouse=True)
def reset_data_provider():
    """每个测试后重置data_provider"""
    from core.data_provider import data_provider
    original_state = data_provider.is_logged_in
    yield
    data_provider.is_logged_in = original_state


@pytest.fixture
def expected_result_structure():
    """期望的结果结构"""
    return {
        'code': str,
        'date': str,
        'strategy': str,
    }


@pytest.fixture
def benchmark_data():
    """性能测试基准数据"""
    return {
        'scan_20_stocks': {'target_time': 10.0},  # 20只股票，10秒内完成
        'scan_100_stocks': {'target_time': 30.0},  # 100只股票，30秒内完成
        'scan_300_stocks': {'target_time': 90.0},  # 300只股票，90秒内完成
    }

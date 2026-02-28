import pytest
import pandas as pd
import numpy as np
from trader.backtester import Backtester


@pytest.fixture
def sample_data():
    dates = pd.date_range("2024-01-01", periods=200)
    np.random.seed(42)
    return pd.DataFrame({
        "Open": np.random.uniform(100, 110, 200),
        "High": np.random.uniform(110, 120, 200),
        "Low": np.random.uniform(90, 100, 200),
        "Close": 100 + np.cumsum(np.random.randn(200)),
        "Volume": np.random.randint(1000, 10000, 200),
    }, index=dates)


def test_run_backtest(sample_data):
    backtester = Backtester(sample_data)
    results = backtester.run()
    assert results is not None
    assert "total_trades" in results
    assert "win_rate" in results

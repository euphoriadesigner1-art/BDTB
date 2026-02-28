import pytest
import pandas as pd
import numpy as np
from trader.indicators import TechnicalIndicators


@pytest.fixture
def sample_data():
    dates = pd.date_range("2024-01-01", periods=100)
    data = {
        "Open": np.random.uniform(100, 110, 100),
        "High": np.random.uniform(110, 120, 100),
        "Low": np.random.uniform(90, 100, 100),
        "Close": np.random.uniform(100, 110, 100),
        "Volume": np.random.randint(1000, 10000, 100),
    }
    return pd.DataFrame(data, index=dates)


def test_rsi(sample_data):
    indicators = TechnicalIndicators(sample_data)
    rsi = indicators.rsi()
    assert rsi is not None
    assert len(rsi) == 100
    assert 0 <= rsi.iloc[-1] <= 100


def test_macd(sample_data):
    indicators = TechnicalIndicators(sample_data)
    macd, signal, hist = indicators.macd()
    assert macd is not None
    assert signal is not None
    assert hist is not None


def test_moving_averages(sample_data):
    indicators = TechnicalIndicators(sample_data)
    ma20 = indicators.sma(20)
    ma50 = indicators.sma(50)
    assert ma20 is not None
    assert ma50 is not None

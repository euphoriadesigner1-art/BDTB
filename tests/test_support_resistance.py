import pytest
import pandas as pd
import numpy as np
from trader.support_resistance import SupportResistance


@pytest.fixture
def sample_data():
    dates = pd.date_range("2024-01-01", periods=100)
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(100) * 2)
    return pd.DataFrame({"Close": close, "High": close + 5, "Low": close - 5}, index=dates)


def test_find_support_resistance(sample_data):
    sr = SupportResistance(sample_data)
    levels = sr.find_levels()
    assert levels is not None
    assert len(levels) > 0


def test_current_price_position(sample_data):
    sr = SupportResistance(sample_data)
    position = sr.get_current_position()
    assert position is not None
    assert "support" in position
    assert "resistance" in position

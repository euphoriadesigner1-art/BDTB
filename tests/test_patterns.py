import pytest
import pandas as pd
import numpy as np
from trader.patterns import PatternDetector


@pytest.fixture
def sample_data():
    dates = pd.date_range("2024-01-01", periods=50)
    return pd.DataFrame({
        "Open": [100, 102, 101, 103, 102, 104, 103, 105, 104, 106] * 5,
        "High": [105, 107, 106, 108, 107, 109, 108, 110, 109, 111] * 5,
        "Low": [95, 97, 96, 98, 97, 99, 98, 100, 99, 101] * 5,
        "Close": [102, 101, 103, 102, 104, 103, 105, 104, 106, 105] * 5,
    }, index=dates)


def test_detect_patterns(sample_data):
    detector = PatternDetector(sample_data)
    patterns = detector.detect_all()
    assert patterns is not None
    assert "candlesticks" in patterns

import pytest
import pandas as pd
import numpy as np
from trader.signals import SignalGenerator


@pytest.fixture
def sample_data():
    dates = pd.date_range("2024-01-01", periods=100)
    np.random.seed(42)
    return pd.DataFrame({
        "Open": np.random.uniform(100, 110, 100),
        "High": np.random.uniform(110, 120, 100),
        "Low": np.random.uniform(90, 100, 100),
        "Close": np.random.uniform(100, 110, 100),
        "Volume": np.random.randint(1000, 10000, 100),
    }, index=dates)


def test_generate_signal(sample_data):
    generator = SignalGenerator(sample_data)
    signal = generator.generate()
    assert signal is not None
    assert "action" in signal
    assert signal["action"] in ["buy", "sell", "hold"]


def test_risk_metrics(sample_data):
    generator = SignalGenerator(sample_data)
    risk = generator.get_risk_metrics()
    assert risk is not None
    assert "risk_reward_ratio" in risk

import pytest
import pandas as pd
import numpy as np
from trader.predictor import PricePredictor


@pytest.fixture
def sample_data():
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=200)
    data = {
        "Close": 100 + np.cumsum(np.random.randn(200)),
        "RSI": np.random.uniform(30, 70, 200),
        "MACD": np.random.randn(200),
        "MACD_Signal": np.random.randn(200),
        "SMA_20": 100 + np.cumsum(np.random.randn(200) * 0.5),
    }
    return pd.DataFrame(data, index=dates)


def test_prepare_features(sample_data):
    predictor = PricePredictor()
    X, y = predictor.prepare_features(sample_data)
    assert X is not None
    assert y is not None
    assert len(X) == len(y)


def test_train_and_predict(sample_data):
    predictor = PricePredictor(model_type="random_forest")
    predictor.train(sample_data)
    prediction = predictor.predict(sample_data)
    assert prediction is not None
    assert "direction" in prediction
    assert "confidence" in prediction

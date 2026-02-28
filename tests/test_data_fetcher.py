import pytest
from trader.data_fetcher import DataFetcher


def test_fetch_historical_data():
    fetcher = DataFetcher()
    df = fetcher.fetch("EURUSD=X", period="1y", interval="1d")
    assert df is not None
    assert len(df) > 0
    assert "Close" in df.columns


def test_fetch_multiple_assets():
    fetcher = DataFetcher()
    assets = ["XAUUSD=X", "BTCUSD=X"]
    data = fetcher.fetch_multiple(assets, period="1mo")
    assert len(data) == 2
    assert "XAUUSD=X" in data

import pytest
from trader.data_fetcher import DataFetcher
from trader.signals import SignalGenerator
from trader.backtester import Backtester


def test_full_pipeline():
    """Test full data pipeline"""
    fetcher = DataFetcher()
    data = fetcher.fetch("GC=F", period="1mo", interval="1d")
    
    assert data is not None
    assert len(data) > 0
    
    generator = SignalGenerator(data)
    signal = generator.generate()
    
    assert signal is not None
    assert "action" in signal
    assert signal["action"] in ["buy", "sell", "hold"]
    
    risk = generator.get_risk_metrics()
    assert risk is not None
    assert "risk_reward_ratio" in risk

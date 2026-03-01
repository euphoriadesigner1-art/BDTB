import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np


def test_backtester_initialization():
    with patch('trader.mt5_backtester.MT5_AVAILABLE', False):
        from trader.mt5_backtester import MT5Backtester
        backtester = MT5Backtester(initial_balance=10000)
        assert backtester.initial_balance == 10000
        assert backtester.balance == 10000
        assert backtester.position == 0


def test_is_available_returns_false_when_mt5_not_available():
    with patch('trader.mt5_backtester.MT5_AVAILABLE', False):
        from trader.mt5_backtester import MT5Backtester
        backtester = MT5Backtester()
        assert backtester.is_available() == False


def test_run_backtest_returns_error_when_mt5_not_available():
    with patch('trader.mt5_backtester.MT5_AVAILABLE', False):
        from trader.mt5_backtester import MT5Backtester
        backtester = MT5Backtester()
        result = backtester.run_backtest("EURUSD")
        assert "error" in result
        assert result["error"] == "MT5 not available"


def test_reset_resets_state():
    with patch('trader.mt5_backtester.MT5_AVAILABLE', False):
        from trader.mt5_backtester import MT5Backtester
        backtester = MT5Backtester(initial_balance=10000)
        backtester.balance = 5000
        backtester.position = 10
        backtester.trades = [{"test": "trade"}]
        
        backtester.reset()
        
        assert backtester.balance == 10000
        assert backtester.position == 0
        assert backtester.trades == []

import pytest
from unittest.mock import Mock, patch


def test_trader_initialization():
    with patch('trader.mt5_trader.MT5_AVAILABLE', False):
        from trader.mt5_trader import MT5Trader
        trader = MT5Trader()
        assert trader.connected == False


def test_is_available_returns_false_when_mt5_not_available():
    with patch('trader.mt5_trader.MT5_AVAILABLE', False):
        from trader.mt5_trader import MT5Trader
        trader = MT5Trader()
        assert trader.is_available() == False


def test_get_positions_returns_empty_when_not_connected():
    with patch('trader.mt5_trader.MT5_AVAILABLE', False):
        from trader.mt5_trader import MT5Trader
        trader = MT5Trader()
        assert trader.get_positions() == []


def test_close_position_returns_error_when_not_connected():
    with patch('trader.mt5_trader.MT5_AVAILABLE', False):
        from trader.mt5_trader import MT5Trader
        trader = MT5Trader()
        result = trader.close_position(12345)
        assert result["success"] == False
        assert "Not connected" in result["error"]


def test_get_account_info_returns_empty_when_not_connected():
    with patch('trader.mt5_trader.MT5_AVAILABLE', False):
        from trader.mt5_trader import MT5Trader
        trader = MT5Trader()
        assert trader.get_account_info() == {}

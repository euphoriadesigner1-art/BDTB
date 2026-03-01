import pytest
from unittest.mock import Mock, patch, MagicMock


def test_client_initialization():
    with patch('trader.mt5_client.MT5_AVAILABLE', False):
        from trader.mt5_client import MT5Client
        client = MT5Client()
        assert client.connected == False


def test_is_available_returns_false_when_mt5_not_available():
    with patch('trader.mt5_client.MT5_AVAILABLE', False):
        from trader.mt5_client import MT5Client
        client = MT5Client()
        assert client.is_available() == False


def test_get_symbols_returns_empty_when_not_connected():
    with patch('trader.mt5_client.MT5_AVAILABLE', False):
        from trader.mt5_client import MT5Client
        client = MT5Client()
        assert client.get_symbols() == []


def test_fetch_candles_returns_empty_when_not_connected():
    with patch('trader.mt5_client.MT5_AVAILABLE', False):
        from trader.mt5_client import MT5Client
        client = MT5Client()
        result = client.fetch_candles("EURUSD")
        assert result.empty == True


def test_get_account_info_returns_empty_when_not_connected():
    with patch('trader.mt5_client.MT5_AVAILABLE', False):
        from trader.mt5_client import MT5Client
        client = MT5Client()
        assert client.get_account_info() == {}


def test_place_order_returns_error_when_not_connected():
    with patch('trader.mt5_client.MT5_AVAILABLE', False):
        from trader.mt5_client import MT5Client
        client = MT5Client()
        result = client.place_order("EURUSD", "BUY", 0.01)
        assert result["success"] == False
        assert "Not connected" in result["error"]


def test_get_positions_returns_empty_when_not_connected():
    with patch('trader.mt5_client.MT5_AVAILABLE', False):
        from trader.mt5_client import MT5Client
        client = MT5Client()
        assert client.get_positions() == []


def test_close_position_returns_error_when_not_connected():
    with patch('trader.mt5_client.MT5_AVAILABLE', False):
        from trader.mt5_client import MT5Client
        client = MT5Client()
        result = client.close_position(12345)
        assert result["success"] == False
        assert "Not connected" in result["error"]

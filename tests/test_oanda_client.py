import pytest
from unittest.mock import Mock, patch, MagicMock
from trader.oanda_client import OANDAClient


def test_client_initialization():
    client = OANDAClient(api_key="test_key", practice=True)
    assert client.practice == True
    assert client.api_key == "test_key"


def test_client_initialization_live():
    client = OANDAClient(api_key="test_key", practice=False)
    assert client.practice == False

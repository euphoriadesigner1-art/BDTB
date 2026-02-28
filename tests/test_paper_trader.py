import pytest
from trader.paper_trader import PaperTrader


def test_paper_trader_initialization():
    trader = PaperTrader(initial_balance=10000)
    assert trader.balance == 10000
    assert trader.position == 0


def test_buy_order():
    trader = PaperTrader(initial_balance=10000)
    result = trader.buy("XAU_USD", units=1, price=2000.0)
    assert result["success"] == True
    assert trader.position == 1
    assert trader.balance < 10000


def test_sell_order():
    trader = PaperTrader(initial_balance=10000)
    trader.buy("XAU_USD", units=1, price=2000.0)
    result = trader.sell("XAU_USD", units=1, price=2100.0)
    assert result["success"] == True
    assert trader.position == 0
    assert trader.balance > 10000


def test_get_status():
    trader = PaperTrader(initial_balance=10000)
    status = trader.get_status()
    assert status["balance"] == 10000
    assert status["position"] == 0


def test_reset():
    trader = PaperTrader(initial_balance=10000)
    trader.buy("XAU_USD", units=10, price=2000.0)
    trader.reset()
    assert trader.balance == 10000
    assert trader.position == 0

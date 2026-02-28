# OANDA API Integration Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add OANDA API integration for historical data fetching and paper trading.

**Architecture:** Add OANDA as an alternative data source to the existing data_fetcher.py module. Create a new oanda_client.py wrapper and paper_trader.py for simulated trading.

**Tech Stack:** Python, oandapyV20 library, OANDA Practice API

---

## Task 1: Add OANDA Dependency

**Files:**
- Modify: `Trader/pyproject.toml`

**Step 1: Update pyproject.toml**

```toml
dependencies = [
    "yfinance>=0.2.36",
    "pandas>=2.1.0",
    "numpy>=1.26.0",
    "ta-lib>=0.4.28",
    "scikit-learn>=1.4.0",
    "xgboost>=2.0.0",
    "streamlit>=1.30.0",
    "plotly>=5.18.0",
    "python-dotenv>=1.0.0",
    "oandapyV20>=0.6.7",
]
```

**Step 2: Commit**

```bash
git add Trader/pyproject.toml
git commit -m "feat: add oandapyV20 dependency"
```

---

## Task 2: Create OANDA Client Module

**Files:**
- Create: `Trader/tests/test_oanda_client.py`
- Create: `Trader/src/trader/oanda_client.py`

**Step 1: Write the failing test**

```python
# Trader/tests/test_oanda_client.py
import pytest
from unittest.mock import Mock, patch
from trader.oanda_client import OANDAClient


def test_client_initialization():
    client = OANDAClient(api_key="test_key", practice=True)
    assert client.practice == True
    assert client.api_key == "test_key"


@patch('trader.oanda_client.API')
def test_fetch_candles(mock_api):
    mock_api.return_value.instrument.candle.return_value = {
        "candles": [
            {"time": "2024-01-01", "o": 100.0, "h": 105.0, "l": 95.0, "c": 102.0, "v": 1000}
        ]
    }
    client = OANDAClient(api_key="test", practice=True)
    candles = client.fetch_candles("XAU_USD", count=100)
    assert candles is not None
```

**Step 2: Run test to verify it fails**

Run: `cd Trader && python3 -m pytest tests/test_oanda_client.py -v`
Expected: FAIL (ModuleNotFoundError)

**Step 3: Write minimal implementation**

```python
# Trader/src/trader/oanda_client.py
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime


class OANDAClient:
    """OANDA API client for fetching historical data"""
    
    def __init__(self, api_key: str, practice: bool = True):
        self.api_key = api_key
        self.practice = practice
        environment = "practice" if practice else "live"
        self.client = oandapyV20.API(access_token=api_key, environment=environment)
    
    def fetch_candles(self, instrument: str, count: int = 100, 
                      granularity: str = "D") -> pd.DataFrame:
        """Fetch historical candle data from OANDA"""
        params = {
            "count": count,
            "granularity": granularity,
        }
        
        try:
            response = self.client.request(
                instruments.InstrumentCandles(instrument=instrument, params=params)
            )
            candles = response.get("candles", [])
            
            data = []
            for c in candles:
                data.append({
                    "time": c["time"],
                    "Open": float(c["mid"]["o"]),
                    "High": float(c["mid"]["h"]),
                    "["mid"]["l"]),
                    "Close": float(c["Low": float(cmid"]["c"]),
                    "Volume": int(c["volume"])
                })
            
            df = pd.DataFrame(data)
            df["time"] = pd.to_datetime(df["time"])
            df.set_index("time", inplace=True)
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        try:
            response = self.client.request(self.client.account())
            return response
        except Exception as e:
            return {"error": str(e)}
```

**Step 4: Run test to verify it passes**

Run: `cd Trader && python3 -m pytest tests/test_oanda_client.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add Trader/tests/test_oanda_client.py Trader/src/trader/oanda_client.py
git commit -m "feat: add OANDA API client module"
```

---

## Task 3: Update Data Fetcher to Support OANDA

**Files:**
- Modify: `Trader/src/trader/data_fetcher.py`
- Modify: `Trader/tests/test_data_fetcher.py`

**Step 1: Update data_fetcher.py**

Add OANDA as an option in the fetch method:

```python
# Add to imports
from .oanda_client import OANDAClient

# Add to DataFetcher class
def fetch_from_oanda(self, symbol: str, period: str = "1y", 
                     interval: str = "1d", api_key: str = None) -> pd.DataFrame:
    """Fetch data from OANDA API"""
    if api_key is None:
        api_key = os.getenv("OANDA_API_KEY", "")
    
    # Map symbol to OANDA format
    oanda_symbol = symbol.replace("=", "_").replace("-", "_")
    if oanda_symbol == "GC_F":
        oanda_symbol = "XAU_USD"
    elif oanda_symbol == "BTC_USD":
        oanda_symbol = "BTC_USD"
    elif oanda_symbol == "USDJPY_X":
        oanda_symbol = "USD_JPY"
    
    # Map interval to OANDA granularity
    granularity_map = {
        "1m": "M1", "5m": "M5", "15m": "M15",
        "1h": "H1", "4h": "H4", "1d": "D", "1wk": "W"
    }
    granularity = granularity_map.get(interval, "D")
    
    client = OANDAClient(api_key, practice=True)
    
    # Convert period to count
    period_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "5y": 1825}
    count = period_map.get(period, 365)
    
    return client.fetch_candles(oanda_symbol, count=count, granularity=granularity)
```

**Step 2: Run existing tests**

Run: `cd Trader && python3 -m pytest tests/test_data_fetcher.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add Trader/src/trader/data_fetcher.py
git commit -m "feat: add OANDA data source to data fetcher"
```

---

## Task 4: Create Paper Trader Module

**Files:**
- Create: `Trader/tests/test_paper_trader.py`
- Create: `Trader/src/trader/paper_trader.py`

**Step 1: Write the failing test**

```python
# Trader/tests/test_paper_trader.py
import pytest
import pandas as pd
import numpy as np
from trader.paper_trader import PaperTrader


def test_paper_trader_initialization():
    trader = PaperTrader(initial_balance=10000)
    assert trader.balance == 10000
    assert trader.position == 0


def test_buy_order():
    trader = PaperTrader(initial_balance=10000)
    trader.buy("XAU_USD", 100, 2000.0)
    assert trader.position > 0
    assert trader.balance < 10000


def test_sell_order():
    trader = PaperTrader(initial_balance=10000)
    trader.sell("XAU_USD", 100, 2000.0)
    assert trader.balance > 10000
```

**Step 2: Run test to verify it fails**

Run: `cd Trader && python3 -m pytest tests/test_paper_trader.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# Trader/src/trader/paper_trader.py
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime


class PaperTrader:
    """Simulate trading without real money"""
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0
        self.position_entry_price = 0
        self.trades: List[Dict] = []
        self.current_symbol = None
    
    def buy(self, symbol: str, units: int, price: float) -> Dict:
        """Execute a buy order"""
        cost = units * price
        
        if cost > self.balance:
            return {"success": False, "error": "Insufficient balance"}
        
        self.balance -= cost
        self.position = units
        self.position_entry_price = price
        self.current_symbol = symbol
        
        trade = {
            "type": "BUY",
            "symbol": symbol,
            "units": units,
            "price": price,
            "cost": cost,
            "time": datetime.now(),
            "balance": self.balance
        }
        self.trades.append(trade)
        
        return {"success": True, "trade": trade}
    
    def sell(self, symbol: str, units: int, price: float) -> Dict:
        """Execute a sell order"""
        if self.position == 0:
            return {"success": False, "error": "No position to sell"}
        
        proceeds = units * price
        profit = proceeds - (self.position * self.position_entry_price)
        
        self.balance += proceeds
        self.position = 0
        self.position_entry_price = 0
        
        trade = {
            "type": "SELL",
            "symbol": symbol,
            "units": units,
            "price": price,
            "proceeds": proceeds,
            "profit": profit,
            "time": datetime.now(),
            "balance": self.balance
        }
        self.trades.append(trade)
        
        return {"success": True, "trade": trade}
    
    def get_status(self) -> Dict:
        """Get current trading status"""
        return {
            "balance": self.balance,
            "position": self.position,
            "entry_price": self.position_entry_price,
            "total_trades": len(self.trades),
            "total_profit": sum(t.get("profit", 0) for t in self.trades)
        }
    
    def reset(self):
        """Reset to initial state"""
        self.balance = self.initial_balance
        self.position = 0
        self.position_entry_price = 0
        self.trades = []
        self.current_symbol = None
```

**Step 4: Run test to verify it passes**

Run: `cd Trader && python3 -m pytest tests/test_paper_trader.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add Trader/tests/test_paper_trader.py Trader/src/trader/paper_trader.py
git commit -m "feat: add paper trader module"
```

---

## Task 5: Add OANDA Settings to Dashboard

**Files:**
- Modify: `Trader/src/trader/dashboard.py`

**Step 1: Add OANDA settings section**

Add to sidebar:

```python
st.markdown("---")
st.header("Data Source")
data_source = st.radio("Choose data source:", ["Yahoo Finance", "OANDA API"])

if data_source == "OANDA API":
    oanda_key = st.text_input("OANDA API Key", type="password", 
                              help="Get your API key from OANDA dashboard")
    st.caption("Use practice account API key for testing")
```

**Step 2: Update data fetching logic**

```python
if data_source == "OANDA API":
    if not oanda_key:
        st.error("Please enter your OANDA API key")
    else:
        data = fetcher.fetch_from_oanda(actual_symbol, period, interval, oanda_key)
else:
    data = fetcher.fetch(actual_symbol, period, interval)
```

**Step 3: Commit**

```bash
git add Trader/src/trader/dashboard.py
git commit -m "feat: add OANDA API option to dashboard"
```

---

## Summary

| Task | Description |
|------|-------------|
| 1 | Add OANDA dependency to pyproject.toml |
| 2 | Create OANDA client module |
| 3 | Update data fetcher to support OANDA |
| 4 | Create paper trader module |
| 5 | Add OANDA settings to dashboard |

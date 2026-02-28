# MetaTrader 5 Integration Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add MetaTrader 5 integration for historical data fetching, backtesting, and live trading.

**Architecture:** Create MT5 client module that connects to local MT5 terminal for data and trade execution. Similar to OANDA integration but with MT5's more extensive API.

**Tech Stack:** Python, MetaTrader5 library, existing trading bot modules

---

## Task 1: Add MetaTrader5 Dependency

**Files:**
- Modify: `Trader/requirements.txt`

**Step 1: Add to requirements.txt**

```
yfinance>=0.2.36
pandas>=2.1.0
numpy>=1.26.0
scikit-learn>=1.4.0
streamlit>=1.30.0
plotly>=5.18.0
python-dotenv>=1.0.0
```

Note: MetaTrader5 will be optional - only loads if MT5 is installed and running.

**Step 2: Commit**

```bash
git add Trader/requirements.txt
git commit -m "feat: prepare for MT5 integration"
```

---

## Task 2: Create MT5 Client Module

**Files:**
- Create: `Trader/tests/test_mt5_client.py`
- Create: `Trader/src/trader/mt5_client.py`

**Step 1: Write the failing test**

```python
# Trader/tests/test_mt5_client.py
import pytest
from unittest.mock import Mock, patch
from trader.mt5_client import MT5Client


def test_client_initialization():
    client = MT5Client()
    assert client.connected == False


@patch('trader.mt5_client.MT5')
def test_connect(mock_mt5):
    mock_mt5.initialize.return_value = True
    client = MT5Client()
    result = client.connect()
    assert result == True
```

**Step 2: Run test to verify it fails**

Run: `cd Trader && python3 -m pytest tests/test_mt5_client.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# Trader/src/trader/mt5_client.py
import MetaTrader5 as mt5
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime


class MT5Client:
    """MetaTrader 5 client for data and trading"""
    
    def __init__(self):
        self.connected = False
        self.account_info = None
    
    def connect(self) -> bool:
        """Initialize MT5 connection"""
        if not mt5.initialize():
            return False
        self.connected = True
        self.account_info = mt5.account_info()
        return True
    
    def disconnect(self):
        """Disconnect from MT5"""
        mt5.shutdown()
        self.connected = False
    
    def get_symbols(self) -> List[str]:
        """Get available trading symbols"""
        if not self.connected:
            return []
        return [s.name for s in mt5.symbols_get()]
    
    def fetch_candles(self, symbol: str, timeframe: str = "H1", 
                      count: int = 1000) -> pd.DataFrame:
        """Fetch historical candlestick data"""
        if not self.connected:
            return pd.DataFrame()
        
        timeframe_map = {
            "1m": mt5.TIMEFRAME_M1,
            "5m": mt5.TIMEFRAME_M5,
            "15m": mt5.TIMEFRAME_M15,
            "30m": mt5.TIMEFRAME_M30,
            "1h": mt5.TIMEFRAME_H1,
            "4h": mt5.TIMEFRAME_H4,
            "1d": mt5.TIMEFRAME_D1,
            "1w": mt5.TIMEFRAME_W1,
        }
        
        tf = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
        
        if rates is None:
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 
                          'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
        return df
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.connected or self.account_info is None:
            return {}
        
        return {
            "login": self.account_info.login,
            "balance": self.account_info.balance,
            "equity": self.account_info.equity,
            "profit": self.account_info.profit,
            "margin": self.account_info.margin,
            "currency": self.account_info.currency,
        }
    
    def place_order(self, symbol: str, order_type: str, volume: float, 
                   price: float = None, sl: float = None, tp: float = None) -> Dict:
        """Place a trading order"""
        if not self.connected:
            return {"success": False, "error": "Not connected"}
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return {"success": False, "error": "Symbol not found"}
        
        if not symbol_info.visible:
            mt5.symbol_select(symbol, True)
        
        point = symbol_info.point
        
        if order_type.upper() == "BUY":
            order_type_enum = mt5.ORDER_TYPE_BUY
            price = price or mt5.symbol_info_tick(symbol).ask
        else:
            order_type_enum = mt5.ORDER_TYPE_SELL
            price = price or mt5.symbol_info_tick(symbol).bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type_enum,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "Python MT5 order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        if sl:
            request["sl"] = sl
        if tp:
            request["tp"] = tp
        
        result = mt5.order_send(request)
        
        return {
            "success": result.retcode == mt5.TRADE_RETCODE_DONE,
            "order_id": result.order,
            "retcode": result.retcode,
            "comment": result.comment
        }
```

**Step 4: Run test to verify it passes**

Run: `cd Trader && python3 -m pytest tests/test_mt5_client.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add Trader/tests/test_mt5_client.py Trader/src/trader/mt5_client.py
git commit -m "feat: add MetaTrader 5 client module"
```

---

## Task 3: Update Data Fetcher to Support MT5

**Files:**
- Modify: `Trader/src/trader/data_fetcher.py`

**Step 1: Add MT5 method**

```python
try:
    from .mt5_client import MT5Client
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

def fetch_from_mt5(self, symbol: str, period: str = "1y", 
                   interval: str = "1d") -> pd.DataFrame:
    """Fetch data from MetaTrader 5"""
    if not MT5_AVAILABLE:
        return pd.DataFrame()
    
    try:
        client = MT5Client()
        if not client.connect():
            return pd.DataFrame()
        
        timeframe_map = {
            "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1h", "4h": "4h", "1d": "1d", "1wk": "1w"
        }
        timeframe = timeframe_map.get(interval, "1h")
        
        count_map = {"1mo": 720, "3mo": 2160, "6mo": 4320, "1y": 8760, "5y": 43800}
        count = count_map.get(period, 1000)
        
        data = client.fetch_candles(symbol, timeframe, count)
        client.disconnect()
        return data
    except:
        return pd.DataFrame()
```

**Step 2: Commit**

```bash
git add Trader/src/trader/data_fetcher.py
git commit -m "feat: add MT5 data source to data fetcher"
```

---

## Task 4: Create MT5 Trader Module

**Files:**
- Create: `Trader/src/trader/mt5_trader.py`

**Step 1: Write implementation**

```python
from .mt5_client import MT5Client
from typing import Dict, List
from datetime import datetime


class MT5Trader:
    """Execute trades via MetaTrader 5"""
    
    def __init__(self):
        self.client = MT5Client()
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to MT5"""
        self.connected = self.client.connect()
        return self.connected
    
    def disconnect(self):
        """Disconnect from MT5"""
        self.client.disconnect()
        self.connected = False
    
    def buy(self, symbol: str, volume: float, sl: float = None, tp: float = None) -> Dict:
        """Execute buy order"""
        if not self.connected:
            return {"success": False, "error": "Not connected"}
        return self.client.place_order(symbol, "BUY", volume, sl=sl, tp=tp)
    
    def sell(self, symbol: str, volume: float, sl: float = None, tp: float = None) -> Dict:
        """Execute sell order"""
        if not self.connected:
            return {"success": False, "error": "Not connected"}
        return self.client.place_order(symbol, "SELL", volume, sl=sl, tp=tp)
    
    def get_positions(self) -> List[Dict]:
        """Get open positions"""
        if not self.connected:
            return []
        
        positions = mt5.positions_get()
        if positions is None:
            return []
        
        return [{
            "ticket": p.ticket,
            "symbol": p.symbol,
            "volume": p.volume,
            "type": "BUY" if p.type == 0 else "SELL",
            "profit": p.profit,
            "open_price": p.price_open,
            "current_price": p.price_current,
        } for p in positions]
    
    def close_position(self, ticket: int) -> Dict:
        """Close an open position"""
        if not self.connected:
            return {"success": False, "error": "Not connected"}
        
        position = mt5.position_get(ticket=ticket)
        if position is None:
            return {"success": False, "error": "Position not found"}
        
        symbol = position.symbol
        volume = position.volume
        order_type = mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "position": ticket,
            "deviation": 20,
            "magic": 234000,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        return {"success": result.retcode == mt5.TRADE_RETCODE_DONE, "retcode": result.retcode}
```

**Step 2: Commit**

```bash
git add Trader/src/trader/mt5_trader.py
git commit -m "feat: add MT5 trader module"
```

---

## Task 5: Create MT5 Backtester Module

**Files:**
- Create: `Trader/src/trader/mt5_backtester.py`

**Step 1: Write implementation**

```python
from .mt5_client import MT5Client
from .signals import SignalGenerator
import pandas as pd
from typing import Dict, List


class MT5Backtester:
    """Backtest strategies using MT5 historical data"""
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0
        self.position_entry = 0
        self.trades = []
    
    def run_backtest(self, symbol: str, timeframe: str = "H1", 
                    count: int = 1000) -> Dict:
        """Run backtest on MT5 data"""
        client = MT5Client()
        
        if not client.connect():
            return {"error": "Failed to connect to MT5"}
        
        data = client.fetch_candles(symbol, timeframe, count)
        client.disconnect()
        
        if data.empty:
            return {"error": "No data fetched"}
        
        for i in range(50, len(data) - 1):
            window = data.iloc[:i+1]
            generator = SignalGenerator(window)
            signal = generator.generate()
            
            current_price = data.iloc[i]["Close"]
            
            if signal["action"] == "BUY" and self.position == 0:
                self.position = self.balance / current_price
                self.balance = 0
                self.position_entry = current_price
                
            elif signal["action"] == "SELL" and self.position > 0:
                self.balance = self.position * current_price
                profit = self.balance - (self.position * self.position_entry)
                self.trades.append({
                    "entry": self.position_entry,
                    "exit": current_price,
                    "profit": profit,
                    "type": "SELL"
                })
                self.position = 0
        
        total_return = (self.balance - self.initial_balance) / self.initial_balance * 100
        winning = len([t for t in self.trades if t["profit"] > 0])
        
        return {
            "initial_balance": self.initial_balance,
            "final_balance": self.balance,
            "total_return": total_return,
            "total_trades": len(self.trades),
            "winning_trades": winning,
            "win_rate": winning / len(self.trades) * 100 if self.trades else 0,
            "trades": self.trades
        }
```

**Step 2: Commit**

```bash
git add Trader/src/trader/mt5_backtester.py
git commit -m "feat: add MT5 backtester module"
```

---

## Task 6: Add MT5 Settings to Dashboard

**Files:**
- Modify: `Trader/src/trader/dashboard.py`

**Step 1: Add MT5 option to sidebar**

Add to data source section:
```python
data_source = st.radio("Choose data source:", 
    ["Yahoo Finance", "OANDA API", "MetaTrader 5"], horizontal=True)

if data_source == "MetaTrader 5":
    st.info("MT5: Make sure MetaTrader 5 is running and connected")
```

**Step 2: Update data fetching logic**

```python
if data_source == "MetaTrader 5":
    try:
        from trader.data_fetcher import MT5Fetcher
        data = MT5Fetcher().fetch_from_mt5(actual_symbol, period, interval)
    except:
        data = pd.DataFrame()
```

**Step 3: Commit**

```bash
git add Trader/src/trader/dashboard.py
git commit -m "feat: add MT5 option to dashboard"
```

---

## Summary

| Task | Description |
|------|-------------|
| 1 | Add MetaTrader5 to requirements |
| 2 | Create MT5 client module |
| 3 | Update data fetcher for MT5 |
| 4 | Create MT5 trader module |
| 5 | Create MT5 backtester module |
| 6 | Add MT5 to dashboard |

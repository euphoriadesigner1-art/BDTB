# Binance Data Source Integration Plan

**Goal:** Add Binance as a crypto data source for the trading bot.

---

## Task 1: Add Binance Fetch Method to DataFetcher

**Files:** `src/trader/data_fetcher.py`

```python
def fetch_from_binance(self, symbol: str, period: str = "1y", 
                       interval: str = "1d") -> pd.DataFrame:
    """Fetch data from Binance public API"""
    import requests
    
    # Convert symbol to Binance format: BTCUSDT (no separators)
    binance_symbol = symbol.replace("-", "").replace("=", "").replace("/", "")
    if not binance_symbol.endswith("USDT"):
        binance_symbol += "USDT"
    
    # Map intervals to Binance kline intervals
    interval_map = {
        "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "4h": "4h", "1d": "1d", "1wk": "1w"
    }
    binance_interval = interval_map.get(interval, "1d")
    
    # Calculate limit based on period
    limit_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "5y": 1825}
    limit = min(limit_map.get(period, 365), 1000)  # Max 1000 candles
    
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": binance_symbol, "interval": binance_interval, "limit": limit}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data, columns=[
            'time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df.set_index('time', inplace=True)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
        
        return df
    except:
        return pd.DataFrame()
```

---

## Task 2: Add Binance to Dashboard

**Files:** `src/trader/dashboard.py`

1. Add "Binance" to data source radio button
2. Add logic to call `fetch_from_binance()` when selected

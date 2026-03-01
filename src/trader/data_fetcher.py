import yfinance as yf
import pandas as pd
from typing import Dict, List
import os
import requests

try:
    from .oanda_client import OANDAClient
    OANDA_AVAILABLE = True
except ImportError:
    OANDA_AVAILABLE = False

try:
    from .mt5_client import MT5Client
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False


class DataFetcher:
    """Fetches historical forex data from Yahoo Finance or OANDA"""
    
    def __init__(self, cache_dir: str = "data"):
        self.cache_dir = cache_dir
    
    def fetch(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical data for a single asset from Yahoo Finance"""
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        return df
    
    def fetch_multiple(self, symbols: List[str], period: str = "1y", interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """Fetch historical data for multiple assets"""
        return {symbol: self.fetch(symbol, period, interval) for symbol in symbols}
    
    def fetch_from_oanda(self, symbol: str, period: str = "1y", 
                         interval: str = "1d", api_key: str = None) -> pd.DataFrame:
        """Fetch data from OANDA API"""
        if not OANDA_AVAILABLE:
            return pd.DataFrame()
        
        if api_key is None:
            api_key = os.getenv("OANDA_API_KEY", "")
        
        if not api_key or not OANDA_AVAILABLE:
            return pd.DataFrame()
        
        oanda_symbol = self._convert_symbol_to_oanda(symbol)
        granularity = self._convert_interval_to_granularity(interval)
        
        try:
            client = OANDAClient(api_key, practice=True)
        except:
            return pd.DataFrame()
        
        period_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "5y": 1825}
        count = period_map.get(period, 365)
        
        return client.fetch_candles(oanda_symbol, count=count, granularity=granularity)
    
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
    
    def fetch_from_binance(self, symbol: str, period: str = "1y", 
                           interval: str = "1d") -> pd.DataFrame:
        """Fetch data from Binance public API"""
        binance_symbol = symbol.replace("-", "").replace("=", "").replace("/", "")
        if not binance_symbol.endswith("USDT"):
            binance_symbol += "USDT"
        
        interval_map = {
            "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1h", "4h": "4h", "1d": "1d", "1wk": "1w"
        }
        binance_interval = interval_map.get(interval, "1d")
        
        limit_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "5y": 1825}
        limit = min(limit_map.get(period, 365), 1000)
        
        url = "https://api.binance.com/api/v3/klines"
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
    
    def _convert_symbol_to_oanda(self, symbol: str) -> str:
        """Convert Yahoo Finance symbol to OANDA format"""
        mapping = {
            "GC=F": "XAU_USD",
            "BTC-USD": "BTC_USD",
            "USDJPY=X": "USD_JPY",
            "EURUSD=X": "EUR_USD",
            "GBPUSD=X": "GBP_USD",
            "AUDUSD=X": "AUD_USD",
            "USDCAD=X": "USD_CAD",
        }
        return mapping.get(symbol, symbol.replace("=", "_").replace("-", "_"))
    
    def _convert_interval_to_granularity(self, interval: str) -> str:
        """Convert interval to OANDA granularity"""
        mapping = {
            "1m": "M1",
            "5m": "M5", 
            "15m": "M15",
            "30m": "M30",
            "1h": "H1",
            "4h": "H4",
            "1d": "D",
            "1wk": "W"
        }
        return mapping.get(interval, "D")

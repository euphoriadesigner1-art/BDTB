import yfinance as yf
import pandas as pd
from typing import Dict, List
import os

try:
    from .oanda_client import OANDAClient
    OANDA_AVAILABLE = True
except ImportError:
    OANDA_AVAILABLE = False


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

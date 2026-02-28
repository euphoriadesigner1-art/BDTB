import pandas as pd
import numpy as np
from typing import Tuple


class TechnicalIndicators:
    """Calculate technical indicators for forex analysis"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def rsi(self, period: int = 14) -> pd.Series:
        delta = self.data["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        exp1 = self.data["Close"].ewm(span=fast, adjust=False).mean()
        exp2 = self.data["Close"].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        hist = macd - signal_line
        return macd, signal_line, hist
    
    def sma(self, period: int) -> pd.Series:
        return self.data["Close"].rolling(window=period).mean()
    
    def ema(self, period: int) -> pd.Series:
        return self.data["Close"].ewm(span=period, adjust=False).mean()
    
    def bollinger_bands(self, period: int = 20, nbdevup: float = 2.0, nbdevdn: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        sma = self.data["Close"].rolling(window=period).mean()
        std = self.data["Close"].rolling(window=period).std()
        upper = sma + (std * nbdevup)
        lower = sma - (std * nbdevdn)
        return upper, sma, lower
    
    def calculate_all(self) -> pd.DataFrame:
        """Calculate all indicators and return as DataFrame"""
        df = self.data.copy()
        df["RSI"] = self.rsi()
        df["MACD"], df["MACD_Signal"], df["MACD_Hist"] = self.macd()
        df["SMA_20"] = self.sma(20)
        df["SMA_50"] = self.sma(50)
        df["EMA_20"] = self.ema(20)
        df["BB_Upper"], df["BB_Middle"], df["BB_Lower"] = self.bollinger_bands()
        return df

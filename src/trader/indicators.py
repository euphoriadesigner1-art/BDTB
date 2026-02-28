import pandas as pd
import numpy as np
import talib
from typing import Tuple


class TechnicalIndicators:
    """Calculate technical indicators for forex analysis"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def rsi(self, period: int = 14) -> pd.Series:
        close = self.data["Close"].values
        rsi = talib.RSI(close, timeperiod=period)
        return pd.Series(rsi, index=self.data.index)
    
    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        close = self.data["Close"].values
        macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        return (
            pd.Series(macd, index=self.data.index),
            pd.Series(macd_signal, index=self.data.index),
            pd.Series(macd_hist, index=self.data.index)
        )
    
    def sma(self, period: int) -> pd.Series:
        close = self.data["Close"].values
        sma = talib.SMA(close, timeperiod=period)
        return pd.Series(sma, index=self.data.index)
    
    def ema(self, period: int) -> pd.Series:
        close = self.data["Close"].values
        ema = talib.EMA(close, timeperiod=period)
        return pd.Series(ema, index=self.data.index)
    
    def bollinger_bands(self, period: int = 20, nbdevup: float = 2.0, nbdevdn: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        close = self.data["Close"].values
        upper, middle, lower = talib.BBANDS(close, timeperiod=period, nbdevup=nbdevup, nbdevdn=nbdevdn)
        return (
            pd.Series(upper, index=self.data.index),
            pd.Series(middle, index=self.data.index),
            pd.Series(lower, index=self.data.index)
        )
    
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

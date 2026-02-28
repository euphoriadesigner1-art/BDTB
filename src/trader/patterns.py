import pandas as pd
import numpy as np
from typing import Dict, List


class PatternDetector:
    """Detect candlestick and chart patterns"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def _get_body(self, i):
        return abs(self.data["Close"].iloc[i] - self.data["Open"].iloc[i])
    
    def _get_upper_shadow(self, i):
        return self.data["High"].iloc[i] - max(self.data["Close"].iloc[i], self.data["Open"].iloc[i])
    
    def _get_lower_shadow(self, i):
        return min(self.data["Close"].iloc[i], self.data["Open"].iloc[i]) - self.data["Low"].iloc[i]
    
    def _is_doji(self, i, threshold=0.1):
        body = self._get_body(i)
        range_val = self.data["High"].iloc[i] - self.data["Low"].iloc[i]
        if range_val == 0:
            return False
        return body / range_val < threshold
    
    def _is_hammer(self, i):
        body = self._get_body(i)
        lower_shadow = self._get_lower_shadow(i)
        upper_shadow = self._get_upper_shadow(i)
        range_val = self.data["High"].iloc[i] - self.data["Low"].iloc[i]
        return lower_shadow > body * 2 and upper_shadow < body
    
    def _is_engulfing(self, i):
        if i < 1:
            return False
        prev_bearish = self.data["Close"].iloc[i-1] < self.data["Open"].iloc[i-1]
        curr_bullish = self.data["Close"].iloc[i] > self.data["Open"].iloc[i]
        prev_body = abs(self.data["Close"].iloc[i-1] - self.data["Open"].iloc[i-1])
        curr_body = abs(self.data["Close"].iloc[i] - self.data["Open"].iloc[i])
        return prev_bearish and curr_bullish and curr_body > prev_body
    
    def detect_all(self) -> Dict[str, List[Dict]]:
        """Detect all patterns"""
        results = {"candlesticks": []}
        
        for i in range(len(self.data)):
            pattern = None
            signal = 0
            
            if self._is_doji(i):
                pattern = "DOJI"
                signal = 0
            elif self._is_hammer(i):
                pattern = "HAMMER"
                signal = 1
            elif self._is_hammer(i) and self.data["Close"].iloc[i] < self.data["Open"].iloc[i]:
                pattern = "HANGINGMAN"
                signal = -1
            elif self._is_engulfing(i):
                pattern = "ENGULFING"
                signal = 1 if self.data["Close"].iloc[i] > self.data["Open"].iloc[i] else -1
            
            if pattern:
                results["candlesticks"].append({
                    "pattern": pattern,
                    "dates": [self.data.index[i]],
                    "signals": [signal]
                })
        
        return results
    
    def get_latest_patterns(self) -> List[Dict]:
        """Get the most recent patterns"""
        all_results = self.detect_all()
        patterns = []
        
        for category in all_results.values():
            for item in category:
                if len(item.get("dates", [])) > 0:
                    latest_date = item["dates"][-1]
                    patterns.append({
                        "pattern": "CDL" + item["pattern"],
                        "date": latest_date,
                        "signal": item["signals"][-1]
                    })
        
        patterns.sort(key=lambda x: x["date"], reverse=True)
        return patterns[:5]

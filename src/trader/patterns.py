import pandas as pd
import numpy as np
import talib
from typing import Dict, List


class PatternDetector:
    """Detect candlestick and chart patterns"""
    
    PATTERNS = [
        "CDLDOJI", "CDLHAMMER", "CDLHANGINGMAN", "CDLENGULFING",
        "CDLMORNINGSTAR", "CDLEVENINGSTAR", "CDLPIERCING",
        "CDLDARKCLOUDCOVER", "CDLXSIDEGAP3METHODS"
    ]
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def detect_all(self) -> Dict[str, List[Dict]]:
        """Detect all patterns"""
        o = np.asarray(self.data["Open"].values, dtype=np.float64)
        h = np.asarray(self.data["High"].values, dtype=np.float64)
        l = np.asarray(self.data["Low"].values, dtype=np.float64)
        c = np.asarray(self.data["Close"].values, dtype=np.float64)
        
        results = {"candlesticks": []}
        
        for pattern in self.PATTERNS:
            func = getattr(talib, pattern)
            signals = func(o, h, l, c)
            
            found = np.where(signals != 0)[0]
            if len(found) > 0:
                results["candlesticks"].append({
                    "pattern": pattern,
                    "dates": [self.data.index[i] for i in found],
                    "signals": [int(signals[i]) for i in found]
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
                        "pattern": item["pattern"],
                        "date": latest_date,
                        "signal": item["signals"][-1]
                    })
        
        patterns.sort(key=lambda x: x["date"], reverse=True)
        return patterns[:5]

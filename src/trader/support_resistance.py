import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


class SupportResistance:
    """Detect support and resistance levels"""
    
    def __init__(self, data: pd.DataFrame, lookback: int = 50):
        self.data = data
        self.lookback = lookback
    
    def find_levels(self, num_levels: int = 5) -> List[float]:
        """Find key support and resistance levels"""
        highs = self.data["High"].tail(self.lookback)
        lows = self.data["Low"].tail(self.lookback)
        
        all_levels = list(highs) + list(lows)
        
        levels = []
        for price in all_levels:
            if not any(abs(price - l) / l < 0.01 for l in levels):
                levels.append(price)
        
        levels.sort(reverse=True)
        return levels[:num_levels]
    
    def get_current_position(self) -> Dict[str, float]:
        """Get current price position relative to S/R levels"""
        current_price = self.data["Close"].iloc[-1]
        levels = self.find_levels()
        
        support = max([l for l in levels if l < current_price], default=current_price * 0.99)
        resistance = min([l for l in levels if l > current_price], default=current_price * 1.01)
        
        return {
            "current_price": current_price,
            "support": support,
            "resistance": resistance,
            "distance_to_support": (current_price - support) / current_price * 100,
            "distance_to_resistance": (resistance - current_price) / current_price * 100,
        }

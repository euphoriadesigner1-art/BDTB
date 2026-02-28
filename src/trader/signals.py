import pandas as pd
import numpy as np
from typing import Dict
from .indicators import TechnicalIndicators
from .support_resistance import SupportResistance
from .patterns import PatternDetector
from .predictor import PricePredictor


class SignalGenerator:
    """Generate unified trading signals from all indicators"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.indicators = TechnicalIndicators(data)
        self.sr = SupportResistance(data)
        self.patterns = PatternDetector(data)
        self.predictor = PricePredictor()
    
    def generate(self) -> Dict[str, any]:
        """Generate unified trading signal"""
        data_with_indicators = self.indicators.calculate_all()
        
        buy_score = 0
        sell_score = 0
        
        rsi = self.indicators.rsi().iloc[-1]
        if rsi < 30:
            buy_score += 2
        elif rsi > 70:
            sell_score += 2
        
        macd, signal, hist = self.indicators.macd()
        if macd.iloc[-1] > signal.iloc[-1]:
            buy_score += 1
        else:
            sell_score += 1
        
        latest_patterns = self.patterns.get_latest_patterns()
        for p in latest_patterns:
            if p["signal"] > 0:
                buy_score += 1
            elif p["signal"] < 0:
                sell_score += 1
        
        try:
            self.predictor.train(data_with_indicators)
            prediction = self.predictor.predict(data_with_indicators)
            if prediction["direction"] == "up":
                buy_score += 2
            else:
                sell_score += 2
        except:
            pass
        
        if buy_score > sell_score + 1:
            action = "buy"
        elif sell_score > buy_score + 1:
            action = "sell"
        else:
            action = "hold"
        
        confidence = abs(buy_score - sell_score) / (buy_score + sell_score + 1) * 100
        
        return {
            "action": action,
            "confidence": min(confidence, 100),
            "buy_score": buy_score,
            "sell_score": sell_score,
            "rsi": rsi,
            "latest_patterns": latest_patterns,
            "support_resistance": self.sr.get_current_position()
        }
    
    def get_risk_metrics(self, action: str = "hold") -> Dict[str, float]:
        """Calculate risk/reward metrics"""
        position = self.sr.get_current_position()
        
        entry = position["current_price"]
        support = position["support"]
        resistance = position["resistance"]
        
        if action.upper() == "SELL":
            stop_loss = resistance
            take_profit = support
        else:
            stop_loss = support
            take_profit = resistance
        
        risk = abs(entry - stop_loss) / entry * 100
        reward = abs(take_profit - entry) / entry * 100
        risk_reward = reward / risk if risk > 0 else 0
        
        return {
            "entry_price": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_percent": risk,
            "reward_percent": reward,
            "risk_reward_ratio": risk_reward
        }

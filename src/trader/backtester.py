import pandas as pd
import numpy as np
from typing import Dict, List
from .signals import SignalGenerator


class Backtester:
    """Backtest trading signals on historical data"""
    
    def __init__(self, data: pd.DataFrame, initial_balance: float = 10000):
        self.data = data
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0
        self.trades = []
    
    def run(self) -> Dict[str, any]:
        """Run backtest"""
        signals = []
        
        for i in range(50, len(self.data) - 1):
            window = self.data.iloc[:i+1]
            generator = SignalGenerator(window)
            signal = generator.generate()
            signals.append(signal)
            
            if signal["action"] == "buy" and self.position == 0:
                self.position = self.balance / window["Close"].iloc[-1]
                self.balance = 0
                self.trades.append({"type": "buy", "price": window["Close"].iloc[-1], "index": i})
            
            elif signal["action"] == "sell" and self.position > 0:
                self.balance = self.position * window["Close"].iloc[-1]
                self.trades.append({"type": "sell", "price": window["Close"].iloc[-1], "index": i, "pnl": self.balance})
                self.position = 0
        
        if self.position > 0:
            self.balance = self.position * self.data["Close"].iloc[-1]
        
        total_return = (self.balance - self.initial_balance) / self.initial_balance * 100
        winning_trades = [t for t in self.trades if t.get("pnl", 0) > self.initial_balance * 0.01]
        win_rate = len(winning_trades) / (len(self.trades) / 2) * 100 if len(self.trades) > 0 else 0
        
        return {
            "total_trades": len(self.trades) / 2,
            "winning_trades": len(winning_trades),
            "win_rate": win_rate,
            "initial_balance": self.initial_balance,
            "final_balance": self.balance,
            "total_return": total_return,
            "trades": self.trades
        }

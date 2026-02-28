from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime


class PaperTrader:
    """Simulate trading without real money"""
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0
        self.position_entry_price = 0
        self.trades: List[Dict] = []
        self.current_symbol = None
    
    def buy(self, symbol: str, units: int, price: float) -> Dict:
        """Execute a buy order"""
        cost = units * price
        
        if cost > self.balance:
            return {"success": False, "error": "Insufficient balance"}
        
        self.balance -= cost
        self.position = units
        self.position_entry_price = price
        self.current_symbol = symbol
        
        trade = {
            "type": "BUY",
            "symbol": symbol,
            "units": units,
            "price": price,
            "cost": cost,
            "time": datetime.now(),
            "balance": self.balance
        }
        self.trades.append(trade)
        
        return {"success": True, "trade": trade}
    
    def sell(self, symbol: str, units: int, price: float) -> Dict:
        """Execute a sell order"""
        if self.position == 0:
            return {"success": False, "error": "No position to sell"}
        
        proceeds = units * price
        profit = proceeds - (self.position * self.position_entry_price)
        
        self.balance += proceeds
        self.position = 0
        self.position_entry_price = 0
        
        trade = {
            "type": "SELL",
            "symbol": symbol,
            "units": units,
            "price": price,
            "proceeds": proceeds,
            "profit": profit,
            "time": datetime.now(),
            "balance": self.balance
        }
        self.trades.append(trade)
        
        return {"success": True, "trade": trade}
    
    def get_status(self) -> Dict:
        """Get current trading status"""
        return {
            "balance": self.balance,
            "position": self.position,
            "entry_price": self.position_entry_price,
            "total_trades": len(self.trades),
            "total_profit": sum(t.get("profit", 0) for t in self.trades)
        }
    
    def reset(self):
        """Reset to initial state"""
        self.balance = self.initial_balance
        self.position = 0
        self.position_entry_price = 0
        self.trades = []
        self.current_symbol = None

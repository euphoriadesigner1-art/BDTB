try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    mt5 = None
    MT5_AVAILABLE = False

from .mt5_client import MT5Client
from .signals import SignalGenerator
import pandas as pd
from typing import Dict, List


class MT5Backtester:
    """Backtest strategies using MT5 historical data"""
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0
        self.position_entry = 0
        self.trades = []
    
    def is_available(self) -> bool:
        """Check if MT5 is available"""
        return MT5_AVAILABLE
    
    def run_backtest(self, symbol: str, timeframe: str = "H1", 
                    count: int = 1000) -> Dict:
        """Run backtest on MT5 data"""
        if not MT5_AVAILABLE:
            return {"error": "MT5 not available"}
        
        client = MT5Client()
        
        if not client.connect():
            return {"error": "Failed to connect to MT5"}
        
        data = client.fetch_candles(symbol, timeframe, count)
        client.disconnect()
        
        if data.empty:
            return {"error": "No data fetched"}
        
        self.balance = self.initial_balance
        self.position = 0
        self.position_entry = 0
        self.trades = []
        
        for i in range(50, len(data) - 1):
            window = data.iloc[:i+1]
            generator = SignalGenerator(window)
            signal = generator.generate()
            
            current_price = data.iloc[i]["Close"]
            
            if signal["action"] == "BUY" and self.position == 0:
                self.position = self.balance / current_price
                self.balance = 0
                self.position_entry = current_price
                
            elif signal["action"] == "SELL" and self.position > 0:
                self.balance = self.position * current_price
                profit = self.balance - (self.position * self.position_entry)
                self.trades.append({
                    "entry": self.position_entry,
                    "exit": current_price,
                    "profit": profit,
                    "type": "SELL"
                })
                self.position = 0
        
        if self.position > 0:
            final_price = data.iloc[-1]["Close"]
            self.balance = self.position * final_price
        
        total_return = (self.balance - self.initial_balance) / self.initial_balance * 100
        winning = len([t for t in self.trades if t["profit"] > 0])
        
        return {
            "initial_balance": self.initial_balance,
            "final_balance": self.balance,
            "total_return": total_return,
            "total_trades": len(self.trades),
            "winning_trades": winning,
            "win_rate": winning / len(self.trades) * 100 if self.trades else 0,
            "trades": self.trades
        }
    
    def reset(self):
        """Reset backtester state"""
        self.balance = self.initial_balance
        self.position = 0
        self.position_entry = 0
        self.trades = []

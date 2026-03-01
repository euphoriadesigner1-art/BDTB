try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    mt5 = None
    MT5_AVAILABLE = False

from .mt5_client import MT5Client
from typing import Dict, List
from datetime import datetime


class MT5Trader:
    """Execute trades via MetaTrader 5"""
    
    def __init__(self):
        self.client = MT5Client()
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to MT5"""
        self.connected = self.client.connect()
        return self.connected
    
    def disconnect(self):
        """Disconnect from MT5"""
        self.client.disconnect()
        self.connected = False
    
    def is_available(self) -> bool:
        """Check if MT5 is available"""
        return MT5_AVAILABLE
    
    def buy(self, symbol: str, volume: float, sl: float = None, tp: float = None) -> Dict:
        """Execute buy order"""
        if not self.connected:
            return {"success": False, "error": "Not connected"}
        return self.client.place_order(symbol, "BUY", volume, sl=sl, tp=tp)
    
    def sell(self, symbol: str, volume: float, sl: float = None, tp: float = None) -> Dict:
        """Execute sell order"""
        if not self.connected:
            return {"success": False, "error": "Not connected"}
        return self.client.place_order(symbol, "SELL", volume, sl=sl, tp=tp)
    
    def get_positions(self) -> List[Dict]:
        """Get open positions"""
        if not self.connected or not MT5_AVAILABLE:
            return []
        
        positions = mt5.positions_get()
        if positions is None:
            return []
        
        return [{
            "ticket": p.ticket,
            "symbol": p.symbol,
            "volume": p.volume,
            "type": "BUY" if p.type == 0 else "SELL",
            "profit": p.profit,
            "open_price": p.price_open,
            "current_price": p.price_current,
        } for p in positions]
    
    def close_position(self, ticket: int) -> Dict:
        """Close an open position"""
        if not self.connected or not MT5_AVAILABLE:
            return {"success": False, "error": "Not connected"}
        
        position = mt5.position_get(ticket=ticket)
        if position is None:
            return {"success": False, "error": "Position not found"}
        
        symbol = position.symbol
        volume = position.volume
        order_type = mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "position": ticket,
            "deviation": 20,
            "magic": 234000,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        return {"success": result.retcode == mt5.TRADE_RETCODE_DONE, "retcode": result.retcode}
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.connected:
            return {}
        return self.client.get_account_info()

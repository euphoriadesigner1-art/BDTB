try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    mt5 = None
    MT5_AVAILABLE = False

import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime


class MT5Client:
    """MetaTrader 5 client for data and trading"""
    
    def __init__(self):
        self.connected = False
        self.account_info = None
    
    def connect(self) -> bool:
        """Initialize MT5 connection"""
        if not MT5_AVAILABLE:
            return False
        
        if not mt5.initialize():
            return False
        
        self.connected = True
        self.account_info = mt5.account_info()
        return True
    
    def disconnect(self):
        """Disconnect from MT5"""
        if MT5_AVAILABLE:
            mt5.shutdown()
        self.connected = False
    
    def is_available(self) -> bool:
        """Check if MT5 is available"""
        return MT5_AVAILABLE
    
    def get_symbols(self) -> List[str]:
        """Get available trading symbols"""
        if not self.connected or not MT5_AVAILABLE:
            return []
        
        symbols = mt5.symbols_get()
        return [s.name for s in symbols] if symbols else []
    
    def fetch_candles(self, symbol: str, timeframe: str = "H1", 
                     count: int = 1000) -> pd.DataFrame:
        """Fetch historical candlestick data"""
        if not self.connected or not MT5_AVAILABLE:
            return pd.DataFrame()
        
        timeframe_map = {
            "1m": mt5.TIMEFRAME_M1,
            "5m": mt5.TIMEFRAME_M5,
            "15m": mt5.TIMEFRAME_M15,
            "30m": mt5.TIMEFRAME_M30,
            "1h": mt5.TIMEFRAME_H1,
            "4h": mt5.TIMEFRAME_H4,
            "1d": mt5.TIMEFRAME_D1,
            "1w": mt5.TIMEFRAME_W1,
        }
        
        tf = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
        
        if rates is None:
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        df.rename(columns={
            'open': 'Open', 
            'high': 'High', 
            'low': 'Low', 
            'close': 'Close', 
            'tick_volume': 'Volume'
        }, inplace=True)
        return df
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.connected or not MT5_AVAILABLE or self.account_info is None:
            return {}
        
        return {
            "login": self.account_info.login,
            "balance": self.account_info.balance,
            "equity": self.account_info.equity,
            "profit": self.account_info.profit,
            "margin": self.account_info.margin,
            "currency": self.account_info.currency,
        }
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        if not self.connected or not MT5_AVAILABLE:
            return None
        
        info = mt5.symbol_info(symbol)
        if info is None:
            return None
        
        return {
            "name": info.name,
            "bid": info.bid,
            "ask": info.ask,
            "point": info.point,
            "digits": info.digits,
            "volume_min": info.volume_min,
            "volume_max": info.volume_max,
        }
    
    def place_order(self, symbol: str, order_type: str, volume: float, 
                   price: float = None, sl: float = None, tp: float = None) -> Dict:
        """Place a trading order"""
        if not self.connected or not MT5_AVAILABLE:
            return {"success": False, "error": "Not connected"}
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return {"success": False, "error": "Symbol not found"}
        
        if not symbol_info.visible:
            mt5.symbol_select(symbol, True)
        
        point = symbol_info.point
        
        if order_type.upper() == "BUY":
            order_type_enum = mt5.ORDER_TYPE_BUY
            tick = mt5.symbol_info_tick(symbol)
            price = price or tick.ask if tick else None
        else:
            order_type_enum = mt5.ORDER_TYPE_SELL
            tick = mt5.symbol_info_tick(symbol)
            price = price or tick.bid if tick else None
        
        if price is None:
            return {"success": False, "error": "Could not get price"}
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type_enum,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "Python MT5 order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        if sl:
            request["sl"] = sl
        if tp:
            request["tp"] = tp
        
        result = mt5.order_send(request)
        
        return {
            "success": result.retcode == mt5.TRADE_RETCODE_DONE,
            "order_id": result.order,
            "retcode": result.retcode,
            "comment": result.comment
        }
    
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

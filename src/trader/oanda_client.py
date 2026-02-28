import oandapyV20
from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime


class OANDAClient:
    """OANDA API client for fetching historical data"""
    
    def __init__(self, api_key: str, practice: bool = True):
        self.api_key = api_key
        self.practice = practice
        environment = "practice" if practice else "live"
        self.client = API(access_token=api_key, environment=environment)
    
    def fetch_candles(self, instrument: str, count: int = 100, 
                      granularity: str = "D") -> pd.DataFrame:
        """Fetch historical candle data from OANDA"""
        params = {
            "count": count,
            "granularity": granularity,
        }
        
        try:
            response = self.client.request(
                instruments.InstrumentCandles(instrument=instrument, params=params)
            )
            candles = response.get("candles", [])
            
            data = []
            for c in candles:
                data.append({
                    "time": c["time"],
                    "Open": float(c["mid"]["o"]),
                    "High": float(c["mid"]["h"]),
                    "Low": float(c["mid"]["l"]),
                    "Close": float(c["mid"]["c"]),
                    "Volume": int(c["volume"])
                })
            
            df = pd.DataFrame(data)
            df["time"] = pd.to_datetime(df["time"])
            df.set_index("time", inplace=True)
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        try:
            from oandapyV20.endpoints.accounts import AccountDetails
            response = self.client.request(AccountDetails(accountID=self._get_account_id()))
            return response
        except Exception as e:
            return {"error": str(e)}
    
    def _get_account_id(self) -> str:
        """Get default account ID"""
        try:
            from oandapyV20.endpoints.accounts import Accounts
            response = self.client.request(Accounts())
            return response["accounts"][0]["id"]
        except Exception:
            return ""

import pandas as pd
import os
from pathlib import Path
from typing import Optional


class DataCache:
    """Caches fetched data to avoid repeated API calls"""
    
    def __init__(self, cache_dir: str = "data"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_path(self, symbol: str) -> Path:
        return self.cache_dir / f"{symbol.replace('=', '_')}.parquet"
    
    def save(self, df: pd.DataFrame, symbol: str) -> None:
        df.to_parquet(self._get_path(symbol))
    
    def load(self, symbol: str) -> Optional[pd.DataFrame]:
        path = self._get_path(symbol)
        if path.exists():
            return pd.read_parquet(path)
        return None

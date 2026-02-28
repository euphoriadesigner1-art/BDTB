# Forex Trading Bot Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a forex trading bot that generates Buy/Sell signals, identifies Support/Resistance levels, predicts price direction, and recognizes patterns using historical data.

**Architecture:** Hybrid approach combining technical indicators (RSI, MACD, Moving Averages) for signals + traditional ML (Random Forest/XGBoost) for price direction prediction + pattern recognition.

**Tech Stack:** Python, yfinance, pandas, TA-Lib, scikit-learn/XGBoost, Streamlit

---

## Phase 1: Project Setup

### Task 1: Initialize Python Project

**Files:**
- Create: `Trader/pyproject.toml`
- Create: `Trader/src/trader/__init__.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "trader-bot"
version = "0.1.0"
description = "Forex trading bot with signals and predictions"
requires-python = ">=3.11"
dependencies = [
    "yfinance>=0.2.36",
    "pandas>=2.1.0",
    "numpy>=1.26.0",
    "ta-lib>=0.4.28",
    "scikit-learn>=1.4.0",
    "xgboost>=2.0.0",
    "streamlit>=1.30.0",
    "plotly>=5.18.0",
    "python-dotenv>=1.0.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.12.0",
]
```

**Step 2: Create src/trader/__init__.py**

```python
"""Trader Bot - Forex Trading Signal Generator"""

__version__ = "0.1.0"
```

**Step 3: Commit**

```bash
git add Trader/pyproject.toml Trader/src/trader/__init__.py
git commit -m "feat: initialize trader-bot project"
```

---

## Phase 2: Data Layer

### Task 2: Data Fetcher Module

**Files:**
- Create: `Trader/tests/test_data_fetcher.py`
- Create: `Trader/src/trader/data_fetcher.py`
- Modify: `Trader/pyproject.toml`

**Step 1: Write the failing test**

```python
# Trader/tests/test_data_fetcher.py
import pytest
from trader.data_fetcher import DataFetcher

def test_fetch_historical_data():
    fetcher = DataFetcher()
    df = fetcher.fetch("EURUSD=X", period="1y", interval="1d")
    assert df is not None
    assert len(df) > 0
    assert "Close" in df.columns

def test_fetch_multiple_assets():
    fetcher = DataFetcher()
    assets = ["XAUUSD=X", "BTCUSD=X"]
    data = fetcher.fetch_multiple(assets, period="1mo")
    assert len(data) == 2
    assert "XAUUSD=X" in data
```

**Step 2: Run test to verify it fails**

Run: `cd Trader && python -m pytest tests/test_data_fetcher.py -v`
Expected: FAIL (ModuleNotFoundError)

**Step 3: Write minimal implementation**

```python
# Trader/src/trader/data_fetcher.py
import yfinance as yf
import pandas as pd
from typing import Dict, List

class DataFetcher:
    """Fetches historical forex data from Yahoo Finance"""
    
    def __init__(self, cache_dir: str = "data"):
        self.cache_dir = cache_dir
    
    def fetch(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical data for a single asset"""
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        return df
    
    def fetch_multiple(self, symbols: List[str], period: str = "1y", interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """Fetch historical data for multiple assets"""
        return {symbol: self.fetch(symbol, period, interval) for symbol in symbols}
```

**Step 4: Run test to verify it passes**

Run: `cd Trader && python -m pytest tests/test_data_fetcher.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add Trader/tests/test_data_fetcher.py Trader/src/trader/data_fetcher.py
git commit -m "feat: add data fetcher module for Yahoo Finance"
```

---

### Task 3: Data Cache Module

**Files:**
- Create: `Trader/tests/test_cache.py`
- Create: `Trader/src/trader/cache.py`

**Step 1: Write the failing test**

```python
# Trader/tests/test_cache.py
import pytest
import pandas as pd
from trader.cache import DataCache

def test_save_and_load():
    cache = DataCache("data/test_cache")
    df = pd.DataFrame({"Close": [1.0, 2.0, 3.0]})
    cache.save(df, "TEST")
    loaded = cache.load("TEST")
    assert loaded is not None
    assert len(loaded) == 3

def test_load_missing():
    cache = DataCache("data/test_cache")
    result = cache.load("NONEXISTENT")
    assert result is None
```

**Step 2: Run test to verify it fails**

Run: `cd Trader && python -m pytest tests/test_cache.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Trader/src/trader/cache.py
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
```

**Step 4: Run test to verify it passes**

Run: `cd Trader && python -m pytest tests/test_cache.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add Trader/tests/test_cache.py Trader/src/trader/cache.py
git commit -m "feat: add data cache module"
```

---

## Phase 3: Analysis Engine

### Task 4: Technical Indicators Module

**Files:**
- Create: `Trader/tests/test_indicators.py`
- Create: `Trader/src/trader/indicators.py`

**Step 1: Write the failing test**

```python
# Trader/tests/test_indicators.py
import pytest
import pandas as pd
import numpy as np
from trader.indicators import TechnicalIndicators

@pytest.fixture
def sample_data():
    dates = pd.date_range("2024-01-01", periods=100)
    data = {
        "Open": np.random.uniform(100, 110, 100),
        "High": np.random.uniform(110, 120, 100),
        "Low": np.random.uniform(90, 100, 100),
        "Close": np.random.uniform(100, 110, 100),
        "Volume": np.random.randint(1000, 10000, 100),
    }
    return pd.DataFrame(data, index=dates)

def test_rsi(sample_data):
    indicators = TechnicalIndicators(sample_data)
    rsi = indicators.rsi()
    assert rsi is not None
    assert len(rsi) == 100
    assert 0 <= rsi.iloc[-1] <= 100

def test_macd(sample_data):
    indicators = TechnicalIndicators(sample_data)
    macd, signal, hist = indicators.macd()
    assert macd is not None
    assert signal is not None
    assert hist is not None

def test_moving_averages(sample_data):
    indicators = TechnicalIndicators(sample_data)
    ma20 = indicators.sma(20)
    ma50 = indicators.sma(50)
    assert ma20 is not None
    assert ma50 is not None
```

**Step 2: Run test to verify it fails**

Run: `cd Trader && python -m pytest tests/test_indicators.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Trader/src/trader/indicators.py
import pandas as pd
import numpy as np
import talib
from typing import Tuple

class TechnicalIndicators:
    """Calculate technical indicators for forex analysis"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def rsi(self, period: int = 14) -> pd.Series:
        close = self.data["Close"].values
        rsi = talib.RSI(close, timeperiod=period)
        return pd.Series(rsi, index=self.data.index)
    
    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        close = self.data["Close"].values
        macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        return (
            pd.Series(macd, index=self.data.index),
            pd.Series(macd_signal, index=self.data.index),
            pd.Series(macd_hist, index=self.data.index)
        )
    
    def sma(self, period: int) -> pd.Series:
        close = self.data["Close"].values
        sma = talib.SMA(close, timeperiod=period)
        return pd.Series(sma, index=self.data.index)
    
    def ema(self, period: int) -> pd.Series:
        close = self.data["Close"].values
        ema = talib.EMA(close, timeperiod=period)
        return pd.Series(ema, index=self.data.index)
    
    def bollinger_bands(self, period: int = 20, nbdevup: float = 2.0, nbdevdn: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        close = self.data["Close"].values
        upper, middle, lower = talib.BBANDS(close, timeperiod=period, nbdevup=nbdevup, nbdevdn=nbdevdn)
        return (
            pd.Series(upper, index=self.data.index),
            pd.Series(middle, index=self.data.index),
            pd.Series(lower, index=self.data.index)
        )
    
    def calculate_all(self) -> pd.DataFrame:
        """Calculate all indicators and return as DataFrame"""
        df = self.data.copy()
        df["RSI"] = self.rsi()
        df["MACD"], df["MACD_Signal"], df["MACD_Hist"] = self.macd()
        df["SMA_20"] = self.sma(20)
        df["SMA_50"] = self.sma(50)
        df["EMA_20"] = self.ema(20)
        df["BB_Upper"], df["BB_Middle"], df["BB_Lower"] = self.bollinger_bands()
        return df
```

**Step 4: Run test to verify it passes**

Run: `cd Trader && python -m pytest tests/test_indicators.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add Trader/tests/test_indicators.py Trader/src/trader/indicators.py
git commit -m "feat: add technical indicators module"
```

---

### Task 5: Support/Resistance Detector

**Files:**
- Create: `Trader/tests/test_support_resistance.py`
- Create: `Trader/src/trader/support_resistance.py`

**Step 1: Write the failing test**

```python
# Trader/tests/test_support_resistance.py
import pytest
import pandas as pd
import numpy as np
from trader.support_resistance import SupportResistance

@pytest.fixture
def sample_data():
    dates = pd.date_range("2024-01-01", periods=100)
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(100) * 2)
    return pd.DataFrame({"Close": close, "High": close + 5, "Low": close - 5}, index=dates)

def test_find_support_resistance(sample_data):
    sr = SupportResistance(sample_data)
    levels = sr.find_levels()
    assert levels is not None
    assert len(levels) > 0

def test_current_price_position(sample_data):
    sr = SupportResistance(sample_data)
    position = sr.get_current_position()
    assert position is not None
    assert "support" in position
    assert "resistance" in position
```

**Step 2: Run test to verify it fails**

Run: `cd Trader && python -m pytest tests/test_support_resistance.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Trader/src/trader/support_resistance.py
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
```

**Step 4: Run test to verify it passes**

Run: `cd Trader && python -m pytest tests/test_support_resistance.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add Trader/tests/test_support_resistance.py Trader/src/trader/support_resistance.py
git commit -m "feat: add support/resistance detector"
```

---

### Task 6: Pattern Recognition Module

**Files:**
- Create: `Trader/tests/test_patterns.py`
- Create: `Trader/src/trader/patterns.py`

**Step 1: Write the failing test**

```python
# Trader/tests/test_patterns.py
import pytest
import pandas as pd
import numpy as np
from trader.patterns import PatternDetector

@pytest.fixture
def sample_data():
    dates = pd.date_range("2024-01-01", periods=50)
    return pd.DataFrame({
        "Open": [100, 102, 101, 103, 102, 104, 103, 105, 104, 106] * 5,
        "High": [105, 107, 106, 108, 107, 109, 108, 110, 109, 111] * 5,
        "Low": [95, 97, 96, 98, 97, 99, 98, 100, 99, 101] * 5,
        "Close": [102, 101, 103, 102, 104, 103, 105, 104, 106, 105] * 5,
    }, index=dates)

def test_detect_patterns(sample_data):
    detector = PatternDetector(sample_data)
    patterns = detector.detect_all()
    assert patterns is not None
    assert "candlesticks" in patterns
```

**Step 2: Run test to verify it fails**

Run: `cd Trader && python -m pytest tests/test_patterns.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Trader/src/trader/patterns.py
import pandas as pd
import numpy as np
import talib
from typing import Dict, List

class PatternDetector:
    """Detect candlestick and chart patterns"""
    
    PATTERNS = [
        "CDLDOJI", "CDLHAMMER", "CDLHANGINGMAN", "CDLENGULFING",
        "CDLMORNINGSTAR", "CDLEVENINGSTAR", "CDLSTAR", "CDLPIERCING",
        "CDLDARKCLOUDCOVER", "CDLXSIDEGAP3METHODS"
    ]
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def detect_all(self) -> Dict[str, List[Dict]]:
        """Detect all patterns"""
        o = self.data["Open"].values
        h = self.data["High"].values
        l = self.data["Low"].values
        c = self.data["Close"].values
        
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
```

**Step 4: Run test to verify it passes**

Run: `cd Trader && python -m pytest tests/test_patterns.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add Trader/tests/test_patterns.py Trader/src/trader/patterns.py
git commit -m "feat: add pattern recognition module"
```

---

### Task 7: ML Price Direction Predictor

**Files:**
- Create: `Trader/tests/test_predictor.py`
- Create: `Trader/src/trader/predictor.py`

**Step 1: Write the failing test**

```python
# Trader/tests/test_predictor.py
import pytest
import pandas as pd
import numpy as np
from trader.predictor import PricePredictor

@pytest.fixture
def sample_data():
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=200)
    data = {
        "Close": 100 + np.cumsum(np.random.randn(200)),
        "RSI": np.random.uniform(30, 70, 200),
        "MACD": np.random.randn(200),
        "MACD_Signal": np.random.randn(200),
        "SMA_20": 100 + np.cumsum(np.random.randn(200) * 0.5),
    }
    return pd.DataFrame(data, index=dates)

def test_prepare_features(sample_data):
    predictor = PricePredictor()
    X, y = predictor.prepare_features(sample_data)
    assert X is not None
    assert y is not None
    assert len(X) == len(y)

def test_train_and_predict(sample_data):
    predictor = PricePredictor(model_type="random_forest")
    predictor.train(sample_data)
    prediction = predictor.predict(sample_data)
    assert prediction is not None
    assert "direction" in prediction
    assert "confidence" in prediction
```

**Step 2: Run test to verify it fails**

Run: `cd Trader && python -m pytest tests/test_predictor.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Trader/src/trader/predictor.py
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class PricePredictor:
    """ML model to predict price direction"""
    
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
    
    def prepare_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for training"""
        df = data.copy()
        
        df["Returns"] = df["Close"].pct_change()
        df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
        
        df = df.dropna()
        
        self.feature_columns = ["RSI", "MACD", "MACD_Signal", "SMA_20", "Returns"]
        available_cols = [c for c in self.feature_columns if c in df.columns]
        
        X = df[available_cols].values
        y = df["Target"].values
        
        return X, y
    
    def train(self, data: pd.DataFrame) -> None:
        """Train the prediction model"""
        X, y = self.prepare_features(data)
        
        if len(X) < 50:
            raise ValueError("Not enough data for training")
        
        X_scaled = self.scaler.fit_transform(X)
        
        if self.model_type == "random_forest":
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        self.model.fit(X_scaled, y)
    
    def predict(self, data: pd.DataFrame) -> Dict[str, any]:
        """Predict price direction"""
        if self.model is None:
            return {"direction": "neutral", "confidence": 0, "error": "Model not trained"}
        
        X, _ = self.prepare_features(data)
        X_scaled = self.scaler.transform(X[-1:])
        
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        direction = "up" if prediction == 1 else "down"
        confidence = float(max(probabilities)) * 100
        
        return {
            "direction": direction,
            "confidence": confidence,
            "model": self.model_type
        }
    
    def backtest(self, data: pd.DataFrame, train_size: float = 0.8) -> Dict[str, any]:
        """Backtest the model"""
        df = data.copy()
        train_data = df.iloc[:int(len(df) * train_size)]
        test_data = df.iloc[int(len(df) * train_size):]
        
        self.train(train_data)
        
        correct = 0
        total = 0
        
        for i in range(len(test_data) - 1):
            window = test_data.iloc[:i+1]
            if len(window) > 10:
                try:
                    pred = self.predict(window)
                    actual = "up" if test_data.iloc[i+1]["Close"] > test_data.iloc[i]["Close"] else "down"
                    if pred["direction"] == actual:
                        correct += 1
                    total += 1
                except:
                    pass
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            "accuracy": accuracy,
            "total_predictions": total,
            "correct_predictions": correct
        }
```

**Step 4: Run test to verify it passes**

Run: `cd Trader && python -m pytest tests/test_predictor.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add Trader/tests/test_predictor.py Trader/src/trader/predictor.py
git commit -m "feat: add ML price direction predictor"
```

---

### Task 8: Signals Generator

**Files:**
- Create: `Trader/tests/test_signals.py`
- Create: `Trader/src/trader/signals.py`

**Step 1: Write the failing test**

```python
# Trader/tests/test_signals.py
import pytest
import pandas as pd
import numpy as np
from trader.signals import SignalGenerator

@pytest.fixture
def sample_data():
    dates = pd.date_range("2024-01-01", periods=100)
    np.random.seed(42)
    return pd.DataFrame({
        "Open": np.random.uniform(100, 110, 100),
        "High": np.random.uniform(110, 120, 100),
        "Low": np.random.uniform(90, 100, 100),
        "Close": np.random.uniform(100, 110, 100),
        "Volume": np.random.randint(1000, 10000, 100),
    }, index=dates)

def test_generate_signal(sample_data):
    generator = SignalGenerator(sample_data)
    signal = generator.generate()
    assert signal is not None
    assert "action" in signal
    assert signal["action"] in ["buy", "sell", "hold"]

def test_risk_metrics(sample_data):
    generator = SignalGenerator(sample_data)
    risk = generator.get_risk_metrics()
    assert risk is not None
    assert "risk_reward_ratio" in risk
```

**Step 2: Run test to verify it fails**

Run: `cd Trader && python -m pytest tests/test_signals.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Trader/src/trader/signals.py
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
    
    def get_risk_metrics(self) -> Dict[str, float]:
        """Calculate risk/reward metrics"""
        position = self.sr.get_current_position()
        
        entry = position["current_price"]
        support = position["support"]
        resistance = position["resistance"]
        
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
```

**Step 4: Run test to verify it passes**

Run: `cd Trader && python -m pytest tests/test_signals.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add Trader/tests/test_signals.py Trader/src/trader/signals.py
git commit -m "feat: add signals generator"
```

---

### Task 9: Backtester Module

**Files:**
- Create: `Trader/tests/test_backtester.py`
- Create: `Trader/src/trader/backtester.py`

**Step 1: Write the failing test**

```python
# Trader/tests/test_backtester.py
import pytest
import pandas as pd
import numpy as np
from trader.backtester import Backtester

@pytest.fixture
def sample_data():
    dates = pd.date_range("2024-01-01", periods=200)
    np.random.seed(42)
    return pd.DataFrame({
        "Open": np.random.uniform(100, 110, 200),
        "High": np.random.uniform(110, 120, 200),
        "Low": np.random.uniform(90, 100, 200),
        "Close": 100 + np.cumsum(np.random.randn(200)),
        "Volume": np.random.randint(1000, 10000, 200),
    }, index=dates)

def test_run_backtest(sample_data):
    backtester = Backtester(sample_data)
    results = backtester.run()
    assert results is not None
    assert "total_trades" in results
    assert "win_rate" in results
```

**Step 2: Run test to verify it fails**

Run: `cd Trader && python -m pytest tests/test_backv`
Expected:tester.py - FAIL

**Step 3: Write minimal implementation**

```python
# Trader/src/trader/backtester.py
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
```

**Step 4: Run test to verify it passes**

Run: `cd Trader && python -m pytest tests/test_backtester.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add Trader/tests/test_backtester.py Trader/src/trader/backtester.py
git commit -m "feat: add backtester module"
```

---

## Phase 4: CLI Interface

### Task 10: CLI Module

**Files:**
- Create: `Trader/src/trader/cli.py`

**Step 1: Write the implementation**

```python
# Trader/src/trader/cli.py
import argparse
import sys
from .data_fetcher import DataFetcher
from .signals import SignalGenerator
from .backtester import Backtester

def main():
    parser = argparse.ArgumentParser(description="Forex Trading Bot")
    parser.add_argument("--symbol", "-s", required=True, help="Forex symbol (e.g., XAUUSD=X)")
    parser.add_argument("--period", "-p", default="1y", help="Period (1d, 1mo, 1y, 5y)")
    parser.add_argument("--interval", "-i", default="1d", help="Interval (1m, 1h, 1d)")
    parser.add_argument("--backtest", "-b", action="store_true", help="Run backtest")
    
    args = parser.parse_args()
    
    print(f"Fetching data for {args.symbol}...")
    fetcher = DataFetcher()
    data = fetcher.fetch(args.symbol, period=args.period, interval=args.interval)
    
    if data is None or len(data) == 0:
        print(f"Error: No data fetched for {args.symbol}")
        sys.exit(1)
    
    print(f"Generating signals...")
    generator = SignalGenerator(data)
    signal = generator.generate()
    risk = generator.get_risk_metrics()
    
    print("\n" + "="*50)
    print(f"TRADING SIGNAL FOR {args.symbol}")
    print("="*50)
    print(f"Action: {signal['action'].upper()}")
    print(f"Confidence: {signal['confidence']:.1f}%")
    print(f"RSI: {signal['rsi']:.2f}")
    print(f"\nSupport/Resistance:")
    print(f"  Support: {risk['stop_loss']:.2f}")
    print(f"  Resistance: {risk['take_profit']:.2f}")
    print(f"  Risk/Reward: {risk['risk_reward_ratio']:.2f}")
    print("="*50)
    
    if args.backtest:
        print("\nRunning backtest...")
        backtester = Backtester(data)
        results = backtester.run()
        print(f"\nBacktest Results:")
        print(f"  Total Trades: {results['total_trades']}")
        print(f"  Win Rate: {results['win_rate']:.1f}%")
        print(f"  Total Return: {results['total_return']:.2f}%")

if __name__ == "__main__":
    main()
```

**Step 2: Update pyproject.toml to add CLI entry point**

```toml
[project.scripts]
trader = "trader.cli:main"
```

**Step 3: Commit**

```bash
git add Trader/src/trader/cli.py
git commit -m "feat: add CLI interface"
```

---

## Phase 5: Streamlit Dashboard

### Task 11: Streamlit Dashboard

**Files:**
- Create: `Trader/src/trader/dashboard.py`

**Step 1: Write the implementation**

```python
# Trader/src/trader/dashboard.py
import streamlit as st
import pandas as pd
from .data_fetcher import DataFetcher
from .indicators import TechnicalIndicators
from .signals import SignalGenerator
from .support_resistance import SupportResistance
from .patterns import PatternDetector
import plotly.graph_objects as go

st.set_page_config(page_title="Forex Trading Bot", layout="wide")

st.title("📈 Forex Trading Signal Generator")

with st.sidebar:
    st.header("Settings")
    symbol = st.selectbox("Symbol", ["XAUUSD=X", "BTCUSD=X", "USDJPY=X"])
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "5y"])
    interval = st.selectbox("Interval", ["1h", "4h", "1d", "1wk"])

if st.button("Generate Signals"):
    with st.spinner("Fetching data..."):
        fetcher = DataFetcher()
        data = fetcher.fetch(symbol, period=period, interval=interval)
        
        if data is None or len(data) == 0:
            st.error("No data fetched")
        else:
            generator = SignalGenerator(data)
            signal = generator.generate()
            risk = generator.get_risk_metrics()
            indicators = TechnicalIndicators(data)
            sr = SupportResistance(data)
            patterns = PatternDetector(data)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Signal", signal["action"].upper(), f"{signal['confidence']:.1f}% confidence")
            
            with col2:
                st.metric("Current Price", f"${risk['entry_price']:.2f}")
            
            with col3:
                st.metric("Risk/Reward", f"1:{risk['risk_reward_ratio']:.2f}")
            
            st.subheader("Support & Resistance")
            sr_col1, sr_col2 = st.columns(2)
            sr_col1.metric("Support", f"${risk['stop_loss']:.2f}")
            sr_col2.metric("Resistance", f"${risk['take_profit']:.2f}")
            
            st.subheader("Technical Indicators")
            ind_df = indicators.calculate_all()
            st.line_chart(ind_df[["Close", "SMA_20", "SMA_50", "BB_Upper", "BB_Lower"]])
            
            st.subheader("RSI")
            st.line_chart(ind_df["RSI"])
            
            st.subheader("Recent Patterns")
            recent_patterns = patterns.get_latest_patterns()
            for p in recent_patterns:
                st.write(f"- {p['pattern']} on {p['date'].date()}")

if __name__ == "__main__":
    import sys
    sys.argv = ["streamlit", "run", __file__]
    import subprocess
    subprocess.run(sys.argv)
```

**Step 2: Create dashboard launcher script**

```python
# Trader/run_dashboard.py
#!/usr/bin/env python
import sys
import subprocess

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "src/trader/dashboard.py"]
    subprocess.run(sys.argv)
```

**Step 3: Commit**

```bash
git add Trader/src/trader/dashboard.py Trader/run_dashboard.py
git commit -m "feat: add Streamlit dashboard"
```

---

## Phase 6: Integration & Testing

### Task 12: Integration Tests

**Files:**
- Create: `Trader/tests/test_integration.py`

**Step 1: Write integration test**

```python
# Trader/tests/test_integration.py
import pytest
from trader.data_fetcher import DataFetcher
from trader.signals import SignalGenerator
from trader.backtester import Backtester

def test_full_pipeline():
    """Test full data pipeline"""
    fetcher = DataFetcher()
    data = fetcher.fetch("XAUUSD=X", period="1mo", interval="1d")
    
    assert data is not None
    assert len(data) > 0
    
    generator = SignalGenerator(data)
    signal = generator.generate()
    
    assert signal is not None
    assert "action" in signal
    assert signal["action"] in ["buy", "sell", "hold"]
    
    risk = generator.get_risk_metrics()
    assert risk is not None
    assert "risk_reward_ratio" in risk
```

**Step 2: Run test**

Run: `cd Trader && python -m pytest tests/test_integration.py -v`

**Step 3: Commit**

```bash
git add Trader/tests/test_integration.py
git commit -m "test: add integration tests"
```

---

## Summary

**Total Tasks:** 12

| Phase | Tasks |
|-------|-------|
| Project Setup | 1 |
| Data Layer | 2-3 |
| Analysis Engine | 4-9 |
| CLI Interface | 10 |
| Dashboard | 11 |
| Integration | 12 |

Each task follows TDD: write failing test → implement → pass → commit.

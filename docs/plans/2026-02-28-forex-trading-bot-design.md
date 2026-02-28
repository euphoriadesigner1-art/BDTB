# Forex Trading Bot Design

**Date:** 2026-02-28  
**Project:** Forex Trading Signal Generator

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Trader Bot System                        │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ├── Yahoo Finance API (yfinance)                          │
│  ├── TradingView (manual import / CSV)                      │
│  └── Local data cache (SQLite/Parquet)                     │
├─────────────────────────────────────────────────────────────┤
│  Analysis Engine                                            │
│  ├── Technical Indicators (RSI, MACD, MA, Bollinger Bands) │
│  ├── Support/Resistance Detector                            │
│  ├── Pattern Recognition (candlestick patterns)            │
│  └── ML Price Direction Predictor (Random Forest/XGBoost)   │
├─────────────────────────────────────────────────────────────┤
│  Output Layer                                               │
│  ├── CLI (predictions, reports)                            │
│  └── Streamlit Dashboard (charts, signals, controls)        │
└─────────────────────────────────────────────────────────────┘
```

## 2. Core Components

| Component | Description |
|-----------|-------------|
| `data_fetcher` | Fetches OHLCV data from Yahoo Finance, caches locally |
| `indicators` | Calculates technical indicators using TA-Lib/pandas |
| `pattern_detector` | Identifies candlestick patterns (doji, hammer, engulfing, etc.) |
| `support_resistance` | Finds S/R levels using pivot points and clustering |
| `predictor` | ML model trained on historical data to predict price direction |
| `backtester` | Simulates trades on historical data with risk metrics |
| `signals_generator` | Combines all indicators into unified Buy/Sell/Hold signals |

## 3. Data Flow

1. **Fetch** → Get OHLCV data from Yahoo Finance (configurable lookback)
2. **Process** → Calculate indicators, detect patterns, find S/R levels
3. **Predict** → Run ML model for price direction prediction
4. **Generate** → Combine all into unified signal with confidence score
5. **Output** → Display via CLI or render interactive dashboard
6. **Backtest** → Run historical simulation to validate signals

## 4. Supported Assets & Timeframes

- **Pairs:** XAU/USD, BTC/USD, USD/JPY
- **Timeframes:** 1hr, 4hr, Daily, Weekly

## 5. Success Metrics

| Metric | Description |
|--------|-------------|
| Signal Accuracy | % of correct Buy/Sell predictions (via backtesting) |
| Backtesting Results | P&L, win rate, Sharpe ratio |
| Top Indicators | Which indicators correlate with price movement |
| Risk/Reward | Recommended stop-loss, take-profit levels per trade |

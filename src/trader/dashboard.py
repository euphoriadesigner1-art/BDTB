import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from trader.data_fetcher import DataFetcher
from trader.indicators import TechnicalIndicators
from trader.signals import SignalGenerator
from trader.support_resistance import SupportResistance
from trader.patterns import PatternDetector
import plotly.graph_objects as go

st.set_page_config(page_title="Billion Dollar Forex Bot", layout="wide")

if 'theme' not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

if st.session_state.theme == "dark":
    st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        color: #1f1f1f;
    }
    .stMarkdown, .stText, p, div, span, label {
        color: #1f1f1f !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1f1f1f !important;
    }
    .stMetricLabel {
        color: #1f1f1f !important;
    }
    .stMetricValue {
        color: #1f1f1f !important;
    }
    .stCaption {
        color: #666666 !important;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    col_theme1, col_theme2 = st.columns([1, 1])
    with col_theme1:
        st.write("🌙" if st.session_state.theme == "dark" else "☀️")
    with col_theme2:
        st.button("Toggle Theme", on_click=toggle_theme, key="theme_toggle")
    
    st.header("Settings")
    
    forex_pairs = [
        "XAU/USD (Gold)",
        "XAG/USD (Silver)",
        "EUR/USD (Euro/US Dollar)",
        "GBP/USD (British Pound/US Dollar)",
        "USD/JPY (US Dollar/Japanese Yen)",
        "USD/CHF (US Dollar/Swiss Franc)",
        "AUD/USD (Australian Dollar/US Dollar)",
        "USD/CAD (US Dollar/Canadian Dollar)",
        "NZD/USD (New Zealand Dollar/US Dollar)",
        "EUR/GBP (Euro/British Pound)",
        "EUR/JPY (Euro/Japanese Yen)",
        "GBP/JPY (British Pound/Japanese Yen)",
        "AUD/JPY (Australian Dollar/Japanese Yen)",
        "EUR/CHF (Euro/Swiss Franc)",
    ]
    
    crypto_pairs = [
        "BTC/USD (Bitcoin)",
        "ETH/USD (Ethereum)",
        "XRP/USD (Ripple)",
        "SOL/USD (Solana)",
        "ADA/USD (Cardano)",
        "DOGE/USD (Dogecoin)",
        "DOT/USD (Polkadot)",
        "MATIC/USD (Polygon)",
        "LTC/USD (Litecoin)",
        "AVAX/USD (Avalanche)",
    ]
    
    all_pairs = ["🔵 Forex"] + forex_pairs + ["🟠 Crypto"] + crypto_pairs
    
    symbol = st.selectbox("Symbol", all_pairs, index=1)
    
    if symbol.startswith("🔵") or symbol.startswith("🟠"):
        st.warning("Select a trading pair above")
        st.stop()
    
    symbol_map = {
        "XAU/USD (Gold)": "GC=F",
        "XAG/USD (Silver)": "SI=F",
        "EUR/USD (Euro/US Dollar)": "EURUSD=X",
        "GBP/USD (British Pound/US Dollar)": "GBPUSD=X",
        "USD/JPY (US Dollar/Japanese Yen)": "USDJPY=X",
        "USD/CHF (US Dollar/Swiss Franc)": "USDCHF=X",
        "AUD/USD (Australian Dollar/US Dollar)": "AUDUSD=X",
        "USD/CAD (US Dollar/Canadian Dollar)": "USDCAD=X",
        "NZD/USD (New Zealand Dollar/US Dollar)": "NZDUSD=X",
        "EUR/GBP (Euro/British Pound)": "EURGBP=X",
        "EUR/JPY (Euro/Japanese Yen)": "EURJPY=X",
        "GBP/JPY (British Pound/Japanese Yen)": "GBPJPY=X",
        "AUD/JPY (Australian Dollar/Japanese Yen)": "AUDJPY=X",
        "EUR/CHF (Euro/Swiss Franc)": "EURCHF=X",
        "BTC/USD (Bitcoin)": "BTC-USD",
        "ETH/USD (Ethereum)": "ETH-USD",
        "XRP/USD (Ripple)": "XRP-USD",
        "SOL/USD (Solana)": "SOL-USD",
        "ADA/USD (Cardano)": "ADA-USD",
        "DOGE/USD (Dogecoin)": "DOGE-USD",
        "DOT/USD (Polkadot)": "DOT-USD",
        "MATIC/USD (Polygon)": "MATIC-USD",
        "LTC/USD (Litecoin)": "LTC-USD",
        "AVAX/USD (Avalanche)": "AVAX-USD",
    }
    actual_symbol = symbol_map.get(symbol, symbol)
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "5y"])
    interval = st.selectbox("Interval", ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1wk"])
    
    st.markdown("---")
    st.header("Data Source")
    data_source = st.radio("Choose data source:", ["Yahoo Finance", "Binance", "OANDA API", "MetaTrader 5"], horizontal=True)
    
    oanda_key = None
    mt5_available = False
    if data_source == "OANDA API":
        oanda_key = st.text_input("OANDA API Key", type="password", 
                                  help="Get your API key from OANDA dashboard")
        st.caption("Use practice account API key for testing")
        if not oanda_key:
            st.warning("Enter your OANDA API key to use OANDA data")
    
    if data_source == "MetaTrader 5":
        try:
            from trader.mt5_client import MT5Client
            client = MT5Client()
            mt5_available = client.is_available()
            if mt5_available:
                st.success("MetaTrader 5 is available")
            else:
                st.warning("MT5 not installed. Install MetaTrader 5 to use this data source.")
        except:
            st.warning("MT5 not available. Install MetaTrader 5 to use this data source.")
    
    st.markdown("---")
    st.markdown("### 📖 Trading Glossary")
    with st.expander("What do these terms mean?"):
        st.markdown("""
        **Buy Signal** - Technical indicators suggest the price may go up. Good time to consider buying.
        
        **Sell Signal** - Technical indicators suggest the price may go down. Consider closing positions.
        
        **Hold** - Indicators are mixed or unclear. Wait for clearer signals.
        
        **RSI (Relative Strength Index)** - Measures how fast price is changing. 
        - Above 70 = Overbought (may drop)
        - Below 30 = Oversold (may rise)
        
        **MACD** - Shows relationship between two moving averages.
        - MACD crosses above signal line = Bullish
        - MACD crosses below signal line = Bearish
        
        **Support** - Price level where buying pressure historically exceeds selling pressure.
        
        **Resistance** - Price level where selling pressure historically exceeds buying pressure.
        
        **Risk/Reward Ratio** - Potential profit vs potential loss.
        - 1:2 means risking $1 to potentially make $2
        
        **SMA/EMA** - Moving averages that smooth out price data.
        - Short-term MA crossing above long-term MA = Bullish sign
        """)
    
    with st.expander("What are candlestick patterns?"):
        st.markdown("""
        **Doji** - Open and close are equal. Indicates indecision.
        
        **Hammer** - Small body at top, long lower wick. Bullish reversal signal.
        
        **Engulfing** - Current candle completely covers previous one. Strong reversal signal.
        
        **Morning Star** - 3-day bullish reversal pattern.
        
        **Evening Star** - 3-day bearish reversal pattern.
        
        **Piercing** - Bullish reversal (2nd candle opens below low, closes above middle).
        
        **Dark Cloud Cover** - Bearish reversal (2nd candle opens above high, closes below middle).
        """)
    
    with st.expander("What are the different order types?"):
        st.markdown("""
        ### 📝 Order Execution Types
        
        **Market Execution** - Buy or sell immediately at the current market price. 
        - Executes instantly at the best available price.
        - Best for: Quick entries when you need to enter NOW.
        
        **Buy Limit** - Place a buy order BELOW the current price.
        - Example: Price is $2000, you set Buy Limit at $1980.
        - Executes when price drops to $1980.
        - Best for: Buying at a discount (meanwhile waiting).
        
        **Sell Limit** - Place a sell order ABOVE the current price.
        - Example: Price is $2000, you set Sell Limit at $2020.
        - Executes when price rises to $2020.
        - Best for: Taking profit at a target price.
        
        **Buy Stop** - Buy when price rises ABOVE current price.
        - Example: Price is $2000, you set Buy Stop at $2010.
        - Executes when price breaks above $2010 (confirms upward momentum).
        - Best for: Chasing price higher or breaking out.
        
        **Sell Stop** - Sell when price falls BELOW current price.
        - Example: Price is $2000, you set Sell Stop at $1990.
        - Executes when price drops below $1990 (confirms downward momentum).
        - Best for: Shorting or stopping out of longs.
        
        **Buy Stop Limit** - Buy when price rises to a level, but with price limit.
        - Combines Buy Stop + Buy Limit.
        - Sets a "ceiling" price you won't pay above.
        - Best for: Breakout trading with price protection.
        
        **Sell Stop Limit** - Sell when price falls to a level, but with price limit.
        - Combines Sell Stop + Sell Limit.
        - Sets a "floor" price you won't sell below.
        - Best for: Breakdown trading with price protection.
        """)
    
    with st.expander("When to use which order type?"):
        st.markdown("""
        ### 🎯 Quick Reference
        
        | Signal | Recommended Order Type |
        |--------|----------------------|
        | Strong momentum up | Market Execution or Buy Stop |
        | Expecting pullback | Buy Limit |
        | Strong momentum down | Market Execution or Sell Stop |
        | Expecting bounce | Sell Limit |
        | Breakout confirmation | Buy Stop Limit |
        | Breakdown confirmation | Sell Stop Limit |
        
        ### 💡 Pro Tips
        
        - **Market Execution**: Use when speed matters most
        - **Limit Orders**: Use when you want better pricing and can wait
        - **Stop Orders**: Use when you want confirmation before entering
        - **Stop-Limit**: Use when you want confirmation BUT also price protection
        """)

st.title("💰 Billion Dollar Forex Signal Bot")

pair_name = symbol.split(" (")[0] if "(" in symbol else symbol
pair_display = symbol.split(" (")[1].replace(")", "") if "(" in symbol else ""
st.caption(f"📊 Trading: {pair_name} ({pair_display})")

if st.button("Generate Signals", type="primary"):
    with st.spinner("Fetching data and analyzing..."):
        try:
            fetcher = DataFetcher()
            
            source_name = "Yahoo Finance"
            
            if data_source == "Binance":
                data = fetcher.fetch_from_binance(actual_symbol, period=period, interval=interval)
                if data.empty:
                    st.warning("Binance API unavailable on cloud. Using Yahoo Finance instead.")
                    data = fetcher.fetch(actual_symbol, period=period, interval=interval)
                    source_name = "Yahoo Finance (fallback)"
                else:
                    source_name = "Binance"
            elif data_source == "OANDA API" and oanda_key:
                data = fetcher.fetch_from_oanda(actual_symbol, period=period, interval=interval, api_key=oanda_key)
                source_name = "OANDA API"
            elif data_source == "MetaTrader 5":
                data = fetcher.fetch_from_mt5(actual_symbol, period=period, interval=interval)
                source_name = "MetaTrader 5"
            else:
                data = fetcher.fetch(actual_symbol, period=period, interval=interval)
            
            # Check if data is valid
            if data is None:
                st.error(f"No data found for {symbol}. Try a different pair or period.")
                st.stop()
            
            if not hasattr(data, '__len__') or len(data) == 0:
                st.error(f"No data found for {symbol}. The {data_source} API may be blocked. Try Yahoo Finance instead.")
                st.stop()
            
            if data.empty:
                st.error(f"No data found for {symbol}. The {data_source} API may be blocked. Try Yahoo Finance instead.")
                st.stop()
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.stop()
        
        generator = SignalGenerator(data)
        signal = generator.generate()
        risk = generator.get_risk_metrics(signal['action'])
        indicators = TechnicalIndicators(data)
        sr = SupportResistance(data)
        patterns = PatternDetector(data)
        
        st.markdown("---")
        st.subheader("🎯 Trading Signal")
        
        col1, col2, col3, col4 = st.columns(4)
        
        signal_emoji = "🟢" if signal["action"].upper() == "BUY" else ("🔴" if signal["action"].upper() == "SELL" else "🟡")
        
        with col1:
            st.metric("Signal", f"{signal_emoji} {signal['action'].upper()}", f"{signal['confidence']:.1f}% confidence")
        
        with col2:
            st.metric("Current Price", f"${risk['entry_price']:.2f}")
        
        with col3:
            risk_color = "normal" if risk['risk_reward_ratio'] >= 1.5 else "inverse"
            st.metric("Risk/Reward", f"1:{risk['risk_reward_ratio']:.2f}", delta_color=risk_color)
        
        with col4:
            rsi_val = signal['rsi']
            rsi_status = "Overbought (sell)" if rsi_val > 70 else ("Oversold (buy)" if rsi_val < 30 else "Neutral")
            st.metric("RSI", f"{rsi_val:.1f}", rsi_status)
        
        st.markdown("---")
        
        st.subheader("🎯 Recommended Order Type")
        
        action = signal["action"].upper()
        rsi = signal['rsi']
        
        if action == "BUY":
            if rsi < 30:
                recommended_order = "Buy Limit"
                reason = "RSI oversold - price may bounce. Use Buy Limit to enter at better price."
                emoji = "📉"
            elif rsi > 70:
                recommended_order = "Buy Stop"
                reason = "RSI overbought but trending up. Use Buy Stop to enter on breakout."
                emoji = "🚀"
            else:
                recommended_order = "Market Execution"
                reason = "Neutral conditions. Market execution gets you in immediately."
                emoji = "⚡"
        elif action == "SELL":
            if rsi > 70:
                recommended_order = "Sell Limit"
                reason = "RSI overbought - price may drop. Use Sell Limit to exit at better price."
                emoji = "📈"
            elif rsi < 30:
                recommended_order = "Sell Stop"
                reason = "RSI oversold but trending down. Use Sell Stop to enter on breakdown."
                emoji = "🔻"
            else:
                recommended_order = "Market Execution"
                reason = "Neutral conditions. Market execution gets you in immediately."
                emoji = "⚡"
        else:
            recommended_order = "Wait"
            reason = "Signal is HOLD. Wait for clearer signals before entering."
            emoji = "⏸️"
        
        col_order1, col_order2 = st.columns([1, 2])
        with col_order1:
            st.info(f"{emoji} **{recommended_order}**")
        with col_order2:
            st.caption(reason)
        
        st.markdown("---")
        
        st.subheader("📊 Support & Resistance Levels")
        st.caption("Support is where price tends to find a floor. Resistance is where price tends to hit a ceiling.")
        
        sr_col1, sr_col2, sr_col3, sr_col4 = st.columns(4)
        with sr_col1:
            st.metric("Current Price", f"${risk['entry_price']:.2f}")
        with sr_col2:
            st.metric("Support (Stop-Loss)", f"${risk['stop_loss']:.2f}", delta=f"-{risk['risk_percent']:.2f}%", delta_color="inverse")
        with sr_col3:
            st.metric("Resistance (Take-Profit)", f"${risk['take_profit']:.2f}", delta=f"+{risk['reward_percent']:.2f}%", delta_color="normal")
        with sr_col4:
            risk_desc = "Good" if risk['risk_reward_ratio'] >= 2 else ("Fair" if risk['risk_reward_ratio'] >= 1 else "Poor")
            st.metric("Trade Quality", risk_desc)
        
        st.markdown("---")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("📈 Price with Moving Averages")
            st.caption("SMA = Simple Moving Average. When price is above MA, it's generally bullish.")
            ind_df = indicators.calculate_all()
            chart_data = ind_df[["Close", "SMA_20", "SMA_50"]].dropna()
            st.line_chart(chart_data)
        
        with col_chart2:
            st.subheader("📉 Bollinger Bands")
            st.caption("Price tends to bounce between the bands. Upper = potential overbought, Lower = potential oversold.")
            bb_data = ind_df[["Close", "BB_Upper", "BB_Middle", "BB_Lower"]].dropna()
            st.line_chart(bb_data)
        
        st.markdown("---")
        
        st.subheader("🔄 MACD Indicator")
        st.caption("MACD (blue) crossing above Signal (orange) = Buy signal. MACD crossing below = Sell signal.")
        macd_df = ind_df[["MACD", "MACD_Signal"]].dropna()
        st.line_chart(macd_df)
        
        st.subheader("💪 RSI (Relative Strength Index)")
        st.caption("RSI above 70 = Overbought (price may fall). RSI below 30 = Oversold (price may rise).")
        rsi_data = ind_df["RSI"].dropna()
        st.line_chart(rsi_data)
        
        st.markdown("---")
        
        st.subheader("🕯️ Recent Candlestick Patterns")
        st.caption("Patterns that may indicate future price direction.")
        recent_patterns = patterns.get_latest_patterns()
        
        if recent_patterns:
            pattern_data = []
            for p in recent_patterns:
                signal_type = "Bullish" if p["signal"] > 0 else "Bearish"
                pattern_data.append({
                    "Pattern": p["pattern"].replace("CDL", ""),
                    "Date": p["date"].date(),
                    "Signal": signal_type
                })
            st.table(pd.DataFrame(pattern_data))
        else:
            st.info("No significant patterns detected in recent data.")
        
        st.markdown("---")
        
        with st.expander("📋 Detailed Signal Breakdown"):
            st.markdown(f"""
            **How the signal was calculated:**
            
            - **Buy Score:** {signal['buy_score']} (higher = more buy signals)
            - **Sell Score:** {signal['sell_score']} (higher = more sell signals)
            - **RSI:** {signal['rsi']:.2f} ({'Oversold - potential buy' if signal['rsi'] < 30 else ('Overbought - potential sell' if signal['rsi'] > 70 else 'Neutral')})
            
            **Pattern Analysis:**
            {len(recent_patterns)} pattern(s) detected in recent candles.
            """)
        
        st.success("✅ Analysis complete. Always do your own research before making trading decisions.")

st.markdown("---")
st.caption("⚠️ Disclaimer: This tool is for educational purposes only. Not financial advice. Always do your own research.")

if __name__ == "__main__":
    import sys
    sys.argv = ["streamlit", "run", __file__]
    import subprocess
    subprocess.run(sys.argv)

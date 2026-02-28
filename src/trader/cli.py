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
    risk = generator.get_risk_metrics(signal['action'])
    
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

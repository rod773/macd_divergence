# MACD Divergence

MACD Divergence detection indicator implemented in multiple platforms: MQL5 (MetaTrader 5), Pine Script v5 (TradingView), and Python (backtesting).

## Overview

This project detects **bullish and bearish divergences** between price and the MACD oscillator. Divergences occur when price makes new highs/lows but the MACD does not confirm, often signaling potential reversals.

### Divergence Types

| Type | Price | MACD | Signal |
|------|-------|------|--------|
| **Classical Bullish** | Lower Low | Higher Low | Buy opportunity |
| **Reverse Bullish** | Higher Low | Lower Low | Trend continuation |
| **Classical Bearish** | Higher High | Lower High | Sell opportunity |
| **Reverse Bearish** | Lower High | Higher High | Trend continuation |

## Files

### `macd_divergence.mq5` — MetaTrader 5 Indicator
- Original MQL5 implementation by Alain Verleyen (based on FX5's MQL4 code)
- Detects classical and reverse divergences
- Draws trendlines on price chart and indicator window
- Displays alerts on recent divergences
- Runs in a separate indicator window

### `macd_divergence_ea.mq5` — MetaTrader 5 Expert Advisor
- Automated trading EA based on the divergence indicator
- Opens long/short positions on divergence signals
- Configurable risk management (risk %, risk/reward ratio, SL multiplier)
- Supports opposite-signal exit and trailing stop
- Uses the same divergence detection logic as the indicator

### `macd_divergence.pine` — TradingView Pine Script v5 Indicator
- Port of the MQL5 logic to Pine Script v5
- Uses custom extrema detection (3-condition check on MACD, 4-condition search on Signal buffer)
- Draws trendlines on price chart and indicator window
- Plots classical and reverse divergence labels
- Configurable inputs (MACD params, trendline toggles, alerts)

### `macd_divergence_backtest.py` — Python Backtester
- Port of the MQL5 divergence logic to Python
- Uses `yfinance` for data, `pandas`/`numpy` for computation, `matplotlib` for plotting
- Configurable parameters: symbol, timeframe, MACD settings, SL/TP, risk per trade
- Generates backtest report with win rate, profit factor, Sharpe ratio, max drawdown
- Outputs equity curve chart and trade CSV

## Installation

### MetaTrader 5
1. Copy `macd_divergence.mq5` or `macd_divergence_ea.mq5` to your MT5 `MQL5/Indicators` or `MQL5/Experts` folder
2. Compile in MetaEditor
3. Drag onto a chart

### TradingView
1. Open Pine Script Editor (bottom panel)
2. Paste `macd_divergence.pine`
3. Click "Add to Chart"

### Python Backtester
```bash
pip install numpy pandas yfinance matplotlib
python macd_divergence_backtest.py
```

## Python Backtest Configuration

Edit `main()` in `macd_divergence_backtest.py`:

```python
bt = MACDDivergenceBacktest(
    symbol='AAPL',              # ticker symbol
    start='2020-01-01',         # start date
    end='2025-01-01',           # end date
    interval='1d',              # '1d', '1h', etc.
    fast=12, slow=26, signal=9, # MACD parameters
    sl_type='swing',            # 'swing', 'atr', or 'fixed'
    sl_mult=1.0,                # SL multiplier
    tp_type='rr',               # 'rr', 'atr', or 'opposite'
    tp_mult=2.0,                # TP multiplier (risk:reward)
    risk_per_trade=0.02,        # 2% risk per trade
    initial_capital=10000,
    commission=0.001,           # 0.1% per trade
    use_classical=True,         # trade classical divergences
    use_reverse=True            # trade reverse divergences
)
```

## Detection Algorithm

The core logic (shared across all implementations):

1. **Extrema Detection**: Identify local troughs/peaks on the MACD line using a 3-condition check (current bar vs 2 previous bars + 1 next bar)
2. **Historical Search**: Search backwards for the last significant trough/peak using the Signal line (4-condition check) then verify on MACD (4-condition check)
3. **Divergence Check**: Compare current and last extrema for price/MACD divergence
4. **Classification**: Classical (stronger signal) vs Reverse (continuation signal)

## Credits

- **Original MQL4 indicator**: FX5 (http://codebase.mql4.com/1115)
- **MQL5 rewrite**: Alain Verleyen (http://www.alamga.be)
- **Python backtester & Pine Script port**: Community contributions

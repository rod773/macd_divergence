import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# MACD DIVERGENCE BACKTEST
# Strategy logic ported from MQL5 / Pine Script indicator
# ============================================================

class MACDDivergenceBacktest:
    def __init__(self, symbol, start, end, interval='1d', 
                 fast=12, slow=26, signal=9,
                 sl_type='swing', sl_mult=1.0, 
                 tp_type='rr', tp_mult=2.0,
                 risk_per_trade=0.01, initial_capital=10000,
                 commission=0.001, use_classical=True, use_reverse=True):
        """
        Parameters:
        -----------
        symbol: str - e.g. 'AAPL', 'EURUSD=X'
        start, end: str - dates 'YYYY-MM-DD'
        interval: str - '1d', '1h', etc.
        fast, slow, signal: MACD parameters
        sl_type: 'swing' or 'atr' or 'fixed'
        sl_mult: multiplier for SL (e.g., 1.0 = full swing, 0.5 = half swing)
        tp_type: 'rr' (risk:reward) or 'opposite' or 'atr'
        tp_mult: multiplier for TP (e.g., 2.0 = 2x risk)
        risk_per_trade: float - fraction of capital to risk per trade
        initial_capital: float
        commission: float - fraction per trade (e.g., 0.001 = 0.1%)
        use_classical: bool - trade classical divergences
        use_reverse: bool - trade reverse (hidden) divergences
        """
        self.symbol = symbol
        self.start = start
        self.end = end
        self.interval = interval
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.sl_type = sl_type
        self.sl_mult = sl_mult
        self.tp_type = tp_type
        self.tp_mult = tp_mult
        self.risk_per_trade = risk_per_trade
        self.initial_capital = initial_capital
        self.commission = commission
        self.use_classical = use_classical
        self.use_reverse = use_reverse
        
    def fetch_data(self):
        print(f"Fetching {self.symbol} from {self.start} to {self.end} ({self.interval})")
        df = yf.download(self.symbol, start=self.start, end=self.end, interval=self.interval, progress=False)
        if df.empty:
            raise ValueError(f"No data returned for {self.symbol}")
        # Flatten multi-index columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        df = df.reset_index()
        print(f"Loaded {len(df)} bars")
        return df
    
    def compute_macd(self, df):
        close = df['Close'].values
        ema_fast = pd.Series(close).ewm(span=self.fast, adjust=False).mean().values
        ema_slow = pd.Series(close).ewm(span=self.slow, adjust=False).mean().values
        macd_line = ema_fast - ema_slow
        signal_line = pd.Series(macd_line).ewm(span=self.signal, adjust=False).mean().values
        df['MACD'] = macd_line
        df['Signal'] = signal_line
        return df
    
    def find_divergences(self, df):
        """
        Exact MQL5 logic ported:
        - Main detection: 3-condition extrema on MACD
        - Historical search: 4-condition extrema on Signal, then MACD
        - Classical vs Reverse divergence classification
        """
        n = len(df)
        macd = df['MACD'].values
        sig = df['Signal'].values
        high = df['High'].values
        low = df['Low'].values
        
        bullish_signals = []  # (idx, type, last_extremum_idx)
        bearish_signals = []
        
        # Need at least 5 bars for the logic
        for shift in range(5, n - 1):
            # --- Bullish Divergence Detection ---
            # macdBuffer[shift]<=macdBuffer[shift-1] && 
            # macdBuffer[shift]<macdBuffer[shift-2] && 
            # macdBuffer[shift]<macdBuffer[shift+1]
            if (macd[shift] <= macd[shift-1] and 
                macd[shift] < macd[shift-2] and 
                macd[shift] < macd[shift+1]):
                
                current_extremum = shift
                last_extremum = self._get_last_trough(shift, macd, sig)
                
                if last_extremum > 0:
                    # Classical: macd[current] > macd[last] && low[current] < low[last]
                    if (macd[current_extremum] > macd[last_extremum] and 
                        low[current_extremum] < low[last_extremum]):
                        if self.use_classical:
                            bullish_signals.append((shift, 'classical', last_extremum))
                    # Reverse: macd[current] < macd[last] && low[current] > low[last]
                    elif (macd[current_extremum] < macd[last_extremum] and 
                          low[current_extremum] > low[last_extremum]):
                        if self.use_reverse:
                            bullish_signals.append((shift, 'reverse', last_extremum))
            
            # --- Bearish Divergence Detection ---
            # macdBuffer[shift]>=macdBuffer[shift-1] && 
            # macdBuffer[shift]>macdBuffer[shift-2] && 
            # macdBuffer[shift]>macdBuffer[shift+1]
            if (macd[shift] >= macd[shift-1] and 
                macd[shift] > macd[shift-2] and 
                macd[shift] > macd[shift+1]):
                
                current_extremum = shift
                last_extremum = self._get_last_peak(shift, macd, sig)
                
                if last_extremum > 0:
                    # Classical: macd[current] < macd[last] && high[current] > high[last]
                    if (macd[current_extremum] < macd[last_extremum] and 
                        high[current_extremum] > high[last_extremum]):
                        if self.use_classical:
                            bearish_signals.append((shift, 'classical', last_extremum))
                    # Reverse: macd[current] > macd[last] && high[current] < high[last]
                    elif (macd[current_extremum] > macd[last_extremum] and 
                          high[current_extremum] < high[last_extremum]):
                        if self.use_reverse:
                            bearish_signals.append((shift, 'reverse', last_extremum))
        
        return bullish_signals, bearish_signals
    
    def _get_last_trough(self, shift, macd, sig):
        """GetIndicatorLastTrough - MQL5 port"""
        for i in range(shift - 5, 1, -1):
            # Signal trough: 4 conditions
            if (sig[i] <= sig[i-1] and sig[i] <= sig[i-2] and
                sig[i] <= sig[i+1] and sig[i] <= sig[i+2]):
                for j in range(i, 1, -1):
                    # MACD trough: 4 conditions
                    if (macd[j] <= macd[j-1] and macd[j] < macd[j-2] and
                        macd[j] <= macd[j+1] and macd[j] < macd[j+2]):
                        return j
        return 0
    
    def _get_last_peak(self, shift, macd, sig):
        """GetIndicatorLastPeak - MQL5 port"""
        for i in range(shift - 5, 1, -1):
            # Signal peak: 4 conditions
            if (sig[i] >= sig[i-1] and sig[i] >= sig[i-2] and
                sig[i] >= sig[i+1] and sig[i] >= sig[i+2]):
                for j in range(i, 1, -1):
                    # MACD peak: 4 conditions
                    if (macd[j] >= macd[j-1] and macd[j] > macd[j-2] and
                        macd[j] >= macd[j+1] and macd[j] > macd[j+2]):
                        return j
        return 0
    
    def run_backtest(self):
        df = self.fetch_data()
        df = self.compute_macd(df)
        bullish_sigs, bearish_sigs = self.find_divergences(df)
        
        print(f"Bullish divergences found: {len(bullish_sigs)} ({sum(1 for _,t,_ in bullish_sigs if t=='classical')} classical, {sum(1 for _,t,_ in bullish_sigs if t=='reverse')} reverse)")
        print(f"Bearish divergences found: {len(bearish_sigs)} ({sum(1 for _,t,_ in bearish_sigs if t=='classical')} classical, {sum(1 for _,t,_ in bearish_sigs if t=='reverse')} reverse)")
        
        trades = []
        capital = self.initial_capital
        equity_curve = [capital]
        in_position = False
        position = None
        
        # Create signal markers
        df['Signal_Bull'] = False
        df['Signal_Bear'] = False
        for idx, div_type, last_idx in bullish_sigs:
            df.loc[idx, 'Signal_Bull'] = True
        for idx, div_type, last_idx in bearish_sigs:
            df.loc[idx, 'Signal_Bear'] = True
        
        # --- Simulate bar by bar ---
        for i in range(1, len(df)):
            current_time = df.loc[i, 'Date'] if 'Date' in df.columns else df.loc[i, 'Datetime']
            open_price = df.loc[i, 'Open']
            high_price = df.loc[i, 'High']
            low_price = df.loc[i, 'Low']
            close_price = df.loc[i, 'Close']
            
            # Check for signal on previous bar (enter on current bar open)
            has_bull_signal = df.loc[i-1, 'Signal_Bull'] if i > 0 else False
            has_bear_signal = df.loc[i-1, 'Signal_Bear'] if i > 0 else False
            
            # Close existing position if opposite signal
            if in_position and position is not None:
                should_close = False
                close_reason = ''
                
                if position['direction'] == 'long' and has_bear_signal:
                    should_close = True
                    close_reason = 'opposite_signal'
                elif position['direction'] == 'short' and has_bull_signal:
                    should_close = True
                    close_reason = 'opposite_signal'
                
                # Check SL/TP
                if not should_close:
                    if position['direction'] == 'long':
                        if low_price <= position['sl']:
                            should_close = True
                            close_reason = 'sl'
                        elif high_price >= position['tp']:
                            should_close = True
                            close_reason = 'tp'
                    else:  # short
                        if high_price >= position['sl']:
                            should_close = True
                            close_reason = 'sl'
                        elif low_price <= position['tp']:
                            should_close = True
                            close_reason = 'tp'
                
                if should_close:
                    if close_reason == 'sl':
                        exit_price = position['sl']
                    elif close_reason == 'tp':
                        exit_price = position['tp']
                    else:
                        exit_price = open_price
                    
                    if position['direction'] == 'long':
                        pnl = (exit_price - position['entry']) / position['entry']
                    else:
                        pnl = (position['entry'] - exit_price) / position['entry']
                    
                    pnl -= self.commission * 2
                    trade_pnl = position['size'] * pnl
                    capital += trade_pnl
                    
                    trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': current_time,
                        'direction': position['direction'],
                        'entry': position['entry'],
                        'exit': exit_price,
                        'sl': position['sl'],
                        'tp': position['tp'],
                        'size': position['size'],
                        'pnl_pct': pnl * 100,
                        'pnl_abs': trade_pnl,
                        'reason': close_reason,
                        'div_type': position['div_type']
                    })
                    in_position = False
                    position = None
            
            # Enter new position if no position and signal
            if not in_position:
                direction = None
                div_type = None
                if has_bull_signal:
                    direction = 'long'
                    div_type = [t for idx, t, _ in bullish_sigs if idx == i-1][0] if bullish_sigs else 'classical'
                elif has_bear_signal:
                    direction = 'short'
                    div_type = [t for idx, t, _ in bearish_sigs if idx == i-1][0] if bearish_sigs else 'classical'
                
                if direction:
                    entry_price = open_price
                    
                    # Calculate Stop Loss
                    if self.sl_type == 'swing':
                        if direction == 'long':
                            sl = min(df.loc[max(0,i-5):i-1, 'Low']) * self.sl_mult
                        else:
                            sl = max(df.loc[max(0,i-5):i-1, 'High']) * (2 - self.sl_mult)
                    elif self.sl_type == 'atr':
                        atr = self._calculate_atr(df, i, period=14)
                        if direction == 'long':
                            sl = entry_price - atr * self.sl_mult
                        else:
                            sl = entry_price + atr * self.sl_mult
                    else:  # fixed
                        sl_pct = 0.02 * self.sl_mult
                        if direction == 'long':
                            sl = entry_price * (1 - sl_pct)
                        else:
                            sl = entry_price * (1 + sl_pct)
                    
                    # Calculate Take Profit
                    if self.tp_type == 'rr':
                        risk = abs(entry_price - sl) / entry_price
                        tp_pct = risk * self.tp_mult
                        if direction == 'long':
                            tp = entry_price * (1 + tp_pct)
                        else:
                            tp = entry_price * (1 - tp_pct)
                    elif self.tp_type == 'atr':
                        atr = self._calculate_atr(df, i, period=14)
                        if direction == 'long':
                            tp = entry_price + atr * self.tp_mult
                        else:
                            tp = entry_price - atr * self.tp_mult
                    else:  # opposite
                        tp = None  # Will be set by opposite signal
                    
                    risk_amount = capital * self.risk_per_trade
                    risk_pct = abs(entry_price - sl) / entry_price
                    if risk_pct < 0.0001:
                        risk_pct = 0.001
                    position_size = risk_amount / risk_pct
                    
                    position = {
                        'direction': direction,
                        'entry': entry_price,
                        'sl': sl,
                        'tp': tp,
                        'size': position_size,
                        'entry_date': current_time,
                        'div_type': div_type
                    }
                    in_position = True
                    capital -= capital * self.commission
            
            equity_curve.append(capital)
        
        df['Equity'] = equity_curve[:len(df)]
        return df, trades
    
    def _calculate_atr(self, df, i, period=14):
        highs = df['High'].values[max(0, i-period):i]
        lows = df['Low'].values[max(0, i-period):i]
        closes = df['Close'].values[max(0, i-period):i]
        if len(highs) < 2:
            return (highs[-1] - lows[-1]) if len(highs) > 0 else 0.01
        tr1 = highs[1:] - lows[1:]
        tr2 = np.abs(highs[1:] - closes[:-1])
        tr3 = np.abs(lows[1:] - closes[:-1])
        tr = np.maximum(np.maximum(tr1, tr2), tr3)
        return np.mean(tr) if len(tr) > 0 else 0.01
    
    def report(self, trades, df):
        if not trades:
            print("No trades executed.")
            return {}
        
        trades_df = pd.DataFrame(trades)
        total_trades = len(trades_df)
        wins = trades_df[trades_df['pnl_abs'] > 0]
        losses = trades_df[trades_df['pnl_abs'] <= 0]
        win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
        
        avg_win = wins['pnl_abs'].mean() if len(wins) > 0 else 0
        avg_loss = losses['pnl_abs'].mean() if len(losses) > 0 else 0
        
        gross_profit = wins['pnl_abs'].sum() if len(wins) > 0 else 0
        gross_loss = abs(losses['pnl_abs'].sum()) if len(losses) > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        total_return = (df['Equity'].iloc[-1] - self.initial_capital) / self.initial_capital * 100
        max_dd = self._max_drawdown(df['Equity'].values)
        
        # Sharpe ratio (daily returns)
        equity = df['Equity'].values
        returns = np.diff(equity) / equity[:-1]
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Symbol: {self.symbol}")
        print(f"Period: {self.start} to {self.end}")
        print(f"MACD: ({self.fast}, {self.slow}, {self.signal})")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Capital: ${df['Equity'].iloc[-1]:,.2f}")
        print(f"Total Return: {total_return:.2f}%")
        print(f"-"*60)
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Avg Win: ${avg_win:.2f}")
        print(f"Avg Loss: ${avg_loss:.2f}")
        print(f"Max Drawdown: {max_dd:.2f}%")
        print(f"Sharpe Ratio: {sharpe:.2f}")
        print(f"-"*60)
        
        # By divergence type
        if 'div_type' in trades_df.columns:
            for div in ['classical', 'reverse']:
                subset = trades_df[trades_df['div_type'] == div]
                if len(subset) > 0:
                    wr = len(subset[subset['pnl_abs'] > 0]) / len(subset) * 100
                    print(f"{div.title()} div: {len(subset)} trades, Win Rate: {wr:.1f}%, P&L: ${subset['pnl_abs'].sum():.2f}")
        
        print("="*60)
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_return': total_return,
            'max_drawdown': max_dd,
            'sharpe': sharpe,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'trades': trades_df
        }
    
    def _max_drawdown(self, equity):
        peak = np.maximum.accumulate(equity)
        drawdown = (peak - equity) / peak
        return np.max(drawdown) * 100
    
    def plot(self, df, trades, save_path='backtest_results.png'):
        fig, axes = plt.subplots(3, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [2, 1, 1]})
        
        # Price chart
        ax1 = axes[0]
        ax1.plot(df['Close'], label='Close', color='black', alpha=0.7, linewidth=0.8)
        
        # Mark divergences
        bull_idx = df[df['Signal_Bull']].index
        bear_idx = df[df['Signal_Bear']].index
        ax1.scatter(bull_idx, df.loc[bull_idx, 'Close'], marker='^', color='green', s=80, label='Bull Div', zorder=5)
        ax1.scatter(bear_idx, df.loc[bear_idx, 'Close'], marker='v', color='red', s=80, label='Bear Div', zorder=5)
        
        # Mark trades
        for t in trades:
            entry_idx = df[df['Date'] == t['entry_date']].index[0] if 'Date' in df.columns else \
                        df[df['Datetime'] == t['entry_date']].index[0]
            exit_idx = df[df['Date'] == t['exit_date']].index[0] if 'Date' in df.columns else \
                       df[df['Datetime'] == t['exit_date']].index[0]
            color = 'green' if t['pnl_abs'] > 0 else 'red'
            ax1.plot([entry_idx, exit_idx], [t['entry'], t['exit']], color=color, alpha=0.5, linewidth=2)
        
        ax1.set_title(f'{self.symbol} - MACD Divergence Strategy')
        ax1.legend(loc='upper left')
        ax1.set_ylabel('Price')
        
        # MACD
        ax2 = axes[1]
        ax2.plot(df['MACD'], label='MACD', color='magenta', linewidth=0.8)
        ax2.plot(df['Signal'], label='Signal', color='blue', linewidth=0.8)
        ax2.axhline(0, color='gray', linestyle='--', alpha=0.5)
        ax2.legend(loc='upper left')
        ax2.set_ylabel('MACD')
        
        # Equity curve
        ax3 = axes[2]
        ax3.plot(df['Equity'], label='Equity', color='blue', linewidth=1)
        ax3.axhline(self.initial_capital, color='gray', linestyle='--', alpha=0.5)
        ax3.set_ylabel('Equity ($)')
        ax3.set_xlabel('Bar')
        ax3.legend()
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Chart saved to {save_path}")


def main():
    # Default backtest on AAPL daily
    # You can change symbol, timeframe, and parameters below
    
    bt = MACDDivergenceBacktest(
        symbol='AAPL',
        start='2020-01-01',
        end='2025-01-01',
        interval='1d',
        fast=12, slow=26, signal=9,
        sl_type='swing', sl_mult=1.0,
        tp_type='rr', tp_mult=2.0,
        risk_per_trade=0.02,
        initial_capital=10000,
        commission=0.001,
        use_classical=True,
        use_reverse=True
    )
    
    df, trades = bt.run_backtest()
    metrics = bt.report(trades, df)
    bt.plot(df, trades, save_path='macd_divergence_backtest.png')
    
    # Save trades to CSV
    if trades:
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv('macd_divergence_trades.csv', index=False)
        print("Trades saved to macd_divergence_trades.csv")

if __name__ == '__main__':
    main()

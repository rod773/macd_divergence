from fpdf import FPDF

class MACDDivergencePDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 10, 'MACD Divergence Indicator & Strategy', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(41, 98, 255)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, title, 0, 1, 'L', fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(41, 98, 255)
        self.cell(0, 8, title, 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bullet_point(self, text):
        self.set_font('Helvetica', '', 10)
        self.cell(10, 5, '', 0, 0)
        self.multi_cell(0, 5, f'- {text}')
        self.ln(1)

    def code_block(self, text):
        self.set_font('Courier', '', 9)
        self.set_fill_color(240, 240, 240)
        self.multi_cell(0, 5, text, fill=True)
        self.ln(2)

pdf = MACDDivergencePDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=15)

# Title Page
pdf.add_page()
pdf.set_font('Helvetica', 'B', 24)
pdf.ln(40)
pdf.cell(0, 15, 'MACD Divergence', 0, 1, 'C')
pdf.set_font('Helvetica', '', 14)
pdf.cell(0, 10, 'Indicator & Strategy Guide', 0, 1, 'C')
pdf.ln(20)
pdf.set_font('Helvetica', '', 11)
pdf.cell(0, 8, 'A comprehensive guide to detecting and trading', 0, 1, 'C')
pdf.cell(0, 8, 'MACD divergences across multiple platforms', 0, 1, 'C')
pdf.ln(30)
pdf.set_font('Helvetica', 'I', 10)
pdf.cell(0, 8, 'Platforms: MetaTrader 5 | TradingView | Python', 0, 1, 'C')
pdf.cell(0, 8, 'Author: Community', 0, 1, 'C')

# Table of Contents
pdf.add_page()
pdf.chapter_title('Table of Contents')
toc = [
    '1. Introduction to MACD Divergence',
    '2. Divergence Types',
    '3. Detection Algorithm',
    '4. Indicator Parameters',
    '5. Trading Strategy',
    '6. Risk Management',
    '7. Platform Implementations',
    '8. Backtesting Results',
    '9. Best Practices',
    '10. References'
]
for item in toc:
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, item, 0, 1, 'L')
pdf.ln(10)

# Chapter 1: Introduction
pdf.add_page()
pdf.chapter_title('1. Introduction to MACD Divergence')
pdf.body_text(
    'MACD (Moving Average Convergence Divergence) is one of the most popular technical indicators '
    'used by traders worldwide. It measures the relationship between two exponential moving averages '
    '(EMAs) of a security\'s price.'
)
pdf.body_text(
    'A divergence occurs when the price of an asset moves in the opposite direction of a technical '
    'indicator. In the context of MACD, a divergence happens when:'
)
pdf.bullet_point('Price makes a new high but MACD does not (bearish divergence)')
pdf.bullet_point('Price makes a new low but MACD does not (bullish divergence)')
pdf.body_text(
    'Divergences are powerful signals because they often precede trend reversals. They indicate '
    'that the momentum behind a price move is weakening, even if the price itself is still trending.'
)

pdf.section_title('Why MACD Divergences Matter')
pdf.body_text(
    'MACD divergences are particularly valuable because:'
)
pdf.bullet_point('They provide early warning of potential trend reversals')
pdf.bullet_point('They can confirm or contradict other technical signals')
pdf.bullet_point('They work across multiple timeframes (intraday, daily, weekly)')
pdf.bullet_point('They are relatively easy to identify visually')

# Chapter 2: Divergence Types
pdf.add_page()
pdf.chapter_title('2. Divergence Types')
pdf.body_text(
    'This indicator detects four types of divergences, classified by their direction and strength:'
)

pdf.section_title('2.1 Classical Bullish Divergence')
pdf.body_text('Signal: Potential bottom / reversal to the upside')
pdf.bullet_point('Price makes a LOWER LOW')
pdf.bullet_point('MACD makes a HIGHER LOW')
pdf.bullet_point('Interpretation: Selling pressure is weakening')

pdf.section_title('2.2 Reverse Bullish Divergence')
pdf.body_text('Signal: Trend continuation to the upside')
pdf.bullet_point('Price makes a HIGHER LOW')
pdf.bullet_point('MACD makes a LOWER LOW')
pdf.bullet_point('Interpretation: Temporary pullback in uptrend')

pdf.section_title('2.3 Classical Bearish Divergence')
pdf.body_text('Signal: Potential top / reversal to the downside')
pdf.bullet_point('Price makes a HIGHER HIGH')
pdf.bullet_point('MACD makes a LOWER HIGH')
pdf.bullet_point('Interpretation: Buying pressure is weakening')

pdf.section_title('2.4 Reverse Bearish Divergence')
pdf.body_text('Signal: Trend continuation to the downside')
pdf.bullet_point('Price makes a LOWER HIGH')
pdf.bullet_point('MACD makes a HIGHER HIGH')
pdf.bullet_point('Interpretation: Temporary bounce in downtrend')

# Chapter 3: Detection Algorithm
pdf.add_page()
pdf.chapter_title('3. Detection Algorithm')
pdf.body_text(
    'The detection algorithm uses a multi-step process to identify reliable divergences:'
)

pdf.section_title('Step 1: MACD Calculation')
pdf.code_block(
    'EMA_fast = EMA(close, 12)\n'
    'EMA_slow = EMA(close, 26)\n'
    'MACD = EMA_fast - EMA_slow\n'
    'Signal = EMA(MACD, 9)\n'
    'Histogram = MACD - Signal'
)

pdf.section_title('Step 2: Extrema Detection (3-Condition Check)')
pdf.body_text(
    'A bar is identified as a local trough or peak on the MACD line when:'
)
pdf.bullet_point('Current value <= previous value (non-strict)')
pdf.bullet_point('Current value < two-bars-ago value (strict)')
pdf.bullet_point('Current value < next-bar value (strict)')

pdf.section_title('Step 3: Historical Search (4-Condition Check)')
pdf.body_text(
    'To find the last significant trough/peak, the algorithm searches backwards:'
)
pdf.bullet_point('First checks the Signal line with 4 conditions (<= and < comparisons)')
pdf.bullet_point('Then verifies the MACD line has a corresponding trough/peak')
pdf.bullet_point('Search range: up to 5 bars back from current detection')

pdf.section_title('Step 4: Divergence Comparison')
pdf.body_text(
    'Compare current and last extrema:'
)
pdf.bullet_point('Bullish: Compare lows of price and MACD')
pdf.bullet_point('Bearish: Compare highs of price and MACD')
pdf.bullet_point('Classical: Price and MACD move in opposite directions')
pdf.bullet_point('Reverse: Price and MACD move in same direction')

# Chapter 4: Parameters
pdf.add_page()
pdf.chapter_title('4. Indicator Parameters')

pdf.section_title('MACD Settings')
pdf.bullet_point('Fast Length: 12 (default) - Period for fast EMA')
pdf.bullet_point('Slow Length: 26 (default) - Period for slow EMA')
pdf.bullet_point('Signal Smoothing: 9 (default) - Period for signal line')

pdf.section_title('Display Settings')
pdf.bullet_point('Draw Indicator Trend Lines: Show/hide trendlines on MACD panel')
pdf.bullet_point('Draw Price Trend Lines: Show/hide trendlines on price chart')
pdf.bullet_point('Display Alert: Enable/disable alerts on divergence detection')

# Chapter 5: Trading Strategy
pdf.add_page()
pdf.chapter_title('5. Trading Strategy')

pdf.section_title('Entry Rules')
pdf.body_text('LONG Entry:')
pdf.bullet_point('Detect Classical Bullish Divergence')
pdf.bullet_point('Enter at open of next bar after signal')
pdf.bullet_point('Optional: Close existing short position')

pdf.body_text('SHORT Entry:')
pdf.bullet_point('Detect Classical Bearish Divergence')
pdf.bullet_point('Enter at open of next bar after signal')
pdf.bullet_point('Optional: Close existing long position')

pdf.section_title('Exit Rules')
pdf.bullet_point('Stop Loss: Below recent swing low (long) or above swing high (short)')
pdf.bullet_point('Take Profit: Based on risk:reward ratio (default 2:1)')
pdf.bullet_point('Opposite Signal: Close position on opposite divergence')

# Chapter 6: Risk Management
pdf.add_page()
pdf.chapter_title('6. Risk Management')

pdf.section_title('Position Sizing')
pdf.body_text(
    'The backtester uses risk-based position sizing:'
)
pdf.code_block(
    'Risk Amount = Capital x Risk Per Trade\n'
    'Risk % = |Entry - SL| / Entry\n'
    'Position Size = Risk Amount / Risk %'
)

pdf.section_title('Stop Loss Methods')
pdf.bullet_point('Swing: Use recent swing low/high (default)')
pdf.bullet_point('ATR: Based on Average True Range')
pdf.bullet_point('Fixed: Fixed percentage from entry')

pdf.section_title('Take Profit Methods')
pdf.bullet_point('Risk:Reward: Multiplier of risk (default 2x)')
pdf.bullet_point('ATR: Based on Average True Range')
pdf.bullet_point('Opposite: Exit on opposite signal')

# Chapter 7: Platform Implementations
pdf.add_page()
pdf.chapter_title('7. Platform Implementations')

pdf.section_title('MetaTrader 5 (MQL5)')
pdf.bullet_point('macd_divergence.mq5: Visual indicator with trendlines')
pdf.bullet_point('macd_divergence_ea.mq5: Automated trading EA')
pdf.bullet_point('Original implementation by Alain Verleyen')

pdf.section_title('TradingView (Pine Script v5)')
pdf.bullet_point('macd_divergence.pine: Port of MQL5 logic')
pdf.bullet_point('Includes labels and trendlines')
pdf.bullet_point('Compatible with all TradingView assets')

pdf.section_title('Python Backtester')
pdf.bullet_point('macd_divergence_backtest.py')
pdf.bullet_point('Uses yfinance for data')
pdf.bullet_point('Generates detailed performance reports')
pdf.bullet_point('Outputs equity curve and trade CSV')

# Chapter 8: Backtesting
pdf.add_page()
pdf.chapter_title('8. Backtesting Results')

pdf.body_text(
    'The backtester provides comprehensive metrics:'
)
pdf.bullet_point('Total Trades: Number of trades executed')
pdf.bullet_point('Win Rate: Percentage of profitable trades')
pdf.bullet_point('Profit Factor: Gross profit / gross loss')
pdf.bullet_point('Total Return: Overall account growth')
pdf.bullet_point('Max Drawdown: Largest peak-to-trough decline')
pdf.bullet_point('Sharpe Ratio: Risk-adjusted returns')

pdf.section_title('Running a Backtest')
pdf.code_block(
    'python macd_divergence_backtest.py\n\n'
    '# Or customize parameters:\n'
    'bt = MACDDivergenceBacktest(\n'
    '    symbol="EURUSD=X",\n'
    '    start="2020-01-01",\n'
    '    end="2025-01-01",\n'
    '    interval="1d"\n'
    ')\n'
    'df, trades = bt.run_backtest()\n'
    'metrics = bt.report(trades, df)'
)

# Chapter 9: Best Practices
pdf.add_page()
pdf.chapter_title('9. Best Practices')

pdf.section_title('When to Use Divergences')
pdf.bullet_point('In trending markets (not ranging)')
pdf.bullet_point('On higher timeframes (4H, Daily, Weekly)')
pdf.bullet_point('Combined with other technical analysis')
pdf.bullet_point('With proper risk management')

pdf.section_title('Common Mistakes to Avoid')
pdf.bullet_point('Trading divergences in isolation')
pdf.bullet_point('Ignoring the overall trend')
pdf.bullet_point('Using too tight stop losses')
pdf.bullet_point('Overtrading on every divergence signal')

pdf.section_title('Optimization Tips')
pdf.bullet_point('Test different MACD parameters for your asset')
pdf.bullet_point('Adjust lookback periods for different timeframes')
pdf.bullet_point('Combine with volume analysis')
pdf.bullet_point('Use multiple timeframe analysis')

# Chapter 10: References
pdf.add_page()
pdf.chapter_title('10. References')
pdf.body_text('Technical Analysis Resources:')
pdf.bullet_point('MACD - Investopedia')
pdf.bullet_point('Divergence Trading - TradingView')
pdf.bullet_point('MQL5 Documentation')
pdf.bullet_point('Pine Script Reference Manual')

pdf.body_text('Original Code:')
pdf.bullet_point('FX5 MACD Divergence (MQL4)')
pdf.bullet_point('Alain Verleyen MQL5 Rewrite')
pdf.bullet_point('Community Pine Script Port')

pdf.body_text('Libraries Used:')
pdf.bullet_point('yfinance - Yahoo Finance data')
pdf.bullet_point('pandas - Data manipulation')
pdf.bullet_point('numpy - Numerical computing')
pdf.bullet_point('matplotlib - Charting')

# Save
pdf.output('MACD_Divergence_Guide.pdf')
print('PDF generated: MACD_Divergence_Guide.pdf')

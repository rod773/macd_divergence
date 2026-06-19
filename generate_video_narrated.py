import fitz
import pyttsx3
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image
import os
import time

PDF_FILE = 'MACD_Divergence_Guide.pdf'
OUTPUT_VIDEO = 'MACD_Divergence_Guide_YT.mp4'
WIDTH = 1920
HEIGHT = 1080

NARRATIONS = {
    0: "MACD Divergence. A comprehensive guide to detecting and trading MACD divergences across multiple platforms. MetaTrader 5, TradingView, and Python.",
    1: "Table of Contents. This guide covers Introduction to MACD Divergence, Divergence Types, Detection Algorithm, Indicator Parameters, Trading Strategy, Risk Management, Platform Implementations, Backtesting Results, Best Practices, and References.",
    2: "Introduction to MACD Divergence. MACD is one of the most popular technical indicators. A divergence occurs when price moves opposite to the indicator. Bullish divergence happens when price makes a new low but MACD does not. Bearish divergence happens when price makes a new high but MACD does not. Divergences are powerful signals because they often precede trend reversals.",
    3: "Why MACD Divergences Matter. They provide early warning of potential trend reversals. They can confirm or contradict other technical signals. They work across multiple timeframes. And they are relatively easy to identify visually.",
    4: "Divergence Types. We detect four types. Classical Bullish: Price lower low, MACD higher low, potential bottom reversal. Reverse Bullish: Price higher low, MACD lower low, trend continuation. Classical Bearish: Price higher high, MACD lower high, potential top reversal. Reverse Bearish: Price lower high, MACD higher high, trend continuation.",
    5: "Detection Algorithm Step 1 and 2. First, we calculate MACD with standard parameters: Fast EMA 12, Slow EMA 26, Signal line 9. Then we detect extrema using a three condition check on the MACD line.",
    6: "Detection Algorithm Step 3 and 4. We search backwards for the last significant trough or peak using the Signal line with a four condition check. Then we compare current and last extrema for divergence. Classical means price and MACD move in opposite directions. Reverse means they move in the same direction.",
    7: "Indicator Parameters. MACD Settings: Fast Length 12, Slow Length 26, Signal Smoothing 9. Display Settings: Draw Indicator Trend Lines, Draw Price Trend Lines, and Display Alert options are all configurable.",
    8: "Trading Strategy. Entry Rules: For long entries, detect Classical Bullish Divergence and enter at the open of the next bar. For short entries, detect Classical Bearish Divergence. Exit Rules: Stop loss below recent swing low or above swing high. Take profit based on risk to reward ratio, default two to one.",
    9: "Risk Management. Position sizing uses risk based calculation. Stop loss methods include Swing, ATR, and Fixed. Take profit methods include Risk to Reward, ATR, and Opposite signal exit.",
    10: "Platform Implementations. MetaTrader 5: Indicator with trendlines and alerts, plus Expert Advisor for automated trading. TradingView: Pine Script v5 indicator matching MQL5 logic. Python Backtester: Uses yfinance for data, generates detailed performance reports.",
    11: "Backtesting Results and Best Practices. The backtester provides Total Trades, Win Rate, Profit Factor, Total Return, Maximum Drawdown, and Sharpe Ratio. Use divergences in trending markets on higher timeframes. Combine with other technical analysis and always use proper risk management.",
    12: "References and Credits. Original code by FX5 for MQL4, rewritten by Alain Verleyen for MQL5. Community ports to Pine Script and Python. Thank you for watching."
}

def generate_audio_pyttsx3(text, output_path, engine):
    engine.save_to_file(text, output_path)
    engine.runAndWait()

def main():
    os.makedirs('_temp', exist_ok=True)

    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)

    doc = fitz.open(PDF_FILE)
    clips = []

    for page_num in range(len(doc)):
        print(f'Processing page {page_num + 1}/{len(doc)}...')

        # PDF to image
        page = doc.load_page(page_num)
        zoom_x = WIDTH / page.rect.width
        zoom_y = HEIGHT / page.rect.height
        zoom = min(zoom_x, zoom_y)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        img_path = f'_temp/page_{page_num}.png'
        pix.save(img_path)
        img = Image.open(img_path)
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        img.save(img_path)

        # Generate audio
        audio_path = f'_temp/audio_{page_num}.wav'
        narration = NARRATIONS.get(page_num, f"Page {page_num + 1}")
        generate_audio_pyttsx3(narration, audio_path, engine)

        # Get audio duration
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration + 0.5

        video_clip = ImageClip(img_path).set_duration(duration)
        video_clip = video_clip.set_audio(audio_clip)

        clips.append(video_clip)
        print(f'  Page {page_num + 1}: {duration:.1f}s')

    doc.close()

    print('\nConcatenating video...')
    final_video = concatenate_videoclips(clips, method='compose')

    print('Writing video file...')
    final_video.write_videofile(
        OUTPUT_VIDEO,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        bitrate='5000k'
    )

    for f in os.listdir('_temp'):
        os.remove(os.path.join('_temp', f))
    os.rmdir('_temp')

    total_duration = sum(c.duration for c in clips)
    print(f'\nVideo saved: {OUTPUT_VIDEO}')
    print(f'Total duration: {total_duration:.1f} seconds')

if __name__ == '__main__':
    main()

import fitz
from PIL import Image
from moviepy.editor import AudioFileClip
import subprocess
import sys
import os
import json

PDF_FILE = 'MACD_Divergence_Guide.pdf'
WIDTH = 1920
HEIGHT = 1080
VOICE = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0'

NARRATIONS = {
    0: "Divergencia MACD. Una guia completa para detectar y operar divergencias MACD en multiples plataformas. MetaTrader 5, TradingView y Python.",
    1: "Tabla de contenidos. Esta guia cubre Introduccion a la Divergencia MACD, Tipos de Divergencia, Algoritmo de Deteccion, Parametros del Indicador, Estrategia de Trading, Gestion de Riesgo, Implementaciones en Plataformas, Resultados de Backtesting, Mejores Practicas y Referencias.",
    2: "Introduccion a la Divergencia MACD. El MACD es uno de los indicadores tecnicos mas populares. Una divergencia ocurre cuando el precio se mueve en direccion opuesta al indicador. La divergencia alcista ocurre cuando el precio hace un nuevo minimo pero el MACD no. La divergencia bajista ocurre cuando el precio hace un nuevo maximo pero el MACD no.",
    3: "Por que importan las Divergencias MACD. Proporcionan una alerta temprana de posibles inversiones de tendencia. Pueden confirmar o contradecir otras senales tecnicas. Funcionan en multiples marcos de tiempo. Y son relativamente faciles de identificar visualmente.",
    4: "Tipos de Divergencia. Detectamos cuatro tipos. Clasica Alcista: Precio minimo mas bajo, MACD minimo mas alto, potencial inversion de fondo. Reversa Alcista: Precio minimo mas alto, MACD minimo mas bajo, continuacion de tendencia. Clasica Bajista: Precio maximo mas alto, MACD maximo mas bajo, potencial inversion de techo. Reversa Bajista: Precio maximo mas bajo, MACD maximo mas alto, continuacion de tendencia.",
    5: "Algoritmo de Deteccion Paso 1. Primero calculamos el MACD con parametros estandar: EMA Rapida 12, EMA Lenta 26, Linea de Senal 9. Luego detectamos extremos usando una verificacion de tres condiciones en la linea MACD.",
    6: "Algoritmo de Deteccion Paso 2. Buscamos hacia atras el ultimo valle o pico significativo usando la linea de Senal con una verificacion de cuatro condiciones. Luego comparamos los extremos actuales y anteriores para encontrar divergencia.",
    7: "Parametros del Indicador. Configuracion MACD: Longitud Rapida 12, Longitud Lenta 26, Suavizado de Senal 9. Opciones de visualizacion: Lineas de Tendencia del Indicador, Lineas de Tendencia de Precio, y Alertas configurables.",
    8: "Estrategia de Trading. Reglas de Entrada: Para entradas largas, detectar Divergencia Clasica Alcista y entrar en la apertura de la siguiente vela. Para entradas cortas, detectar Divergencia Clasica Bajista. Reglas de Salida: Stop loss debajo del minimo reciente o encima del maximo reciente. Take profit basado en relacion riesgo beneficio.",
    9: "Gestion de Riesgo. Calculo de tamano de posicion basado en porcentaje de riesgo. Metodos de stop loss: Swing, ATR y Fijo. Metodos de take profit: Relacion Riesgo Beneficio, ATR y Senal Opuesta.",
    10: "Implementaciones en Plataformas. MetaTrader 5: Indicador con lineas de tendencia y alertas, mas Asesor Experto para trading automatico. TradingView: Indicador en Pine Script v5 que replica la logica MQL5. Backtester en Python: Usa yfinance para datos, genera reportes detallados de rendimiento.",
    11: "Backtesting y Mejores Practicas. El backtester proporciona total de operaciones, tasa de acierto, factor de beneficio, retorno total, drawdown maximo y ratio de Sharpe. Use divergencias en mercados de tendencia en marcos de tiempo altos con gestion de riesgo adecuada.",
    12: "Referencias y Creditos. Codigo original de FX5 para MQL4, reescrito por Alain Verleyen para MQL5. Ports comunitarios a Pine Script y Python. Gracias por ver."
}

AUDIO_SCRIPT = '''
import pyttsx3
import sys
text = sys.argv[1]
outpath = sys.argv[2]
voice = sys.argv[3]
engine = pyttsx3.init()
engine.setProperty("rate", 155)
engine.setProperty("voice", voice)
engine.save_to_file(text, outpath)
engine.runAndWait()
engine.stop()
'''

def gen_audio(idx, text):
    out = f'_temp/audio_{idx}.wav'
    if os.path.exists(out) and os.path.getsize(out) > 0:
        print(f'  Audio {idx}: exists')
        return out
    print(f'  Audio {idx}: generating...')
    result = subprocess.run(
        [sys.executable, '-c', AUDIO_SCRIPT, text, out, VOICE],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        print(f'  ERROR: {result.stderr[:200]}')
    return out

def main():
    os.makedirs('_temp', exist_ok=True)

    print("Step 1: Generating Spanish audio...")
    for idx, text in NARRATIONS.items():
        gen_audio(idx, text)

    print("\nStep 2: Converting PDF pages...")
    doc = fitz.open(PDF_FILE)
    for page_num in range(len(doc)):
        img_path = f'_temp/page_{page_num}.png'
        if os.path.exists(img_path):
            print(f'  Page {page_num + 1}: exists')
            continue
        print(f'  Page {page_num + 1}...')
        page = doc.load_page(page_num)
        zoom = min(WIDTH / page.rect.width, HEIGHT / page.rect.height)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        pix.save(img_path)
        img = Image.open(img_path)
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        img.save(img_path)
    doc.close()

    print("\nStep 3: Getting durations...")
    metadata = {}
    for page_num in range(len(NARRATIONS)):
        audio_path = f'_temp/audio_{page_num}.wav'
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            clip = AudioFileClip(audio_path)
            metadata[str(page_num)] = {'duration': clip.duration + 0.5}
            clip.close()
        else:
            metadata[str(page_num)] = {'duration': 6.0}

    with open('_temp/metadata.json', 'w') as f:
        json.dump(metadata, f)

    total = sum(v['duration'] for v in metadata.values())
    print(f"\nAll assets ready! Total: {total:.1f}s")
    print("Run build_video.py next.")

if __name__ == '__main__':
    main()

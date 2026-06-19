import fitz  # PyMuPDF
from moviepy.editor import ImageClip, concatenate_videoclips
import os

PDF_FILE = 'MACD_Divergence_Guide.pdf'
OUTPUT_VIDEO = 'MACD_Divergence_Guide.mp4'
DPI = 150
SECONDS_PER_PAGE = 5

doc = fitz.open(PDF_FILE)
clips = []

for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    pix = page.get_pixmap(dpi=DPI)
    img_path = f'_page_{page_num}.png'
    pix.save(img_path)
    clip = ImageClip(img_path).set_duration(SECONDS_PER_PAGE)
    clips.append(clip)
    print(f'Page {page_num + 1}/{len(doc)} converted')

doc.close()

video = concatenate_videoclips(clips, method='compose')
video.write_videofile(OUTPUT_VIDEO, fps=24, codec='libx264')

for page_num in range(len(clips)):
    img_path = f'_page_{page_num}.png'
    if os.path.exists(img_path):
        os.remove(img_path)

print(f'\nVideo saved: {OUTPUT_VIDEO}')

from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import json
import os

OUTPUT_VIDEO = 'MACD_Divergence_Guide_YT.mp4'

def main():
    with open('_temp/metadata.json', 'r') as f:
        metadata = json.load(f)

    clips = []
    for page_num_str, info in metadata.items():
        page_num = int(page_num_str)
        img_path = f'_temp/page_{page_num}.png'
        audio_path = f'_temp/audio_{page_num}.wav'

        if not os.path.exists(img_path):
            print(f'Skipping page {page_num + 1}: no image')
            continue

        print(f'Building clip {page_num + 1} ({info["duration"]:.1f}s)...')

        audio_clip = AudioFileClip(audio_path)
        video_clip = ImageClip(img_path).set_duration(info['duration'])
        video_clip = video_clip.set_audio(audio_clip)
        clips.append(video_clip)

    print('\nConcatenating...')
    final_video = concatenate_videoclips(clips, method='compose')

    print('Writing MP4...')
    final_video.write_videofile(
        OUTPUT_VIDEO,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        bitrate='5000k'
    )

    total = sum(c.duration for c in clips)
    print(f'\nSaved: {OUTPUT_VIDEO}')
    print(f'Duration: {total:.1f}s')

if __name__ == '__main__':
    main()

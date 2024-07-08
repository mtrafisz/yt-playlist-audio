#!/bin/python3

import sys
import os
import concurrent.futures
from pytube import YouTube, Playlist
from pathlib import Path
from tqdm import tqdm

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <playlist url>")
    exit(1)

p = Playlist(sys.argv[1])

temp_path = Path('.', '.temp')
output_path = Path('.', p.title)
workers = max(os.cpu_count(), 1)

print(f"Downloading '{p.title}'")

if not output_path.exists():
    output_path.mkdir()
if not temp_path.exists():
    temp_path.mkdir()

def download_and_convert(url, progress_bar):
    try:
        v = YouTube(url)

        audio_mp4 = v.streams.filter(only_audio=True).first()
        audio_name = audio_mp4.default_filename.strip()

        audio_mp4_path = Path(temp_path, audio_name)
        audio_mp3_path = Path(output_path, audio_name).with_suffix('.mp3')

        if audio_mp3_path.exists():
            audio_mp3_path.unlink()

        retries = 2

        while retries > 0:
            retries -= 1

            try:
                audio_mp4.download(temp_path)
            except Exception as e:
                print(f"Error downloading {url}: {e}")
                if retries > 0:
                    print("Retrying...")
                else:
                    raise e

        import ffmpeg
        (
            ffmpeg.input(audio_mp4_path).output(str(audio_mp3_path),
                loglevel='quiet').run()
        )

    except Exception as e:
        print(f"Error processing {url}: {e}") 

    progress_bar.update(1)

try:
    with tqdm(total=len(p.video_urls), desc="Download progress", unit="video") as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(download_and_convert, url, progress_bar) for url in p.video_urls]
            for future in concurrent.futures.as_completed(futures):
                future.result()
finally:
    import shutil
    shutil.rmtree(temp_path, ignore_errors=True)
    os.system('stty sane')


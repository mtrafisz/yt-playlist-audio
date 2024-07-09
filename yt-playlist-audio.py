#!/bin/python3

import sys
import argparse
import os

import concurrent.futures
import threading
import queue

from pytube import YouTube, Playlist
from pathlib import Path
from tqdm import tqdm
import ffmpeg
import shutil

arg_parser = argparse.ArgumentParser(
    prog="yt-playlist-audio",
    description="Download songs from a YouTube playlist.")
arg_parser.add_argument("playlist_url", help="URL of the YouTube playlist.", type=str)
arg_parser.add_argument("-o", "--output", help="Output directory.", type=str, default=".")
arg_parser.add_argument("-f", "--force", help="Download all files, even if they already exist.", action="store_true")
arg_parser.add_argument("-n", "--num-workers", help="Number of workers.", type=int, default=os.cpu_count())
arg_parser.add_argument("-v", "--verbose", help="Show debug information and ffmpeg output", action="store_true")
arg_parser.add_argument('-q', '--quiet', help='Do not output anything', action='store_true')
args = arg_parser.parse_args()

if args.verbose and args.quiet:
    print("Cannot be both verbose and quiet. Make up your mind.")
    exit(1)

temp_path = Path(args.output) / ".ypa_temp"
temp_path.mkdir(exist_ok=True, parents=True)

output_path: Path

def convert(mp4_path, mp3_path):
    ffmpeg.input(mp4_path).output(str(mp3_path),
                loglevel=('quiet' if not args.verbose else 'info')).run()

def download_and_convert(url, progress_bar=None):
    global output_path

    try:
        v = YouTube(url)

        audio_mp4 = v.streams.filter(only_audio=True).first()
        audio_name = audio_mp4.default_filename.strip()

        audio_mp4_path = temp_path / audio_name
        audio_mp3_path = output_path / audio_name.replace(".mp4", ".mp3")

        if not audio_mp3_path.exists() or args.force:
            audio_mp4.download(temp_path)
            convert(audio_mp4_path, audio_mp3_path)

    except Exception as e:
        if args.quiet: return;
        print(f"Error downloading {url}: {e}")

    if progress_bar:
        progress_bar.update(1)
        
def download_playlist(playlist_url):
    global output_path

    playlist = Playlist(playlist_url)
    urls = playlist.video_urls

    output_path = Path(args.output) / playlist.title
    output_path.mkdir(exist_ok=True)

    if not args.quiet:
        print(f"Downloading {len(urls)} songs from {playlist.title} to {output_path}")

    progress_bar = tqdm(total=len(urls), desc="Downloading", unit="song", unit_scale=True) if not args.quiet else None
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.num_workers) as executor:
        futures = []
        for url in urls:
            futures.append(executor.submit(download_and_convert, url, progress_bar))

        for future in concurrent.futures.as_completed(futures):
            pass

try:
    download_playlist(args.playlist_url)
except Exception as e:
    if args.quiet: exit(1)
    print(f"Error downloading playlist: {e}")
finally:
    shutil.rmtree(temp_path)
    os.system('stty sane')
            

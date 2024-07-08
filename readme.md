# YtPlaylistAudio

Simple YouTube playlist downloading tool.

All You have to do, is providing the playlist url, and this tool will download
all of your songs in mp3 format to your PC.

## Usage

```bash
# venv initialization, etc.
pip install -r requirements.txt
python3 yt-playlist-audio.py <url to playlist>
```

## Requirements

You have to have `ffmpeg` binary accessible in your PATH.

## Info/Why?

- Pytube downloads audio streams in mp4 format. This script couples Pytube with ffmpeg to immediately convert those files into mp3s.

- Also, it splits the downloading process into multiple threads to speed up the process.

- With 6 cores, it takes around 1.5 seconds/song.

- I couldn't get the `pytube.cli.at_progress` to work, so I used `tqdm` to show the progress of downloading.

- I've only tested this script on Linux Mint, with Kitty terminal.

## License

This project uses following packages:
  - [pytube](https://github.com/pytube/pytube)
  - [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)
  - [tqdm](https://github.com/tqdm/tqdm)

I do not claim any rights to those packages.

`YtPlaylistAudio` is itself licensed under [MIT licese](LICENSE).


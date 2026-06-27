import os
import yt_dlp
from pydub import AudioSegment


DOWNLOAD_DIR = "download"
CHUNK_DIR = "chunks"


def download_audio(youtube_url):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    output_template = os.path.join(DOWNLOAD_DIR, "audio.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": False,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    mp3_file = os.path.join(DOWNLOAD_DIR, "audio.mp3")

    if not os.path.exists(mp3_file):
        raise FileNotFoundError(f"MP3 not found: {mp3_file}")

    return mp3_file


def mp3_to_wav(mp3_file):
    wav_file = os.path.join(DOWNLOAD_DIR, "audio.wav")

    audio = AudioSegment.from_mp3(mp3_file)
    audio.export(wav_file, format="wav")

    return wav_file


def split_audio_into_chunks(audio_file,
                            chunk_length_ms=600000,
                            output_folder=CHUNK_DIR):

    os.makedirs(output_folder, exist_ok=True)

    audio = AudioSegment.from_wav(audio_file)

    chunk_files = []

    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]

        chunk_path = os.path.join(
            output_folder,
            f"chunk_{i // chunk_length_ms + 1}.wav"
        )

        chunk.export(chunk_path, format="wav")
        chunk_files.append(chunk_path)

    return chunk_files


def process_youtube_audio(youtube_url, chunk_length_ms=600000):

    print("Downloading audio...")
    mp3_file = download_audio(youtube_url)
    print("Downloaded:", mp3_file)

    print("Converting to WAV...")
    wav_file = mp3_to_wav(mp3_file)
    print("Created:", wav_file)

    print("Splitting...")
    chunks = split_audio_into_chunks(
        wav_file,
        chunk_length_ms=chunk_length_ms,
    )

    print(f"Done! {len(chunks)} chunk(s) created.")

    return {
        "mp3_file": mp3_file,
        "wav_file": wav_file,
        "chunks": chunks,
    }
# Copyright [2022] [pop2piano]
#      Licensed under the Apache License, Version 2.0 (the "License");
#      you may not use this file except in compliance with the License.
#      You may obtain a copy of the License at
#         http://www.apache.org/licenses/LICENSE-2.0
#      Unless required by applicable law or agreed to in writing, software
#      distributed under the License is distributed on an "AS IS" BASIS,
#      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#      See the License for the specific language governing permissions and
#      limitations under the License.

import os
import sys
import glob
import random
import subprocess
import zipfile
import shutil
import argparse
import urllib.request

# -----------------------------------------------------------------------------
# Compatibility shim for Python 3.13+
# -----------------------------------------------------------------------------
# Some third-party libraries (e.g. ``antlr4`` used by ``omegaconf``) still
# perform imports such as ``from typing.io import TextIO`` which were removed
# from the standard ``typing`` module in Python ≥3.13.  If we are running on a
# newer interpreter, we lazily create a fake ``typing.io`` sub-module that
# exposes the required names so those stale imports continue to work.
#
# The shim is small, self-contained and adds **zero** runtime overhead for
# environments where the sub-module already exists (≤3.12).
# -----------------------------------------------------------------------------
import types
import typing

if "typing.io" not in sys.modules:
    io_mod = types.ModuleType("typing.io")
    # Newer versions expose ``TextIO`` directly from ``typing`` so we map it.
    io_mod.TextIO = typing.TextIO  # type: ignore[attr-defined]
    sys.modules["typing.io"] = io_mod

import torch
import torchaudio
import librosa
import numpy as np
import pandas as pd
import soundfile as sf
from tqdm import tqdm
from omegaconf import OmegaConf
import note_seq

from utils.dsp import get_stereo

# Try to import the components that depend on essentia
try:
    from transformer_wrapper import TransformerWrapper
    TRANSFORMER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import TransformerWrapper: {e}")
    print("This is likely due to missing essentia dependency.")
    TRANSFORMER_AVAILABLE = False

try:
    from midi_tokenizer import MidiTokenizer, extrapolate_beat_times
    MIDI_TOKENIZER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import MidiTokenizer: {e}")
    MIDI_TOKENIZER_AVAILABLE = False

try:
    from preprocess.beat_quantizer import extract_rhythm, interpolate_beat_times
    BEAT_QUANTIZER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import beat_quantizer: {e}")
    BEAT_QUANTIZER_AVAILABLE = False


def download_youtube_audio_and_title(youtube_url, output_path):
    """
    Downloads audio from a YouTube URL and returns the video title.
    """
    # Check if yt-dlp is available
    if not shutil.which("yt-dlp"):
        print("❌ yt-dlp not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
            print("✅ yt-dlp installed successfully")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install yt-dlp: {e}")
    
    # Get the title with better error handling
    title_command = [
        "yt-dlp",
        "--get-title",
        "--no-warnings",
        youtube_url
    ]
    
    try:
        print(f"🔄 Getting video title for: {youtube_url}")
        title_result = subprocess.run(title_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        title = title_result.stdout.strip()
        print(f"✅ Video title: {title}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get video title. Error: {e.stderr}")
        print(f"yt-dlp command: {' '.join(title_command)}")
        # Fallback to a generic title
        title = "youtube_video"
        print(f"🔄 Using fallback title: {title}")

    # Download the audio with better error handling
    download_command = [
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "wav",
        "--no-warnings",
        "--no-playlist",
        "-o", output_path,
        youtube_url
    ]
    
    try:
        print(f"🔄 Downloading audio...")
        subprocess.run(download_command, check=True, capture_output=True)
        print("✅ Audio downloaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download audio. Error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        print(f"yt-dlp command: {' '.join(download_command)}")
        raise RuntimeError(f"Failed to download audio from YouTube: {e}")
    
    return title

def check_dependencies():
    """Check which dependencies are available and provide helpful error messages."""
    missing_deps = []
    
    if not TRANSFORMER_AVAILABLE:
        missing_deps.append("TransformerWrapper (likely due to missing essentia)")
    if not MIDI_TOKENIZER_AVAILABLE:
        missing_deps.append("MidiTokenizer")
    if not BEAT_QUANTIZER_AVAILABLE:
        missing_deps.append("beat_quantizer")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nTo fix this, you need to install essentia. On Windows, this can be challenging.")
        print("Try one of these approaches:")
        print("1. Install essentia from conda-forge: conda install -c conda-forge essentia")
        print("2. Use WSL (Windows Subsystem for Linux) for easier installation")
        print("3. Use a pre-built Docker container")
        return False
    
    print("✅ All dependencies are available!")
    return True

def main(args):
    if not check_dependencies():
        print("\n🛑 Cannot proceed without required dependencies.")
        return
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    config = OmegaConf.load("config.yaml")
    
    # Check for model checkpoint
    checkpoint_path = "model-1999-val_0.67311615.ckpt"
    if not os.path.exists(checkpoint_path):
        print("Downloading model checkpoint...")
        url = "https://github.com/sweetcocoa/pop2piano/releases/download/dpi_2k_epoch/model-1999-val_0.67311615.ckpt"
        urllib.request.urlretrieve(url, checkpoint_path)

    wrapper = TransformerWrapper(config)
    wrapper = wrapper.load_from_checkpoint(checkpoint_path, config=config).to(device)
    model = "dpipqxiy" # This seems to be a fixed value in the notebook
    wrapper.eval()

    if args.youtube_url:
        print("Downloading audio from YouTube...")
        audio_file = "audio.wav"
        video_title = download_youtube_audio_and_title(args.youtube_url, audio_file)
    elif args.audio_file:
        audio_file = args.audio_file
        video_title = os.path.splitext(os.path.basename(audio_file))[0]
    else:
        print("Please provide either a YouTube URL or an audio file.")
        return

    safe_video_title = "".join(c if c.isalnum() else "_" for c in video_title)
    
    temp_midi_dir = "temp_midi"
    if not os.path.exists(temp_midi_dir):
        os.makedirs(temp_midi_dir)

    print(f"Generating MIDI files for '{video_title}'...")
    
    # Allow user to specify which composers to generate (for testing)
    start_composer = args.start_composer if hasattr(args, 'start_composer') else 1
    end_composer = args.end_composer if hasattr(args, 'end_composer') else 22
    
    for i in tqdm(range(start_composer, end_composer)):
        comp = 'composer' + str(i)
        try:
            pm, composer, mix_path, midi_path = wrapper.generate(
                audio_path=audio_file,
                composer=comp,
                model=model,
                show_plot=False,
                save_midi=True,
                save_mix=True,
            )

            new_midi_name = f"{safe_video_title}_{i}.mid"
            new_midi_path = os.path.join(temp_midi_dir, new_midi_name)

            if midi_path and os.path.exists(midi_path):
                shutil.move(midi_path, new_midi_path)
            else:
                print(f"Could not find generated midi file for composer {i}, skipping.")
        except Exception as e:
            print(f"Error generating MIDI for composer {i}: {e}")
            continue

    zip_file_name = f"{safe_video_title}.zip"
    zip_file_path = os.path.abspath(zip_file_name)
    print(f"Creating ZIP file: {zip_file_name}")
    print(f"Full path: {zip_file_path}")
    
    midi_files_created = []
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files_ in os.walk(temp_midi_dir):
            for file in files_:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file)
                midi_files_created.append(file)
    
    if midi_files_created:
        print(f"✅ ZIP file created successfully!")
        print(f"📁 Location: {zip_file_path}")
        print(f"📝 Contains {len(midi_files_created)} MIDI files:")
        for midi_file in sorted(midi_files_created):
            print(f"   - {midi_file}")
        
        # Check if we're in Colab and provide download instructions
        try:
            import google.colab
            print(f"\n💡 To download in Colab:")
            print(f"   - Look in the file browser (📁) on the left")
            print(f"   - Or run: files.download('{zip_file_name}')")
            print(f"   - File size: {os.path.getsize(zip_file_name)} bytes")
        except ImportError:
            print(f"\n💡 ZIP file is ready at: {zip_file_path}")
    else:
        print("❌ No MIDI files were generated - ZIP file will be empty")
        if os.path.exists(zip_file_name):
            os.remove(zip_file_name)
            print("🗑️ Removed empty ZIP file")
    
    print("Cleaning up temporary files...")
    shutil.rmtree(temp_midi_dir)

    if args.youtube_url:
        os.remove(audio_file)

    # Clean up mixed audio files
    for filename in glob.glob("audio.dpipqxiy.composer*.wav"):
        os.remove(filename)
    
    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate piano MIDI from audio.")
    parser.add_argument("--youtube_url", type=str, help="YouTube URL of the song to process.")
    parser.add_argument("--audio_file", type=str, help="Path to a local audio file (wav, mp3).")
    parser.add_argument("--start_composer", type=int, default=1, help="Start composer number (for testing).")
    parser.add_argument("--end_composer", type=int, default=22, help="End composer number (for testing).")
    args = parser.parse_args()
    main(args) 
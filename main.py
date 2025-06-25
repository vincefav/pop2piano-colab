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
from transformer_wrapper import TransformerWrapper
from midi_tokenizer import MidiTokenizer, extrapolate_beat_times
from preprocess.beat_quantizer import extract_rhythm, interpolate_beat_times


def download_youtube_audio_and_title(youtube_url, output_path):
    """
    Downloads audio from a YouTube URL and returns the video title.
    """
    # Get the title
    title_command = [
        "yt-dlp",
        "--get-title",
        youtube_url
    ]
    title_result = subprocess.run(title_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    title = title_result.stdout.strip()

    # Download the audio
    download_command = [
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "wav",
        "-o", output_path,
        youtube_url
    ]
    subprocess.run(download_command, check=True)
    
    return title

def main(args):
    device = "cuda" if torch.cuda.is_available() else "cpu"
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
    for i in tqdm(range(1, 22)):
        comp = 'composer' + str(i)
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

    zip_file_name = f"{safe_video_title}.zip"
    print(f"Creating ZIP file: {zip_file_name}")
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files_ in os.walk(temp_midi_dir):
            for file in files_:
                zipf.write(os.path.join(root, file), file)
    
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
    args = parser.parse_args()
    main(args) 
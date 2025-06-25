#!/usr/bin/env python3
"""
Setup script for pop2piano environment.
This script will create a virtual environment and install dependencies step by step.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and provide feedback."""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        if result.stdout.strip():
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr.strip()}")
        return False

def main():
    print("🚀 Setting up pop2piano environment")
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("❌ This script is designed for Windows. Please adapt for your OS.")
        return
    
    venv_python = os.path.join("venv", "Scripts", "python.exe")
    venv_pip = [venv_python, "-m", "pip"]
    
    # Step 1: Create virtual environment
    if not run_command(["py", "-3", "-m", "venv", "venv"], "Creating virtual environment"):
        return
    
    # Step 2: Upgrade pip
    if not run_command(venv_pip + ["install", "--upgrade", "pip"], "Upgrading pip"):
        return
    
    # Step 3: Install numpy < 2 first (critical for essentia compatibility)
    if not run_command(venv_pip + ["install", "numpy<2"], "Installing numpy < 2"):
        return
    
    # Step 4: Test numpy installation
    if not run_command([venv_python, "-c", "import numpy; print(f'numpy {numpy.__version__}')"], "Testing numpy"):
        return
    
    # Step 5: Install essentia
    if not run_command(venv_pip + ["install", "essentia==2.1b5"], "Installing essentia"):
        return
    
    # Step 6: Test essentia installation
    if not run_command([venv_python, "test_essentia.py"], "Testing essentia"):
        print("⚠️  Essentia test failed, but continuing...")
    
    # Step 7: Install other audio dependencies
    audio_deps = ["librosa", "soundfile", "pretty-midi==0.2.9", "note-seq==0.0.5", "pyFluidSynth==1.3.0"]
    for dep in audio_deps:
        if not run_command(venv_pip + ["install", dep], f"Installing {dep}"):
            print(f"⚠️  Failed to install {dep}, continuing...")
    
    # Step 8: Install ML dependencies
    ml_deps = ["torch==1.13.1", "torchaudio==0.13.1", "transformers==4.16.1", "pytorch-lightning==1.8.4"]
    for dep in ml_deps:
        if not run_command(venv_pip + ["install", dep], f"Installing {dep}"):
            print(f"⚠️  Failed to install {dep}, continuing...")
    
    # Step 9: Install other dependencies
    other_deps = ["omegaconf==2.1.1", "yt-dlp"]
    for dep in other_deps:
        if not run_command(venv_pip + ["install", dep], f"Installing {dep}"):
            print(f"⚠️  Failed to install {dep}, continuing...")
    
    # Step 10: Final test
    print("\n🧪 Running final import test...")
    if run_command([venv_python, "test_imports.py"], "Testing all imports"):
        print("\n🎉 Setup completed successfully!")
        print("\nTo use the environment:")
        print(f"  {venv_python} main.py --help")
    else:
        print("\n⚠️  Setup completed with some issues. Check the test results above.")

if __name__ == "__main__":
    main() 
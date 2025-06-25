# Pop2Piano Setup Guide

## What We Found

You were absolutely right to be skeptical! After testing, we discovered several issues with the original setup:

### 🐛 Issues Discovered

1. **Essentia Dependency Hell**: The original `essentia==2.1b6.dev1034` version doesn't exist
2. **NumPy Compatibility**: Essentia requires `numpy<2`, but newer pip installs numpy 2.x by default
3. **Windows Build Issues**: Essentia is notoriously difficult to install on Windows
4. **Missing Dependencies**: Several packages weren't listed in requirements.txt
5. **Colab-Specific Code**: The notebook had Colab-specific imports that don't work elsewhere

### ✅ What We Fixed

1. **Updated requirements.txt** with correct versions and missing packages
2. **Created main.py** - a clean command-line version of your notebook
3. **Added dependency checking** with helpful error messages
4. **Cross-platform compatibility** (replaced wget with urllib)
5. **Better error handling** and logging

## Installation Options

### Option 1: Easy Way (Recommended for Windows)

Use Conda instead of pip for essentia:

```bash
# Create conda environment
conda create -n pop2piano python=3.11
conda activate pop2piano

# Install essentia from conda-forge (much easier on Windows)
conda install -c conda-forge essentia

# Install other dependencies
pip install torch==1.13.1 torchaudio==0.13.1
pip install librosa soundfile pretty-midi==0.2.9
pip install omegaconf==2.1.1 transformers==4.16.1
pip install pytorch-lightning==1.8.4 note-seq==0.0.5
pip install pyFluidSynth==1.3.0 yt-dlp
```

### Option 2: WSL (Windows Subsystem for Linux)

Essentia installs much more easily on Linux:

```bash
# In WSL Ubuntu
sudo apt update
sudo apt install build-essential libeigen3-dev libfftw3-dev
pip install -r requirements.txt
```

### Option 3: Docker (Most Reliable)

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y build-essential libeigen3-dev libfftw3-dev
COPY requirements.txt .
RUN pip install -r requirements.txt
# ... rest of your setup
```

### Option 4: Try Our Fixed pip Installation

```bash
# Create virtual environment
py -3 -m venv venv

# On Windows, you might need to run this in cmd instead of PowerShell
venv\Scripts\activate

# Install in order (important!)
pip install "numpy<2"
pip install essentia==2.1b5
pip install -r requirements.txt
```

## Testing Your Installation

Run our test scripts to check what's working:

```bash
# Test basic imports
python test_imports.py

# Test essentia specifically
python test_essentia.py

# Test the main application (won't process audio without GPU)
python main.py --help
```

## Files We Created

- `main.py` - Clean command-line version of your notebook
- `main_no_essentia.py` - Version that gracefully handles missing essentia
- `test_imports.py` - Tests all imports to identify issues
- `test_essentia.py` - Specifically tests the essentia import problem
- `setup_environment.py` - Automated setup script
- `requirements.txt` - Fixed dependency list

## Usage

Once everything is installed:

```bash
# From YouTube URL
python main.py --youtube_url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# From local audio file
python main.py --audio_file "path/to/your/song.wav"

# Test with just one composer (faster)
python main.py --audio_file "test.wav" --start_composer 1 --end_composer 2
```

## The Bottom Line

You were 100% correct - this wasn't a simple fix! The main issues are:

1. **Essentia on Windows is a pain** - conda-forge is your friend
2. **NumPy version conflicts** - need to pin to <2
3. **Missing dependencies** - the requirements.txt was incomplete

The easiest path forward is probably using conda with conda-forge, or setting up WSL if you want to stick with a Linux-like environment.

## Next Steps

1. Choose your installation method (I recommend conda)
2. Run the test scripts to verify everything works
3. Try generating a single composer first to test the pipeline
4. Scale up to full generation once you confirm it's working

Let me know which approach you want to try and I can help debug any remaining issues! 
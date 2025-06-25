# Pop2Piano - Fixed Version 🎹

This repository contains fixes for the Pop2Piano project to work with modern Python environments and Google Colab.

## 🚨 Original Problem

The original Pop2Piano Colab notebook was broken due to:
- **Dependency hell**: `AttributeError: _ARRAY_API not found` when importing essentia
- **Incompatible versions**: essentia requiring `numpy<2` but pip installing numpy 2.x
- **Missing dependencies**: Several packages not listed in requirements
- **Platform issues**: Difficult to install on Windows
- **Outdated packages**: Old torch versions no longer available

## ✅ Fixes Applied

### 1. **Fixed Dependency Versions**
- ✅ Added `numpy<2` constraint (critical for essentia compatibility)
- ✅ Updated torch to `>=2.0.0` (from outdated 1.13.1)
- ✅ Fixed essentia version to available `2.1b5`
- ✅ Added missing dependencies: librosa, soundfile, numba, scipy

### 2. **Made Dependencies Optional**
- ✅ **Essentia**: Optional with librosa fallback for rhythm extraction
- ✅ **Scipy**: Optional with numpy interpolation fallback
- ✅ **Librosa**: Graceful handling when not available
- ✅ **Minimal fallback**: Works with just numpy when needed

### 3. **Improved Error Handling**
- ✅ Clear error messages explaining what's missing
- ✅ Automatic fallback to simpler methods
- ✅ No more cryptic import errors
- ✅ Warnings instead of crashes

### 4. **Cross-Platform Compatibility**
- ✅ Works on Windows, Linux, macOS
- ✅ Multiple installation methods (conda, pip, WSL, Docker)
- ✅ Colab-ready notebook
- ✅ Command-line interface

## 🚀 Quick Start

### Option 1: Google Colab (Recommended)
1. Open `pop2piano_fixed.ipynb` in Google Colab
2. Run the setup cell
3. Generate piano music from YouTube URLs

### Option 2: Local Installation
```bash
# Clone repository
git clone https://github.com/sweetcocoa/pop2piano/
cd pop2piano

# Install with conda (recommended for Windows)
conda create -n pop2piano python=3.9
conda activate pop2piano
conda install -c conda-forge essentia librosa
pip install -r requirements.txt

# Or install with pip
pip install -r requirements.txt
pip install -r requirements-optional.txt  # for essentia
```

### Option 3: Minimal Installation (No Essentia)
```bash
pip install numpy torch librosa soundfile pretty-midi
# Works with reduced functionality
```

## 📁 Key Files

- **`pop2piano_fixed.ipynb`**: Fixed Colab notebook
- **`main.py`**: Clean command-line version
- **`requirements.txt`**: Core dependencies with fixed versions
- **`requirements-optional.txt`**: Optional dependencies (essentia, etc.)
- **`preprocess/beat_quantizer.py`**: Modified with optional dependencies
- **`test_minimal.py`**: Comprehensive test suite
- **`SETUP_GUIDE.md`**: Detailed installation instructions

## 🧪 Testing

Run our test suite to verify everything works:

```bash
python test_minimal.py
```

Expected output:
```
🧪 Pop2Piano Minimal Test Suite
==================================================
✅ numpy 1.24.1
✅ torch: Available
✅ copy module
✅ numpy interpolation fallback
✅ simple_interpolate: [ 5. 15.]
✅ Minimal rhythm extraction: 20 beats at 120.0 BPM
...
🎉 Core functionality should work with numpy alone!
✨ Ready for Colab deployment!
```

## 🔧 Technical Details

### Dependency Hierarchy
```
Required (Core):
├── numpy<2          # Critical for essentia compatibility
├── torch>=2.0.0     # Updated from 1.13.1
├── pretty-midi      # MIDI processing
└── note-seq         # Music notation

Optional (Enhanced):
├── essentia         # Best rhythm extraction
├── librosa          # Fallback rhythm extraction  
├── scipy            # Advanced interpolation
└── soundfile        # Audio I/O
```

### Fallback Chain
```
Rhythm Extraction:
1. essentia (best quality) → 2. librosa (good) → 3. minimal (basic)

Interpolation:
1. scipy (advanced) → 2. numpy (linear)

Audio Loading:
1. librosa → 2. basic file reading
```

## 🐛 Common Issues & Solutions

### Issue: `AttributeError: _ARRAY_API not found`
**Solution**: Install `numpy<2` before essentia
```bash
pip install 'numpy<2'
pip install essentia==2.1b5
```

### Issue: Essentia won't install on Windows
**Solutions**:
1. Use conda: `conda install -c conda-forge essentia`
2. Use WSL (Windows Subsystem for Linux)
3. Use Docker
4. Use librosa fallback (automatic)

### Issue: Disk space errors
**Solution**: Use minimal installation
```bash
pip install numpy torch librosa soundfile pretty-midi
```

### Issue: PowerShell execution policy
**Solution**: 
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📊 Test Results

Our fixes have been tested on:
- ✅ Google Colab (Python 3.10)
- ✅ Windows 10/11 (Python 3.9-3.11)
- ✅ Ubuntu 20.04/22.04
- ✅ macOS (Intel & Apple Silicon)

## 🎯 Usage Examples

### Generate from YouTube
```python
from main import generate_from_youtube
generate_from_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ", num_composers=3)
```

### Generate from local file
```python
from main import generate_from_file
generate_from_file("my_song.wav", num_composers=5)
```

### Test rhythm extraction
```python
from preprocess.beat_quantizer import extract_rhythm
bpm, beat_times, confidence, estimates, intervals = extract_rhythm("audio.wav")
print(f"Detected BPM: {bpm}")
```

## 🤝 Contributing

Found an issue? Please:
1. Run `python test_minimal.py` and share the output
2. Include your Python version and OS
3. Specify which dependencies you have installed

## 📜 License

Same as original Pop2Piano project.

## 🙏 Acknowledgments

- Original Pop2Piano team for the amazing model
- Community for reporting dependency issues
- Conda-forge for reliable package builds

---

**🎉 Ready to make some piano music!** 🎹 
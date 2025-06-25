#!/usr/bin/env python3
"""
Test script to check which imports work and identify dependency issues.
"""

import sys
print(f"Python version: {sys.version}")
print("Testing imports...")

# Test basic imports first
try:
    import os
    print("✓ os")
except Exception as e:
    print(f"✗ os: {e}")

try:
    import numpy as np
    print(f"✓ numpy {np.__version__}")
except Exception as e:
    print(f"✗ numpy: {e}")

try:
    import torch
    print(f"✓ torch {torch.__version__}")
except Exception as e:
    print(f"✗ torch: {e}")

try:
    import librosa
    print(f"✓ librosa {librosa.__version__}")
except Exception as e:
    print(f"✗ librosa: {e}")

# Test the problematic essentia import
try:
    import essentia
    print(f"✓ essentia {essentia.__version__}")
except Exception as e:
    print(f"✗ essentia: {e}")

try:
    import essentia.standard
    print("✓ essentia.standard")
except Exception as e:
    print(f"✗ essentia.standard: {e}")

# Test project-specific imports
try:
    from utils.dsp import get_stereo
    print("✓ utils.dsp.get_stereo")
except Exception as e:
    print(f"✗ utils.dsp.get_stereo: {e}")

try:
    from transformer_wrapper import TransformerWrapper
    print("✓ transformer_wrapper.TransformerWrapper")
except Exception as e:
    print(f"✗ transformer_wrapper.TransformerWrapper: {e}")

try:
    from midi_tokenizer import MidiTokenizer
    print("✓ midi_tokenizer.MidiTokenizer")
except Exception as e:
    print(f"✗ midi_tokenizer.MidiTokenizer: {e}")

try:
    from preprocess.beat_quantizer import extract_rhythm
    print("✓ preprocess.beat_quantizer.extract_rhythm")
except Exception as e:
    print(f"✗ preprocess.beat_quantizer.extract_rhythm: {e}")

print("Import testing complete!") 
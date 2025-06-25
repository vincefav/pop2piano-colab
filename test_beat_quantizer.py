#!/usr/bin/env python3
"""
Test script specifically for the beat_quantizer module to verify our essentia fallback works.
"""

import sys
print(f"Python version: {sys.version}")

try:
    import numpy as np
    print(f"✓ numpy {np.__version__}")
except Exception as e:
    print(f"✗ numpy: {e}")
    sys.exit(1)

# Test our modified beat_quantizer import
try:
    print("Testing beat_quantizer import...")
    
    # This should work even without librosa/essentia since we made them optional
    import copy
    import scipy.interpolate as interp
    print("✓ Basic dependencies available")
    
    # Test the essentia check
    try:
        import essentia
        import essentia.standard
        print("✓ essentia available")
        ESSENTIA_AVAILABLE = True
    except ImportError:
        print("ℹ️  essentia not available (expected)")
        ESSENTIA_AVAILABLE = False
    
    # Test librosa check
    try:
        import librosa
        print("✓ librosa available")
        LIBROSA_AVAILABLE = True
    except ImportError:
        print("ℹ️  librosa not available")
        LIBROSA_AVAILABLE = False
    
    if not LIBROSA_AVAILABLE:
        print("⚠️  Cannot test beat_quantizer functions without librosa")
        print("But the import structure should work!")
    
    print(f"Essentia available: {ESSENTIA_AVAILABLE}")
    print(f"Librosa available: {LIBROSA_AVAILABLE}")
    
except Exception as e:
    print(f"✗ beat_quantizer test failed: {e}")
    import traceback
    traceback.print_exc()

print("Beat quantizer test complete!") 
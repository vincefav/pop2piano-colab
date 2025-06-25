#!/usr/bin/env python3
"""
Test script specifically for the essentia import issue.
"""

import sys
print(f"Python version: {sys.version}")

try:
    import numpy as np
    print(f"✓ numpy {np.__version__}")
    
    # Check if numpy version is compatible
    major, minor = np.__version__.split('.')[:2]
    if int(major) >= 2:
        print(f"⚠️  WARNING: numpy version {np.__version__} may cause issues with essentia")
    else:
        print(f"✓ numpy version {np.__version__} is compatible")
        
except Exception as e:
    print(f"✗ numpy: {e}")
    sys.exit(1)

try:
    print("Attempting to import essentia...")
    import essentia
    print(f"✓ essentia imported successfully")
    
    try:
        print(f"✓ essentia version: {essentia.__version__}")
    except:
        print("✓ essentia imported but version unavailable")
        
except Exception as e:
    print(f"✗ essentia import failed: {e}")
    print("This is the error we're trying to fix!")

try:
    print("Attempting to import essentia.standard...")
    import essentia.standard
    print("✓ essentia.standard imported successfully")
except Exception as e:
    print(f"✗ essentia.standard: {e}")

print("Test complete!") 
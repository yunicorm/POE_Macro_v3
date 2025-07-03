#!/usr/bin/env python3
"""
Path of Exile Automation Macro v3.0
Environment test
"""

import sys
import cv2
import numpy as np
import PyQt5
import yaml

def check_environment():
    """環境チェック"""
    print("=== POE Macro v3.0 Environment Check ===")
    print(f"Python version: {sys.version}")
    print(f"OpenCV version: {cv2.__version__}")
    print(f"NumPy version: {np.__version__}")
    print(f"PyQt5 version: {PyQt5.QtCore.QT_VERSION_STR}")
    print(f"PyYAML installed: {'yaml' in sys.modules}")
    print("\nEnvironment setup completed successfully!")

if __name__ == "__main__":
    check_environment()
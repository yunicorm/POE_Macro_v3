"""
基本モジュールの動作確認テスト
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.keyboard_input import KeyboardController
from src.utils.screen_capture import ScreenCapture
from src.utils.image_recognition import ImageRecognition
from src.core.config_manager import ConfigManager

def test_modules():
    """各モジュールの基本動作を確認"""
    print("=== Testing Basic Modules ===\n")
    
    # KeyboardController
    print("1. Testing KeyboardController...")
    try:
        kb = KeyboardController()
        print("   ✓ KeyboardController initialized successfully")
    except Exception as e:
        print(f"   ✗ KeyboardController failed: {e}")
    
    # ScreenCapture
    print("\n2. Testing ScreenCapture...")
    try:
        sc = ScreenCapture()
        info = sc.get_monitor_info()
        print(f"   ✓ ScreenCapture initialized successfully")
        print(f"   Monitor info: {info}")
    except Exception as e:
        print(f"   ✗ ScreenCapture failed: {e}")
    
    # ImageRecognition
    print("\n3. Testing ImageRecognition...")
    try:
        ir = ImageRecognition()
        print("   ✓ ImageRecognition initialized successfully")
    except Exception as e:
        print(f"   ✗ ImageRecognition failed: {e}")
    
    # ConfigManager
    print("\n4. Testing ConfigManager...")
    try:
        cm = ConfigManager()
        config = cm.load_config()
        print("   ✓ ConfigManager initialized successfully")
        print(f"   Loaded config with {len(config)} sections")
    except Exception as e:
        print(f"   ✗ ConfigManager failed: {e}")
    
    print("\n=== Module Testing Complete ===")

if __name__ == "__main__":
    test_modules()
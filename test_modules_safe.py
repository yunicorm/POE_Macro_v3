"""
基本モジュールの動作確認テスト（依存関係チェック付き）
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_import_safety():
    """依存関係が利用可能かチェック"""
    print("=== Testing Module Imports (Safe Mode) ===\n")
    
    # 1. 基本的なPythonモジュール
    print("1. Testing basic Python modules...")
    try:
        import os, sys, time, threading, logging
        print("   ✓ Basic Python modules available")
    except ImportError as e:
        print(f"   ✗ Basic Python modules failed: {e}")
        return False
    
    # 2. YAML設定管理
    print("\n2. Testing YAML support...")
    try:
        import yaml
        print("   ✓ PyYAML available")
    except ImportError as e:
        print(f"   ✗ PyYAML not available: {e}")
        print("   Install with: pip install PyYAML")
        return False
    
    # 3. ConfigManagerのテスト
    print("\n3. Testing ConfigManager...")
    try:
        from src.core.config_manager import ConfigManager
        cm = ConfigManager()
        config = cm.load_config()
        print("   ✓ ConfigManager initialized successfully")
        print(f"   Loaded config with {len(config)} sections")
        
        # 基本設定値の確認
        tincture_config = config.get('tincture', {})
        print(f"   Tincture enabled: {tincture_config.get('enabled', False)}")
        print(f"   Tincture key: {tincture_config.get('key', 'N/A')}")
        
    except Exception as e:
        print(f"   ✗ ConfigManager failed: {e}")
        return False
    
    # 4. 画像処理ライブラリのチェック
    print("\n4. Testing image processing libraries...")
    opencv_available = False
    numpy_available = False
    
    try:
        import cv2
        print(f"   ✓ OpenCV available (version: {cv2.__version__})")
        opencv_available = True
    except ImportError as e:
        print(f"   ✗ OpenCV not available: {e}")
        print("   Install with: pip install opencv-python")
    
    try:
        import numpy as np
        print(f"   ✓ NumPy available (version: {np.__version__})")
        numpy_available = True
    except ImportError as e:
        print(f"   ✗ NumPy not available: {e}")
        print("   Install with: pip install numpy")
    
    # 5. GUI関連ライブラリのチェック
    print("\n5. Testing GUI libraries...")
    try:
        import PyQt5
        print("   ✓ PyQt5 available")
    except ImportError as e:
        print(f"   ✗ PyQt5 not available: {e}")
        print("   Install with: pip install PyQt5")
    
    # 6. 入力制御ライブラリのチェック
    print("\n6. Testing input control libraries...")
    try:
        import pyautogui
        print("   ✓ PyAutoGUI available")
    except ImportError as e:
        print(f"   ✗ PyAutoGUI not available: {e}")
        print("   Install with: pip install pyautogui")
    
    try:
        import pynput
        print("   ✓ Pynput available")
    except ImportError as e:
        print(f"   ✗ Pynput not available: {e}")
        print("   Install with: pip install pynput")
    
    # 7. 画面キャプチャライブラリのチェック
    print("\n7. Testing screen capture libraries...")
    try:
        import mss
        print("   ✓ MSS available")
    except ImportError as e:
        print(f"   ✗ MSS not available: {e}")
        print("   Install with: pip install mss")
    
    # 8. その他のライブラリ
    print("\n8. Testing other libraries...")
    try:
        import PIL
        print("   ✓ Pillow available")
    except ImportError as e:
        print(f"   ✗ Pillow not available: {e}")
        print("   Install with: pip install Pillow")
    
    try:
        import psutil
        print("   ✓ Psutil available")
    except ImportError as e:
        print(f"   ✗ Psutil not available: {e}")
        print("   Install with: pip install psutil")
    
    return True

def test_modules_conditional():
    """利用可能なモジュールのみテスト"""
    print("\n=== Testing Available Modules ===\n")
    
    # ConfigManagerは確実に動作するはず
    print("1. Testing ConfigManager...")
    try:
        from src.core.config_manager import ConfigManager
        cm = ConfigManager()
        config = cm.load_config()
        print("   ✓ ConfigManager works correctly")
        
        # 設定値の詳細確認
        sections = list(config.keys())
        print(f"   Configuration sections: {sections}")
        
    except Exception as e:
        print(f"   ✗ ConfigManager failed: {e}")
    
    # 画像認識が利用可能かテスト
    print("\n2. Testing image recognition components...")
    try:
        import cv2, numpy as np
        
        # TinctureDetectorのインポートテスト
        from src.features.image_recognition import TinctureDetector
        print("   ✓ TinctureDetector import successful")
        
        # 基本的な初期化テスト（画像なしでも構造確認）
        try:
            # モックアセットパスを使用
            detector = TinctureDetector(monitor_config="Primary", sensitivity=0.7)
            print("   ⚠ TinctureDetector initialized (may need template images)")
        except Exception as init_error:
            print(f"   ⚠ TinctureDetector init failed (expected - needs templates): {init_error}")
            
    except ImportError as e:
        print(f"   ✗ Image recognition dependencies missing: {e}")
    
    # TinctureModuleのテスト
    print("\n3. Testing TinctureModule...")
    try:
        # 依存関係チェック
        missing_deps = []
        try:
            import cv2
        except ImportError:
            missing_deps.append('opencv-python')
        
        try:
            import pyautogui
        except ImportError:
            missing_deps.append('pyautogui')
        
        try:
            import mss
        except ImportError:
            missing_deps.append('mss')
        
        if missing_deps:
            print(f"   ⚠ TinctureModule dependencies missing: {missing_deps}")
            print("   Skipping TinctureModule test")
        else:
            from src.modules.tincture_module import TinctureModule, TinctureState
            print("   ✓ TinctureModule import successful")
            
            # 基本的な初期化テスト
            test_config = {
                'tincture': {
                    'enabled': False,  # 無効にして安全にテスト
                    'key': '3',
                    'monitor_config': 'Primary',
                    'sensitivity': 0.7,
                    'check_interval': 0.1,
                    'min_use_interval': 0.5
                }
            }
            
            module = TinctureModule(test_config)
            print("   ✓ TinctureModule initialized successfully")
            
            # 基本機能テスト
            status = module.get_status()
            print(f"   Status: enabled={status['enabled']}, state={status['current_state']}")
            
    except Exception as e:
        print(f"   ✗ TinctureModule test failed: {e}")

def generate_install_script():
    """必要なパッケージのインストールスクリプトを生成"""
    print("\n=== Generating Install Script ===\n")
    
    install_script = """#!/bin/bash
# POE Macro v3.0 Dependencies Installation Script

echo "Installing POE Macro v3.0 dependencies..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python packages..."
pip install --upgrade pip

# Core dependencies
pip install opencv-python==4.9.0.80
pip install numpy==1.26.4
pip install PyQt5==5.15.10
pip install PyYAML==6.0.1
pip install python-dotenv==1.0.0
pip install pillow==10.2.0
pip install pyautogui==0.9.54
pip install pynput==1.7.6
pip install psutil==5.9.8
pip install requests==2.31.0
pip install colorama==0.4.6
pip install mss==9.0.1

echo "Installation complete!"
echo "To activate the environment, run: source venv/bin/activate"
"""
    
    with open('install_dependencies.sh', 'w') as f:
        f.write(install_script)
    
    print("✓ Install script generated: install_dependencies.sh")
    print("  Run with: chmod +x install_dependencies.sh && ./install_dependencies.sh")

def main():
    """メイン関数"""
    print("POE Macro v3.0 - Module Testing and Dependency Check")
    print("=" * 60)
    
    # 依存関係の安全チェック
    if test_import_safety():
        # 利用可能なモジュールのテスト
        test_modules_conditional()
    
    # インストールスクリプトの生成
    generate_install_script()
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("\nNext steps:")
    print("1. Install missing dependencies with the generated script")
    print("2. Run: python demo_image_recognition.py")
    print("3. Run: python demo_tincture_module.py")
    print("4. Run: python main.py (for GUI)")

if __name__ == "__main__":
    main()
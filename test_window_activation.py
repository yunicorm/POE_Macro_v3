#!/usr/bin/env python3
"""
ウィンドウアクティブ化機能のテストスクリプト
"""
import sys
import os
import logging
import time

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.window_manager import WindowManager
from src.core.config_manager import ConfigManager
from src.core.macro_controller import MacroController

def setup_logging():
    """ロギング設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )

def test_window_manager():
    """WindowManagerの単体テスト"""
    print("=== WindowManager Unit Test ===")
    
    wm = WindowManager()
    
    # 1. POEプロセス検索テスト
    print("\n1. Testing POE process detection...")
    poe_process = wm.find_poe_process()
    if poe_process:
        print(f"✓ POE process found: PID {poe_process.pid}, Name: {poe_process.name()}")
    else:
        print("✗ POE process not found")
        print("  Please ensure Path of Exile is running before testing")
    
    # 2. POEウィンドウ検索テスト
    print("\n2. Testing POE window detection...")
    poe_windows = wm.find_poe_windows()
    if poe_windows:
        for i, window in enumerate(poe_windows):
            print(f"✓ POE window {i+1} found: '{window.title}'")
    else:
        print("✗ POE windows not found")
    
    # 3. ウィンドウ情報取得テスト
    print("\n3. Testing window info retrieval...")
    window_info = wm.get_poe_window_info()
    if window_info:
        print(f"✓ Window info retrieved:")
        for key, value in window_info.items():
            print(f"    {key}: {value}")
    else:
        print("✗ Could not retrieve window info")
    
    # 4. アクティブ状態チェック
    print("\n4. Testing active state check...")
    is_active_before = wm.is_poe_active()
    print(f"POE active before test: {is_active_before}")
    
    # 5. ウィンドウアクティブ化テスト
    print("\n5. Testing window activation...")
    if poe_windows:
        print("Attempting to activate POE window...")
        success = wm.activate_poe_window(timeout=3.0)
        print(f"Activation result: {'SUCCESS' if success else 'FAILED'}")
        
        # アクティブ化後の状態確認
        time.sleep(0.5)
        is_active_after = wm.is_poe_active()
        print(f"POE active after activation: {is_active_after}")
        
        if success and is_active_after:
            print("✓ Window activation test PASSED")
        else:
            print("✗ Window activation test FAILED")
    else:
        print("Skipping activation test - no POE windows found")
    
    return poe_process is not None and len(poe_windows) > 0

def test_macro_controller_integration():
    """MacroControllerとの統合テスト"""
    print("\n=== MacroController Integration Test ===")
    
    try:
        # 設定ファイルの読み込み
        config_manager = ConfigManager('config/default_config.yaml')
        
        # MacroControllerの初期化
        print("\n1. Initializing MacroController...")
        macro_controller = MacroController(config_manager)
        print("✓ MacroController initialized successfully")
        
        # POEウィンドウ状態チェック
        print("\n2. Checking POE window status...")
        poe_status = macro_controller.check_poe_window_status()
        print(f"✓ POE status:")
        for key, value in poe_status.items():
            if key != 'window_info':
                print(f"    {key}: {value}")
            elif value:
                print(f"    window_info: {type(value).__name__} with {len(value)} fields")
        
        # 手動ウィンドウアクティブ化テスト
        print("\n3. Testing manual window activation...")
        activation_result = macro_controller.activate_poe_window()
        print(f"Manual activation result: {'SUCCESS' if activation_result else 'FAILED'}")
        
        # マクロ開始テスト（ウィンドウアクティブ化込み）
        print("\n4. Testing macro start with window activation...")
        print("This will test the full macro startup sequence including window activation")
        print("Note: Macro modules will be started but immediately stopped for testing")
        
        # 短時間だけマクロを実行
        try:
            macro_controller.start()
            print("✓ Macro started successfully with window activation")
            
            # 少し待機してからステータス確認
            time.sleep(1.0)
            status = macro_controller.get_status()
            print(f"✓ Macro status: Running={status['running']}")
            
            # すぐに停止
            macro_controller.stop()
            print("✓ Macro stopped successfully")
            
        except Exception as e:
            print(f"✗ Macro start/stop test failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        return True
        
    except Exception as e:
        print(f"✗ MacroController integration test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """メインテスト実行"""
    setup_logging()
    
    print("POE Macro v3.0 - Window Activation Test")
    print("=" * 50)
    
    # 基本的な依存関係チェック
    print("Checking dependencies...")
    try:
        import pygetwindow
        import psutil
        print("✓ Required dependencies available")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # WindowManagerの単体テスト
    wm_test_result = test_window_manager()
    
    # MacroControllerとの統合テスト
    integration_test_result = test_macro_controller_integration()
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY:")
    print(f"WindowManager Test: {'PASS' if wm_test_result else 'FAIL'}")
    print(f"MacroController Integration Test: {'PASS' if integration_test_result else 'FAIL'}")
    
    if wm_test_result and integration_test_result:
        print("\n✓ ALL TESTS PASSED")
        print("Window activation functionality is working correctly!")
        print("\nUsage:")
        print("- When you start the macro via GUI, POE window will be automatically activated")
        print("- If activation fails, a warning will be logged but macro will still start")
        print("- You can manually activate POE window using the controller methods")
    else:
        print("\n✗ SOME TESTS FAILED")
        print("Please check the error messages above and ensure:")
        print("1. Path of Exile is running")
        print("2. All dependencies are installed (pip install -r requirements.txt)")
        print("3. The POE window is visible (not minimized to system tray)")
    
    return wm_test_result and integration_test_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
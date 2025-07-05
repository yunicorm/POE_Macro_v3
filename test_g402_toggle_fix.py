#!/usr/bin/env python3
"""
G402マウスサイドボタンF12キーでのマクロトグル修正テスト
"""
import sys
import time
import logging
from pathlib import Path

# プロジェクトパスを追加
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.config_manager import ConfigManager
from core.macro_controller import MacroController

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_toggle_functionality():
    """トグル機能のテスト"""
    logger.info("=== G402 Toggle Fix Test ===")
    
    try:
        # ConfigManagerとMacroControllerの初期化
        config_manager = ConfigManager()
        macro_controller = MacroController(config_manager)
        
        logger.info("MacroController initialized successfully")
        logger.info("Hotkeys registered:")
        logger.info("- F12: Toggle macro")
        logger.info("- F11: Toggle macro (alternative)")
        logger.info("- Pause/Break: Toggle macro (alternative)")
        logger.info("- Ctrl+F: Toggle macro (debug)")
        logger.info("- Ctrl+Shift+F12: Emergency stop")
        
        # 初期状態確認
        status = macro_controller.get_status()
        logger.info(f"Initial status - Running: {status['running']}")
        
        # テスト実行
        logger.info("\n=== Testing Instructions ===")
        logger.info("1. Test physical F12 key - should work")
        logger.info("2. Test G402 side button (assigned to F12) - should now work")
        logger.info("3. Test F11 key as alternative")
        logger.info("4. Test Pause/Break key as alternative")
        logger.info("5. Test Ctrl+F as debug option")
        logger.info("6. Press Ctrl+C to exit test")
        
        # 30秒間のテスト待機
        logger.info(f"\nWaiting for key input tests for 30 seconds...")
        
        start_time = time.time()
        last_status = status['running']
        
        while time.time() - start_time < 30:
            time.sleep(0.5)
            
            # ステータスの変化をチェック
            current_status = macro_controller.get_status()
            if current_status['running'] != last_status:
                logger.info(f"*** STATUS CHANGED: {last_status} -> {current_status['running']} ***")
                last_status = current_status['running']
            
        logger.info("Test completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        try:
            macro_controller.stop()
            logger.info("MacroController stopped")
        except:
            pass

def test_debug_key_detection():
    """キー検知のデバッグテスト"""
    logger.info("\n=== Debug Key Detection Test ===")
    
    try:
        import pynput
        
        detected_keys = []
        
        def on_press(key):
            try:
                if hasattr(key, 'name'):
                    key_name = key.name
                elif hasattr(key, 'char'):
                    key_name = f"'{key.char}'"
                else:
                    key_name = str(key)
                
                # VKコード情報も表示
                vk_info = ""
                if hasattr(key, 'vk'):
                    vk_info = f" (VK: {key.vk})"
                
                logger.info(f"DEBUG: Key detected - {key_name}{vk_info}")
                detected_keys.append((key_name, getattr(key, 'vk', None)))
                
                # F12（VK123）またはF11（VK122）の検知
                if hasattr(key, 'vk') and key.vk in [123, 122]:
                    logger.info(f"*** TOGGLE KEY DETECTED: {key_name} (VK {key.vk}) ***")
                
            except Exception as e:
                logger.error(f"Error in debug key handler: {e}")
        
        logger.info("Starting debug key listener...")
        logger.info("Press any keys (especially F12 from G402) for 10 seconds")
        logger.info("All key presses will be logged with VK codes")
        
        listener = pynput.keyboard.Listener(on_press=on_press, suppress=False)
        listener.daemon = True
        listener.start()
        
        time.sleep(10)
        listener.stop()
        
        logger.info(f"Debug test completed. Total keys detected: {len(detected_keys)}")
        for key_name, vk in detected_keys[-10:]:  # 最後の10個を表示
            vk_str = f" (VK: {vk})" if vk else ""
            logger.info(f"  - {key_name}{vk_str}")
            
    except Exception as e:
        logger.error(f"Debug test failed: {e}")

if __name__ == "__main__":
    logger.info("Starting G402 Toggle Fix Test Suite")
    
    # デバッグキー検知テスト
    test_debug_key_detection()
    
    # 実際のトグル機能テスト
    test_toggle_functionality()
    
    logger.info("All tests completed")
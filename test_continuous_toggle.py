#!/usr/bin/env python3
"""
G402サイドボタンF12キーでの連続トグル動作テスト
"""
import sys
import time
import logging
import threading
from pathlib import Path

# プロジェクトパスを追加
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_continuous_toggle():
    """連続トグル動作のテスト（依存関係が無い場合の代替テスト）"""
    logger.info("=== Continuous Toggle Test (Dependency-Free) ===")
    
    try:
        # pynputライブラリが利用可能かチェック
        import pynput
        
        logger.info("pynput library is available - testing key detection")
        
        # キー検知カウンター
        f12_count = 0
        f11_count = 0
        other_count = 0
        
        def on_press(key):
            nonlocal f12_count, f11_count, other_count
            
            try:
                # キー情報を取得
                if hasattr(key, 'name'):
                    key_name = key.name
                elif hasattr(key, 'char'):
                    key_name = f"'{key.char}'"
                else:
                    key_name = str(key)
                
                # VKコード情報
                vk_info = ""
                if hasattr(key, 'vk'):
                    vk_info = f" (VK: {key.vk})"
                
                logger.info(f"Key detected: {key_name}{vk_info}")
                
                # F12またはVK123の検知
                if (hasattr(key, 'vk') and key.vk == 123) or key == pynput.keyboard.Key.f12:
                    f12_count += 1
                    logger.info(f"*** F12 DETECTED (Count: {f12_count}) ***")
                    # リスナーを停止せずに継続
                
                # F11またはVK122の検知
                elif (hasattr(key, 'vk') and key.vk == 122) or key == pynput.keyboard.Key.f11:
                    f11_count += 1
                    logger.info(f"*** F11 DETECTED (Count: {f11_count}) ***")
                
                else:
                    other_count += 1
                
                # ESCで終了
                if key == pynput.keyboard.Key.esc:
                    logger.info("ESC pressed - stopping test")
                    return False
                
            except Exception as e:
                logger.error(f"Error in key handler: {e}")
        
        logger.info("Starting continuous toggle test...")
        logger.info("Instructions:")
        logger.info("1. Press F12 multiple times (physical keyboard)")
        logger.info("2. Press G402 side button (F12) multiple times")
        logger.info("3. Press F11 as alternative")
        logger.info("4. Press ESC to stop test")
        logger.info("5. Test will automatically stop after 30 seconds")
        
        # リスナー開始
        listener = pynput.keyboard.Listener(
            on_press=on_press,
            suppress=False  # 仮想キーも検知
        )
        listener.daemon = True
        listener.start()
        
        # 30秒間テスト実行
        start_time = time.time()
        while time.time() - start_time < 30:
            if not listener.running:
                logger.warning("Listener stopped unexpectedly")
                break
            time.sleep(0.5)
        
        # リスナー停止
        listener.stop()
        
        # 結果表示
        logger.info(f"\n=== Test Results ===")
        logger.info(f"F12 detections: {f12_count}")
        logger.info(f"F11 detections: {f11_count}")
        logger.info(f"Other key detections: {other_count}")
        logger.info(f"Total detections: {f12_count + f11_count + other_count}")
        
        # 成功判定
        if f12_count > 0:
            logger.info("✅ SUCCESS: F12 key detection is working")
            if f12_count >= 2:
                logger.info("✅ SUCCESS: Continuous F12 detection confirmed")
            else:
                logger.warning("⚠️  WARNING: Only one F12 detection - try pressing multiple times")
        else:
            logger.error("❌ FAILED: No F12 detections")
        
        return f12_count >= 2
        
    except ImportError:
        logger.warning("pynput library not available - cannot test key detection")
        logger.info("Please install dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_macro_controller_toggle():
    """MacroControllerを使った実際のトグルテスト"""
    logger.info("\n=== MacroController Toggle Test ===")
    
    try:
        from core.config_manager import ConfigManager
        from core.macro_controller import MacroController
        
        # MacroController初期化
        config_manager = ConfigManager()
        macro_controller = MacroController(config_manager)
        
        logger.info("MacroController initialized successfully")
        
        # 初期状態確認
        status = macro_controller.get_status()
        logger.info(f"Initial status - Running: {status['running']}")
        
        # リスナー状態確認
        listener_status = macro_controller.get_listener_status()
        logger.info(f"Listener status: {listener_status}")
        
        # 30秒間の動作監視
        logger.info("\nMonitoring for toggle operations for 30 seconds...")
        logger.info("Try pressing G402 side button (F12) multiple times")
        
        start_time = time.time()
        last_status = status['running']
        toggle_count = 0
        
        while time.time() - start_time < 30:
            time.sleep(0.5)
            
            # ステータス変化をチェック
            current_status = macro_controller.get_status()
            if current_status['running'] != last_status:
                toggle_count += 1
                logger.info(f"*** TOGGLE {toggle_count}: {last_status} -> {current_status['running']} ***")
                last_status = current_status['running']
            
            # リスナー状態をチェック（5秒ごと）
            if int(time.time() - start_time) % 5 == 0:
                listener_status = macro_controller.get_listener_status()
                all_running = all(listener_status.values())
                if not all_running:
                    logger.warning(f"Some listeners stopped: {listener_status}")
                    logger.info("Attempting to restart listeners...")
                    macro_controller.restart_hotkey_listeners()
        
        # 結果表示
        logger.info(f"\n=== MacroController Test Results ===")
        logger.info(f"Total toggles detected: {toggle_count}")
        
        # 最終リスナー状態確認
        final_listener_status = macro_controller.get_listener_status()
        logger.info(f"Final listener status: {final_listener_status}")
        
        # クリーンアップ
        macro_controller.stop()
        
        # 成功判定
        if toggle_count >= 2:
            logger.info("✅ SUCCESS: Continuous toggle operations confirmed")
            return True
        elif toggle_count == 1:
            logger.warning("⚠️  WARNING: Only one toggle detected - may still have issues")
            return False
        else:
            logger.error("❌ FAILED: No toggle operations detected")
            return False
        
    except Exception as e:
        logger.error(f"MacroController test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    logger.info("Starting Continuous Toggle Test Suite")
    
    # 基本的なキー検知テスト
    basic_success = test_continuous_toggle()
    
    # MacroControllerでの実際のトグルテスト
    macro_success = test_macro_controller_toggle()
    
    # 最終結果
    logger.info(f"\n=== Final Results ===")
    logger.info(f"Basic key detection test: {'✅ PASSED' if basic_success else '❌ FAILED'}")
    logger.info(f"MacroController toggle test: {'✅ PASSED' if macro_success else '❌ FAILED'}")
    
    if basic_success and macro_success:
        logger.info("🎉 ALL TESTS PASSED - Continuous toggle should work properly")
    elif basic_success:
        logger.warning("⚠️  Key detection works but MacroController may have issues")
    else:
        logger.error("❌ TESTS FAILED - Check dependencies and configuration")
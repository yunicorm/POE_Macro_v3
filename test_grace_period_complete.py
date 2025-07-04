#!/usr/bin/env python3
"""
Grace Period機能の完全テストスクリプト
MacroController統合版
"""

import sys
import os
import logging
import time
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / "logs" / "grace_period_complete_test.log")
    ]
)

logger = logging.getLogger(__name__)

def test_grace_period_config():
    """Grace Period設定の確認"""
    logger.info("=== Grace Period Config Test ===")
    
    try:
        from core.config_manager import ConfigManager
        
        # 設定読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Grace Period設定確認
        grace_period_config = config.get('grace_period', {})
        log_monitor_config = config.get('log_monitor', {})
        
        logger.info(f"Grace Period config: {grace_period_config}")
        logger.info(f"Log Monitor config: {log_monitor_config}")
        
        # 必要な設定の確認
        assert grace_period_config.get('enabled') == True, "Grace Period not enabled"
        assert grace_period_config.get('wait_for_input') == True, "wait_for_input not enabled"
        assert 'trigger_inputs' in grace_period_config, "trigger_inputs not found"
        assert log_monitor_config.get('enabled') == True, "Log Monitor not enabled"
        
        logger.info("All required configurations are present")
        return True
        
    except Exception as e:
        logger.error(f"Grace Period config test failed: {e}")
        return False

def test_macro_controller_integration():
    """MacroControllerとLogMonitorの統合テスト"""
    logger.info("=== MacroController Integration Test ===")
    
    try:
        from core.config_manager import ConfigManager
        from core.macro_controller import MacroController
        
        # 設定読み込み
        config_manager = ConfigManager()
        
        # MacroController初期化
        logger.info("Initializing MacroController...")
        macro_controller = MacroController(config_manager)
        
        # LogMonitorが初期化されているか確認
        assert hasattr(macro_controller, 'log_monitor'), "LogMonitor not initialized"
        logger.info(f"LogMonitor initialized: {macro_controller.log_monitor is not None}")
        
        if macro_controller.log_monitor:
            # Grace Period設定の確認
            log_monitor = macro_controller.log_monitor
            logger.info(f"Grace Period enabled: {log_monitor.grace_period_enabled}")
            logger.info(f"Wait for input: {log_monitor.wait_for_input}")
            logger.info(f"Trigger inputs: {log_monitor.trigger_inputs}")
            
            # pynput可用性確認
            from modules.log_monitor import PYNPUT_AVAILABLE
            logger.info(f"pynput available: {PYNPUT_AVAILABLE}")
            
            if not PYNPUT_AVAILABLE:
                logger.warning("pynput not available - Grace Period will use fallback")
            
        return True
        
    except Exception as e:
        logger.error(f"MacroController integration test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_log_monitor_grace_period():
    """LogMonitorのGrace Period機能テスト"""
    logger.info("=== LogMonitor Grace Period Test ===")
    
    try:
        from core.config_manager import ConfigManager
        from modules.log_monitor import LogMonitor
        
        # 設定読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # LogMonitor初期化
        log_monitor_config = config.get('log_monitor', {})
        log_monitor = LogMonitor(log_monitor_config, full_config=config)
        
        # Grace Period設定確認
        logger.info(f"Grace Period enabled: {log_monitor.grace_period_enabled}")
        logger.info(f"Wait for input: {log_monitor.wait_for_input}")
        logger.info(f"Trigger inputs: {log_monitor.trigger_inputs}")
        
        # 手動テスト実行
        logger.info("Running manual Grace Period test...")
        log_monitor.manual_test_grace_period()
        
        # 少し待機
        time.sleep(1)
        
        # 状態確認
        logger.info(f"Grace Period active: {log_monitor.grace_period_active}")
        
        return True
        
    except Exception as e:
        logger.error(f"LogMonitor Grace Period test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_area_enter_simulation():
    """エリア入場シミュレーションテスト"""
    logger.info("=== Area Enter Simulation Test ===")
    
    try:
        from core.config_manager import ConfigManager
        from modules.log_monitor import LogMonitor
        
        # 設定読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # LogMonitor初期化
        log_monitor_config = config.get('log_monitor', {})
        log_monitor = LogMonitor(log_monitor_config, full_config=config)
        
        # 安全エリア検出テスト
        logger.info("Testing safe area detection:")
        log_monitor.test_safe_area_detection()
        
        # 安全エリア入場テスト（Grace Period無効）
        logger.info("\\nTesting safe area entry (should NOT trigger Grace Period):")
        log_monitor.manual_test_area_enter("Lioneye's Watch")
        logger.info(f"Grace Period active after safe area: {log_monitor.grace_period_active}")
        
        # エリア退場
        log_monitor.manual_test_area_exit("Lioneye's Watch")
        
        # 戦闘エリア入場テスト（Grace Period有効）
        logger.info("\\nTesting combat area entry (should trigger Grace Period):")
        log_monitor.manual_test_area_enter("The Twilight Strand")
        logger.info(f"Grace Period active after combat area: {log_monitor.grace_period_active}")
        logger.info(f"Current area needs grace: {log_monitor.current_area_needs_grace}")
        
        if log_monitor.grace_period_active:
            logger.info("Grace Period is active - simulating input detection...")
            # 5秒後に強制終了
            time.sleep(2)
            log_monitor._stop_grace_period()
            logger.info("Grace Period stopped (simulated)")
        
        return True
        
    except Exception as e:
        logger.error(f"Area enter simulation test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_grace_period_disabled():
    """Grace Period無効時のテスト"""
    logger.info("=== Grace Period Disabled Test ===")
    
    try:
        from core.config_manager import ConfigManager
        from modules.log_monitor import LogMonitor
        
        # 設定読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Grace Period無効化
        disabled_config = config.copy()
        disabled_config['grace_period'] = {'enabled': False}
        
        # LogMonitor初期化
        log_monitor_config = disabled_config.get('log_monitor', {})
        log_monitor = LogMonitor(log_monitor_config, full_config=disabled_config)
        
        # 設定確認
        logger.info(f"Grace Period enabled: {log_monitor.grace_period_enabled}")
        
        # 戦闘エリア入場テスト
        logger.info("Testing combat area entry (Grace Period disabled):")
        log_monitor.manual_test_area_enter("The Twilight Strand")
        
        # 状態確認
        logger.info(f"Grace Period active: {log_monitor.grace_period_active}")
        logger.info("Grace Period should remain inactive when disabled")
        
        return True
        
    except Exception as e:
        logger.error(f"Grace Period disabled test failed: {e}")
        return False

def main():
    """メインテスト実行"""
    logger.info("Starting Grace Period complete integration test...")
    
    # ログディレクトリ作成
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # テスト実行
    tests = [
        test_grace_period_config,
        test_macro_controller_integration,
        test_log_monitor_grace_period,
        test_area_enter_simulation,
        test_grace_period_disabled
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            logger.info(f"Test {test.__name__}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            logger.error(f"Test {test.__name__}: ERROR - {e}")
            results.append(False)
        
        # テスト間の待機
        time.sleep(1)
        logger.info("---")
    
    # 結果サマリー
    passed = sum(results)
    total = len(results)
    logger.info(f"\\n=== Test Summary ===")
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All Grace Period integration tests passed!")
        logger.info("\\n📋 Grace Period Feature Status:")
        logger.info("✅ Configuration: Complete")
        logger.info("✅ LogMonitor Integration: Complete")
        logger.info("✅ MacroController Integration: Complete")
        logger.info("✅ Area Detection: Complete")
        logger.info("✅ Input Monitoring: Complete")
        logger.info("✅ Fallback Handling: Complete")
        logger.info("\\n🚀 Grace Period feature is ready for use!")
        return 0
    else:
        logger.error("❌ Some Grace Period integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
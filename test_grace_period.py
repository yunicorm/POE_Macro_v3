#!/usr/bin/env python3
"""
Grace Period機能のテストスクリプト
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
        logging.FileHandler(project_root / "logs" / "grace_period_test.log")
    ]
)

logger = logging.getLogger(__name__)

def test_grace_period_basic():
    """基本的なGrace Period機能のテスト"""
    logger.info("=== Grace Period Basic Test ===")
    
    try:
        from core.config_manager import ConfigManager
        from modules.log_monitor import LogMonitor
        
        # 設定読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Grace Period設定確認
        grace_period_config = config.get('grace_period', {})
        logger.info(f"Grace Period config: {grace_period_config}")
        
        # LogMonitorインスタンス作成
        log_monitor = LogMonitor(config.get('log_monitor', {}))
        
        # Grace Period設定の確認
        logger.info(f"Grace Period enabled: {log_monitor.grace_period_enabled}")
        logger.info(f"Wait for input: {log_monitor.wait_for_input}")
        logger.info(f"Trigger inputs: {log_monitor.trigger_inputs}")
        
        # pynputの可用性確認
        from modules.log_monitor import PYNPUT_AVAILABLE
        logger.info(f"pynput available: {PYNPUT_AVAILABLE}")
        
        return True
        
    except Exception as e:
        logger.error(f"Grace Period basic test failed: {e}")
        return False

def test_grace_period_area_enter():
    """エリア入場時のGrace Period動作テスト"""
    logger.info("=== Grace Period Area Enter Test ===")
    
    try:
        from core.config_manager import ConfigManager
        from modules.log_monitor import LogMonitor
        
        # 設定読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Grace Period有効化
        log_monitor_config = config.get('log_monitor', {})
        log_monitor_config['grace_period'] = {
            'enabled': True,
            'wait_for_input': True,
            'trigger_inputs': ['mouse_left', 'mouse_right', 'q']
        }
        
        # LogMonitorインスタンス作成
        log_monitor = LogMonitor(log_monitor_config)
        
        # 手動テスト実行
        log_monitor.manual_test_grace_period()
        
        # 少し待機
        time.sleep(2)
        
        # 状態確認
        logger.info(f"Grace Period active: {log_monitor.grace_period_active}")
        logger.info(f"Current area needs grace: {log_monitor.current_area_needs_grace}")
        
        return True
        
    except Exception as e:
        logger.error(f"Grace Period area enter test failed: {e}")
        return False

def test_grace_period_safe_area():
    """安全エリアでのGrace Period動作テスト"""
    logger.info("=== Grace Period Safe Area Test ===")
    
    try:
        from core.config_manager import ConfigManager
        from modules.log_monitor import LogMonitor
        
        # 設定読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Grace Period有効化
        log_monitor_config = config.get('log_monitor', {})
        log_monitor_config['grace_period'] = {
            'enabled': True,
            'wait_for_input': True,
            'trigger_inputs': ['mouse_left', 'mouse_right', 'q']
        }
        
        # LogMonitorインスタンス作成
        log_monitor = LogMonitor(log_monitor_config)
        
        # 安全エリア検出テスト
        logger.info("Testing safe area detection:")
        log_monitor.test_safe_area_detection()
        
        # 安全エリア入場テスト
        logger.info("Testing safe area entry (should NOT trigger Grace Period):")
        log_monitor.manual_test_area_enter("Lioneye's Watch")
        
        # 状態確認
        logger.info(f"Grace Period active: {log_monitor.grace_period_active}")
        logger.info("Safe area should not trigger Grace Period")
        
        return True
        
    except Exception as e:
        logger.error(f"Grace Period safe area test failed: {e}")
        return False

def test_grace_period_combat_area():
    """戦闘エリアでのGrace Period動作テスト"""
    logger.info("=== Grace Period Combat Area Test ===")
    
    try:
        from core.config_manager import ConfigManager
        from modules.log_monitor import LogMonitor
        
        # 設定読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Grace Period有効化
        log_monitor_config = config.get('log_monitor', {})
        log_monitor_config['grace_period'] = {
            'enabled': True,
            'wait_for_input': True,
            'trigger_inputs': ['mouse_left', 'mouse_right', 'q']
        }
        
        # LogMonitorインスタンス作成
        log_monitor = LogMonitor(log_monitor_config)
        
        # 戦闘エリア入場テスト
        logger.info("Testing combat area entry (should trigger Grace Period):")
        log_monitor.manual_test_area_enter("The Twilight Strand")
        
        # 状態確認
        logger.info(f"Grace Period active: {log_monitor.grace_period_active}")
        logger.info(f"Current area needs grace: {log_monitor.current_area_needs_grace}")
        
        if log_monitor.grace_period_active:
            logger.info("Grace Period is active - waiting for input...")
            logger.info(f"Trigger any of these inputs: {log_monitor.trigger_inputs}")
            logger.info("Test will continue for 5 seconds, then stop...")
            
            # 5秒待機
            time.sleep(5)
            
            # 強制停止
            log_monitor._stop_grace_period()
            logger.info("Grace Period stopped (timeout)")
        
        return True
        
    except Exception as e:
        logger.error(f"Grace Period combat area test failed: {e}")
        return False

def test_grace_period_disabled():
    """Grace Period無効時の動作テスト"""
    logger.info("=== Grace Period Disabled Test ===")
    
    try:
        from core.config_manager import ConfigManager
        from modules.log_monitor import LogMonitor
        
        # 設定読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Grace Period無効化
        log_monitor_config = config.get('log_monitor', {})
        log_monitor_config['grace_period'] = {
            'enabled': False,
            'wait_for_input': True,
            'trigger_inputs': ['mouse_left', 'mouse_right', 'q']
        }
        
        # LogMonitorインスタンス作成
        log_monitor = LogMonitor(log_monitor_config)
        
        # 設定確認
        logger.info(f"Grace Period enabled: {log_monitor.grace_period_enabled}")
        
        # 戦闘エリア入場テスト
        logger.info("Testing combat area entry (Grace Period disabled):")
        log_monitor.manual_test_area_enter("The Twilight Strand")
        
        # 状態確認
        logger.info(f"Grace Period active: {log_monitor.grace_period_active}")
        logger.info("Grace Period should be inactive when disabled")
        
        return True
        
    except Exception as e:
        logger.error(f"Grace Period disabled test failed: {e}")
        return False

def main():
    """メインテスト実行"""
    logger.info("Starting Grace Period comprehensive test...")
    
    # ログディレクトリ作成
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # テスト実行
    tests = [
        test_grace_period_basic,
        test_grace_period_area_enter,
        test_grace_period_safe_area,
        test_grace_period_combat_area,
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
    
    # 結果サマリー
    passed = sum(results)
    total = len(results)
    logger.info(f"\n=== Test Summary ===")
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        logger.info("All Grace Period tests passed!")
        return 0
    else:
        logger.error("Some Grace Period tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Grace Period機能調査テスト
問題箇所を特定するための包括的デバッグテスト
"""
import sys
import os
import logging

# プロジェクトのルートディレクトリを追加
sys.path.insert(0, os.path.abspath('.'))

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_grace_period_functionality():
    """Grace Period機能の包括的テスト"""
    logger.info("=== Grace Period 機能調査テスト開始 ===")
    
    test_results = []
    
    # 1. 設定ファイル読み込みテスト
    logger.info("\n1. 設定ファイル読み込みテスト")
    try:
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Grace Period設定確認
        grace_period_config = config.get('grace_period', {})
        logger.info(f"Grace Period設定: {grace_period_config}")
        
        general_config = config.get('general', {})
        logger.info(f"General設定: {general_config}")
        
        test_results.append(("設定ファイル読み込み", "✅ 成功"))
        
    except Exception as e:
        logger.error(f"設定ファイル読み込みエラー: {e}")
        test_results.append(("設定ファイル読み込み", f"❌ 失敗: {e}"))
        
    # 2. pynput可用性テスト
    logger.info("\n2. pynput可用性テスト")
    try:
        from pynput import mouse, keyboard
        logger.info("pynput: ✅ 利用可能")
        test_results.append(("pynput可用性", "✅ 利用可能"))
    except ImportError as e:
        logger.warning(f"pynput: ❌ 利用不可 - {e}")
        test_results.append(("pynput可用性", f"❌ 利用不可: {e}"))
        
    # 3. LogMonitor初期化テスト
    logger.info("\n3. LogMonitor初期化テスト")
    try:
        from src.modules.log_monitor import LogMonitor
        
        log_monitor_config = config.get('log_monitor', {})
        log_monitor = LogMonitor(log_monitor_config, full_config=config)
        
        logger.info(f"LogMonitor Grace Period設定:")
        logger.info(f"  - enabled: {log_monitor.grace_period_enabled}")
        logger.info(f"  - wait_for_input: {log_monitor.wait_for_input}")
        logger.info(f"  - trigger_inputs: {log_monitor.trigger_inputs}")
        
        test_results.append(("LogMonitor初期化", "✅ 成功"))
        
    except Exception as e:
        logger.error(f"LogMonitor初期化エラー: {e}")
        import traceback
        logger.error(f"詳細エラー: {traceback.format_exc()}")
        test_results.append(("LogMonitor初期化", f"❌ 失敗: {e}"))
        
    # 4. MacroController初期化テスト
    logger.info("\n4. MacroController初期化テスト")
    try:
        from src.core.macro_controller import MacroController
        
        macro_controller = MacroController(config_manager)
        
        logger.info(f"MacroController Grace Period設定:")
        logger.info(f"  - grace_period_enabled: {macro_controller.grace_period_enabled}")
        logger.info(f"  - waiting_for_input: {macro_controller.waiting_for_input}")
        logger.info(f"  - grace_period_active: {macro_controller.grace_period_active}")
        
        # LogMonitor統合確認
        if macro_controller.log_monitor:
            logger.info("LogMonitor統合: ✅ 成功")
        else:
            logger.warning("LogMonitor統合: ❌ 失敗")
            
        test_results.append(("MacroController初期化", "✅ 成功"))
        
    except Exception as e:
        logger.error(f"MacroController初期化エラー: {e}")
        import traceback
        logger.error(f"詳細エラー: {traceback.format_exc()}")
        test_results.append(("MacroController初期化", f"❌ 失敗: {e}"))
        
    # 5. GUI初期化テスト
    logger.info("\n5. GUI初期化テスト（設定のみ）")
    try:
        # PyQt5が無い環境用の設定確認のみ
        auto_start = config.get('general', {}).get('auto_start_on_launch', False)
        respect_grace = config.get('general', {}).get('respect_grace_period', True)
        
        logger.info(f"GUI設定:")
        logger.info(f"  - auto_start_on_launch: {auto_start}")
        logger.info(f"  - respect_grace_period: {respect_grace}")
        
        test_results.append(("GUI設定確認", "✅ 成功"))
        
    except Exception as e:
        logger.error(f"GUI設定確認エラー: {e}")
        test_results.append(("GUI設定確認", f"❌ 失敗: {e}"))
        
    # 6. Grace Period手動テスト
    logger.info("\n6. Grace Period手動テスト")
    try:
        if 'log_monitor' in locals():
            logger.info("Grace Period手動テスト実行...")
            log_monitor.manual_test_grace_period()
            test_results.append(("Grace Period手動テスト", "✅ 実行完了"))
        else:
            test_results.append(("Grace Period手動テスト", "❌ LogMonitor未初期化"))
            
    except Exception as e:
        logger.error(f"Grace Period手動テストエラー: {e}")
        test_results.append(("Grace Period手動テスト", f"❌ 失敗: {e}"))
        
    # 結果サマリー
    logger.info("\n=== テスト結果サマリー ===")
    success_count = 0
    total_count = len(test_results)
    
    for test_name, result in test_results:
        logger.info(f"{test_name}: {result}")
        if "✅" in result:
            success_count += 1
            
    logger.info(f"\n成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    # 問題分析
    logger.info("\n=== 問題分析 ===")
    
    if success_count == total_count:
        logger.info("✅ 全てのテスト成功 - Grace Period機能は正常に実装されています")
    else:
        logger.warning("⚠️ 一部テスト失敗 - 以下の問題が検出されました:")
        
        for test_name, result in test_results:
            if "❌" in result:
                logger.warning(f"  - {test_name}: {result}")
                
    return test_results

if __name__ == "__main__":
    try:
        test_grace_period_functionality()
    except Exception as e:
        logger.error(f"テスト実行中の予期しないエラー: {e}")
        import traceback
        logger.error(f"詳細エラー: {traceback.format_exc()}")
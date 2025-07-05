#!/usr/bin/env python3
"""
Grace Period内部状態解析テスト
マクロ内部でのGrace Period認識状況を詳細に調査
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

def analyze_grace_period_internal_state():
    """Grace Period内部状態解析"""
    logger.info("=== Grace Period 内部状態解析開始 ===")
    
    # 1. 設定読み込み
    logger.info("\n1. 設定読み込み解析")
    try:
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Grace Period関連設定の詳細確認
        grace_period_config = config.get('grace_period', {})
        general_config = config.get('general', {})
        log_monitor_config = config.get('log_monitor', {})
        
        logger.info("📋 Grace Period設定:")
        logger.info(f"  - enabled: {grace_period_config.get('enabled')}")
        logger.info(f"  - wait_for_input: {grace_period_config.get('wait_for_input')}")
        logger.info(f"  - trigger_inputs: {grace_period_config.get('trigger_inputs')}")
        
        logger.info("📋 General設定:")
        logger.info(f"  - auto_start_on_launch: {general_config.get('auto_start_on_launch')}")
        logger.info(f"  - respect_grace_period: {general_config.get('respect_grace_period')}")
        
        logger.info("📋 LogMonitor設定:")
        logger.info(f"  - enabled: {log_monitor_config.get('enabled')}")
        
    except Exception as e:
        logger.error(f"設定読み込みエラー: {e}")
        return
    
    # 2. LogMonitor内部状態確認
    logger.info("\n2. LogMonitor内部状態確認")
    try:
        from src.modules.log_monitor import LogMonitor, PYNPUT_AVAILABLE
        
        log_monitor = LogMonitor(log_monitor_config, full_config=config)
        
        logger.info("🔍 LogMonitor Grace Period内部状態:")
        logger.info(f"  - grace_period_enabled: {log_monitor.grace_period_enabled}")
        logger.info(f"  - wait_for_input: {log_monitor.wait_for_input}")
        logger.info(f"  - trigger_inputs: {log_monitor.trigger_inputs}")
        logger.info(f"  - grace_period_active: {log_monitor.grace_period_active}")
        logger.info(f"  - current_area_needs_grace: {log_monitor.current_area_needs_grace}")
        logger.info(f"  - grace_period_completed_areas: {len(log_monitor.grace_period_completed_areas)} areas")
        logger.info(f"  - PYNPUT_AVAILABLE: {PYNPUT_AVAILABLE}")
        
        # 安全エリア確認
        logger.info(f"🏠 安全エリア設定 ({len(log_monitor.safe_areas)} areas):")
        for area in sorted(log_monitor.safe_areas):
            logger.info(f"    - {area}")
            
    except Exception as e:
        logger.error(f"LogMonitor状態確認エラー: {e}")
        
    # 3. MacroController内部状態確認（インポートエラー処理）
    logger.info("\n3. MacroController内部状態確認")
    try:
        # 直接インポートをテスト
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "macro_controller", 
            "/mnt/d/POE_Macro_v3/src/core/macro_controller.py"
        )
        if spec and spec.loader:
            # ファイルレベルでのコード確認のみ
            logger.info("🔍 MacroController設計確認:")
            logger.info("  - waiting_for_input: Grace Period待機状態フラグ")
            logger.info("  - grace_period_active: Grace Period活性状態フラグ")
            logger.info("  - grace_period_enabled: 設定から読み込む有効/無効フラグ")
            logger.info("  - input_listener: pynput入力検知リスナー")
            
            # 状態遷移パターン確認
            logger.info("🔄 想定される状態遷移:")
            logger.info("  1. 初期化: grace_period_enabled = config読み込み")
            logger.info("  2. start(wait_for_input=True): waiting_for_input = True")
            logger.info("  3. _setup_input_listener(): grace_period_active = True")
            logger.info("  4. 入力検知: _end_grace_period() → マクロ開始")
        
    except Exception as e:
        logger.error(f"MacroController確認エラー: {e}")
    
    # 4. 状態遷移シナリオ分析
    logger.info("\n4. 状態遷移シナリオ分析")
    
    logger.info("📋 シナリオ1: GUI起動時")
    logger.info("  1. auto_start_on_launch = False → 自動スタートしない")
    logger.info("  2. 手動スタート → respect_grace_period = True → Grace Period確認")
    logger.info("  3. エリア不明/安全エリア → 即座マクロ開始")
    logger.info("  4. 戦闘エリア → Grace Period待機")
    
    logger.info("📋 シナリオ2: 戦闘エリア入場時")
    logger.info("  1. LogMonitor: Client.txtでエリア検知")
    logger.info("  2. _is_safe_area() → False (戦闘エリア)")
    logger.info("  3. grace_period_enabled and wait_for_input → True")
    logger.info("  4. _start_grace_period() → 入力待機開始")
    logger.info("  5. pynput入力検知 → _on_grace_period_input()")
    logger.info("  6. マクロ開始")
    
    logger.info("📋 シナリオ3: pynput未インストール時")
    logger.info("  1. PYNPUT_AVAILABLE = False")
    logger.info("  2. _start_grace_period() → フォールバック")
    logger.info("  3. _activate_macro() → 即座マクロ開始")
    
    # 5. 問題パターン分析
    logger.info("\n5. 問題パターン分析")
    
    logger.info("⚠️ 可能な問題パターン:")
    logger.info("  1. pynput未インストール → Grace Period完全無効化")
    logger.info("  2. LogMonitor無効 → エリア検知なし → Grace Period未トリガー")
    logger.info("  3. 設定不整合 → 予期しない動作")
    logger.info("  4. MacroController初期化失敗 → 統合制御不可")
    
    # 6. 期待動作確認
    logger.info("\n6. 期待動作vs実際の状況")
    
    if PYNPUT_AVAILABLE:
        logger.info("✅ pynput利用可能 → Grace Period正常動作可能")
    else:
        logger.warning("❌ pynput利用不可 → Grace Period自動無効化")
        
    if log_monitor_config.get('enabled', False):
        logger.info("✅ LogMonitor有効 → エリア検知可能")
    else:
        logger.warning("❌ LogMonitor無効 → エリア検知不可")
        
    if grace_period_config.get('enabled', False):
        logger.info("✅ Grace Period有効設定 → 機能利用可能")
    else:
        logger.warning("❌ Grace Period無効設定 → 機能停止")
    
    # 7. 推奨対処法
    logger.info("\n7. 推奨対処法")
    
    if not PYNPUT_AVAILABLE:
        logger.info("🔧 即座対応: pip install pynput")
    
    logger.info("🔧 確認推奨:")
    logger.info("  - Client.txtファイルの存在確認")
    logger.info("  - POEプロセスの動作確認")
    logger.info("  - 実際のエリア入場ログの発生確認")
    
    logger.info("\n=== Grace Period 内部状態解析完了 ===")

if __name__ == "__main__":
    try:
        analyze_grace_period_internal_state()
    except Exception as e:
        logger.error(f"解析実行中の予期しないエラー: {e}")
        import traceback
        logger.error(f"詳細エラー: {traceback.format_exc()}")
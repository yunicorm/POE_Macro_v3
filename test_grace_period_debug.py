#!/usr/bin/env python3
"""
Grace Period動作デバッグテスト
戦闘エリア入場時に即座にマクロが開始される問題を特定する
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import logging
from core.config_manager import ConfigManager
from modules.log_monitor import LogMonitor

# ログレベルをDEBUGに設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_grace_period_logic():
    """Grace Period動作ロジックの詳細テスト"""
    print("=== Grace Period動作デバッグテスト ===")
    
    # 設定読み込み
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    print(f"\n1. 設定確認:")
    print(f"   grace_period section: {config.get('grace_period', 'NOT FOUND')}")
    print(f"   log_monitor section: {config.get('log_monitor', 'NOT FOUND')}")
    
    # LogMonitor初期化
    log_monitor_config = config.get('log_monitor', {})
    full_config = config
    
    print(f"\n2. LogMonitor初期化:")
    print(f"   log_monitor_config: {log_monitor_config}")
    print(f"   full_config grace_period: {full_config.get('grace_period', 'NOT FOUND')}")
    
    # LogMonitorを初期化（MacroControllerなしで）
    log_monitor = LogMonitor(log_monitor_config, macro_controller=None, full_config=full_config)
    
    print(f"\n3. LogMonitor Grace Period設定:")
    print(f"   grace_period_enabled: {log_monitor.grace_period_enabled}")
    print(f"   wait_for_input: {log_monitor.wait_for_input}")
    print(f"   trigger_inputs: {log_monitor.trigger_inputs}")
    print(f"   PYNPUT_AVAILABLE: {getattr(log_monitor, 'PYNPUT_AVAILABLE', 'Unknown')}")
    
    print(f"\n4. 戦闘エリア入場シミュレーション:")
    
    # 戦闘エリアの入場をシミュレート
    test_area = "The Twilight Strand"  # 戦闘エリア
    print(f"   エリア: {test_area}")
    print(f"   安全エリア判定: {log_monitor._is_safe_area(test_area)}")
    
    # _handle_area_enter の処理をステップ実行
    print(f"\n5. _handle_area_enter処理詳細:")
    
    # 現在の状態を確認
    print(f"   - in_area (before): {log_monitor.in_area}")
    print(f"   - grace_period_enabled: {log_monitor.grace_period_enabled}")
    print(f"   - wait_for_input: {log_monitor.wait_for_input}")
    print(f"   - grace_period_active (before): {log_monitor.grace_period_active}")
    
    # 手動でエリア入場処理を実行
    print(f"\n6. 手動エリア入場テスト:")
    
    # in_area状態をリセット
    log_monitor.in_area = False
    log_monitor.current_area = None
    log_monitor.grace_period_active = False
    
    # エリア入場処理を実行
    log_monitor.manual_test_area_enter(test_area)
    
    print(f"\n7. エリア入場後の状態:")
    print(f"   - in_area (after): {log_monitor.in_area}")
    print(f"   - current_area: {log_monitor.current_area}")
    print(f"   - grace_period_active (after): {log_monitor.grace_period_active}")
    print(f"   - current_area_needs_grace: {log_monitor.current_area_needs_grace}")
    
    # Grace Period条件の詳細チェック
    print(f"\n8. Grace Period条件詳細チェック:")
    print(f"   - 条件1 (grace_period_enabled): {log_monitor.grace_period_enabled}")
    print(f"   - 条件2 (wait_for_input): {log_monitor.wait_for_input}")
    print(f"   - 条件3 (not _is_safe_area): {not log_monitor._is_safe_area(test_area)}")
    
    # 条件判定の結果
    grace_period_should_start = (
        log_monitor.grace_period_enabled and 
        log_monitor.wait_for_input and 
        not log_monitor._is_safe_area(test_area)
    )
    print(f"   - Grace Period should start: {grace_period_should_start}")
    
    # 実際の_handle_area_enter内のロジックを確認
    print(f"\n9. _handle_area_enter内のロジック詳細:")
    
    # LogMonitorの_handle_area_enter内で使用される条件をチェック
    area_id = f"{test_area}_{int(log_monitor.stats.get('last_area_change', 0) // 3600)}"
    print(f"   - area_id: {area_id}")
    print(f"   - grace_period_completed_areas: {log_monitor.grace_period_completed_areas}")
    print(f"   - area previously completed: {area_id in log_monitor.grace_period_completed_areas}")

if __name__ == "__main__":
    test_grace_period_logic()
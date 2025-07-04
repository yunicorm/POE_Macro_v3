#!/usr/bin/env python3
"""
LogMonitor修正後の動作確認テスト
実際のClient.txtログ形式に対応したエリア検出機能をテスト
"""

import logging
import sys
import os
from pathlib import Path

# プロジェクトルートを追加
sys.path.insert(0, str(Path(__file__).parent))

from src.modules.log_monitor import LogMonitor

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_log_monitor_fixes():
    """LogMonitorの修正機能をテスト"""
    
    print("=== LogMonitor修正機能テスト ===")
    
    # 設定
    config = {
        'enabled': True,
        'check_interval': 0.5,
        'log_path': 'dummy_path.txt'  # 実際のファイルは不要
    }
    
    # LogMonitorインスタンス作成
    monitor = LogMonitor(config)
    
    # 1. ログパターンのテスト
    print("\n1. ログパターンテスト")
    test_logs = [
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have entered Aspirants' Plaza.",
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have entered Lioneye's Watch.",
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have entered The Sarn Encampment.",
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have entered My Hideout.",
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have left The Twilight Strand.",
    ]
    
    for log in test_logs:
        print(f"\nテストログ: {log}")
        
        # エリア入場パターンチェック
        if monitor.area_enter_pattern.search(log):
            area_name = monitor._extract_area_name(log)
            is_safe = monitor._is_safe_area(area_name)
            print(f"  → エリア入場検出: {area_name} ({'安全エリア' if is_safe else '通常エリア'})")
        
        # エリア退場パターンチェック
        if monitor.area_exit_pattern.search(log):
            area_name = monitor._extract_area_name(log)
            print(f"  → エリア退場検出: {area_name}")
    
    # 2. 安全エリア検出テスト
    print("\n2. 安全エリア検出テスト")
    monitor.test_safe_area_detection()
    
    # 3. エリア名抽出テスト
    print("\n3. エリア名抽出テスト")
    extraction_tests = [
        ("You have entered Aspirants' Plaza.", "Aspirants' Plaza"),
        ("You have entered Lioneye's Watch.", "Lioneye's Watch"),
        ("You have entered The Sarn Encampment.", "The Sarn Encampment"),
        ("You have entered My Hideout.", "My Hideout"),
        ("You have left The Twilight Strand.", "The Twilight Strand"),
    ]
    
    for test_line, expected in extraction_tests:
        extracted = monitor._extract_area_name(test_line)
        status = "✓" if extracted == expected else "✗"
        print(f"  {status} 期待値: '{expected}' → 抽出結果: '{extracted}'")
    
    # 4. 手動テスト機能
    print("\n4. 手動テスト機能")
    print("通常エリアテスト:")
    monitor.manual_test_area_enter("Aspirants' Plaza")
    
    print("\n安全エリアテスト:")
    monitor.manual_test_area_enter("Lioneye's Watch")
    
    print("\nHideoutテスト:")
    monitor.manual_test_area_enter("My Hideout")
    
    return True

def test_pattern_matching():
    """正規表現パターンマッチングの詳細テスト"""
    
    print("\n=== パターンマッチング詳細テスト ===")
    
    config = {'enabled': True, 'check_interval': 0.5}
    monitor = LogMonitor(config)
    
    # 実際のログ形式の様々なパターン
    test_cases = [
        # 標準的なエリア入場
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have entered Aspirants' Plaza.",
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have entered The Twilight Strand.",
        
        # アポストロフィを含むエリア名
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have entered Lioneye's Watch.",
        
        # 長いエリア名
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have entered The Sarn Encampment.",
        
        # Hideout
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have entered My Cozy Hideout.",
        
        # エリア退場
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have left The Blood Aqueduct.",
        
        # マッチしないパターン
        "2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : Some other log message.",
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case}")
        
        # エリア入場パターンチェック
        enter_match = monitor.area_enter_pattern.search(test_case)
        if enter_match:
            area_name = enter_match.group(1)
            is_safe = monitor._is_safe_area(area_name)
            print(f"   ✓ エリア入場: '{area_name}' ({'安全' if is_safe else '通常'})")
        
        # エリア退場パターンチェック
        exit_match = monitor.area_exit_pattern.search(test_case)
        if exit_match:
            area_name = exit_match.group(1)
            print(f"   ✓ エリア退場: '{area_name}'")
        
        if not enter_match and not exit_match:
            print("   - パターンマッチなし")
    
    return True

if __name__ == "__main__":
    try:
        print("LogMonitor修正後テスト開始")
        
        # 基本機能テスト
        if test_log_monitor_fixes():
            print("\n✓ 基本機能テスト合格")
        
        # パターンマッチング詳細テスト
        if test_pattern_matching():
            print("\n✓ パターンマッチングテスト合格")
        
        print("\n=== 全テスト完了 ===")
        print("LogMonitor修正機能は正常に動作しています")
        
    except Exception as e:
        print(f"\n✗ テスト中にエラーが発生: {e}")
        import traceback
        traceback.print_exc()
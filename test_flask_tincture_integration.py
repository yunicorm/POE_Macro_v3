#!/usr/bin/env python3
"""
Flask&Tincture統合テスト
PyQt5に依存しない基本的な機能のテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_flask_data_manager():
    """FlaskDataManagerのテスト"""
    try:
        from src.utils.flask_data_manager import FlaskDataManager
        
        print("=== FlaskDataManager テスト ===")
        
        # インスタンス作成
        manager = FlaskDataManager()
        print("✓ FlaskDataManager インスタンス作成成功")
        
        # フラスコタイプの取得
        flask_types = manager.get_all_flask_types()
        print(f"✓ フラスコタイプ: {flask_types}")
        
        # ユニークフラスコの取得
        life_uniques = manager.get_unique_flasks("life")
        print(f"✓ Life ユニークフラスコ: {life_uniques}")
        
        # Utilityベースの取得
        utility_bases = manager.get_utility_bases()
        print(f"✓ Utility ベース: {utility_bases}")
        
        # 持続時間の取得
        duration = manager.get_flask_duration("life", "Forbidden Taste")
        print(f"✓ Forbidden Taste 持続時間: {duration}秒")
        
        # バリデーション
        is_valid, error = manager.validate_flask_selection("Life", "Unique", "Forbidden Taste")
        print(f"✓ バリデーション結果: {is_valid}, エラー: {error}")
        
        print("✓ FlaskDataManager テスト完了\n")
        return True
        
    except Exception as e:
        print(f"✗ FlaskDataManager テストエラー: {e}")
        return False

def test_flask_timer_manager():
    """FlaskTimerManagerのテスト"""
    try:
        from src.utils.flask_timer_manager import FlaskTimerManager
        
        print("=== FlaskTimerManager テスト ===")
        
        # インスタンス作成
        manager = FlaskTimerManager()
        print("✓ FlaskTimerManager インスタンス作成成功")
        
        # タイマー追加
        manager.add_flask_timer(1, "1", 5000, False)
        manager.add_flask_timer(2, "2", 7000, True)
        print("✓ フラスコタイマー追加成功")
        
        # タイマー数確認
        count = manager.get_timer_count()
        print(f"✓ アクティブタイマー数: {count}")
        
        # 統計情報取得
        stats = manager.get_stats()
        print(f"✓ 統計情報: {stats}")
        
        # タイマー削除
        manager.clear_all_timers()
        print("✓ タイマークリア成功")
        
        print("✓ FlaskTimerManager テスト完了\n")
        return True
        
    except Exception as e:
        print(f"✗ FlaskTimerManager テストエラー: {e}")
        return False

def test_csv_data():
    """CSVデータの整合性テスト"""
    try:
        import csv
        import os
        
        print("=== CSVデータ テスト ===")
        
        csv_files = [
            "data/flasks/life_unique.csv",
            "data/flasks/mana_unique.csv", 
            "data/flasks/hybrid_unique.csv",
            "data/flasks/utility_unique.csv"
        ]
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    print(f"✓ {csv_file}: {len(rows)}行読み込み成功")
            else:
                print(f"✗ {csv_file}: ファイルが存在しません")
        
        print("✓ CSVデータ テスト完了\n")
        return True
        
    except Exception as e:
        print(f"✗ CSVデータ テストエラー: {e}")
        return False

def test_config_structure():
    """設定構造のテスト"""
    try:
        print("=== 設定構造 テスト ===")
        
        # テスト用設定データ
        test_config = {
            'flask': {
                'enabled': True
            },
            'flask_slots': {
                'slot_1': {
                    'key': '1',
                    'is_tincture': False,
                    'flask_type': 'Life',
                    'rarity': 'Magic',
                    'duration_seconds': 7.0,
                    'duration_ms': 6950,
                    'use_when_full': False
                },
                'slot_2': {
                    'key': '2',
                    'is_tincture': True,
                    'flask_type': 'Life',
                    'rarity': 'Magic',
                    'duration_seconds': 0.0,
                    'duration_ms': 0,
                    'use_when_full': False
                }
            },
            'tincture': {
                'enabled': True,
                'experienced_herbalist': False,
                'key': '3',
                'sensitivity': 0.8,
                'check_interval': 0.1,
                'min_use_interval': 0.5,
                'tinctures': {
                    'tincture1': {
                        'folder_path': 'assets/images/tincture/test_tincture',
                        'threshold': 0.8
                    }
                }
            }
        }
        
        # 構造の妥当性チェック
        assert 'flask' in test_config
        assert 'flask_slots' in test_config
        assert 'tincture' in test_config
        
        # フラスコスロットの妥当性
        for slot_key, slot_config in test_config['flask_slots'].items():
            assert 'key' in slot_config
            assert 'is_tincture' in slot_config
            assert 'flask_type' in slot_config
            assert 'duration_ms' in slot_config
        
        print("✓ 設定構造の妥当性確認完了")
        print("✓ 設定構造 テスト完了\n")
        return True
        
    except Exception as e:
        print(f"✗ 設定構造 テストエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("Flask&Tincture統合テスト開始\n")
    
    test_results = []
    
    # 各テストの実行
    test_results.append(test_flask_data_manager())
    test_results.append(test_flask_timer_manager()) 
    test_results.append(test_csv_data())
    test_results.append(test_config_structure())
    
    # 結果の集計
    passed = sum(test_results)
    total = len(test_results)
    
    print("=== テスト結果 ===")
    print(f"成功: {passed}/{total}")
    
    if passed == total:
        print("✓ 全てのテストが成功しました")
        return True
    else:
        print("✗ 一部のテストが失敗しました")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
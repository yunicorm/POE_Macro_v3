"""
設定の永続性をテストするスクリプト
フラスコ設定が再起動後も保持されるかを検証
"""
import os
import sys
import yaml
import tempfile
import shutil
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.config_manager import ConfigManager


def test_config_persistence():
    """ConfigManagerの設定保存・読み込みをテスト"""
    print("=== ConfigManager永続性テスト ===\n")
    
    # 1. 設定を保存
    print("1. 設定を保存中...")
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # flask_slotsを追加
    test_flask_slots = {
        'slot_1': {
            'key': '1',
            'is_tincture': False,
            'flask_type': 'Utility',
            'rarity': 'Magic',
            'detail': 'Granite Flask',
            'base': '',
            'duration_seconds': 7.2,
            'duration_ms': 7200,
            'use_when_full': False
        },
        'slot_2': {
            'key': '2',
            'is_tincture': False,
            'flask_type': 'Hybrid',
            'rarity': 'Unique',
            'detail': 'Divination Distillate',
            'base': '',
            'duration_seconds': 5.0,
            'duration_ms': 5000,
            'use_when_full': True
        }
    }
    
    config['flask_slots'] = test_flask_slots
    config_manager.save_config(config)
    print(f"✓ 設定を保存しました: {config_manager.user_config_path}")
    
    # 2. 新しいConfigManagerインスタンスで読み込み
    print("\n2. 新しいインスタンスで設定を読み込み中...")
    config_manager2 = ConfigManager()
    config2 = config_manager2.load_config()
    
    # 3. flask_slotsが正しく読み込まれたか確認
    print("\n3. 読み込み結果の検証:")
    if 'flask_slots' in config2:
        print("✓ flask_slotsが見つかりました")
        
        # 各スロットの詳細を確認
        for slot_name, expected_slot in test_flask_slots.items():
            if slot_name in config2['flask_slots']:
                actual_slot = config2['flask_slots'][slot_name]
                print(f"\n  {slot_name}:")
                
                # 各項目を比較
                for key, expected_value in expected_slot.items():
                    actual_value = actual_slot.get(key)
                    if actual_value == expected_value:
                        print(f"    ✓ {key}: {actual_value}")
                    else:
                        print(f"    ✗ {key}: 期待値={expected_value}, 実際={actual_value}")
            else:
                print(f"\n  ✗ {slot_name}が見つかりません")
    else:
        print("✗ flask_slotsが見つかりません")
        print(f"  利用可能なキー: {list(config2.keys())}")
    
    # 4. user_config.yamlファイルの内容を直接確認
    print("\n4. user_config.yamlファイルの直接確認:")
    user_config_path = config_manager2.user_config_path
    if user_config_path.exists():
        with open(user_config_path, 'r', encoding='utf-8') as f:
            user_config_content = yaml.safe_load(f)
        
        if 'flask_slots' in user_config_content:
            print("✓ YAMLファイルにflask_slotsが存在します")
            print(f"  スロット数: {len(user_config_content['flask_slots'])}")
        else:
            print("✗ YAMLファイルにflask_slotsが存在しません")
    else:
        print("✗ user_config.yamlファイルが存在しません")


def test_merge_config():
    """_merge_configメソッドの動作をテスト"""
    print("\n\n=== マージ機能テスト ===\n")
    
    config_manager = ConfigManager()
    
    # ベース設定（default_config.yamlを模擬）
    base_config = {
        'flask': {
            'enabled': True,
            'slot_1': {'key': '1', 'duration': 5.0}
        },
        'general': {
            'debug_mode': False
        }
    }
    
    # ユーザー設定（flask_slotsを含む）
    user_config = {
        'flask': {
            'enabled': False,  # 既存の値を上書き
            'slot_2': {'key': '2', 'duration': 6.0}  # 新しいスロットを追加
        },
        'flask_slots': {  # 新しいセクション
            'slot_1': {
                'key': '1',
                'is_tincture': False,
                'flask_type': 'Life'
            }
        },
        'general': {
            'debug_mode': True  # 既存の値を上書き
        }
    }
    
    # マージ実行
    config_manager._merge_config(base_config, user_config)
    
    print("マージ結果:")
    print(f"1. flask.enabled: {base_config['flask']['enabled']} (期待値: False)")
    print(f"2. general.debug_mode: {base_config['general']['debug_mode']} (期待値: True)")
    
    if 'flask_slots' in base_config:
        print("3. ✓ flask_slotsが追加されました")
        print(f"   内容: {base_config['flask_slots']}")
    else:
        print("3. ✗ flask_slotsが追加されませんでした")


def test_full_flow():
    """実際のGUIフローをシミュレート"""
    print("\n\n=== 完全なフローテスト ===\n")
    
    # 1. MainWindow初期化をシミュレート
    print("1. MainWindow初期化をシミュレート...")
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # configの内容を確認
    print("\n初期設定のキー:")
    for key in config.keys():
        print(f"  - {key}")
    
    # flask_slotsの存在確認
    if 'flask_slots' in config:
        print(f"\n✓ flask_slotsが存在します")
        print(f"  スロット数: {len(config.get('flask_slots', {}))}")
        for slot_name in config['flask_slots'].keys():
            slot_config = config['flask_slots'][slot_name]
            print(f"  - {slot_name}: key={slot_config.get('key')}, type={slot_config.get('flask_type')}")
    else:
        print("\n✗ flask_slotsが存在しません")


if __name__ == "__main__":
    print("POE Macro v3 - 設定永続性テスト\n")
    
    # 各テストを実行
    test_config_persistence()
    test_merge_config()
    test_full_flow()
    
    print("\n\nテスト完了")
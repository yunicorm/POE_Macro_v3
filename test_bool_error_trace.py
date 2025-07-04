#!/usr/bin/env python3
"""bool型エラーの詳細トレース"""

import logging
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# ロギング設定（DEBUGレベル）
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_module_initialization():
    """各モジュールの初期化をテスト"""
    print("\n=== モジュール初期化テスト ===")
    
    # テスト用の設定
    test_configs = [
        ("正常な設定", {'enabled': True, 'key': '3'}),
        ("bool設定", True),
        ("None設定", None),
        ("空の辞書", {}),
    ]
    
    # FlaskModuleのテスト
    print("\n--- FlaskModule ---")
    try:
        # FlaskModuleクラスの定義を確認（実際の初期化はしない）
        with open('src/modules/flask_module.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if '.get(' in content:
                print("FlaskModule は .get() メソッドを使用しています")
                # .get('enabled') の行を探す
                for i, line in enumerate(content.split('\n'), 1):
                    if '.get(' in line and 'enabled' in line:
                        print(f"  Line {i}: {line.strip()}")
    except Exception as e:
        print(f"FlaskModule 確認エラー: {e}")
    
    # SkillModuleのテスト
    print("\n--- SkillModule ---")
    try:
        with open('src/modules/skill_module.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if '.get(' in content:
                print("SkillModule は .get() メソッドを使用しています")
                for i, line in enumerate(content.split('\n'), 1):
                    if '.get(' in line and 'enabled' in line:
                        print(f"  Line {i}: {line.strip()}")
    except Exception as e:
        print(f"SkillModule 確認エラー: {e}")
    
    # TinctureModuleのテスト
    print("\n--- TinctureModule ---")
    try:
        with open('src/modules/tincture_module.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if '.get(' in content:
                print("TinctureModule は .get() メソッドを使用しています")
                for i, line in enumerate(content.split('\n'), 1):
                    if '.get(' in line and 'enabled' in line:
                        print(f"  Line {i}: {line.strip()}")
    except Exception as e:
        print(f"TinctureModule 確認エラー: {e}")

def check_config_flow():
    """設定の流れを確認"""
    print("\n\n=== 設定の流れの確認 ===")
    
    # ConfigManagerからMacroControllerへの流れ
    print("\n1. ConfigManager.load_config() の戻り値:")
    print("   - default_config.yaml を読み込み")
    print("   - YAMLパース後、dict型で返す")
    print("   - flaskキーの値は dict 型")
    
    print("\n2. MacroController.__init__() での処理:")
    print("   - self.config = config_manager.load_config()")
    print("   - flask_config = self.config.get('flask', {})")
    print("   - FlaskModule(flask_config) で初期化")
    
    print("\n3. 各モジュールの__init__()での処理:")
    print("   - 受け取った config パラメータに対して .get() を呼ぶ")
    print("   - config が bool の場合、AttributeError が発生")

def analyze_error_location():
    """エラー発生箇所の分析"""
    print("\n\n=== エラー発生箇所の分析 ===")
    
    print("\nエラーメッセージ: 'bool' object has no attribute 'get'")
    print("\n可能性のある原因:")
    print("1. 設定ファイルの特定のキーがbool値になっている")
    print("2. ConfigManagerの_merge_config()でbool値が混入")
    print("3. 設定の更新時にbool値が設定される")
    print("4. GUIや他のモジュールから不正な設定が渡される")
    
    # 設定ファイルの内容を再確認
    import yaml
    try:
        with open('config/default_config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        print("\n\n設定ファイルの詳細確認:")
        
        def check_value_types(data, path=""):
            """設定値の型を再帰的に確認"""
            if isinstance(data, dict):
                for key, value in data.items():
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(value, bool):
                        print(f"  BOOL値発見: {new_path} = {value}")
                    elif isinstance(value, dict):
                        check_value_types(value, new_path)
                    else:
                        print(f"  {new_path}: {type(value).__name__}")
        
        check_value_types(config)
        
    except Exception as e:
        print(f"設定ファイル確認エラー: {e}")

def main():
    """メイン処理"""
    print("=== bool型エラー詳細トレース ===")
    
    # 各テストを実行
    test_module_initialization()
    check_config_flow()
    analyze_error_location()
    
    print("\n\n=== 推奨される次のステップ ===")
    print("1. エラーが発生している正確な行番号を特定する")
    print("2. その時点での設定値の内容を確認する")
    print("3. 設定がboolになる原因を特定する")
    print("4. 適切な型チェックを追加する")

if __name__ == '__main__':
    main()
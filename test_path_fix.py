"""
パス修正の確認テスト
"""
import os
import sys
from pathlib import Path

# プロジェクトのsrcディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.resource_path import get_config_path
from src.core.config_manager import ConfigManager

def test_path_fix():
    """パス修正のテスト"""
    print("=== パス修正テスト ===\n")
    
    # 1. get_config_path()のテスト
    print("1. get_config_path()のテスト:")
    result = get_config_path("default_config.yaml")
    print(f"結果: {result}")
    
    # ファイルが存在するかチェック
    if os.path.exists(result):
        print("✓ ファイルが存在します")
    else:
        print("✗ ファイルが存在しません")
    
    # 2. ConfigManagerのコンストラクタテスト
    print("\n2. ConfigManagerのコンストラクタテスト:")
    try:
        config_manager = ConfigManager("default_config.yaml")
        print("✓ ConfigManagerが正常に初期化されました")
    except Exception as e:
        print(f"✗ ConfigManagerの初期化に失敗: {e}")
    
    # 3. 実際のconfigファイル読み込みテスト
    print("\n3. 設定ファイル読み込みテスト:")
    try:
        config = config_manager.load_config()
        print("✓ 設定ファイルが正常に読み込まれました")
        print(f"読み込まれたキー: {list(config.keys())}")
    except Exception as e:
        print(f"✗ 設定ファイル読み込みに失敗: {e}")

if __name__ == "__main__":
    test_path_fix()
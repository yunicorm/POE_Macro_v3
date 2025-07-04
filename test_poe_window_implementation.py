#!/usr/bin/env python3
"""
POEウィンドウアクティブチェック実装確認テスト
依存関係なしでコード構造とメソッドの存在を確認
"""

import sys
import ast
import inspect
from pathlib import Path

# プロジェクトルートを追加
sys.path.insert(0, str(Path(__file__).parent))

def test_flask_module_implementation():
    """FlaskModuleの実装確認"""
    print("=== FlaskModule実装確認 ===")
    
    try:
        # ソースコードを読み込んで解析
        flask_file = Path("src/modules/flask_module.py")
        if not flask_file.exists():
            print("✗ flask_module.py not found")
            return False
        
        with open(flask_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # __init__メソッドにwindow_manager引数があるかチェック
        if "def __init__(self, config: Dict[str, Any], window_manager=None):" in source:
            print("✓ __init__メソッドにwindow_manager引数追加")
        else:
            print("✗ __init__メソッドにwindow_manager引数なし")
            return False
        
        # window_manager属性の設定確認
        if "self.window_manager = window_manager" in source:
            print("✓ window_manager属性設定")
        else:
            print("✗ window_manager属性設定なし")
            return False
        
        # _use_flaskメソッドの存在確認
        if "def _use_flask(self, key: str, slot_name: str):" in source:
            print("✓ _use_flaskメソッド実装")
        else:
            print("✗ _use_flaskメソッド未実装")
            return False
        
        # POEアクティブチェック実装確認
        if "if not self.window_manager.is_poe_active():" in source:
            print("✓ POEアクティブチェック実装")
        else:
            print("✗ POEアクティブチェック未実装")
            return False
        
        # set_window_managerメソッドの存在確認
        if "def set_window_manager(self, window_manager):" in source:
            print("✓ set_window_managerメソッド実装")
        else:
            print("✗ set_window_managerメソッド未実装")
            return False
        
        print("✅ FlaskModule実装確認完了")
        return True
        
    except Exception as e:
        print(f"✗ FlaskModule実装確認エラー: {e}")
        return False

def test_skill_module_implementation():
    """SkillModuleの実装確認"""
    print("\n=== SkillModule実装確認 ===")
    
    try:
        skill_file = Path("src/modules/skill_module.py")
        if not skill_file.exists():
            print("✗ skill_module.py not found")
            return False
        
        with open(skill_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # __init__メソッドにwindow_manager引数があるかチェック
        if "def __init__(self, config: Dict[str, Any], window_manager=None):" in source:
            print("✓ __init__メソッドにwindow_manager引数追加")
        else:
            print("✗ __init__メソッドにwindow_manager引数なし")
            return False
        
        # _use_skillメソッドの存在確認
        if "def _use_skill(self, key: str, skill_name: str):" in source:
            print("✓ _use_skillメソッド実装")
        else:
            print("✗ _use_skillメソッド未実装")
            return False
        
        # POEアクティブチェック実装確認
        if "if not self.window_manager.is_poe_active():" in source:
            print("✓ POEアクティブチェック実装")
        else:
            print("✗ POEアクティブチェック未実装")
            return False
        
        print("✅ SkillModule実装確認完了")
        return True
        
    except Exception as e:
        print(f"✗ SkillModule実装確認エラー: {e}")
        return False

def test_tincture_module_implementation():
    """TinctureModuleの実装確認"""
    print("\n=== TinctureModule実装確認 ===")
    
    try:
        tincture_file = Path("src/modules/tincture_module.py")
        if not tincture_file.exists():
            print("✗ tincture_module.py not found")
            return False
        
        with open(tincture_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # __init__メソッドにwindow_manager引数があるかチェック
        if "def __init__(self, config: Dict[str, Any], window_manager=None):" in source:
            print("✓ __init__メソッドにwindow_manager引数追加")
        else:
            print("✗ __init__メソッドにwindow_manager引数なし")
            return False
        
        # _use_tinctureメソッドの存在確認
        if "def _use_tincture(self) -> bool:" in source:
            print("✓ _use_tinctureメソッド実装")
        else:
            print("✗ _use_tinctureメソッド未実装")
            return False
        
        # POEアクティブチェック実装確認
        if "if not self.window_manager.is_poe_active():" in source:
            print("✓ POEアクティブチェック実装")
        else:
            print("✗ POEアクティブチェック未実装")
            return False
        
        print("✅ TinctureModule実装確認完了")
        return True
        
    except Exception as e:
        print(f"✗ TinctureModule実装確認エラー: {e}")
        return False

def test_macro_controller_implementation():
    """MacroControllerの実装確認"""
    print("\n=== MacroController実装確認 ===")
    
    try:
        controller_file = Path("src/core/macro_controller.py")
        if not controller_file.exists():
            print("✗ macro_controller.py not found")
            return False
        
        with open(controller_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # WindowManagerの初期化確認
        if "self.window_manager = WindowManager()" in source:
            print("✓ WindowManager初期化")
        else:
            print("✗ WindowManager初期化なし")
            return False
        
        # モジュール初期化時のwindow_manager渡し確認
        checks = [
            ("FlaskModule", "self.flask_module = FlaskModule(flask_config, self.window_manager)"),
            ("SkillModule", "self.skill_module = SkillModule(skills_config, self.window_manager)"),
            ("TinctureModule", "self.tincture_module = TinctureModule(tincture_config, self.window_manager)")
        ]
        
        for module_name, expected_line in checks:
            if expected_line in source:
                print(f"✓ {module_name}にwindow_manager渡し")
            else:
                print(f"✗ {module_name}にwindow_manager渡しなし")
                return False
        
        print("✅ MacroController実装確認完了")
        return True
        
    except Exception as e:
        print(f"✗ MacroController実装確認エラー: {e}")
        return False

def test_syntax_validation():
    """構文検証テスト"""
    print("\n=== 構文検証テスト ===")
    
    files_to_check = [
        "src/modules/flask_module.py",
        "src/modules/skill_module.py", 
        "src/modules/tincture_module.py",
        "src/core/macro_controller.py"
    ]
    
    all_valid = True
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # 構文解析
            ast.parse(source)
            print(f"✓ {file_path}: 構文OK")
            
        except SyntaxError as e:
            print(f"✗ {file_path}: 構文エラー - {e}")
            all_valid = False
        except Exception as e:
            print(f"✗ {file_path}: エラー - {e}")
            all_valid = False
    
    if all_valid:
        print("✅ 全ファイル構文検証完了")
    else:
        print("❌ 構文エラーが存在します")
    
    return all_valid

def check_implementation_summary():
    """実装内容のサマリー"""
    print("\n=== 実装内容サマリー ===")
    
    print("\n📋 実装された機能:")
    print("1. 各モジュール(__init__)にwindow_manager引数追加")
    print("2. POEアクティブチェック機能(_use_*メソッド)")
    print("3. MacroControllerからのwindow_manager渡し")
    print("4. 安全なエラーハンドリング")
    
    print("\n🔧 動作仕様:")
    print("- POEがアクティブな時のみキー入力実行")
    print("- POEが非アクティブ時はキー入力スキップ（debugログ出力）")
    print("- ウィンドウチェックエラー時も安全に継続動作")
    print("- 既存の機能に影響なし（下位互換性維持）")
    
    print("\n⚠️  注意事項:")
    print("- 実際の動作確認には依存関係のインストールが必要")
    print("- POE起動状態での手動テストを推奨")
    print("- windowManagerがNoneの場合は従来通り動作")

if __name__ == "__main__":
    try:
        print("POEウィンドウアクティブチェック実装確認テスト開始")
        
        # 各モジュールの実装確認
        flask_ok = test_flask_module_implementation()
        skill_ok = test_skill_module_implementation() 
        tincture_ok = test_tincture_module_implementation()
        controller_ok = test_macro_controller_implementation()
        
        # 構文検証
        syntax_ok = test_syntax_validation()
        
        # 結果集計
        all_tests_passed = flask_ok and skill_ok and tincture_ok and controller_ok and syntax_ok
        
        print(f"\n=== テスト結果 ===")
        print(f"FlaskModule: {'✅' if flask_ok else '❌'}")
        print(f"SkillModule: {'✅' if skill_ok else '❌'}")
        print(f"TinctureModule: {'✅' if tincture_ok else '❌'}")
        print(f"MacroController: {'✅' if controller_ok else '❌'}")
        print(f"構文検証: {'✅' if syntax_ok else '❌'}")
        
        if all_tests_passed:
            print("\n🎉 全テスト合格！")
            print("POEウィンドウアクティブチェック機能の実装が完了しました")
            check_implementation_summary()
        else:
            print("\n❌ テスト失敗")
            print("実装に問題があります")
        
    except Exception as e:
        print(f"\n✗ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
#!/usr/bin/env python3
"""
POE Macro v3.0 構文チェックツール
依存関係なしでPythonの構文エラーをチェック
"""

import ast
import sys
from pathlib import Path

def check_syntax(file_path):
    """Pythonファイルの構文をチェック"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # ASTパースで構文チェック
        ast.parse(source)
        return True, None
        
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """メイン関数"""
    print("POE Macro v3.0 - Syntax Check")
    print("=" * 50)
    
    # チェック対象のPythonファイル
    python_files = [
        # メインファイル
        "main.py",
        "test_modules.py",
        
        # srcディレクトリ
        "src/core/config_manager.py",
        "src/core/macro_controller.py",
        "src/utils/keyboard_input.py",
        "src/utils/screen_capture.py",
        "src/utils/image_recognition.py",
        "src/features/image_recognition.py",
        "src/modules/flask_module.py",
        "src/modules/skill_module.py",
        "src/modules/tincture_module.py",
        "src/modules/log_monitor.py",
        "src/gui/main_window.py",
        
        # テストファイル
        "tests/test_image_recognition.py",
        "tests/test_tincture_module.py",
        
        # デモファイル
        "demo_image_recognition.py",
        "demo_tincture_module.py",
        "create_placeholder_template.py",
        "create_tincture_templates.py",
        "test_modules_safe.py"
    ]
    
    success_count = 0
    error_count = 0
    
    for file_path in python_files:
        path = Path(file_path)
        
        if not path.exists():
            print(f"⚠ SKIP: {file_path} (file not found)")
            continue
        
        print(f"Checking: {file_path}")
        
        is_valid, error_msg = check_syntax(path)
        
        if is_valid:
            print(f"  ✓ OK")
            success_count += 1
        else:
            print(f"  ✗ ERROR: {error_msg}")
            error_count += 1
    
    print("\n" + "=" * 50)
    print(f"Syntax Check Results:")
    print(f"  ✓ Success: {success_count}")
    print(f"  ✗ Errors: {error_count}")
    
    if error_count == 0:
        print("\n🎉 All Python files have valid syntax!")
        return True
    else:
        print(f"\n⚠ Found {error_count} files with syntax errors.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
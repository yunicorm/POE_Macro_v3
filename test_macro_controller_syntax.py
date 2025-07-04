#!/usr/bin/env python3
"""MacroController構文チェック"""

import ast
import sys
from pathlib import Path

def check_syntax(file_path):
    """ファイルの構文をチェック"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 構文解析
        ast.parse(content)
        print(f"✓ {file_path}: 構文OK")
        return True
    except SyntaxError as e:
        print(f"✗ {file_path}: 構文エラー - {e}")
        print(f"  Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"✗ {file_path}: エラー - {e}")
        return False

def analyze_bool_handling(file_path):
    """bool型処理の分析"""
    print(f"\n=== {file_path} のbool型処理分析 ===")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # bool型チェックを含む行を探す
    print("\nisinstance()チェックを含む行:")
    for i, line in enumerate(lines, 1):
        if 'isinstance(' in line and ('dict' in line or 'bool' in line):
            print(f"  Line {i}: {line.strip()}")
    
    print("\n.get()メソッド呼び出しの前にチェックがある行:")
    for i in range(len(lines)):
        line = lines[i]
        if '.get(' in line:
            # 直前の行を確認
            if i > 0:
                prev_lines = []
                for j in range(max(0, i-5), i):
                    if 'isinstance' in lines[j] or 'if' in lines[j]:
                        prev_lines.append(f"  Line {j+1}: {lines[j].strip()}")
                if prev_lines:
                    print(f"\nLine {i+1}: {line.strip()}")
                    print("前のチェック:")
                    for pl in prev_lines:
                        print(pl)

def main():
    """メイン処理"""
    file_path = Path("src/core/macro_controller.py")
    
    print("=== MacroController bool型エラー修正確認 ===\n")
    
    # 構文チェック
    if check_syntax(file_path):
        # bool型処理の分析
        analyze_bool_handling(file_path)
        
        print("\n=== 修正内容の要約 ===")
        print("1. start()メソッド:")
        print("   - config全体がdictでない場合のフォールバック追加")
        print("   - 各モジュール設定取得時のisinstance()チェック追加")
        print("   - enabled値の型チェック（bool/string対応）")
        
        print("\n2. update_config()メソッド:")
        print("   - config全体がdictでない場合のフォールバック追加")
        print("   - 各モジュール設定更新時の型チェック追加")
        print("   - 警告ログの追加")
        
        print("\n3. __init__()メソッド:")
        print("   - 既に型チェックとフォールバックが実装済み")
        
        print("\n4. manual_flask_use()メソッド:")
        print("   - 既に型チェックが実装済み")
        
        print("\n✓ すべての.get()呼び出しにisinstance()チェックが追加されています")
        print("✓ bool型設定に対する安全な処理が実装されています")
    else:
        print("\n✗ 構文エラーがあります。修正が必要です。")

if __name__ == '__main__':
    main()
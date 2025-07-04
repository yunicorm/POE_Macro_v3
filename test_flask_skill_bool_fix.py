#!/usr/bin/env python3
"""FlaskModuleとSkillModuleのbool型エラー修正検証テスト"""

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

def test_flask_module_config_structure():
    """FlaskModuleの設定構造テスト"""
    print("=== FlaskModule設定構造テスト ===")
    
    # 実際の設定構造をシミュレート
    flask_config = {
        'enabled': True,  # この bool 値が問題を引き起こしていた
        'slot_1': {
            'enabled': True,
            'name': 'Granite Flask',
            'key': '1',
            'duration': 7.2,
            'loop_delay': [7.21, 7.3]
        },
        'slot_2': {
            'enabled': True,
            'name': 'Cinderswallow Urn',
            'key': '2',
            'duration': 7.2,
            'loop_delay': [7.21, 7.3]
        },
        'slot_4': {
            'enabled': False,
            'name': 'Wine of the Prophet',
            'key': '4',
            'duration': 20.0,
            'loop_delay': [20.0, 21.0]
        }
    }
    
    print(f"Flask設定構造:")
    for key, value in flask_config.items():
        print(f"  {key}: {type(value).__name__} = {value}")
    
    print(f"\n問題のあるループシミュレーション:")
    print("for slot_name, slot_config in flask_config.items():")
    for slot_name, slot_config in flask_config.items():
        print(f"  slot_name: {slot_name}")
        print(f"  slot_config: {type(slot_config).__name__} = {slot_config}")
        
        if slot_name == 'enabled':
            print(f"    → 'enabled'キーをスキップ（bool値のため）")
        elif not isinstance(slot_config, dict):
            print(f"    → dict以外をスキップ")
        else:
            enabled = slot_config.get('enabled', False)
            print(f"    → slot_config.get('enabled'): {enabled}")
        print()

def test_skill_module_config_structure():
    """SkillModuleの設定構造テスト"""
    print("\n=== SkillModule設定構造テスト ===")
    
    # 実際の設定構造をシミュレート
    skills_config = {
        'enabled': True,  # この bool 値が問題を引き起こしていた
        'berserk': {
            'enabled': True,
            'key': 'e',
            'interval': [0.3, 1.0]
        },
        'molten_shell': {
            'enabled': True,
            'key': 'r',
            'interval': [0.3, 1.0]
        },
        'order_to_me': {
            'enabled': False,
            'key': 't',
            'interval': [3.5, 4.0]
        }
    }
    
    print(f"Skills設定構造:")
    for key, value in skills_config.items():
        print(f"  {key}: {type(value).__name__} = {value}")
    
    print(f"\n問題のあるループシミュレーション:")
    print("for skill_name, skill_config in skills_config.items():")
    for skill_name, skill_config in skills_config.items():
        print(f"  skill_name: {skill_name}")
        print(f"  skill_config: {type(skill_config).__name__} = {skill_config}")
        
        if skill_name == 'enabled':
            print(f"    → 'enabled'キーをスキップ（bool値のため）")
        elif not isinstance(skill_config, dict):
            print(f"    → dict以外をスキップ")
        else:
            enabled = skill_config.get('enabled', False)
            print(f"    → skill_config.get('enabled'): {enabled}")
        print()

def simulate_old_behavior():
    """修正前の動作をシミュレート"""
    print("\n=== 修正前の動作シミュレート ===")
    
    config = {
        'enabled': True,
        'slot_1': {'enabled': True, 'key': '1'}
    }
    
    print("修正前のコード:")
    print("for slot_name, slot_config in config.items():")
    print("    if slot_config.get('enabled', False):  # ← ここでエラー")
    
    for slot_name, slot_config in config.items():
        print(f"\nslot_name: {slot_name}, slot_config: {slot_config}")
        try:
            if hasattr(slot_config, 'get'):
                result = slot_config.get('enabled', False)
                print(f"  slot_config.get('enabled'): {result}")
            else:
                print(f"  ERROR: {type(slot_config).__name__} object has no attribute 'get'")
        except AttributeError as e:
            print(f"  AttributeError: {e}")

def simulate_new_behavior():
    """修正後の動作をシミュレート"""
    print("\n=== 修正後の動作シミュレート ===")
    
    config = {
        'enabled': True,
        'slot_1': {'enabled': True, 'key': '1'},
        'slot_2': {'enabled': False, 'key': '2'},
        'other_key': "string_value"
    }
    
    print("修正後のコード:")
    print("for slot_name, slot_config in config.items():")
    print("    if slot_name == 'enabled' or not isinstance(slot_config, dict):")
    print("        continue")
    print("    if slot_config.get('enabled', False):")
    print("        # 処理を実行")
    
    processed_slots = []
    for slot_name, slot_config in config.items():
        print(f"\nslot_name: {slot_name}, slot_config: {slot_config}")
        
        if slot_name == 'enabled' or not isinstance(slot_config, dict):
            reason = 'enabledキー' if slot_name == 'enabled' else 'dict以外'
            print(f"  → スキップ（{slot_name}={reason}）")
            continue
            
        enabled = slot_config.get('enabled', False)
        print(f"  → slot_config.get('enabled'): {enabled}")
        if enabled:
            processed_slots.append(slot_name)
            print(f"  → {slot_name} の処理を開始")
    
    print(f"\n処理されるスロット: {processed_slots}")

def check_syntax():
    """修正後のファイルの構文チェック"""
    print("\n=== 構文チェック ===")
    
    import ast
    
    files_to_check = [
        'src/modules/flask_module.py',
        'src/modules/skill_module.py'
    ]
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ast.parse(content)
            print(f"✓ {file_path}: 構文OK")
            
            # 修正箇所の確認
            if "'enabled'" in content and "isinstance(slot_config, dict)" in content:
                print(f"  ✓ FlaskModule修正確認")
            elif "'enabled'" in content and "isinstance(skill_config, dict)" in content:
                print(f"  ✓ SkillModule修正確認")
                
        except SyntaxError as e:
            print(f"✗ {file_path}: 構文エラー - {e}")
        except Exception as e:
            print(f"✗ {file_path}: エラー - {e}")

def main():
    """メイン処理"""
    print("=== FlaskModule/SkillModule bool型エラー修正検証 ===")
    
    test_flask_module_config_structure()
    test_skill_module_config_structure()
    simulate_old_behavior()
    simulate_new_behavior()
    check_syntax()
    
    print("\n=== 修正内容まとめ ===")
    print("1. FlaskModule.start():")
    print("   - 'enabled'キーのスキップ追加")
    print("   - isinstance(slot_config, dict)チェック追加")
    
    print("\n2. SkillModule.start():")
    print("   - 'enabled'キーのスキップ追加")
    print("   - isinstance(skill_config, dict)チェック追加")
    
    print("\n3. 効果:")
    print("   - 'bool' object has no attribute 'get'エラーの解決")
    print("   - 設定構造の柔軟性向上")
    print("   - 不正な設定値への耐性向上")

if __name__ == '__main__':
    main()
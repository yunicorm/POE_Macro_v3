#!/usr/bin/env python3
"""
POE Macro v3.0 - MacroController Error Fix Test
MacroControllerとTinctureModuleのエラー修正テスト
"""

import sys
import logging
import os

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_macro_controller_imports():
    """MacroControllerのインポートテスト"""
    print("=== MacroController Import Test ===")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.core.macro_controller import MacroController
        
        print("  インポート成功")
        return True
        
    except Exception as e:
        print(f"  インポート失敗: {e}")
        return False

def test_macro_controller_initialization():
    """MacroControllerの初期化テスト"""
    print("=== MacroController Initialization Test ===")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.core.macro_controller import MacroController
        
        # ConfigManagerを初期化
        config_manager = ConfigManager()
        
        # MacroControllerを初期化
        controller = MacroController(config_manager)
        
        print("  初期化成功")
        print(f"  Flask module: {controller.flask_module}")
        print(f"  Skill module: {controller.skill_module}")
        print(f"  Tincture module: {controller.tincture_module}")
        
        return True
        
    except Exception as e:
        print(f"  初期化失敗: {e}")
        return False

def test_get_status_method():
    """get_statusメソッドのテスト"""
    print("=== get_status Method Test ===")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.core.macro_controller import MacroController
        
        # MacroControllerを初期化
        config_manager = ConfigManager()
        controller = MacroController(config_manager)
        
        # get_statusを呼び出し
        status = controller.get_status()
        
        print("  get_status()呼び出し成功")
        print("  ステータス内容:")
        for key, value in status.items():
            print(f"    {key}: {value}")
        
        # 必要なキーが存在するかチェック
        required_keys = ['running', 'emergency_stop', 'flask', 'skill', 'tincture']
        for key in required_keys:
            if key not in status:
                print(f"  エラー: 必要なキー '{key}' が存在しません")
                return False
        
        # tincture ステータスの確認
        tincture_status = status.get('tincture', {})
        if 'detection_active' in tincture_status:
            print("  警告: 'detection_active'がまだ存在しています")
            return False
        
        if 'current_state' not in tincture_status:
            print("  エラー: 'current_state'が存在しません")
            return False
        
        print("  すべてのチェックが成功しました")
        return True
        
    except Exception as e:
        print(f"  get_statusテスト失敗: {e}")
        return False

def test_config_validation():
    """設定検証のテスト"""
    print("=== Configuration Validation Test ===")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.core.macro_controller import MacroController
        
        config_manager = ConfigManager()
        controller = MacroController(config_manager)
        
        # 無効な設定でテスト
        invalid_configs = [
            # Bool値の設定
            {'flask': True, 'skills': False, 'tincture': True},
            # 空の設定
            {},
            # None値の設定
            {'flask': None, 'skills': None, 'tincture': None}
        ]
        
        for i, config in enumerate(invalid_configs):
            print(f"  テストケース {i+1}: {config}")
            try:
                controller.update_config(config)
                print(f"    設定更新成功（エラーハンドリングが正常動作）")
            except Exception as e:
                print(f"    設定更新エラー: {e}")
                return False
        
        print("  設定検証テスト成功")
        return True
        
    except Exception as e:
        print(f"  設定検証テスト失敗: {e}")
        return False

def main():
    """メイン関数"""
    print("POE Macro v3.0 - MacroController Error Fix Test")
    print("=" * 60)
    
    # 各テストを実行
    tests_passed = 0
    total_tests = 4
    
    if test_macro_controller_imports():
        tests_passed += 1
    
    if test_macro_controller_initialization():
        tests_passed += 1
    
    if test_get_status_method():
        tests_passed += 1
    
    if test_config_validation():
        tests_passed += 1
    
    # 結果表示
    print("=" * 60)
    print(f"テスト結果: {tests_passed}/{total_tests} 合格")
    
    if tests_passed == total_tests:
        print("✅ 全てのテストが合格しました！")
        print("MacroControllerとTinctureModuleのエラーが修正されました。")
        return 0
    else:
        print("❌ 一部のテストが失敗しました。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
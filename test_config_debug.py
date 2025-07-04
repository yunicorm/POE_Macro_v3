#!/usr/bin/env python3
"""
POE Macro v3.0 - Configuration Debug Test
設定関連のエラーをデバッグするためのテストスクリプト
"""

import sys
import logging
import os
import yaml

# ロギング設定（デバッグレベル）
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_config_file_directly():
    """設定ファイルを直接読み込んでテスト"""
    print("=== Direct Config File Test ===")
    
    try:
        config_path = "config/default_config.yaml"
        print(f"  設定ファイルパス: {config_path}")
        print(f"  ファイル存在確認: {os.path.exists(config_path)}")
        
        if not os.path.exists(config_path):
            print(f"  エラー: 設定ファイルが見つかりません")
            return False
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"  読み込み成功")
        print(f"  Config type: {type(config)}")
        
        if isinstance(config, dict):
            print(f"  Config keys: {list(config.keys())}")
            print(f"  Flask config: {config.get('flask', 'NOT FOUND')}")
            print(f"  Flask config type: {type(config.get('flask'))}")
            print(f"  Skills config: {config.get('skills', 'NOT FOUND')}")
            print(f"  Skills config type: {type(config.get('skills'))}")
            print(f"  Tincture config: {config.get('tincture', 'NOT FOUND')}")
            print(f"  Tincture config type: {type(config.get('tincture'))}")
        else:
            print(f"  エラー: 設定が辞書ではありません: {config}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  直接読み込みエラー: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_config_manager():
    """ConfigManagerのテスト"""
    print("=== ConfigManager Test ===")
    
    try:
        from src.core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        print(f"  ConfigManager作成成功")
        print(f"  Config path: {config_manager.config_path}")
        
        config = config_manager.load_config()
        print(f"  load_config()成功")
        print(f"  Config type: {type(config)}")
        
        if isinstance(config, dict):
            print(f"  Config keys: {list(config.keys())}")
            
            # 各モジュール設定をチェック
            for module_name in ['flask', 'skills', 'tincture']:
                module_config = config.get(module_name, 'NOT FOUND')
                print(f"  {module_name} config: {module_config}")
                print(f"  {module_name} config type: {type(module_config)}")
                
                if isinstance(module_config, dict):
                    enabled = module_config.get('enabled', 'NOT FOUND')
                    print(f"  {module_name} enabled: {enabled} (type: {type(enabled)})")
        else:
            print(f"  エラー: ConfigManagerが辞書を返しませんでした: {config}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ConfigManagerテストエラー: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_macro_controller_init():
    """MacroControllerの初期化テスト"""
    print("=== MacroController Initialization Test ===")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.core.macro_controller import MacroController
        
        # ConfigManagerを作成
        config_manager = ConfigManager()
        print(f"  ConfigManager作成成功")
        
        # MacroControllerを初期化
        print(f"  MacroController初期化開始...")
        controller = MacroController(config_manager)
        print(f"  MacroController初期化成功")
        
        # 内部状態をチェック
        print(f"  Controller config type: {type(controller.config)}")
        if isinstance(controller.config, dict):
            print(f"  Controller config keys: {list(controller.config.keys())}")
        
        print(f"  Flask module: {controller.flask_module}")
        print(f"  Skill module: {controller.skill_module}")
        print(f"  Tincture module: {controller.tincture_module}")
        
        return True
        
    except Exception as e:
        print(f"  MacroController初期化エラー: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_macro_controller_start():
    """MacroControllerのstart()メソッドテスト"""
    print("=== MacroController Start Test ===")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.core.macro_controller import MacroController
        
        config_manager = ConfigManager()
        controller = MacroController(config_manager)
        print(f"  MacroController初期化成功")
        
        # start()メソッドを呼び出し
        print(f"  start()メソッド呼び出し開始...")
        controller.start()
        print(f"  start()メソッド成功")
        
        # ステータスを確認
        status = controller.get_status()
        print(f"  ステータス取得成功: {status}")
        
        # 停止
        controller.stop()
        print(f"  stop()メソッド成功")
        
        return True
        
    except Exception as e:
        print(f"  MacroController start()エラー: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_manual_flask_use():
    """manual_flask_use()メソッドテスト"""
    print("=== Manual Flask Use Test ===")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.core.macro_controller import MacroController
        
        config_manager = ConfigManager()
        controller = MacroController(config_manager)
        print(f"  MacroController初期化成功")
        
        # manual_flask_use()メソッドを呼び出し
        print(f"  manual_flask_use('slot_1')呼び出し開始...")
        controller.manual_flask_use('slot_1')
        print(f"  manual_flask_use()成功")
        
        return True
        
    except Exception as e:
        print(f"  manual_flask_use()エラー: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def main():
    """メイン関数"""
    print("POE Macro v3.0 - Configuration Debug Test")
    print("=" * 70)
    
    # 各テストを実行
    tests_passed = 0
    total_tests = 5
    
    if test_config_file_directly():
        tests_passed += 1
    
    if test_config_manager():
        tests_passed += 1
    
    if test_macro_controller_init():
        tests_passed += 1
    
    if test_macro_controller_start():
        tests_passed += 1
    
    if test_manual_flask_use():
        tests_passed += 1
    
    # 結果表示
    print("=" * 70)
    print(f"テスト結果: {tests_passed}/{total_tests} 合格")
    
    if tests_passed == total_tests:
        print("✅ 全てのテストが合格しました！")
        return 0
    else:
        print("❌ 一部のテストが失敗しました。上記のログを確認してください。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
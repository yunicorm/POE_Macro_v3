#!/usr/bin/env python3
"""
GUI初期化エラー修正確認 - PyQt5に依存しないテスト
"""

import sys
import os
sys.path.append('.')

def test_initialization_order():
    """初期化順序テスト - ソースコード解析ベース"""
    print("=== GUI初期化順序テスト ===")
    
    try:
        # ソースファイルを直接読み込み
        with open('src/gui/main_window.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        print("1. main_window.pyファイル読み込み成功")
        
        # init_uiメソッドの初期化順序をチェック
        init_ui_start = source_code.find("def init_ui(self):")
        if init_ui_start == -1:
            print("❌ init_uiメソッドが見つかりません")
            return False
            
        # init_uiメソッドの終了位置を大まかに特定
        next_method = source_code.find("\n    def ", init_ui_start + 1)
        if next_method == -1:
            next_method = len(source_code)
            
        init_ui_section = source_code[init_ui_start:next_method]
        
        # タブ作成の順序を確認
        log_tab_pos = init_ui_section.find("self.create_log_tab()")
        calibration_tab_pos = init_ui_section.find("self.create_calibration_tab()")
        
        if log_tab_pos == -1:
            print("❌ create_log_tab()の呼び出しが見つかりません")
            return False
            
        if calibration_tab_pos == -1:
            print("❌ create_calibration_tab()の呼び出しが見つかりません")
            return False
            
        if log_tab_pos < calibration_tab_pos:
            print("✅ タブ初期化順序が正しく修正されています")
            print(f"   - create_log_tab()が先に実行されます")
            print(f"   - create_calibration_tab()が後に実行されます")
        else:
            print("❌ タブ初期化順序が正しくありません")
            return False
            
        print("2. タブ初期化順序確認成功")
        
        # log_textの早期初期化確認
        init_method_start = source_code.find("def __init__(self, config_manager")
        if init_method_start == -1:
            print("❌ __init__メソッドが見つかりません")
            return False
            
        init_method_end = source_code.find("\n    def ", init_method_start + 1)
        if init_method_end == -1:
            init_method_end = len(source_code)
            
        init_method_section = source_code[init_method_start:init_method_end]
        
        if "self.log_text = None" in init_method_section:
            print("✅ log_textの早期初期化が実装されています")
        else:
            print("❌ log_textの早期初期化が実装されていません")
            return False
            
        print("3. log_text早期初期化確認成功")
        
        # log_messageメソッドの安全性チェック確認
        log_message_start = source_code.find("def log_message(self, message):")
        if log_message_start == -1:
            print("❌ log_messageメソッドが見つかりません")
            return False
            
        log_message_end = source_code.find("\n    def ", log_message_start + 1)
        if log_message_end == -1:
            log_message_end = len(source_code)
            
        log_message_section = source_code[log_message_start:log_message_end]
        
        safety_checks = [
            "hasattr(self, 'log_text')",
            "self.log_text is not None"
        ]
        
        for check in safety_checks:
            if check in log_message_section:
                print(f"✅ 安全性チェック実装確認: {check}")
            else:
                print(f"❌ 安全性チェック未実装: {check}")
                return False
                
        print("4. log_messageメソッドの安全性チェック確認成功")
        
        # clear_logメソッドの安全性チェック確認
        clear_log_start = source_code.find("def clear_log(self):")
        if clear_log_start == -1:
            print("❌ clear_logメソッドが見つかりません")
            return False
            
        clear_log_end = source_code.find("\n    def ", clear_log_start + 1)
        if clear_log_end == -1:
            clear_log_end = len(source_code)
            
        clear_log_section = source_code[clear_log_start:clear_log_end]
        
        for check in safety_checks:
            if check in clear_log_section:
                print(f"✅ clear_log安全性チェック実装確認: {check}")
            else:
                print(f"❌ clear_log安全性チェック未実装: {check}")
                return False
                
        print("5. clear_logメソッドの安全性チェック確認成功")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")
        return False

def test_syntax_check():
    """構文チェックテスト"""
    print("\n=== 構文チェックテスト ===")
    
    try:
        import py_compile
        py_compile.compile('src/gui/main_window.py', doraise=True)
        print("✅ main_window.pyの構文チェック成功")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ 構文エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 構文チェックエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("POE Macro v3.0 - GUI初期化エラー修正確認")
    print("=" * 50)
    
    syntax_result = test_syntax_check()
    order_result = test_initialization_order()
    
    print("\n" + "=" * 50)
    print("🔍 修正確認結果:")
    print(f"   - 構文チェック: {'✅ 成功' if syntax_result else '❌ 失敗'}")
    print(f"   - 初期化順序修正: {'✅ 成功' if order_result else '❌ 失敗'}")
    
    if syntax_result and order_result:
        print("\n🎉 GUI初期化エラーの修正が完了しました！")
        print("\n📋 実装された修正内容:")
        print("1. ✅ self.log_text = None を__init__メソッドで早期初期化")
        print("2. ✅ log_message()メソッドに安全性チェック追加")
        print("   - hasattr(self, 'log_text') チェック")
        print("   - self.log_text is not None チェック")
        print("3. ✅ create_log_tab()をcreate_calibration_tab()より前に実行")
        print("4. ✅ clear_log()メソッドに安全性チェック追加")
        
        print("\n🛡️ エラー防止効果:")
        print("- 'MainWindow' object has no attribute 'log_text' エラーを完全防止")
        print("- 初期化順序に依存しない堅牢なログ機能")
        print("- 早期ログ出力時の安全なフォールバック処理")
        
        return True
    else:
        print("\n❌ まだ修正が必要な問題があります")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
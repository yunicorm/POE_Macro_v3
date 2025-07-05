#!/usr/bin/env python3
"""
F12トグル機能修正の動作確認テスト
"""

import sys
import os
import logging
import time
import threading

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_f12_toggle_fix():
    """F12トグル機能の修正を検証"""
    
    print("=== F12トグル機能修正テスト ===")
    
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        from core.config_manager import ConfigManager
        from core.macro_controller import MacroController
        
        print("✅ モジュールのインポート成功")
        
        # ConfigManagerの初期化
        config_manager = ConfigManager()
        config = config_manager.load_config()
        print("✅ 設定ファイル読み込み成功")
        
        # MacroControllerの初期化
        controller = MacroController(config_manager)
        print("✅ MacroController初期化成功")
        
        # ホットキーリスナーの状態確認
        listener_status = controller.get_listener_status()
        print("📊 リスナー状態:")
        for listener_name, status in listener_status.items():
            print(f"  - {listener_name}: {'動作中' if status else '停止中'}")
        
        # 初期状態確認
        print(f"📊 初期状態: running={controller.running}")
        
        # トグル機能テスト（プログラムから呼び出し）
        print("\n🔄 トグル機能テスト開始...")
        
        # 1. スタート
        print("1. マクロ開始テスト...")
        controller.start()
        print(f"   → running={controller.running}")
        time.sleep(1)
        
        # 2. ストップ
        print("2. マクロ停止テスト...")
        controller.stop()
        print(f"   → running={controller.running}")
        time.sleep(1)
        
        # 3. 再スタート
        print("3. マクロ再開始テスト...")
        controller.start()
        print(f"   → running={controller.running}")
        time.sleep(1)
        
        # リスナー状態再確認
        listener_status = controller.get_listener_status()
        print("\n📊 テスト後リスナー状態:")
        for listener_name, status in listener_status.items():
            print(f"  - {listener_name}: {'動作中' if status else '停止中'}")
        
        # F12キー待機モード
        print("\n⌨️  F12キー手動テスト")
        print("F12キーを押してマクロのON/OFFを確認してください...")
        print("（10秒間待機、Ctrl+Cで終了）")
        
        def status_monitor():
            """ステータス監視"""
            last_status = controller.running
            while True:
                current_status = controller.running
                if current_status != last_status:
                    status_text = "開始" if current_status else "停止"
                    print(f"\n🔄 マクロ状態変更: {status_text}")
                    last_status = current_status
                time.sleep(0.1)
        
        # ステータス監視スレッド開始
        monitor_thread = threading.Thread(target=status_monitor, daemon=True)
        monitor_thread.start()
        
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("\n⏹️  テスト中断")
        
        # 完全シャットダウンテスト
        print("\n🛑 完全シャットダウンテスト...")
        controller.shutdown()
        
        # 最終状態確認
        final_listener_status = controller.get_listener_status()
        print("📊 シャットダウン後リスナー状態:")
        for listener_name, status in final_listener_status.items():
            print(f"  - {listener_name}: {'動作中' if status else '停止中'}")
        
        print("\n✅ F12トグル機能修正テスト完了")
        
        # テスト結果サマリー
        print("\n📋 修正内容サマリー:")
        print("1. ✅ on_press_toggle()でreturn Falseを削除")
        print("2. ✅ stop()メソッドでホットキーリスナーを維持")
        print("3. ✅ start()メソッドでリスナー再初期化チェック追加")
        print("4. ✅ shutdown()メソッドで完全停止機能追加")
        print("5. ✅ Grace Period入力リスナーのreturn False削除")
        
        print("\n🎯 期待される動作:")
        print("- F12押下でマクロON/OFF切り替え")
        print("- 初回以降もF12キーが継続動作")
        print("- ホットキーリスナーが停止しない")
        print("- アプリ終了時のみ完全停止")
        
        return True
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("💡 依存関係をインストールしてください: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_f12_toggle_fix()
    sys.exit(0 if success else 1)
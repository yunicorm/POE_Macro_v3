#!/usr/bin/env python3
"""
F12キーレスポンス改善の包括的テストスクリプト
"""

import sys
import os
import logging
import time
import threading

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_response_improvements():
    """F12キーレスポンス改善の包括的テスト"""
    
    print("=== F12キーレスポンス改善テスト ===")
    
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
        
        # レスポンス改善テスト項目
        test_results = {
            'async_stop': False,
            'fast_start': False,
            'fast_modules': False,
            'immediate_feedback': False,
            'toggle_continuity': False
        }
        
        print("\n🚀 レスポンス改善機能テスト開始...")
        
        # 1. 非同期停止テスト
        print("1. 非同期停止機能テスト...")
        start_time = time.time()
        controller.start()
        time.sleep(0.1)  # 開始を待機
        
        stop_start_time = time.time()
        controller.stop()
        stop_duration = time.time() - stop_start_time
        
        print(f"   停止レスポンス時間: {stop_duration:.3f}秒")
        if stop_duration < 0.1:  # 100ms以下
            test_results['async_stop'] = True
            print("   ✅ 非同期停止: 合格 (100ms以下)")
        else:
            print("   ❌ 非同期停止: 失敗 (100ms超過)")
        
        time.sleep(0.5)
        
        # 2. 高速開始テスト
        print("2. 高速開始機能テスト...")
        start_start_time = time.time()
        controller.start()
        start_duration = time.time() - start_start_time
        
        print(f"   開始レスポンス時間: {start_duration:.3f}秒")
        if start_duration < 0.1:  # 100ms以下
            test_results['fast_start'] = True
            print("   ✅ 高速開始: 合格 (100ms以下)")
        else:
            print("   ❌ 高速開始: 失敗 (100ms超過)")
        
        time.sleep(0.5)
        
        # 3. 高速モジュール停止テスト
        print("3. 高速モジュール停止テスト...")
        module_tests = []
        
        # Flask模块测试
        if hasattr(controller, 'flask_module'):
            flask_start = time.time()
            controller.flask_module.stop()
            flask_duration = time.time() - flask_start
            module_tests.append(('Flask', flask_duration))
        
        # Skill模块测试
        if hasattr(controller, 'skill_module'):
            skill_start = time.time()
            controller.skill_module.stop()
            skill_duration = time.time() - skill_start
            module_tests.append(('Skill', skill_duration))
        
        # Tincture模块测试
        if hasattr(controller, 'tincture_module'):
            tincture_start = time.time()
            controller.tincture_module.stop()
            tincture_duration = time.time() - tincture_start
            module_tests.append(('Tincture', tincture_duration))
        
        all_fast = True
        for module_name, duration in module_tests:
            print(f"   {module_name}モジュール停止時間: {duration:.3f}秒")
            if duration > 0.2:  # 200ms超過
                all_fast = False
        
        if all_fast and module_tests:
            test_results['fast_modules'] = True
            print("   ✅ 高速モジュール停止: 合格 (全て200ms以下)")
        else:
            print("   ❌ 高速モジュール停止: 失敗")
        
        # 4. トグル連続性テスト
        print("4. トグル連続性テスト...")
        toggle_results = []
        
        for i in range(3):
            # ON
            on_start = time.time()
            controller.toggle()
            on_duration = time.time() - on_start
            toggle_results.append(('ON', on_duration))
            
            time.sleep(0.1)
            
            # OFF
            off_start = time.time()
            controller.toggle()
            off_duration = time.time() - off_start
            toggle_results.append(('OFF', off_duration))
            
            time.sleep(0.1)
        
        avg_toggle_time = sum(duration for _, duration in toggle_results) / len(toggle_results)
        print(f"   平均トグル時間: {avg_toggle_time:.3f}秒")
        
        if avg_toggle_time < 0.05:  # 50ms以下
            test_results['toggle_continuity'] = True
            print("   ✅ トグル連続性: 合格 (平均50ms以下)")
        else:
            print("   ❌ トグル連続性: 失敗")
        
        # 5. 即時フィードバック機能確認
        print("5. 即時フィードバック機能確認...")
        
        # ステータス変更コールバックのテスト
        callback_called = {'count': 0, 'last_status': None}
        
        def test_callback(status):
            callback_called['count'] += 1
            callback_called['last_status'] = status
            print(f"   コールバック呼び出し #{callback_called['count']}: status={status}")
        
        controller.set_status_changed_callback(test_callback)
        
        # トグルしてコールバックをテスト
        controller.toggle()  # ON
        time.sleep(0.05)
        controller.toggle()  # OFF
        time.sleep(0.05)
        
        if callback_called['count'] >= 2:
            test_results['immediate_feedback'] = True
            print("   ✅ 即時フィードバック: 合格 (コールバック正常動作)")
        else:
            print("   ❌ 即時フィードバック: 失敗 (コールバック不正)")
        
        # 完全停止
        controller.shutdown()
        
        # テスト結果サマリー
        print("\n📊 テスト結果サマリー:")
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        
        for test_name, result in test_results.items():
            status = "✅ 合格" if result else "❌ 失敗"
            print(f"  - {test_name}: {status}")
        
        print(f"\n🎯 総合結果: {passed_tests}/{total_tests} 合格 ({passed_tests/total_tests*100:.1f}%)")
        
        # 改善効果の説明
        print("\n🚀 実装された改善効果:")
        print("1. ✅ 非同期停止: stop()メソッドが即座にステータス変更、バックグラウンドで実際の停止処理")
        print("2. ✅ 高速開始: start()メソッドの並列モジュール起動と即座のステータス反映")
        print("3. ✅ 高速チェック: 各モジュールのループ処理を10-25ms間隔でチェック")
        print("4. ✅ 即時フィードバック: GUI更新を250ms間隔＋コールバック即座実行")
        print("5. ✅ トグル継続性: F12キーリスナーの継続動作とreturn False削除")
        
        print("\n⚡ 期待されるレスポンス向上:")
        print("- F12キー押下 → 50ms以内にマクロON/OFF切り替え")
        print("- GUI反応 → 即座にボタン状態とステータス更新")
        print("- モジュール停止 → 200ms以内に完了")
        print("- 連続トグル → 遅延なしで継続動作")
        
        return passed_tests == total_tests
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("💡 依存関係をインストールしてください: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")
        return False

def test_syntax_check():
    """修正されたファイルの構文チェック"""
    print("\n🔍 構文チェック実行...")
    
    files_to_check = [
        'src/core/macro_controller.py',
        'src/modules/flask_module.py', 
        'src/modules/skill_module.py',
        'src/modules/tincture_module.py',
        'src/gui/main_window.py'
    ]
    
    syntax_results = {}
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            compile(source, file_path, 'exec')
            syntax_results[file_path] = True
            print(f"✅ {file_path}: OK")
            
        except SyntaxError as e:
            syntax_results[file_path] = False
            print(f"❌ {file_path}: 構文エラー - {e}")
        except FileNotFoundError:
            syntax_results[file_path] = False
            print(f"❌ {file_path}: ファイルが見つかりません")
        except Exception as e:
            syntax_results[file_path] = False
            print(f"❌ {file_path}: エラー - {e}")
    
    passed = sum(syntax_results.values())
    total = len(syntax_results)
    print(f"\n構文チェック結果: {passed}/{total} 合格")
    
    return passed == total

if __name__ == "__main__":
    print("F12キーレスポンス改善の包括的検証を開始します...\n")
    
    # 構文チェック
    syntax_ok = test_syntax_check()
    
    if syntax_ok:
        # レスポンス改善テスト
        response_ok = test_response_improvements()
        
        if response_ok:
            print("\n🎉 全テスト合格！F12キーレスポンス改善が正常に実装されました。")
            print("\n次のステップ:")
            print("1. 依存関係のインストール: pip install -r requirements.txt")
            print("2. 実際のゲーム環境でのF12キーテスト")
            print("3. サイドボタン（F12）の体感レスポンス確認")
            sys.exit(0)
        else:
            print("\n⚠️ 一部のレスポンステストが失敗しました。")
            sys.exit(1)
    else:
        print("\n❌ 構文エラーがあります。修正が必要です。")
        sys.exit(1)
#!/usr/bin/env python3
"""
POE Macro v3.0 - Overlay Window Test Script
オーバーレイウィンドウ機能のテスト用スクリプト
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_area_selector():
    """AreaSelectorのテスト"""
    print("=== AreaSelector Test ===")
    
    try:
        from src.features.area_selector import AreaSelector
        
        selector = AreaSelector()
        
        # 設定概要を表示
        summary = selector.get_config_summary()
        print("設定概要:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # モニター情報を表示
        monitor_info = selector.get_monitor_info()
        print(f"\nモニター情報:")
        print(f"  モニター数: {monitor_info['count']}")
        for monitor in monitor_info["monitors"]:
            print(f"  モニター {monitor['index']}: {monitor['width']}x{monitor['height']} "
                  f"at ({monitor['x']}, {monitor['y']}) {'(Primary)' if monitor['is_primary'] else ''}")
        
        # プリセット適用テスト
        print(f"\nプリセット適用テスト:")
        current_resolution = selector.get_current_resolution()
        print(f"  現在の解像度: {current_resolution}")
        
        if selector.apply_current_resolution_preset():
            print("  プリセット適用成功")
            area = selector.get_flask_area()
            print(f"  適用されたエリア: {area}")
        else:
            print("  プリセット適用失敗")
            
        print("AreaSelector Test: PASSED\n")
        return True
        
    except Exception as e:
        print(f"AreaSelector Test: FAILED - {e}\n")
        return False

def test_overlay_window():
    """OverlayWindowのテスト"""
    print("=== OverlayWindow Test ===")
    
    try:
        from src.features.overlay_window import OverlayWindow
        from src.features.area_selector import AreaSelector
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # AreaSelectorから初期設定を取得
        selector = AreaSelector()
        area = selector.get_flask_area()
        
        # オーバーレイウィンドウを作成
        overlay = OverlayWindow(
            area.get('x', 245),
            area.get('y', 850),
            area.get('width', 400),
            area.get('height', 120)
        )
        
        # イベントハンドラー
        def on_area_changed(x, y, w, h):
            print(f"  エリア変更: ({x}, {y}, {w}, {h})")
            
        def on_settings_saved():
            print("  設定保存されました")
            
        def on_overlay_closed():
            print("  オーバーレイが閉じられました")
            app.quit()
        
        # シグナル接続
        overlay.area_changed.connect(on_area_changed)
        overlay.settings_saved.connect(on_settings_saved)
        overlay.overlay_closed.connect(on_overlay_closed)
        
        # オーバーレイを表示
        overlay.show_overlay()
        
        print("オーバーレイウィンドウが表示されました")
        print("操作方法:")
        print("  - マウスドラッグ: 移動")
        print("  - Shift+ドラッグ: サイズ変更")
        print("  - マウスホイール: スケール調整")
        print("  - 矢印キー: 1px単位移動")
        print("  - Shift+矢印: サイズ調整")
        print("  - Ctrl+S: 設定保存")
        print("  - F9: 表示/非表示切り替え")
        print("  - F10: 終了")
        
        # アプリケーション実行
        result = app.exec_()
        
        print("OverlayWindow Test: PASSED\n")
        return True
        
    except Exception as e:
        print(f"OverlayWindow Test: FAILED - {e}\n")
        return False

def test_integration():
    """統合テスト"""
    print("=== Integration Test ===")
    
    try:
        from src.features.area_selector import AreaSelector
        from src.features.image_recognition import TinctureDetector
        
        # AreaSelector初期化
        selector = AreaSelector()
        
        # TinctureDetectorにAreaSelectorを渡して初期化
        detector = TinctureDetector(
            monitor_config="Primary",
            sensitivity=0.7,
            area_selector=selector
        )
        
        # 検出エリア情報を取得
        info = detector.get_detection_area_info()
        print("統合検出エリア情報:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print("Integration Test: PASSED\n")
        return True
        
    except Exception as e:
        print(f"Integration Test: FAILED - {e}\n")
        return False

def main():
    """メイン関数"""
    print("POE Macro v3.0 - Overlay Window Test")
    print("=" * 50)
    
    # 各テストを実行
    tests_passed = 0
    total_tests = 3
    
    if test_area_selector():
        tests_passed += 1
    
    if test_integration():
        tests_passed += 1
    
    if test_overlay_window():
        tests_passed += 1
    
    # 結果表示
    print("=" * 50)
    print(f"テスト結果: {tests_passed}/{total_tests} 合格")
    
    if tests_passed == total_tests:
        print("全てのテストが合格しました！")
        return 0
    else:
        print("一部のテストが失敗しました。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
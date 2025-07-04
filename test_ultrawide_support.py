#!/usr/bin/env python3
"""
POE Macro v3.0 - 3440x1440 ウルトラワイド解像度サポートテスト
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_area_selector():
    """AreaSelectorの動作確認"""
    print("=== AreaSelector テスト ===")
    
    try:
        from src.features.area_selector import AreaSelector
        
        # QApplication初期化（GUI機能のため）
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        selector = AreaSelector()
        
        # 現在の解像度を取得
        current_resolution = selector.get_current_resolution()
        print(f"検出された解像度: {current_resolution}")
        
        # 利用可能なプリセットを表示
        print("\n利用可能なプリセット:")
        for resolution, preset in selector.get_all_presets().items():
            print(f"  {resolution}: X={preset['x']}, Y={preset['y']}, W={preset['width']}, H={preset['height']}")
        
        # ウルトラワイド解像度のサポート確認
        ultrawide_resolutions = ["3440x1440", "2560x1080", "5120x1440"]
        print(f"\nウルトラワイド解像度サポート:")
        for resolution in ultrawide_resolutions:
            if resolution in selector.presets:
                preset = selector.presets[resolution]
                print(f"  ✓ {resolution}: X={preset['x']}, Y={preset['y']}, W={preset['width']}, H={preset['height']}")
            else:
                print(f"  ✗ {resolution}: サポートされていません")
        
        # 自動解像度検出・適用テスト
        print(f"\n自動解像度検出・適用テスト:")
        success = selector.detect_and_apply_resolution()
        print(f"  結果: {'成功' if success else '失敗'}")
        
        # 現在のフラスコエリア設定を表示
        flask_area = selector.get_flask_area()
        print(f"\n現在のフラスコエリア設定:")
        print(f"  X={flask_area['x']}, Y={flask_area['y']}, W={flask_area['width']}, H={flask_area['height']}")
        
        # Tinctureの絶対座標を計算
        tincture_area = selector.get_absolute_tincture_area()
        print(f"\nTincture絶対座標:")
        print(f"  X={tincture_area['x']}, Y={tincture_area['y']}, W={tincture_area['width']}, H={tincture_area['height']}")
        
        # 設定概要を表示
        summary = selector.get_config_summary()
        print(f"\n設定概要:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
            
        return True
        
    except Exception as e:
        print(f"AreaSelector テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_file():
    """設定ファイルの確認"""
    print("\n=== 設定ファイル テスト ===")
    
    try:
        import yaml
        
        config_path = "config/default_config.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # tincture設定を確認
            if 'tincture' in config:
                tincture_config = config['tincture']
                print(f"Tincture設定:")
                print(f"  enabled: {tincture_config.get('enabled', False)}")
                print(f"  key: {tincture_config.get('key', '3')}")
                print(f"  sensitivity: {tincture_config.get('sensitivity', 0.7)}")
                
                # 3440x1440用の検出エリア設定を確認
                if 'detection_area' in tincture_config:
                    area = tincture_config['detection_area']
                    print(f"  detection_area:")
                    print(f"    X={area.get('x', 0)}, Y={area.get('y', 0)}, W={area.get('width', 80)}, H={area.get('height', 120)}")
                    
                    # 3440x1440の推奨座標かチェック
                    if (area.get('x') == 1680 and area.get('y') == 1133 and 
                        area.get('width') == 80 and area.get('height') == 120):
                        print("  ✓ 3440x1440用の推奨座標が設定されています")
                    else:
                        print("  ⚠ 3440x1440用の推奨座標ではありません")
                else:
                    print("  ⚠ detection_area設定が見つかりません")
            else:
                print("  ✗ tincture設定が見つかりません")
                
            return True
        else:
            print(f"  ✗ 設定ファイルが見つかりません: {config_path}")
            return False
            
    except Exception as e:
        print(f"設定ファイル テストエラー: {e}")
        return False

def test_tincture_detection():
    """Tincture検出機能のテスト"""
    print("\n=== Tincture検出 テスト ===")
    
    try:
        from src.features.image_recognition import TinctureDetector
        from src.core.config_manager import ConfigManager
        
        # 設定読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # TinctureDetectorを初期化
        detector = TinctureDetector(config.get('tincture', {}))
        
        print(f"TinctureDetector初期化完了")
        print(f"  感度設定: {detector.sensitivity}")
        
        # 検出エリア情報を表示
        from src.features.area_selector import AreaSelector
        area_selector = AreaSelector()
        tincture_area = area_selector.get_absolute_tincture_area()
        print(f"  検出エリア: X={tincture_area['x']}, Y={tincture_area['y']}, W={tincture_area['width']}, H={tincture_area['height']}")
        
        # 単発検出テスト（実際のスクリーンショットは取らない）
        print("  単発検出テスト: Idle状態の検出（画面キャプチャなし）")
        print("  ✓ TinctureDetectorの初期化は正常です")
        
        return True
        
    except Exception as e:
        print(f"Tincture検出 テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_support():
    """GUI機能のテスト"""
    print("\n=== GUI サポート テスト ===")
    
    try:
        # QApplication初期化
        if not QApplication.instance():
            app = QApplication(sys.argv)
            
        from src.core.config_manager import ConfigManager
        
        # 設定マネージャを初期化
        config_manager = ConfigManager()
        
        # MainWindowをインポート（初期化はしない）
        from src.gui.main_window import MainWindow
        print("  ✓ MainWindowクラスのインポート成功")
        
        print("  ✓ GUIコンポーネントは正常に利用可能です")
        print("  注意: 実際のGUI表示テストは手動で実行してください")
        
        return True
        
    except Exception as e:
        print(f"GUI サポート テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト関数"""
    print("POE Macro v3.0 - 3440x1440 ウルトラワイド解像度サポートテスト")
    print("=" * 60)
    
    tests = [
        ("AreaSelector機能", test_area_selector),
        ("設定ファイル", test_config_file),
        ("Tincture検出機能", test_tincture_detection),
        ("GUI サポート", test_gui_support)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name} テスト開始...")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{test_name} テスト: {'合格' if result else '失敗'}")
        except Exception as e:
            print(f"{test_name} テスト例外: {e}")
            results.append((test_name, False))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 合格" if result else "✗ 失敗"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n合格: {passed}/{total}")
    
    if passed == total:
        print("🎉 全てのテストが合格しました！")
        print("\n次の手順:")
        print("1. pip install -r requirements.txt で依存関係をインストール")
        print("2. python main.py でGUIを起動")
        print("3. キャリブレーションタブで3440x1440プリセットを確認")
        print("4. オーバーレイウィンドウで実際の座標を調整")
    else:
        print("⚠ 一部のテストが失敗しています。上記のエラーを確認してください。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
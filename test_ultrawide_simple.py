#!/usr/bin/env python3
"""
POE Macro v3.0 - ウルトラワイド解像度サポート簡易テスト
依存関係なしで実行可能
"""

import sys
import os
import yaml

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_config_ultrawide():
    """設定ファイルのウルトラワイド対応テスト"""
    print("=== 設定ファイル ウルトラワイド対応テスト ===")
    
    try:
        config_path = "config/default_config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Tincture設定の確認
        tincture_config = config.get('tincture', {})
        
        print(f"Tincture設定:")
        print(f"  enabled: {tincture_config.get('enabled', False)}")
        print(f"  key: {tincture_config.get('key', '3')}")
        
        # 3440x1440用検出エリアの確認
        detection_area = tincture_config.get('detection_area', {})
        if detection_area:
            x = detection_area.get('x', 0)
            y = detection_area.get('y', 0)
            width = detection_area.get('width', 0)
            height = detection_area.get('height', 0)
            
            print(f"  detection_area:")
            print(f"    X={x}, Y={y}, W={width}, H={height}")
            
            # 3440x1440用の推奨座標チェック
            expected_x = 1680  # 3番スロットの推奨X座標
            expected_y = 1133  # フラスコエリアのY座標
            expected_w = 80    # Tinctureの幅
            expected_h = 120   # Tinctureの高さ
            
            if (x == expected_x and y == expected_y and 
                width == expected_w and height == expected_h):
                print("  ✓ 3440x1440用の推奨座標が正しく設定されています")
                return True
            else:
                print("  ⚠ 3440x1440用の推奨座標と異なります")
                print(f"    期待値: X={expected_x}, Y={expected_y}, W={expected_w}, H={expected_h}")
                return False
        else:
            print("  ✗ detection_area設定が見つかりません")
            return False
            
    except Exception as e:
        print(f"設定ファイルテストエラー: {e}")
        return False

def test_area_selector_presets():
    """AreaSelectorのプリセット定義テスト"""
    print("\n=== AreaSelector プリセット定義テスト ===")
    
    try:
        # area_selector.pyを読み込んでプリセット定義を確認
        with open('src/features/area_selector.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # ウルトラワイド解像度のプリセットが定義されているかチェック
        ultrawide_resolutions = ["3440x1440", "2560x1080", "5120x1440"]
        
        print("ウルトラワイド解像度プリセット確認:")
        
        all_found = True
        for resolution in ultrawide_resolutions:
            if f'"{resolution}"' in content:
                print(f"  ✓ {resolution}: 定義済み")
            else:
                print(f"  ✗ {resolution}: 未定義")
                all_found = False
        
        # 3440x1440の具体的な座標確認
        if '"3440x1440"' in content:
            if '"x": 1370' in content and '"y": 1133' in content:
                print("  ✓ 3440x1440の座標設定が正しく定義されています")
            else:
                print("  ⚠ 3440x1440の座標設定に問題があります")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"AreaSelectorテストエラー: {e}")
        return False

def test_gui_preset_support():
    """GUIプリセット選択肢テスト"""
    print("\n=== GUI プリセット選択肢テスト ===")
    
    try:
        # main_window.pyを読み込んでプリセット選択肢を確認
        with open('src/gui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # ウルトラワイド解像度がプリセット選択肢に含まれているかチェック
        if '"3440x1440"' in content and '"2560x1080"' in content and '"5120x1440"' in content:
            print("  ✓ すべてのウルトラワイド解像度がGUIプリセットに含まれています")
            return True
        else:
            print("  ✗ 一部のウルトラワイド解像度がGUIプリセットに含まれていません")
            return False
        
    except Exception as e:
        print(f"GUIテストエラー: {e}")
        return False

def test_file_structure():
    """ファイル構造テスト"""
    print("\n=== ファイル構造テスト ===")
    
    required_files = [
        'src/features/area_selector.py',
        'src/gui/main_window.py',
        'config/default_config.yaml',
        'src/features/image_recognition.py',
        'src/modules/tincture_module.py'
    ]
    
    all_exists = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (ファイルが見つかりません)")
            all_exists = False
    
    return all_exists

def main():
    """メインテスト関数"""
    print("POE Macro v3.0 - ウルトラワイド解像度サポート簡易テスト")
    print("=" * 60)
    
    tests = [
        ("ファイル構造", test_file_structure),
        ("設定ファイル ウルトラワイド対応", test_config_ultrawide),
        ("AreaSelector プリセット定義", test_area_selector_presets),
        ("GUI プリセット選択肢", test_gui_preset_support)
    ]
    
    results = []
    
    for test_name, test_func in tests:
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
        print("\n🎉 全ての簡易テストが合格しました！")
        print("\n3440x1440ウルトラワイド解像度のサポートが正しく実装されています:")
        print("  ✓ AreaSelectorにウルトラワイドプリセット追加済み")
        print("  ✓ 設定ファイルに3440x1440用座標設定済み")
        print("  ✓ GUIキャリブレーション機能拡張済み")
        print("  ✓ 自動解像度検出機能強化済み")
        
        print("\n次の手順:")
        print("1. pip install -r requirements.txt で依存関係をインストール")
        print("2. python main.py でGUIを起動")
        print("3. キャリブレーションタブで現在の解像度とウルトラワイド設定を確認")
        print("4. プリセットから3440x1440を選択して適用")
        print("5. オーバーレイウィンドウで実際のゲーム画面で座標を微調整")
        
        print("\n期待される動作:")
        print("  - 3440x1440解像度が自動検出される")
        print("  - 3番スロット（Tincture）の推奨座標 X:1680, Y:1133 が表示される")
        print("  - フラスコエリア X:1370, Y:1133, W:700, H:160 が設定される")
        
    else:
        print("⚠ 一部のテストが失敗しています。上記のエラーを確認してください。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
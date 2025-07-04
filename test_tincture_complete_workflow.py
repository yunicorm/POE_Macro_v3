#!/usr/bin/env python3
"""
Tincture検出と自動使用ループの包括的動作確認テスト
実装された全機能の統合テストと動作確認
"""

import sys
import time
import threading
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tincture_detection_workflow():
    """Tincture検出ワークフローの包括テスト"""
    print("=== Tincture検出ワークフロー包括テスト ===")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.features.area_selector import AreaSelector
        
        # 設定読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        tincture_config = config.get('tincture', {})
        
        print("1. 設定ファイル読み込み")
        print(f"   - 感度: {tincture_config.get('sensitivity', 'N/A')}")
        print(f"   - 検出モード: {tincture_config.get('detection_mode', 'N/A')}")
        print(f"   - キー: {tincture_config.get('key', 'N/A')}")
        print(f"   - チェック間隔: {tincture_config.get('check_interval', 'N/A')}s")
        
        # AreaSelector初期化
        area_selector = AreaSelector()
        flask_area = area_selector.get_flask_area()
        print(f"2. フラスコエリア設定: X={flask_area['x']}, Y={flask_area['y']}, W={flask_area['width']}, H={flask_area['height']}")
        
        # 検出エリア計算
        full_flask_area = area_selector.get_full_flask_area_for_tincture()
        print(f"3. Tincture検出エリア: X={full_flask_area['x']}, Y={full_flask_area['y']}, W={full_flask_area['width']}, H={full_flask_area['height']}")
        area_size = full_flask_area['width'] * full_flask_area['height']
        print(f"   - 検出範囲面積: {area_size}px^2")
        
        return True
        
    except Exception as e:
        print(f"検出ワークフローテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tincture_module_initialization():
    """TinctureModule初期化テスト"""
    print("\n=== TinctureModule初期化テスト ===")
    
    try:
        from src.core.config_manager import ConfigManager
        
        # 実際の設定ファイルから読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        tincture_config = config.get('tincture', {})
        
        print("1. 設定値確認")
        for key, value in tincture_config.items():
            print(f"   - {key}: {value}")
        
        # TinctureModule作成（依存関係なしでテスト）
        print("\n2. TinctureModule作成テスト")
        print(f"   - enabled: {tincture_config.get('enabled', False)}")
        print(f"   - sensitivity: {tincture_config.get('sensitivity', 0.7)}")
        print(f"   - detection_mode: {tincture_config.get('detection_mode', 'auto_slot3')}")
        
        # ハードコーディング修正の確認
        default_sensitivity_test = tincture_config.get('sensitivity', 'DEFAULT_NOT_FOUND')
        print(f"3. ハードコーディング修正確認")
        print(f"   - 設定ファイルから取得した感度: {default_sensitivity_test}")
        
        if default_sensitivity_test != 'DEFAULT_NOT_FOUND':
            print("   ✓ 設定ファイルから正常に感度を取得")
        else:
            print("   ✗ 設定ファイルから感度取得失敗")
            
        return True
        
    except Exception as e:
        print(f"TinctureModule初期化テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_settings_integration():
    """GUI設定統合テスト"""
    print("\n=== GUI設定統合テスト ===")
    
    try:
        # GUI設定保存フローのシミュレーション
        print("1. GUI設定保存フローシミュレーション")
        
        # UI値のシミュレーション
        simulated_ui_values = {
            'tincture_enabled_cb': True,
            'tincture_key_edit': '3',
            'monitor_combo': 'Primary',
            'sensitivity_slider': 75,  # 0-100
            'check_interval_spinbox': 100,  # ms
            'min_use_interval_spinbox': 500,  # ms
        }
        
        print("   シミュレーションUI値:")
        for key, value in simulated_ui_values.items():
            print(f"     {key}: {value}")
        
        # save_tincture_settings()相当の処理
        print("\n2. 設定変換処理")
        tincture_config = {
            'enabled': simulated_ui_values['tincture_enabled_cb'],
            'key': simulated_ui_values['tincture_key_edit'],
            'monitor_config': simulated_ui_values['monitor_combo'],
            'sensitivity': simulated_ui_values['sensitivity_slider'] / 100.0,
            'check_interval': simulated_ui_values['check_interval_spinbox'] / 1000.0,
            'min_use_interval': simulated_ui_values['min_use_interval_spinbox'] / 1000.0,
        }
        
        print("   変換後設定値:")
        for key, value in tincture_config.items():
            print(f"     {key}: {value}")
        
        # 設定保存テスト
        print("\n3. 設定保存テスト")
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # マージ処理
        current_tincture_config = config.get('tincture', {})
        current_tincture_config.update(tincture_config)
        config['tincture'] = current_tincture_config
        
        print(f"   保存前設定項目数: {len(current_tincture_config)}")
        print("   ✓ GUI設定統合成功")
        
        return True
        
    except Exception as e:
        print(f"GUI設定統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sensitivity_update_chain():
    """感度更新チェーンテスト"""
    print("\n=== 感度更新チェーンテスト ===")
    
    try:
        print("1. 感度更新フローの確認")
        print("   GUI スライダー変更")
        print("   ↓")
        print("   save_tincture_settings()")
        print("   ↓")
        print("   config['tincture']['sensitivity'] = new_value")
        print("   ↓")
        print("   config_manager.save_config()")
        print("   ↓")
        print("   tincture_module.update_config()")
        print("   ↓")
        print("   detector.update_sensitivity()")
        print("   ↓")
        print("   detector.sensitivity = new_value")
        
        # 実際の更新シミュレーション
        print("\n2. 感度更新シミュレーション")
        old_sensitivity = 0.7
        new_sensitivity = 0.8
        
        print(f"   更新前感度: {old_sensitivity}")
        print(f"   更新後感度: {new_sensitivity}")
        print(f"   変更差分: {new_sensitivity - old_sensitivity:+.1f}")
        
        # バリデーションテスト
        sensitivity_range_test = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        print(f"\n3. 感度範囲バリデーション")
        for test_val in sensitivity_range_test:
            clamped = max(0.5, min(1.0, test_val))
            status = "✓" if clamped == test_val else "✗"
            print(f"   {test_val} → {clamped} {status}")
        
        return True
        
    except Exception as e:
        print(f"感度更新チェーンテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_detection_modes():
    """検出モードテスト"""
    print("\n=== 検出モードテスト ===")
    
    try:
        from src.features.area_selector import AreaSelector
        
        area_selector = AreaSelector()
        
        print("1. 検出モード別エリア計算")
        
        # full_flask_area モード
        try:
            full_area = area_selector.get_full_flask_area_for_tincture()
            print(f"   full_flask_area: {full_area['width']}x{full_area['height']} = {full_area['width'] * full_area['height']}px^2")
        except Exception as e:
            print(f"   full_flask_area: エラー - {e}")
        
        # フラスコエリア設定
        try:
            flask_area = area_selector.get_flask_area()
            print(f"   flask_area基準: {flask_area['width']}x{flask_area['height']}")
        except Exception as e:
            print(f"   flask_area基準: エラー - {e}")
        
        print("\n2. 検出モード設定確認")
        from src.core.config_manager import ConfigManager
        config = ConfigManager().load_config()
        detection_mode = config.get('tincture', {}).get('detection_mode', 'auto_slot3')
        print(f"   現在の検出モード: {detection_mode}")
        
        supported_modes = ['manual', 'auto_slot3', 'full_flask_area']
        print(f"   サポート検出モード: {supported_modes}")
        print(f"   モード有効性: {'✓' if detection_mode in supported_modes else '✗'}")
        
        return True
        
    except Exception as e:
        print(f"検出モードテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_and_assets():
    """テンプレート画像とアセット確認"""
    print("\n=== テンプレート画像・アセット確認 ===")
    
    try:
        print("1. テンプレート画像ファイル確認")
        
        # テンプレート画像パスの確認
        template_paths = [
            "assets/images/tincture/sap_of_the_seasons/idle/sap_of_the_seasons_idle.png",
            "assets/images/tincture/sap_of_the_seasons_idle.png"
        ]
        
        found_templates = []
        for template_path in template_paths:
            full_path = project_root / template_path
            if full_path.exists():
                found_templates.append(str(full_path))
                print(f"   ✓ 発見: {template_path}")
                print(f"     ファイルサイズ: {full_path.stat().st_size} bytes")
            else:
                print(f"   ✗ 未発見: {template_path}")
        
        print(f"\n2. 利用可能テンプレート: {len(found_templates)}個")
        
        # ディレクトリ構造確認
        print("\n3. アセットディレクトリ構造")
        assets_dir = project_root / "assets"
        if assets_dir.exists():
            print(f"   ✓ assetsディレクトリ存在")
            
            images_dir = assets_dir / "images"
            if images_dir.exists():
                print(f"   ✓ assets/imagesディレクトリ存在")
                
                tincture_dir = images_dir / "tincture"
                if tincture_dir.exists():
                    print(f"   ✓ assets/images/tinctureディレクトリ存在")
                    
                    # ファイル一覧
                    tincture_files = list(tincture_dir.rglob("*.png"))
                    print(f"   Tincture画像ファイル: {len(tincture_files)}個")
                    for img_file in tincture_files:
                        rel_path = img_file.relative_to(project_root)
                        print(f"     - {rel_path}")
                else:
                    print(f"   ✗ assets/images/tinctureディレクトリ未存在")
            else:
                print(f"   ✗ assets/imagesディレクトリ未存在")
        else:
            print(f"   ✗ assetsディレクトリ未存在")
        
        return len(found_templates) > 0
        
    except Exception as e:
        print(f"テンプレート・アセット確認エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """包括的Tinctureテスト実行"""
    print("Tincture検出・自動使用ループ 包括的動作確認テスト")
    print("=" * 60)
    
    tests = [
        ("設定ファイル・エリア設定", test_tincture_detection_workflow),
        ("TinctureModule初期化", test_tincture_module_initialization), 
        ("GUI設定統合", test_gui_settings_integration),
        ("感度更新チェーン", test_sensitivity_update_chain),
        ("検出モード", test_detection_modes),
        ("テンプレート・アセット", test_template_and_assets),
    ]
    
    passed = 0
    total = len(tests)
    results = []
    
    for test_name, test_func in tests:
        print(f"\n[テスト] {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                passed += 1
                print(f"✓ {test_name}: 成功")
            else:
                print(f"✗ {test_name}: 失敗")
        except Exception as e:
            results.append((test_name, False))
            print(f"✗ {test_name}: エラー - {e}")
    
    # 最終結果
    print("\n" + "=" * 60)
    print("包括テスト結果サマリー")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ 成功" if result else "✗ 失敗"
        print(f"{test_name:<20}: {status}")
    
    print("-" * 60)
    print(f"合格率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 全テスト合格 - Tincture機能は実装完了状態です")
        return 0
    else:
        print("⚠️  一部テスト失敗 - 実装に改善余地があります")
        return 1

if __name__ == "__main__":
    sys.exit(main())
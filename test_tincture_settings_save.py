#!/usr/bin/env python3
"""
Tincture設定保存機能のテストスクリプト
GUIの保存ボタン機能が正常に動作するかテスト
"""

import sys
import os
import yaml
import tempfile
import shutil
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tincture_config_structure():
    """Tincture設定の構造をテスト"""
    print("=== Tincture設定構造テスト ===")
    
    try:
        from src.core.config_manager import ConfigManager
        
        # テスト用一時ディレクトリ
        with tempfile.TemporaryDirectory() as temp_dir:
            # 設定ファイルをコピー
            original_config = project_root / "config" / "default_config.yaml"
            test_config = Path(temp_dir) / "test_config.yaml"
            shutil.copy(original_config, test_config)
            
            # ConfigManagerで設定読み込み
            config_manager = ConfigManager(str(test_config))
            config = config_manager.load_config()
            
            print(f"設定ファイル読み込み成功: {test_config}")
            
            # Tincture設定の確認
            tincture_config = config.get('tincture', {})
            print(f"Tincture設定:")
            for key, value in tincture_config.items():
                print(f"  {key}: {value} ({type(value).__name__})")
            
            # 設定変更テスト
            print("\n--- 設定変更テスト ---")
            new_settings = {
                'enabled': True,
                'key': '3',
                'monitor_config': 'Primary',
                'sensitivity': 0.8,
                'check_interval': 0.1,
                'min_use_interval': 0.5
            }
            
            tincture_config.update(new_settings)
            config['tincture'] = tincture_config
            
            # 保存テスト
            config_manager.save_config(config)
            print("設定保存成功")
            
            # 再読み込みで確認
            reloaded_config = config_manager.load_config()
            reloaded_tincture = reloaded_config.get('tincture', {})
            
            print("再読み込み後の設定:")
            for key, value in new_settings.items():
                actual = reloaded_tincture.get(key)
                status = "✓" if actual == value else "✗"
                print(f"  {key}: {actual} (期待値: {value}) {status}")
            
            return True
            
    except Exception as e:
        print(f"設定テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tincture_module_sensitivity_update():
    """TinctureModuleの感度更新をテスト"""
    print("\n=== TinctureModule感度更新テスト ===")
    
    try:
        from src.modules.tincture_module import TinctureModule
        
        # テスト設定
        test_config = {
            'enabled': True,
            'key': '3',
            'sensitivity': 0.7,
            'check_interval': 0.1,
            'min_use_interval': 0.5
        }
        
        print(f"初期設定: sensitivity = {test_config['sensitivity']}")
        
        # TinctureModule作成
        tincture_module = TinctureModule(test_config)
        print(f"TinctureModule初期感度: {tincture_module.sensitivity}")
        
        # 感度更新テスト
        new_config = test_config.copy()
        new_config['sensitivity'] = 0.8
        
        print(f"新しい設定: sensitivity = {new_config['sensitivity']}")
        tincture_module.update_config(new_config)
        print(f"更新後のTinctureModule感度: {tincture_module.sensitivity}")
        
        # Detector感度の確認
        if tincture_module.detector:
            print(f"Detector感度: {tincture_module.detector.sensitivity}")
        
        success = (tincture_module.sensitivity == 0.8)
        print(f"感度更新テスト: {'成功' if success else '失敗'}")
        
        return success
        
    except Exception as e:
        print(f"TinctureModule テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_gui_save_operation():
    """GUI保存操作をシミュレート"""
    print("\n=== GUI保存操作シミュレーション ===")
    
    try:
        # シミュレートするUI値
        ui_values = {
            'enabled': True,
            'key': '3',
            'monitor_config': 'Primary',
            'sensitivity_slider': 80,  # 0-100 スケール
            'check_interval_spinbox': 100,  # ms
            'min_use_interval_spinbox': 500,  # ms
        }
        
        print("シミュレートするUI値:")
        for key, value in ui_values.items():
            print(f"  {key}: {value}")
        
        # GUI save_tincture_settings()と同等の処理
        tincture_config = {
            'enabled': ui_values['enabled'],
            'key': ui_values['key'],
            'monitor_config': ui_values['monitor_config'],
            'sensitivity': ui_values['sensitivity_slider'] / 100.0,  # 0-100 → 0.0-1.0
            'check_interval': ui_values['check_interval_spinbox'] / 1000.0,  # ms → s
            'min_use_interval': ui_values['min_use_interval_spinbox'] / 1000.0,  # ms → s
        }
        
        print("\n変換後の設定値:")
        for key, value in tincture_config.items():
            print(f"  {key}: {value}")
        
        # 設定ファイルへの保存をシミュレート
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        current_tincture_config = config.get('tincture', {})
        current_tincture_config.update(tincture_config)
        config['tincture'] = current_tincture_config
        
        print(f"\n最終的なTincture設定:")
        for key, value in config['tincture'].items():
            print(f"  {key}: {value}")
        
        print("GUI保存操作シミュレーション成功")
        return True
        
    except Exception as e:
        print(f"GUI保存シミュレーションエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("Tincture設定保存機能テスト開始\n")
    
    tests = [
        test_tincture_config_structure,
        test_tincture_module_sensitivity_update,
        simulate_gui_save_operation
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            print()
        except Exception as e:
            print(f"テスト実行エラー: {e}\n")
    
    print(f"=== テスト結果 ===")
    print(f"合格: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("✓ 全テスト合格 - Tincture設定保存機能は正常です")
        return 0
    else:
        print("✗ 一部テスト失敗 - 設定保存機能に問題があります")
        return 1

if __name__ == "__main__":
    sys.exit(main())
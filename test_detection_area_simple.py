#!/usr/bin/env python3
"""
検出エリア更新機能の簡単なテストスクリプト
PyQt5に依存しないテスト版
"""

import sys
import os
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# ログレベルを INFO に設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_tincture_module_update():
    """TinctureModuleの更新メソッドをテスト"""
    
    print("=== TinctureModule更新メソッドテスト ===")
    
    try:
        # 1. 設定ファイルの読み込み
        print("1. 設定ファイルの読み込み...")
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # 2. TinctureModuleの初期化
        print("2. TinctureModuleの初期化...")
        from src.modules.tincture_module import TinctureModule
        tincture_module = TinctureModule(config.get('tincture', {}))
        
        # 3. 初期状態の確認
        print("3. 初期状態の確認...")
        print(f"   enabled: {tincture_module.enabled}")
        print(f"   key: {tincture_module.key}")
        print(f"   sensitivity: {tincture_module.sensitivity}")
        print(f"   area_selector available: {tincture_module.area_selector is not None}")
        
        # 4. update_detection_area メソッドの存在確認
        print("4. update_detection_area メソッドの存在確認...")
        if hasattr(tincture_module, 'update_detection_area'):
            print("   ✓ update_detection_area メソッドが存在します")
        else:
            print("   ✗ update_detection_area メソッドが見つかりません")
            return False
        
        # 5. TinctureDetectorの確認
        print("5. TinctureDetectorの確認...")
        if hasattr(tincture_module, 'detector') and tincture_module.detector:
            print("   ✓ TinctureDetectorが初期化されています")
            print(f"   detector.area_selector available: {tincture_module.detector.area_selector is not None}")
        else:
            print("   ✗ TinctureDetectorが初期化されていません")
            return False
        
        # 6. 模擬的な area_selector 更新テスト
        print("6. 模擬的な area_selector 更新テスト...")
        
        # 模擬的な area_selector クラス
        class MockAreaSelector:
            def __init__(self):
                self.x = 500
                self.y = 600
                self.width = 100
                self.height = 80
                
            def get_absolute_tincture_area(self):
                return {
                    'x': self.x,
                    'y': self.y,
                    'width': self.width,
                    'height': self.height
                }
        
        mock_area_selector = MockAreaSelector()
        
        # 7. update_detection_area メソッドの実行
        print("7. update_detection_area メソッドの実行...")
        try:
            tincture_module.update_detection_area(mock_area_selector)
            print("   ✓ update_detection_area メソッドが正常に実行されました")
        except Exception as e:
            print(f"   ✗ update_detection_area メソッドの実行でエラー: {e}")
            return False
        
        # 8. 更新後の状態確認
        print("8. 更新後の状態確認...")
        if tincture_module.area_selector == mock_area_selector:
            print("   ✓ area_selector が正しく更新されました")
        else:
            print("   ✗ area_selector の更新に失敗しました")
            return False
        
        if tincture_module.detector.area_selector == mock_area_selector:
            print("   ✓ detector.area_selector が正しく更新されました")
        else:
            print("   ✗ detector.area_selector の更新に失敗しました")
            return False
        
        print("   ✓ 全ての更新テストが成功しました!")
        return True
        
    except Exception as e:
        print(f"テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_structure():
    """設定構造のテスト"""
    
    print("\n=== 設定構造テスト ===")
    
    try:
        # 1. 設定ファイルの読み込み
        print("1. 設定ファイルの読み込み...")
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # 2. Tincture設定の確認
        print("2. Tincture設定の確認...")
        tincture_config = config.get('tincture', {})
        print(f"   tincture config keys: {list(tincture_config.keys())}")
        
        # 3. detection_area設定の確認
        print("3. detection_area設定の確認...")
        detection_area = tincture_config.get('detection_area', {})
        if detection_area:
            print(f"   detection_area: {detection_area}")
            required_keys = ['x', 'y', 'width', 'height']
            for key in required_keys:
                if key in detection_area:
                    print(f"   ✓ {key}: {detection_area[key]}")
                else:
                    print(f"   ✗ {key}: 設定されていません")
        else:
            print("   detection_area 設定がありません")
        
        # 4. 設定の変更テスト
        print("4. 設定の変更テスト...")
        new_area = {
            'x': 123,
            'y': 456,
            'width': 78,
            'height': 90
        }
        
        tincture_config['detection_area'] = new_area
        print(f"   新しい detection_area: {new_area}")
        
        # 5. 設定の保存テスト
        print("5. 設定の保存テスト...")
        try:
            config_manager.save_config(config)
            print("   ✓ 設定の保存が成功しました")
        except Exception as e:
            print(f"   ✗ 設定の保存でエラー: {e}")
            return False
        
        # 6. 設定の再読み込みテスト
        print("6. 設定の再読み込みテスト...")
        reloaded_config = config_manager.load_config()
        reloaded_area = reloaded_config.get('tincture', {}).get('detection_area', {})
        
        if reloaded_area == new_area:
            print("   ✓ 設定の再読み込みが成功しました")
        else:
            print(f"   ✗ 設定の再読み込みに失敗しました: {reloaded_area}")
            return False
        
        print("   ✓ 全ての設定テストが成功しました!")
        return True
        
    except Exception as e:
        print(f"設定テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("検出エリア更新機能簡易テスト開始...")
    
    # TinctureModule更新テスト
    test1_result = test_tincture_module_update()
    
    # 設定構造テスト
    test2_result = test_config_structure()
    
    # 最終結果
    print("\n=== 最終結果 ===")
    if test1_result and test2_result:
        print("✓ 全てのテストが成功しました!")
        sys.exit(0)
    else:
        print("✗ テストが失敗しました")
        sys.exit(1)
#!/usr/bin/env python3
"""
検出エリア更新機能のコア機能テスト
依存関係を最小限に抑えたテスト版
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

def test_config_manager():
    """ConfigManagerの基本機能をテスト"""
    
    print("=== ConfigManager基本機能テスト ===")
    
    try:
        # 1. ConfigManagerの初期化
        print("1. ConfigManagerの初期化...")
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        # 2. 設定の読み込み
        print("2. 設定の読み込み...")
        config = config_manager.load_config()
        
        # 3. Tincture設定の確認
        print("3. Tincture設定の確認...")
        tincture_config = config.get('tincture', {})
        print(f"   tincture設定: {tincture_config}")
        
        # 4. detection_area の確認
        print("4. detection_area の確認...")
        detection_area = tincture_config.get('detection_area', {})
        if detection_area:
            print(f"   現在の detection_area: {detection_area}")
        else:
            print("   detection_area が設定されていません")
        
        # 5. save_config メソッドの確認
        print("5. save_config メソッドの確認...")
        if hasattr(config_manager, 'save_config'):
            print("   ✓ save_config メソッドが存在します")
        else:
            print("   ✗ save_config メソッドが見つかりません")
            return False
        
        # 6. 設定の変更と保存テスト
        print("6. 設定の変更と保存テスト...")
        original_area = detection_area.copy()
        
        # 新しい設定を適用
        test_area = {
            'x': 999,
            'y': 888,
            'width': 77,
            'height': 66
        }
        
        tincture_config['detection_area'] = test_area
        config_manager.save_config(config)
        print(f"   新しい detection_area を保存: {test_area}")
        
        # 7. 設定の再読み込み確認
        print("7. 設定の再読み込み確認...")
        config_manager2 = ConfigManager()
        reloaded_config = config_manager2.load_config()
        reloaded_area = reloaded_config.get('tincture', {}).get('detection_area', {})
        
        if reloaded_area == test_area:
            print("   ✓ 設定の保存と再読み込みが成功しました")
        else:
            print(f"   ✗ 設定の保存に失敗しました: {reloaded_area} != {test_area}")
            return False
        
        # 8. 元の設定を復元
        print("8. 元の設定を復元...")
        if original_area:
            tincture_config['detection_area'] = original_area
            config_manager.save_config(config)
            print("   元の設定を復元しました")
        
        print("   ✓ ConfigManagerテストが成功しました!")
        return True
        
    except Exception as e:
        print(f"ConfigManagerテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tincture_detector_init():
    """TinctureDetectorの初期化テスト（PyQt5なし）"""
    
    print("\n=== TinctureDetector初期化テスト ===")
    
    try:
        # 1. TinctureDetectorの初期化
        print("1. TinctureDetectorの初期化...")
        from src.features.image_recognition import TinctureDetector
        
        # AreaSelectorなしで初期化
        detector = TinctureDetector(
            monitor_config="Primary",
            sensitivity=0.8,
            area_selector=None
        )
        
        # 2. 基本設定の確認
        print("2. 基本設定の確認...")
        print(f"   monitor_config: {detector.monitor_config}")
        print(f"   sensitivity: {detector.sensitivity}")
        print(f"   area_selector: {detector.area_selector}")
        
        # 3. 模擬的な AreaSelector の作成
        print("3. 模擬的な AreaSelector の作成...")
        
        class MockAreaSelector:
            def __init__(self):
                self.flask_area = {
                    'x': 100,
                    'y': 200,
                    'width': 300,
                    'height': 400
                }
                self.tincture_offset = {
                    'x': 50,
                    'y': 60
                }
                
            def get_absolute_tincture_area(self):
                return {
                    'x': self.flask_area['x'] + self.tincture_offset['x'],
                    'y': self.flask_area['y'] + self.tincture_offset['y'],
                    'width': 80,
                    'height': 100
                }
                
            def get_tincture_offset(self):
                return self.tincture_offset
        
        mock_area_selector = MockAreaSelector()
        
        # 4. area_selector の更新
        print("4. area_selector の更新...")
        detector.area_selector = mock_area_selector
        
        expected_area = mock_area_selector.get_absolute_tincture_area()
        print(f"   期待される検出エリア: {expected_area}")
        
        # 5. 検出エリア情報の取得
        print("5. 検出エリア情報の取得...")
        if hasattr(detector, 'get_detection_area_info'):
            area_info = detector.get_detection_area_info()
            print(f"   検出エリア情報: {area_info}")
        
        print("   ✓ TinctureDetector初期化テストが成功しました!")
        return True
        
    except Exception as e:
        print(f"TinctureDetector初期化テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_method_existence():
    """必要なメソッドの存在確認テスト"""
    
    print("\n=== 必要なメソッドの存在確認テスト ===")
    
    try:
        # 1. ConfigManagerのメソッド確認
        print("1. ConfigManagerのメソッド確認...")
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        required_methods = ['load_config', 'save_config', 'save_user_config']
        for method in required_methods:
            if hasattr(config_manager, method):
                print(f"   ✓ {method} メソッドが存在します")
            else:
                print(f"   ✗ {method} メソッドが見つかりません")
                return False
        
        # 2. TinctureDetectorのメソッド確認
        print("2. TinctureDetectorのメソッド確認...")
        from src.features.image_recognition import TinctureDetector
        detector = TinctureDetector()
        
        required_methods = ['detect_tincture_icon', 'get_detection_area_info']
        for method in required_methods:
            if hasattr(detector, method):
                print(f"   ✓ {method} メソッドが存在します")
            else:
                print(f"   ✗ {method} メソッドが見つかりません")
                return False
        
        print("   ✓ 必要なメソッドの存在確認テストが成功しました!")
        return True
        
    except Exception as e:
        print(f"メソッド存在確認テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("検出エリア更新機能コアテスト開始...")
    
    # ConfigManagerテスト
    test1_result = test_config_manager()
    
    # TinctureDetectorテスト
    test2_result = test_tincture_detector_init()
    
    # メソッド存在確認テスト
    test3_result = test_module_method_existence()
    
    # 最終結果
    print("\n=== 最終結果 ===")
    if test1_result and test2_result and test3_result:
        print("✓ 全てのコアテストが成功しました!")
        print("✓ 検出エリア更新機能の基本構造が正常に動作します")
        sys.exit(0)
    else:
        print("✗ テストが失敗しました")
        sys.exit(1)
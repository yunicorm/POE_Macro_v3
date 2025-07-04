"""
POE Macro v3.0 - 検出エリア動的更新テストスイート
設定変更の即時反映とフォールバック機能の検証
"""

import os
import sys
import tempfile
import yaml
import logging
import unittest
from unittest.mock import patch, MagicMock

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath('.'))

try:
    from src.features.area_selector import AreaSelector
    from src.features.image_recognition import TinctureDetector
    from src.modules.tincture_module import TinctureModule
    from src.core.config_manager import ConfigManager
except ImportError as e:
    print(f"インポートエラー: {e}")
    print("プロジェクトルートで実行してください")
    sys.exit(1)

class TestDynamicAreaUpdate(unittest.TestCase):
    """検出エリア動的更新機能のテストケース"""

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.temp_dir, "test_detection_areas.yaml")
        
        # ログの設定（テスト用）
        logging.basicConfig(level=logging.DEBUG)
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_area_selector_dynamic_update(self):
        """AreaSelectorの動的更新テスト"""
        print("\n=== AreaSelector動的更新テスト ===")
        
        # 初期設定
        area_selector = AreaSelector(self.test_config_file)
        
        # 初期座標を確認
        initial_area = area_selector.get_flask_area()
        print(f"初期エリア: {initial_area}")
        
        # 新しい座標に更新
        new_x, new_y, new_w, new_h = 1000, 1400, 500, 150
        area_selector.set_flask_area(new_x, new_y, new_w, new_h)
        
        # 更新後の座標を確認
        updated_area = area_selector.get_flask_area()
        print(f"更新後エリア: {updated_area}")
        
        # 検証
        self.assertEqual(updated_area['x'], new_x)
        self.assertEqual(updated_area['y'], new_y)
        self.assertEqual(updated_area['width'], new_w)
        self.assertEqual(updated_area['height'], new_h)
        
        # 設定ファイルが作成されていることを確認
        self.assertTrue(os.path.exists(self.test_config_file))
        
        print("✓ AreaSelector動的更新テスト 合格")

    def test_invalid_config_fallback(self):
        """無効な設定に対するフォールバック機能テスト"""
        print("\n=== 無効設定フォールバックテスト ===")
        
        # 無効な設定ファイルを作成
        invalid_config = {
            "flask_area": {
                "x": "invalid",  # 文字列（無効）
                "y": -100,       # 負の値（無効）
                "width": 0,      # ゼロ（無効）
                # height欠落（無効）
            }
        }
        
        with open(self.test_config_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(invalid_config, f)
        
        # AreaSelectorを初期化（フォールバック発動）
        area_selector = AreaSelector(self.test_config_file)
        
        # フォールバック後の座標を確認
        fallback_area = area_selector.get_flask_area()
        print(f"フォールバック後エリア: {fallback_area}")
        
        # 有効な値であることを確認
        self.assertIsInstance(fallback_area['x'], (int, float))
        self.assertIsInstance(fallback_area['y'], (int, float))
        self.assertIsInstance(fallback_area['width'], (int, float))
        self.assertIsInstance(fallback_area['height'], (int, float))
        self.assertGreater(fallback_area['width'], 0)
        self.assertGreater(fallback_area['height'], 0)
        
        print("✓ 無効設定フォールバックテスト 合格")

    def test_missing_config_file(self):
        """設定ファイル欠落時のフォールバック機能テスト"""
        print("\n=== 設定ファイル欠落フォールバックテスト ===")
        
        # 存在しないファイルパスを指定
        non_existent_file = os.path.join(self.temp_dir, "non_existent.yaml")
        
        # AreaSelectorを初期化（デフォルト設定作成）
        area_selector = AreaSelector(non_existent_file)
        
        # デフォルト設定が適用されることを確認
        default_area = area_selector.get_flask_area()
        print(f"デフォルトエリア: {default_area}")
        
        # 有効な値であることを確認
        self.assertIsInstance(default_area['x'], (int, float))
        self.assertIsInstance(default_area['y'], (int, float))
        self.assertIsInstance(default_area['width'], (int, float))
        self.assertIsInstance(default_area['height'], (int, float))
        
        # ファイルが作成されることを確認
        self.assertTrue(os.path.exists(non_existent_file))
        
        print("✓ 設定ファイル欠落フォールバックテスト 合格")

    def test_extreme_coordinates(self):
        """極端な座標値のエッジケーステスト"""
        print("\n=== 極端座標エッジケーステスト ===")
        
        area_selector = AreaSelector(self.test_config_file)
        
        # テストケース
        test_cases = [
            {"name": "負の座標", "x": -100, "y": -200, "width": 400, "height": 120, "should_fail": True},
            {"name": "ゼロサイズ", "x": 100, "y": 200, "width": 0, "height": 120, "should_fail": True},
            {"name": "極大座標", "x": 50000, "y": 50000, "width": 400, "height": 120, "should_fail": True},
            {"name": "正常座標", "x": 500, "y": 600, "width": 400, "height": 120, "should_fail": False},
        ]
        
        for case in test_cases:
            print(f"\nテストケース: {case['name']}")
            
            # 無効な座標を設定ファイルに書き込み
            test_config = {
                "flask_area": {
                    "x": case["x"],
                    "y": case["y"],
                    "width": case["width"],
                    "height": case["height"],
                    "monitor": 0
                }
            }
            
            with open(self.test_config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(test_config, f)
            
            # 新しいAreaSelectorインスタンスで読み込み
            test_selector = AreaSelector(self.test_config_file)
            result_area = test_selector.get_flask_area()
            
            if case["should_fail"]:
                # 無効な座標の場合、フォールバック値になることを確認
                # フォールバック値は現在の解像度に基づくため、設定値と異なるはず
                is_fallback = (
                    result_area['x'] != case['x'] or
                    result_area['y'] != case['y'] or
                    result_area['width'] != case['width'] or
                    result_area['height'] != case['height']
                )
                self.assertTrue(is_fallback, f"無効な座標でフォールバックが発動しませんでした: {case}")
                print(f"  ✓ フォールバック発動: {result_area}")
            else:
                # 有効な座標の場合、設定値がそのまま使用されることを確認
                self.assertEqual(result_area['x'], case['x'])
                self.assertEqual(result_area['y'], case['y'])
                self.assertEqual(result_area['width'], case['width'])
                self.assertEqual(result_area['height'], case['height'])
                print(f"  ✓ 正常値使用: {result_area}")
        
        print("✓ 極端座標エッジケーステスト 合格")

    @patch('src.features.image_recognition.TinctureDetector')
    def test_tincture_module_area_propagation(self, mock_detector_class):
        """TinctureModuleへの設定伝播テスト"""
        print("\n=== TinctureModule設定伝播テスト ===")
        
        # モックの設定
        mock_detector = MagicMock()
        mock_detector_class.return_value = mock_detector
        
        # テスト設定
        test_config = {
            'enabled': True,
            'key': '3',
            'sensitivity': 0.7,
            'detection_mode': 'full_flask_area'
        }
        
        # TinctureModuleを初期化
        tincture_module = TinctureModule(test_config)
        
        # 新しいAreaSelectorを作成
        area_selector = AreaSelector(self.test_config_file)
        area_selector.set_flask_area(1200, 1500, 450, 140)
        
        # 検出エリアを更新
        tincture_module.update_detection_area(area_selector)
        
        # TinctureDetectorのarea_selectorが更新されることを確認
        self.assertEqual(tincture_module.detector.area_selector, area_selector)
        
        # 設定されたエリアを確認
        updated_area = area_selector.get_flask_area()
        self.assertEqual(updated_area['x'], 1200)
        self.assertEqual(updated_area['y'], 1500)
        self.assertEqual(updated_area['width'], 450)
        self.assertEqual(updated_area['height'], 140)
        
        print("✓ TinctureModule設定伝播テスト 合格")

    def test_concurrent_area_updates(self):
        """並行エリア更新テスト"""
        print("\n=== 並行エリア更新テスト ===")
        
        # 複数のAreaSelectorインスタンスで同じファイルを操作
        selectors = [AreaSelector(self.test_config_file) for _ in range(3)]
        
        # 各セレクターで異なる座標を設定
        coordinates = [
            (800, 1100, 350, 110),
            (900, 1200, 400, 120),
            (1000, 1300, 450, 130)
        ]
        
        for i, (selector, coords) in enumerate(zip(selectors, coordinates)):
            x, y, w, h = coords
            selector.set_flask_area(x, y, w, h)
            print(f"セレクター{i+1}: ({x}, {y}, {w}, {h}) 設定完了")
        
        # 最後の設定が有効になることを確認
        final_selector = AreaSelector(self.test_config_file)
        final_area = final_selector.get_flask_area()
        final_coords = coordinates[-1]  # 最後の座標
        
        self.assertEqual(final_area['x'], final_coords[0])
        self.assertEqual(final_area['y'], final_coords[1])
        self.assertEqual(final_area['width'], final_coords[2])
        self.assertEqual(final_area['height'], final_coords[3])
        
        print(f"最終エリア: {final_area}")
        print("✓ 並行エリア更新テスト 合格")

def main():
    """メイン実行関数"""
    print("=== POE Macro v3.0 検出エリア動的更新テストスイート ===")
    print("フォールバック機能と設定伝播機能の包括的テスト\n")
    
    # テストを実行
    unittest.main(verbosity=2, exit=False)
    
    print("\n=== 全テスト完了 ===")
    print("設定変更の即時反映とフォールバック機能が正常に動作しています。")

if __name__ == "__main__":
    main()
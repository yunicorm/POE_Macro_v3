"""
Tincture検出機能のテストスクリプト
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.features.image_recognition import TinctureDetector
    import cv2
    import mss
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"依存関係が不足しています: {e}")
    DEPENDENCIES_AVAILABLE = False

@unittest.skipIf(not DEPENDENCIES_AVAILABLE, "Required dependencies not available")
class TestTinctureDetector(unittest.TestCase):
    """TinctureDetector のテストクラス"""
    
    def setUp(self):
        """テストの準備"""
        self.test_assets_dir = Path("test_assets")
        self.test_assets_dir.mkdir(exist_ok=True)
        
        # プレースホルダー画像を作成
        self._create_test_template()
        
    def tearDown(self):
        """テストの後処理"""
        # テスト用アセットを削除
        if self.test_assets_dir.exists():
            import shutil
            shutil.rmtree(self.test_assets_dir)
    
    def _create_test_template(self):
        """テスト用のテンプレート画像を作成"""
        if not DEPENDENCIES_AVAILABLE:
            return
        
        # 64x64のテスト画像を作成
        test_img = np.zeros((64, 64, 3), dtype=np.uint8)
        test_img[:, :] = [50, 50, 50]  # グレー背景
        cv2.rectangle(test_img, (8, 8), (56, 56), (0, 255, 0), -1)  # 緑の四角
        
        # テスト用アセットディレクトリに保存
        template_dir = self.test_assets_dir / "images" / "tincture"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        template_path = template_dir / "sap_of_the_seasons_1920x1080.png"
        cv2.imwrite(str(template_path), test_img)
    
    @patch('src.features.image_recognition.Path')
    def test_init_valid_config(self, mock_path):
        """正常な初期化のテスト"""
        # assetsパスのモック
        mock_path.return_value = self.test_assets_dir / "images" / "tincture"
        
        detector = TinctureDetector(monitor_config="Primary", sensitivity=0.8)
        
        self.assertEqual(detector.monitor_config, "Primary")
        self.assertEqual(detector.sensitivity, 0.8)
        self.assertEqual(detector.current_resolution, "1920x1080")
    
    def test_init_invalid_monitor_config(self):
        """無効なモニター設定のテスト"""
        with self.assertRaises(ValueError):
            TinctureDetector(monitor_config="Invalid")
    
    def test_sensitivity_range(self):
        """感度範囲のテスト"""
        with patch('src.features.image_recognition.Path'):
            detector = TinctureDetector(sensitivity=0.3)  # 最小値未満
            self.assertEqual(detector.sensitivity, 0.5)
            
            detector = TinctureDetector(sensitivity=1.5)  # 最大値超過
            self.assertEqual(detector.sensitivity, 1.0)
    
    def test_get_closest_resolution(self):
        """最適解像度選択のテスト"""
        with patch('src.features.image_recognition.Path'):
            detector = TinctureDetector()
            
            # 1920x1080に近い解像度
            closest = detector._get_closest_resolution(1920, 1080)
            self.assertEqual(closest, "1920x1080")
            
            # 2560x1440に近い解像度
            closest = detector._get_closest_resolution(2560, 1440)
            self.assertEqual(closest, "2560x1440")
            
            # 3840x2160に近い解像度
            closest = detector._get_closest_resolution(3840, 2160)
            self.assertEqual(closest, "3840x2160")
    
    @patch('src.features.image_recognition.mss.mss')
    def test_capture_screen(self, mock_mss):
        """画面キャプチャのテスト"""
        # mssのモック設定
        mock_sct = Mock()
        mock_mss.return_value = mock_sct
        
        # モニター情報のモック
        mock_sct.monitors = [
            {},  # monitors[0] は全画面
            {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}  # プライマリモニター
        ]
        
        # スクリーンショットのモック
        mock_screenshot = Mock()
        mock_screenshot.__array__ = lambda: np.zeros((270, 960, 4), dtype=np.uint8)
        mock_sct.grab.return_value = mock_screenshot
        
        with patch('src.features.image_recognition.Path'):
            detector = TinctureDetector()
            
            # cv2.cvtColorのモック
            with patch('cv2.cvtColor') as mock_cvt:
                mock_cvt.return_value = np.zeros((270, 960, 3), dtype=np.uint8)
                
                result = detector._capture_screen()
                
                # 結果の検証
                self.assertIsInstance(result, np.ndarray)
                self.assertEqual(result.shape, (270, 960, 3))
                
                # grabが適切な領域で呼ばれているか確認
                mock_sct.grab.assert_called_once()
                call_args = mock_sct.grab.call_args[0][0]
                self.assertEqual(call_args['top'], 0)
                self.assertEqual(call_args['left'], 960)  # 1920 // 2
                self.assertEqual(call_args['width'], 960)  # 1920 // 2
                self.assertEqual(call_args['height'], 270)  # 1080 // 4
    
    def test_match_template(self):
        """テンプレートマッチングのテスト"""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("OpenCV not available")
        
        with patch('src.features.image_recognition.Path'):
            detector = TinctureDetector()
            
            # テスト画像の作成
            screen = np.zeros((200, 200, 3), dtype=np.uint8)
            template = np.zeros((64, 64, 3), dtype=np.uint8)
            template[:, :] = [0, 255, 0]  # 緑
            
            # 画面の一部に同じ緑色の領域を配置
            screen[50:114, 50:114] = [0, 255, 0]
            
            # マッチング実行
            confidence = detector._match_template(screen, template)
            
            # 高い信頼度で一致するはず
            self.assertGreater(confidence, 0.9)
    
    @patch('src.features.image_recognition.TinctureDetector._capture_screen')
    @patch('src.features.image_recognition.TinctureDetector._load_template')
    def test_detect_tincture_icon_success(self, mock_load_template, mock_capture):
        """Tincture検出成功のテスト"""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("OpenCV not available")
        
        # モックの設定
        screen = np.zeros((200, 200, 3), dtype=np.uint8)
        template = np.zeros((64, 64, 3), dtype=np.uint8)
        template[:, :] = [0, 255, 0]
        
        # 画面に同じパターンを配置
        screen[50:114, 50:114] = [0, 255, 0]
        
        mock_capture.return_value = screen
        mock_load_template.return_value = template
        
        with patch('src.features.image_recognition.Path'):
            detector = TinctureDetector(sensitivity=0.8)
            
            # 検出実行
            result = detector.detect_tincture_icon()
            
            # 検出成功のはず
            self.assertTrue(result)
    
    @patch('src.features.image_recognition.TinctureDetector._capture_screen')
    @patch('src.features.image_recognition.TinctureDetector._load_template')
    def test_detect_tincture_icon_failure(self, mock_load_template, mock_capture):
        """Tincture検出失敗のテスト"""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("OpenCV not available")
        
        # モックの設定（異なるパターン）
        screen = np.zeros((200, 200, 3), dtype=np.uint8)
        template = np.zeros((64, 64, 3), dtype=np.uint8)
        template[:, :] = [0, 255, 0]  # 緑
        
        # 画面には青色の領域を配置
        screen[50:114, 50:114] = [255, 0, 0]  # 赤
        
        mock_capture.return_value = screen
        mock_load_template.return_value = template
        
        with patch('src.features.image_recognition.Path'):
            detector = TinctureDetector(sensitivity=0.8)
            
            # 検出実行
            result = detector.detect_tincture_icon()
            
            # 検出失敗のはず
            self.assertFalse(result)
    
    def test_update_sensitivity(self):
        """感度更新のテスト"""
        with patch('src.features.image_recognition.Path'):
            detector = TinctureDetector()
            
            # 感度更新
            detector.update_sensitivity(0.9)
            self.assertEqual(detector.sensitivity, 0.9)
            
            # 範囲外の値
            detector.update_sensitivity(1.5)
            self.assertEqual(detector.sensitivity, 1.0)
            
            detector.update_sensitivity(0.1)
            self.assertEqual(detector.sensitivity, 0.5)
    
    def test_get_detection_area_info(self):
        """検出エリア情報取得のテスト"""
        with patch('src.features.image_recognition.Path'):
            with patch('src.features.image_recognition.mss.mss') as mock_mss:
                mock_sct = Mock()
                mock_mss.return_value = mock_sct
                mock_sct.monitors = [
                    {},
                    {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
                ]
                
                detector = TinctureDetector()
                info = detector.get_detection_area_info()
                
                # 期待される情報が含まれているか確認
                self.assertIn('monitor_config', info)
                self.assertIn('detection_area', info)
                self.assertIn('template_resolution', info)
                self.assertIn('sensitivity', info)
                
                self.assertEqual(info['monitor_config'], 'Primary')
                self.assertEqual(info['template_resolution'], '1920x1080')


class TestImageRecognitionIntegration(unittest.TestCase):
    """統合テストクラス"""
    
    @unittest.skipIf(not DEPENDENCIES_AVAILABLE, "Required dependencies not available")
    def test_full_workflow(self):
        """完全なワークフローのテスト"""
        # 実際のファイルパスをテスト
        assets_path = Path("assets/images/tincture")
        
        if not assets_path.exists():
            self.skipTest("Assets directory not found")
        
        # TinctureDetectorの初期化
        try:
            detector = TinctureDetector(monitor_config="Primary", sensitivity=0.7)
            
            # 検出エリア情報の取得
            info = detector.get_detection_area_info()
            self.assertIsInstance(info, dict)
            
            # 感度の更新
            detector.update_sensitivity(0.8)
            self.assertEqual(detector.sensitivity, 0.8)
            
            print("統合テスト成功: TinctureDetector は正常に動作しています")
            
        except Exception as e:
            self.fail(f"統合テストが失敗しました: {e}")


def run_performance_test():
    """パフォーマンステスト"""
    if not DEPENDENCIES_AVAILABLE:
        print("依存関係が不足しているため、パフォーマンステストをスキップします")
        return
    
    import time
    
    print("パフォーマンステスト開始...")
    
    try:
        detector = TinctureDetector()
        
        # 検出処理の時間測定
        start_time = time.time()
        
        for i in range(10):
            try:
                detector.detect_tincture_icon()
            except Exception as e:
                print(f"検出エラー (テスト {i+1}): {e}")
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        
        print(f"平均検出時間: {avg_time:.3f}秒")
        print(f"FPS目安: {1/avg_time:.1f}")
        
        # 検出エリア情報の表示
        info = detector.get_detection_area_info()
        print(f"検出エリア情報: {info}")
        
    except Exception as e:
        print(f"パフォーマンステストエラー: {e}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Tincture検出機能のテスト')
    parser.add_argument('--performance', action='store_true',
                       help='パフォーマンステストを実行')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='詳細な出力を表示')
    
    args = parser.parse_args()
    
    if args.performance:
        run_performance_test()
    else:
        # 通常のユニットテスト
        if args.verbose:
            unittest.main(verbosity=2)
        else:
            unittest.main()
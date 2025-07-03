"""
TinctureModule の統合テストスクリプト
"""
import sys
import os
import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.modules.tincture_module import TinctureModule, TinctureState
    from src.features.image_recognition import TinctureDetector
    from src.utils.keyboard_input import KeyboardController
    from src.core.config_manager import ConfigManager
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"依存関係が不足しています: {e}")
    DEPENDENCIES_AVAILABLE = False

@unittest.skipIf(not DEPENDENCIES_AVAILABLE, "Required dependencies not available")
class TestTinctureModule(unittest.TestCase):
    """TinctureModule のテストクラス"""
    
    def setUp(self):
        """テストの準備"""
        self.test_config = {
            'tincture': {
                'enabled': True,
                'key': '3',
                'monitor_config': 'Primary',
                'sensitivity': 0.7,
                'check_interval': 0.1,
                'min_use_interval': 0.5
            }
        }
        
        # プレースホルダー画像の作成
        self._create_test_templates()
    
    def tearDown(self):
        """テストの後処理"""
        # テスト用アセットのクリーンアップ
        self._cleanup_test_templates()
    
    def _create_test_templates(self):
        """テスト用のテンプレート画像を作成"""
        try:
            import cv2
            import numpy as np
            
            # テスト用のアセットディレクトリを作成
            test_base_dir = Path("assets/images/tincture/sap_of_the_seasons")
            
            states = ['idle', 'active', 'cooldown']
            resolutions = ['1920x1080', '2560x1440', '3840x2160']
            
            for state in states:
                state_dir = test_base_dir / state
                state_dir.mkdir(parents=True, exist_ok=True)
                
                for resolution in resolutions:
                    # 簡単なテスト画像を作成
                    img = np.zeros((64, 64, 3), dtype=np.uint8)
                    img[:, :] = [50, 50, 50]  # グレー背景
                    
                    if state == 'idle':
                        img[16:48, 16:48] = [0, 255, 0]  # 緑
                    elif state == 'active':
                        img[16:48, 16:48] = [0, 165, 255]  # オレンジ
                    else:  # cooldown
                        img[16:48, 16:48] = [128, 128, 128]  # グレー
                    
                    # ファイル名を作成
                    if state == 'cooldown':
                        filenames = [
                            f"sap_of_the_seasons_cooldown_p000_{resolution}.png",
                            f"sap_of_the_seasons_cooldown_p050_{resolution}.png",
                            f"sap_of_the_seasons_cooldown_p100_{resolution}.png"
                        ]
                    else:
                        filenames = [f"sap_of_the_seasons_{state}_{resolution}.png"]
                    
                    for filename in filenames:
                        filepath = state_dir / filename
                        cv2.imwrite(str(filepath), img)
                        
        except Exception as e:
            print(f"テスト用テンプレート作成エラー: {e}")
    
    def _cleanup_test_templates(self):
        """テスト用テンプレートのクリーンアップ"""
        try:
            import shutil
            test_dir = Path("assets/images/tincture/sap_of_the_seasons")
            if test_dir.exists():
                shutil.rmtree(test_dir)
        except Exception as e:
            print(f"テンプレートクリーンアップエラー: {e}")
    
    def test_init_valid_config(self):
        """正常な初期化のテスト"""
        with patch('src.modules.tincture_module.TinctureDetector'):
            module = TinctureModule(self.test_config)
            
            self.assertEqual(module.enabled, True)
            self.assertEqual(module.key, '3')
            self.assertEqual(module.monitor_config, 'Primary')
            self.assertEqual(module.sensitivity, 0.7)
            self.assertEqual(module.current_state, TinctureState.UNKNOWN)
            self.assertFalse(module.running)
    
    def test_init_disabled_config(self):
        """無効化設定での初期化テスト"""
        config = self.test_config.copy()
        config['tincture']['enabled'] = False
        
        with patch('src.modules.tincture_module.TinctureDetector'):
            module = TinctureModule(config)
            
            self.assertEqual(module.enabled, False)
    
    @patch('src.modules.tincture_module.TinctureDetector')
    def test_start_stop(self, mock_detector):
        """開始・停止のテスト"""
        module = TinctureModule(self.test_config)
        
        # 開始
        module.start()
        self.assertTrue(module.running)
        self.assertIsNotNone(module.thread)
        
        # 少し待機
        time.sleep(0.2)
        
        # 停止
        module.stop()
        self.assertFalse(module.running)
    
    @patch('src.modules.tincture_module.TinctureDetector')
    def test_disabled_start(self, mock_detector):
        """無効化状態での開始テスト"""
        config = self.test_config.copy()
        config['tincture']['enabled'] = False
        
        module = TinctureModule(config)
        
        # 開始を試行
        module.start()
        
        # 開始されないことを確認
        self.assertFalse(module.running)
        self.assertIsNone(module.thread)
    
    def test_state_detection_logic(self):
        """状態検出ロジックのテスト"""
        with patch('src.modules.tincture_module.TinctureDetector') as mock_detector_class:
            # モックの検出器を設定
            mock_detector = Mock()
            mock_detector_class.return_value = mock_detector
            
            module = TinctureModule(self.test_config)
            
            # ACTIVE状態の検出
            mock_detector.detect_tincture_icon.return_value = True
            module.detectors[TinctureState.ACTIVE] = mock_detector
            module.detectors[TinctureState.COOLDOWN] = Mock()
            module.detectors[TinctureState.COOLDOWN].detect_tincture_icon.return_value = False
            module.detectors[TinctureState.IDLE] = Mock()
            module.detectors[TinctureState.IDLE].detect_tincture_icon.return_value = False
            
            # 特定の状態検出メソッドをモック
            with patch.object(module, '_detect_state_specific') as mock_detect:
                mock_detect.side_effect = lambda detector, state: state == TinctureState.ACTIVE
                
                detected_state = module._detect_state()
                self.assertEqual(detected_state, TinctureState.ACTIVE)
    
    @patch('src.modules.tincture_module.TinctureDetector')
    @patch('src.modules.tincture_module.KeyboardController')
    def test_idle_state_handling(self, mock_keyboard_class, mock_detector):
        """IDLE状態処理のテスト"""
        mock_keyboard = Mock()
        mock_keyboard_class.return_value = mock_keyboard
        
        module = TinctureModule(self.test_config)
        
        # IDLE状態の処理
        module._handle_idle_state()
        
        # キーが押されることを確認
        mock_keyboard.press_key.assert_called_once_with('3')
        
        # 統計の更新を確認
        self.assertEqual(module.stats['total_uses'], 1)
        self.assertIsNotNone(module.stats['last_use_timestamp'])
    
    @patch('src.modules.tincture_module.TinctureDetector')
    @patch('src.modules.tincture_module.KeyboardController')
    def test_min_use_interval(self, mock_keyboard_class, mock_detector):
        """最小使用間隔のテスト"""
        mock_keyboard = Mock()
        mock_keyboard_class.return_value = mock_keyboard
        
        module = TinctureModule(self.test_config)
        
        # 最初の使用
        module._handle_idle_state()
        self.assertEqual(mock_keyboard.press_key.call_count, 1)
        
        # 間隔が短い場合の使用（スキップされるはず）
        module._handle_idle_state()
        self.assertEqual(mock_keyboard.press_key.call_count, 1)  # 増えない
        
        # 十分な時間経過後の使用
        module.last_use_time = time.time() - 1.0  # 1秒前に設定
        module._handle_idle_state()
        self.assertEqual(mock_keyboard.press_key.call_count, 2)  # 増える
    
    @patch('src.modules.tincture_module.TinctureDetector')
    def test_config_update(self, mock_detector):
        """設定更新のテスト"""
        module = TinctureModule(self.test_config)
        original_sensitivity = module.sensitivity
        
        # 新しい設定
        new_config = self.test_config.copy()
        new_config['tincture']['sensitivity'] = 0.9
        new_config['tincture']['key'] = '4'
        
        # 設定更新
        module.update_config(new_config)
        
        # 設定が更新されることを確認
        self.assertEqual(module.sensitivity, 0.9)
        self.assertEqual(module.key, '4')
    
    @patch('src.modules.tincture_module.TinctureDetector')
    @patch('src.modules.tincture_module.KeyboardController')
    def test_manual_use(self, mock_keyboard_class, mock_detector):
        """手動使用のテスト"""
        mock_keyboard = Mock()
        mock_keyboard_class.return_value = mock_keyboard
        
        module = TinctureModule(self.test_config)
        
        # 手動使用
        result = module.manual_use()
        
        # 成功することを確認
        self.assertTrue(result)
        mock_keyboard.press_key.assert_called_once_with('3')
        self.assertEqual(module.stats['total_uses'], 1)
    
    @patch('src.modules.tincture_module.TinctureDetector')
    def test_manual_use_disabled(self, mock_detector):
        """無効化状態での手動使用テスト"""
        config = self.test_config.copy()
        config['tincture']['enabled'] = False
        
        module = TinctureModule(config)
        
        # 手動使用を試行
        result = module.manual_use()
        
        # 失敗することを確認
        self.assertFalse(result)
        self.assertEqual(module.stats['total_uses'], 0)
    
    @patch('src.modules.tincture_module.TinctureDetector')
    def test_get_stats(self, mock_detector):
        """統計情報取得のテスト"""
        module = TinctureModule(self.test_config)
        
        stats = module.get_stats()
        
        # 期待されるキーが含まれることを確認
        expected_keys = ['enabled', 'running', 'current_state', 'key', 'monitor_config', 'sensitivity', 'stats']
        for key in expected_keys:
            self.assertIn(key, stats)
        
        # 統計の初期値を確認
        self.assertEqual(stats['stats']['total_uses'], 0)
        self.assertEqual(stats['stats']['successful_detections'], 0)
        self.assertEqual(stats['stats']['failed_detections'], 0)
    
    @patch('src.modules.tincture_module.TinctureDetector')
    def test_get_status(self, mock_detector):
        """ステータス取得のテスト"""
        module = TinctureModule(self.test_config)
        
        status = module.get_status()
        
        # 期待されるキーが含まれることを確認
        expected_keys = ['enabled', 'running', 'current_state', 'last_use_time', 'total_uses']
        for key in expected_keys:
            self.assertIn(key, status)
    
    @patch('src.modules.tincture_module.TinctureDetector')
    def test_reset_stats(self, mock_detector):
        """統計リセットのテスト"""
        module = TinctureModule(self.test_config)
        
        # 統計を変更
        module.stats['total_uses'] = 5
        module.stats['successful_detections'] = 10
        
        # リセット
        module.reset_stats()
        
        # リセットされることを確認
        self.assertEqual(module.stats['total_uses'], 0)
        self.assertEqual(module.stats['successful_detections'], 0)
        self.assertEqual(module.stats['failed_detections'], 0)
        self.assertIsNone(module.stats['last_use_timestamp'])


class TestTinctureModuleIntegration(unittest.TestCase):
    """TinctureModule の統合テストクラス"""
    
    @unittest.skipIf(not DEPENDENCIES_AVAILABLE, "Required dependencies not available")
    def test_full_workflow_with_mocks(self):
        """完全なワークフローのテスト（モック使用）"""
        config = {
            'tincture': {
                'enabled': True,
                'key': '3',
                'monitor_config': 'Primary',
                'sensitivity': 0.7,
                'check_interval': 0.05,  # 短い間隔でテスト
                'min_use_interval': 0.1
            }
        }
        
        with patch('src.modules.tincture_module.TinctureDetector') as mock_detector_class:
            with patch('src.modules.tincture_module.KeyboardController') as mock_keyboard_class:
                # モックの設定
                mock_detector = Mock()
                mock_detector_class.return_value = mock_detector
                mock_keyboard = Mock()
                mock_keyboard_class.return_value = mock_keyboard
                
                # TinctureModule の初期化
                module = TinctureModule(config)
                
                # 検出器の設定
                module.detectors[TinctureState.IDLE] = mock_detector
                module.detectors[TinctureState.ACTIVE] = Mock()
                module.detectors[TinctureState.COOLDOWN] = Mock()
                
                # 検出シナリオの設定
                detection_sequence = [
                    TinctureState.IDLE,      # 最初はIDLE
                    TinctureState.ACTIVE,    # 使用後はACTIVE
                    TinctureState.COOLDOWN,  # その後COOLDOWN
                    TinctureState.IDLE       # 最後にIDLE
                ]
                
                call_count = 0
                def mock_detect_state():
                    nonlocal call_count
                    if call_count < len(detection_sequence):
                        state = detection_sequence[call_count]
                        call_count += 1
                        return state
                    return TinctureState.UNKNOWN
                
                with patch.object(module, '_detect_state', side_effect=mock_detect_state):
                    # モジュール開始
                    module.start()
                    
                    # しばらく実行
                    time.sleep(0.3)
                    
                    # モジュール停止
                    module.stop()
                    
                    # 結果の確認
                    self.assertGreater(module.stats['total_uses'], 0)
                    print(f"統合テスト結果: {module.stats}")


def run_performance_test():
    """パフォーマンステスト"""
    if not DEPENDENCIES_AVAILABLE:
        print("依存関係が不足しているため、パフォーマンステストをスキップします")
        return
    
    print("TinctureModule パフォーマンステスト開始...")
    
    config = {
        'tincture': {
            'enabled': True,
            'key': '3',
            'monitor_config': 'Primary',
            'sensitivity': 0.7,
            'check_interval': 0.05,
            'min_use_interval': 0.1
        }
    }
    
    with patch('src.modules.tincture_module.TinctureDetector') as mock_detector_class:
        with patch('src.modules.tincture_module.KeyboardController') as mock_keyboard_class:
            # モックの設定
            mock_detector = Mock()
            mock_detector_class.return_value = mock_detector
            mock_keyboard = Mock()
            mock_keyboard_class.return_value = mock_keyboard
            
            # TinctureModule の初期化
            module = TinctureModule(config)
            
            # パフォーマンス測定
            start_time = time.time()
            
            # モジュール開始
            module.start()
            
            # 実行時間
            test_duration = 2.0
            time.sleep(test_duration)
            
            # モジュール停止
            module.stop()
            
            end_time = time.time()
            
            # 結果の出力
            stats = module.get_stats()
            print(f"実行時間: {end_time - start_time:.2f}秒")
            print(f"検出成功回数: {stats['stats']['successful_detections']}")
            print(f"検出失敗回数: {stats['stats']['failed_detections']}")
            print(f"使用回数: {stats['stats']['total_uses']}")
            
            # CPU使用率の推定
            if stats['stats']['successful_detections'] > 0:
                checks_per_second = stats['stats']['successful_detections'] / test_duration
                print(f"検出頻度: {checks_per_second:.1f} 回/秒")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='TinctureModule のテスト')
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
"""
Calibration helper methods for MainWindow
"""
import logging
from PyQt5.QtCore import QTimer

logger = logging.getLogger(__name__)

class CalibrationHelpers:
    """Helper class for calibration functionality"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        
    def show_overlay_window(self):
        """オーバーレイウィンドウを表示"""
        try:
            self.main_window.log_message("オーバーレイウィンドウを作成中...")
            logger.info("Starting overlay window creation")
            
            # 必要なモジュールをインポート
            try:
                from src.features.overlay_window import OverlayWindow
                from src.features.area_selector import AreaSelector
                logger.debug("Successfully imported OverlayWindow and AreaSelector")
            except ImportError as ie:
                error_msg = f"モジュールインポートエラー: {ie}"
                self.main_window.log_message(error_msg)
                logger.error(error_msg)
                return
            
            # AreaSelectorの初期化
            if not self.main_window.area_selector:
                logger.debug("Initializing AreaSelector")
                self.main_window.area_selector = AreaSelector()
                self.main_window.log_message("AreaSelectorを初期化しました")
            
            # 現在のエリア情報を取得
            try:
                current_area = self.main_window.area_selector.get_flask_area()
                logger.debug(f"Current area: {current_area}")
                self.main_window.log_message(f"現在のエリア: X={current_area['x']}, Y={current_area['y']}, W={current_area['width']}, H={current_area['height']}")
            except Exception as ae:
                error_msg = f"エリア情報取得エラー: {ae}"
                self.main_window.log_message(error_msg)
                logger.error(error_msg)
                return
            
            # 既存のオーバーレイウィンドウを閉じる
            if self.main_window.overlay_window:
                logger.debug("Closing existing overlay window")
                self.main_window.overlay_window.close()
                self.main_window.overlay_window = None
            
            # 新しいオーバーレイウィンドウを作成
            try:
                logger.debug("Creating new OverlayWindow")
                self.main_window.overlay_window = OverlayWindow(
                    current_area['x'], current_area['y'], 
                    current_area['width'], current_area['height']
                )
                self.main_window.log_message("OverlayWindowを作成しました")
            except Exception as oe:
                error_msg = f"OverlayWindow作成エラー: {oe}"
                self.main_window.log_message(error_msg)
                logger.error(error_msg)
                import traceback
                logger.error(traceback.format_exc())
                return
            
            # コールバック接続
            try:
                logger.debug("Connecting overlay callbacks")
                self.main_window.overlay_window.area_changed.connect(self.on_area_changed)
                self.main_window.overlay_window.settings_saved.connect(self.on_settings_saved)
                self.main_window.overlay_window.closed.connect(self.on_overlay_closed)
                self.main_window.log_message("コールバックを接続しました")
            except Exception as ce:
                error_msg = f"コールバック接続エラー: {ce}"
                self.main_window.log_message(error_msg)
                logger.error(error_msg)
            
            # オーバーレイウィンドウを表示
            try:
                logger.debug("Showing overlay window")
                self.main_window.overlay_window.show()
                self.main_window.log_message(f"オーバーレイウィンドウを表示しました: X={current_area['x']}, Y={current_area['y']}")
                logger.info("Overlay window displayed successfully")
            except Exception as se:
                error_msg = f"オーバーレイ表示エラー: {se}"
                self.main_window.log_message(error_msg)
                logger.error(error_msg)
                import traceback
                logger.error(traceback.format_exc())
            
        except Exception as e:
            error_msg = f"オーバーレイウィンドウ表示エラー: {e}"
            self.main_window.log_message(error_msg)
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
    
    def on_area_changed(self, x, y, width, height):
        """エリア変更時の処理"""
        try:
            self.main_window.current_area_label.setText(f"X: {x}, Y: {y}, W: {width}, H: {height}")
            logger.debug(f"Area changed: X={x}, Y={y}, W={width}, H={height}")
        except Exception as e:
            logger.error(f"Error handling area change: {e}")
    
    def on_settings_saved(self):
        """設定保存時の処理"""
        try:
            # AreaSelectorを更新
            if self.main_window.area_selector:
                # オーバーレイから最新の値を取得して保存
                if self.main_window.overlay_window:
                    geometry = self.main_window.overlay_window.geometry()
                    x, y = geometry.x(), geometry.y()
                    width, height = geometry.width(), geometry.height()
                    
                    self.main_window.area_selector.set_flask_area(x, y, width, height)
                    self.main_window.log_message(f"検出エリア設定を保存: X={x}, Y={y}, W={width}, H={height}")
            
            # 表示を更新
            self.update_resolution_info()
            
            # TinctureDetectorの設定を更新
            self._update_tincture_detector_settings()
            
        except Exception as e:
            self.main_window.log_message(f"設定保存エラー: {e}")
            logger.error(f"Error saving settings: {e}")
    
    def _update_tincture_detector_settings(self):
        """TinctureDetectorの設定を更新"""
        try:
            if (self.main_window.macro_controller and 
                hasattr(self.main_window.macro_controller, 'tincture_module') and
                self.main_window.macro_controller.tincture_module):
                
                # default_config.yamlを更新
                if self.main_window.area_selector:
                    current_area = self.main_window.area_selector.get_flask_area()
                    
                    # 設定を更新
                    if 'tincture' not in self.main_window.config:
                        self.main_window.config['tincture'] = {}
                    
                    self.main_window.config['tincture']['detection_mode'] = 'full_flask_area'
                    
                    # 設定を保存
                    self.main_window.config_manager.save_config(self.main_window.config)
                    
                    # TinctureDetectorを再初期化
                    self._reinitialize_tincture_detector()
                    
                    self.main_window.log_message("TinctureDetector設定を更新しました")
                    
        except Exception as e:
            logger.error(f"Error updating TinctureDetector settings: {e}")
    
    def _reinitialize_tincture_detector(self):
        """TinctureDetectorを再初期化"""
        try:
            if (self.main_window.macro_controller and 
                hasattr(self.main_window.macro_controller, 'tincture_module')):
                
                tincture_module = self.main_window.macro_controller.tincture_module
                
                # 現在の設定を取得
                current_config = self.main_window.config_manager.load_config()
                tincture_config = current_config.get('tincture', {})
                
                # TinctureDetectorを再初期化
                from src.features.image_recognition import TinctureDetector
                new_detector = TinctureDetector(
                    sensitivity=tincture_config.get('sensitivity', 0.7)
                )
                
                # 新しい検出モードを設定
                new_detector.set_detection_mode('full_flask_area')
                
                # 既存のdetectorを置き換え
                old_detector = tincture_module.detector
                tincture_module.detector = new_detector
                
                # ログ出力
                logger.info("TinctureDetector reinitialized with new settings")
                self.main_window.log_message("TinctureDetectorを再初期化しました")
                
        except Exception as e:
            logger.error(f"Error reinitializing TinctureDetector: {e}")
    
    def on_overlay_closed(self):
        """オーバーレイクローズ時の処理"""
        self.main_window.overlay_window = None
    
    def update_resolution_info(self):
        """解像度情報を更新"""
        try:
            from PyQt5.QtWidgets import QApplication
            
            screen = QApplication.primaryScreen()
            if screen:
                size = screen.size()
                width, height = size.width(), size.height()
                self.main_window.resolution_label.setText(f"{width}x{height}")
                
                # ウルトラワイド推奨情報
                if width >= 3440:  # ウルトラワイド解像度
                    self.main_window.suggestion_label.setText("ウルトラワイド検出")
                    self.main_window.suggestion_label.setStyleSheet("color: blue; font-weight: bold;")
                else:
                    self.main_window.suggestion_label.setText("")
            
            # 実際の設定ファイルから現在の座標を読み込み
            if not self.main_window.area_selector:
                from src.features.area_selector import AreaSelector
                self.main_window.area_selector = AreaSelector()
            
            current_area = self.main_window.area_selector.get_flask_area()
            x, y = current_area['x'], current_area['y']
            w, h = current_area['width'], current_area['height']
            
            # GUI表示を実際の設定値で更新
            self.main_window.current_area_label.setText(f"X: {x}, Y: {y}, W: {w}, H: {h}")
            self.main_window.x_spinbox.setValue(x)
            self.main_window.y_spinbox.setValue(y) 
            self.main_window.width_spinbox.setValue(w)
            self.main_window.height_spinbox.setValue(h)
            
            logger.debug(f"Resolution info updated: {width}x{height}, Area: {x},{y},{w},{h}")
            
        except Exception as e:
            logger.error(f"Error updating resolution info: {e}")
    
    def apply_preset(self):
        """プリセットを適用"""
        try:
            preset = self.main_window.preset_combo.currentText()
            
            # プリセット座標の定義
            presets = {
                "1920x1080": {"x": 1520, "y": 1005, "width": 400, "height": 120},
                "2560x1440": {"x": 2027, "y": 1340, "width": 533, "height": 160},
                "3840x2160": {"x": 3040, "y": 2010, "width": 800, "height": 240},
                "3440x1440": {"x": 2720, "y": 1340, "width": 533, "height": 160},
                "2560x1080": {"x": 2027, "y": 1005, "width": 533, "height": 120},
                "5120x1440": {"x": 4267, "y": 1340, "width": 533, "height": 160}
            }
            
            if preset in presets:
                coords = presets[preset]
                
                # SpinBoxに値を設定
                self.main_window.x_spinbox.setValue(coords["x"])
                self.main_window.y_spinbox.setValue(coords["y"])
                self.main_window.width_spinbox.setValue(coords["width"])
                self.main_window.height_spinbox.setValue(coords["height"])
                
                # 設定を適用
                self.apply_manual_settings()
                
                self.main_window.log_message(f"プリセット {preset} を適用しました")
            else:
                self.main_window.log_message("カスタム設定が選択されています")
                
        except Exception as e:
            self.main_window.log_message(f"プリセット適用エラー: {e}")
            logger.error(f"Error applying preset: {e}")
    
    def apply_manual_settings(self):
        """手動設定を適用"""
        try:
            x = self.main_window.x_spinbox.value()
            y = self.main_window.y_spinbox.value()
            width = self.main_window.width_spinbox.value()
            height = self.main_window.height_spinbox.value()
            
            # AreaSelectorに設定
            if not self.main_window.area_selector:
                from src.features.area_selector import AreaSelector
                self.main_window.area_selector = AreaSelector()
            
            self.main_window.area_selector.set_flask_area(x, y, width, height)
            
            # 表示更新
            self.main_window.current_area_label.setText(f"X: {x}, Y: {y}, W: {width}, H: {height}")
            
            # TinctureDetectorの設定を更新
            self._update_tincture_detector_settings()
            
            self.main_window.log_message(f"手動設定を適用: X={x}, Y={y}, W={width}, H={height}")
            
        except Exception as e:
            self.main_window.log_message(f"手動設定適用エラー: {e}")
            logger.error(f"Error applying manual settings: {e}")
    
    def test_detection(self):
        """検出テスト"""
        try:
            if (self.main_window.macro_controller and 
                hasattr(self.main_window.macro_controller, 'tincture_module')):
                
                tincture_module = self.main_window.macro_controller.tincture_module
                if tincture_module and tincture_module.detector:
                    
                    # 検出テストを実行
                    state = tincture_module.detector.get_tincture_state()
                    
                    if state == "IDLE":
                        result = "✓ Tincture IDLE状態を検出しました"
                        self.main_window.test_result_label.setStyleSheet("color: green;")
                    elif state == "ACTIVE":
                        result = "✓ Tincture ACTIVE状態を検出しました"
                        self.main_window.test_result_label.setStyleSheet("color: blue;")
                    else:
                        result = "✗ Tinctureを検出できませんでした"
                        self.main_window.test_result_label.setStyleSheet("color: red;")
                    
                    self.main_window.test_result_label.setText(f"テスト結果: {result}")
                    self.main_window.log_message(f"検出テスト結果: {result}")
                else:
                    self.main_window.log_message("TinctureModuleまたはDetectorが利用できません")
            else:
                self.main_window.log_message("MacroControllerが利用できません")
                
        except Exception as e:
            self.main_window.log_message(f"検出テストエラー: {e}")
            logger.error(f"Error in detection test: {e}")
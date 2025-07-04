"""
POE Macro v3.0 メインGUIウィンドウ
"""
import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QLabel, QPushButton,
                             QCheckBox, QSpinBox, QComboBox, QTextEdit,
                             QGroupBox, QGridLayout, QSlider, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """メインGUIウィンドウクラス"""
    
    def __init__(self, config_manager, macro_controller=None):
        super().__init__()
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.macro_controller = macro_controller
        
        self.setWindowTitle("POE Macro v3.0")
        self.setGeometry(100, 100, 800, 600)
        
        # ログテキスト要素を早期初期化（安全性のため）
        self.log_text = None
        
        # UI要素の初期化
        self.init_ui()
        
        # 定期更新タイマー
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # 1秒毎
        
        logger.info("MainWindow initialized")
    
    def init_ui(self):
        """UI要素を初期化"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 各タブを作成（ログタブを先に作成してlog_textを初期化）
        self.create_log_tab()
        self.create_general_tab()
        self.create_tincture_tab()
        self.create_flask_tab()
        self.create_skills_tab()
        self.create_calibration_tab()
        
        # ステータスバー
        self.statusBar().showMessage("Ready")
    
    def create_general_tab(self):
        """一般設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # マクロ制御グループ
        macro_group = QGroupBox("マクロ制御")
        macro_layout = QGridLayout(macro_group)
        
        self.macro_enabled_cb = QCheckBox("マクロを有効化")
        self.macro_enabled_cb.setChecked(True)
        macro_layout.addWidget(self.macro_enabled_cb, 0, 0)
        
        macro_layout.addWidget(QLabel("緊急停止キー:"), 1, 0)
        self.emergency_key_edit = QLineEdit("F12")
        macro_layout.addWidget(self.emergency_key_edit, 1, 1)
        
        layout.addWidget(macro_group)
        
        # ログ設定グループ
        log_group = QGroupBox("ログ設定")
        log_layout = QGridLayout(log_group)
        
        log_layout.addWidget(QLabel("ログレベル:"), 0, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        log_layout.addWidget(self.log_level_combo, 0, 1)
        
        layout.addWidget(log_group)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("マクロ開始")
        self.start_btn.clicked.connect(self.start_macro)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("マクロ停止")
        self.stop_btn.clicked.connect(self.stop_macro)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "一般")
    
    def create_tincture_tab(self):
        """Tincture設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tincture設定グループ
        tincture_group = QGroupBox("Tincture自動使用設定")
        tincture_layout = QGridLayout(tincture_group)
        
        self.tincture_enabled_cb = QCheckBox("Tincture自動使用を有効化")
        tincture_enabled = self.config.get('tincture', {}).get('enabled', True)
        self.tincture_enabled_cb.setChecked(tincture_enabled)
        tincture_layout.addWidget(self.tincture_enabled_cb, 0, 0, 1, 2)
        
        tincture_layout.addWidget(QLabel("使用キー:"), 1, 0)
        self.tincture_key_edit = QLineEdit()
        tincture_key = self.config.get('tincture', {}).get('key', '3')
        self.tincture_key_edit.setText(tincture_key)
        tincture_layout.addWidget(self.tincture_key_edit, 1, 1)
        
        tincture_layout.addWidget(QLabel("モニター設定:"), 2, 0)
        self.monitor_combo = QComboBox()
        self.monitor_combo.addItems(["Primary", "Center", "Right"])
        monitor_config = self.config.get('tincture', {}).get('monitor_config', 'Primary')
        self.monitor_combo.setCurrentText(monitor_config)
        tincture_layout.addWidget(self.monitor_combo, 2, 1)
        
        tincture_layout.addWidget(QLabel("検出感度:"), 3, 0)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(50, 100)
        sensitivity = int(self.config.get('tincture', {}).get('sensitivity', 0.7) * 100)
        self.sensitivity_slider.setValue(sensitivity)
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity_label)
        tincture_layout.addWidget(self.sensitivity_slider, 3, 1)
        
        self.sensitivity_label = QLabel(f"{sensitivity}%")
        tincture_layout.addWidget(self.sensitivity_label, 3, 2)
        
        layout.addWidget(tincture_group)
        
        # 統計情報グループ
        stats_group = QGroupBox("統計情報")
        stats_layout = QGridLayout(stats_group)
        
        self.tincture_uses_label = QLabel("使用回数: 0")
        stats_layout.addWidget(self.tincture_uses_label, 0, 0)
        
        self.detection_success_label = QLabel("検出成功: 0")
        stats_layout.addWidget(self.detection_success_label, 0, 1)
        
        self.detection_failed_label = QLabel("検出失敗: 0")
        stats_layout.addWidget(self.detection_failed_label, 1, 0)
        
        self.last_use_label = QLabel("最後の使用: なし")
        stats_layout.addWidget(self.last_use_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        self.manual_use_btn = QPushButton("手動使用")
        self.manual_use_btn.clicked.connect(self.manual_use_tincture)
        button_layout.addWidget(self.manual_use_btn)
        
        self.reset_stats_btn = QPushButton("統計リセット")
        self.reset_stats_btn.clicked.connect(self.reset_tincture_stats)
        button_layout.addWidget(self.reset_stats_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Tincture")
    
    def create_flask_tab(self):
        """Flask設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        flask_group = QGroupBox("Flask自動使用設定")
        flask_layout = QGridLayout(flask_group)
        
        self.flask_enabled_cb = QCheckBox("Flask自動使用を有効化")
        flask_enabled = self.config.get('flask', {}).get('enabled', True)
        self.flask_enabled_cb.setChecked(flask_enabled)
        flask_layout.addWidget(self.flask_enabled_cb, 0, 0, 1, 2)
        
        layout.addWidget(flask_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Flask")
    
    def create_skills_tab(self):
        """スキル設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        skills_group = QGroupBox("スキル自動使用設定")
        skills_layout = QGridLayout(skills_group)
        
        self.skills_enabled_cb = QCheckBox("スキル自動使用を有効化")
        skills_enabled = self.config.get('skills', {}).get('enabled', True)
        self.skills_enabled_cb.setChecked(skills_enabled)
        skills_layout.addWidget(self.skills_enabled_cb, 0, 0, 1, 2)
        
        layout.addWidget(skills_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "スキル")
    
    def create_log_tab(self):
        """ログタブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        log_group = QGroupBox("ログ出力")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        button_layout = QHBoxLayout()
        
        clear_log_btn = QPushButton("ログクリア")
        clear_log_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_log_btn)
        
        log_layout.addLayout(button_layout)
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(widget, "ログ")
    
    def create_calibration_tab(self):
        """キャリブレーションタブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 検出エリア設定グループ
        area_group = QGroupBox("検出エリア設定")
        area_layout = QGridLayout(area_group)
        
        # 現在の解像度表示
        area_layout.addWidget(QLabel("検出された解像度:"), 0, 0)
        self.resolution_label = QLabel("1920x1080")
        area_layout.addWidget(self.resolution_label, 0, 1)
        
        # ウルトラワイド推奨情報
        self.suggestion_label = QLabel("")
        area_layout.addWidget(self.suggestion_label, 0, 2)
        
        # 現在の設定表示
        area_layout.addWidget(QLabel("現在の検出エリア:"), 1, 0)
        self.current_area_label = QLabel("読み込み中...")
        area_layout.addWidget(self.current_area_label, 1, 1, 1, 2)
        
        # プリセット選択
        area_layout.addWidget(QLabel("プリセット:"), 2, 0)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["1920x1080", "2560x1440", "3840x2160", "3440x1440", "2560x1080", "5120x1440", "カスタム"])
        area_layout.addWidget(self.preset_combo, 2, 1)
        
        self.apply_preset_btn = QPushButton("プリセット適用")
        self.apply_preset_btn.clicked.connect(self.apply_preset)
        area_layout.addWidget(self.apply_preset_btn, 2, 2)
        
        # オーバーレイ表示ボタン
        self.show_overlay_btn = QPushButton("検出エリア設定を開く")
        self.show_overlay_btn.clicked.connect(self.show_overlay_window)
        area_layout.addWidget(self.show_overlay_btn, 3, 0, 1, 3)
        
        layout.addWidget(area_group)
        
        # 検出テストグループ
        test_group = QGroupBox("検出テスト")
        test_layout = QGridLayout(test_group)
        
        self.test_detection_btn = QPushButton("現在のエリアで検出テスト")
        self.test_detection_btn.clicked.connect(self.test_detection)
        test_layout.addWidget(self.test_detection_btn, 0, 0)
        
        self.test_result_label = QLabel("テスト結果: 未実行")
        test_layout.addWidget(self.test_result_label, 1, 0)
        
        layout.addWidget(test_group)
        
        # 詳細設定グループ
        detail_group = QGroupBox("詳細設定")
        detail_layout = QGridLayout(detail_group)
        
        detail_layout.addWidget(QLabel("X座標:"), 0, 0)
        self.x_spinbox = QSpinBox()
        self.x_spinbox.setRange(0, 3840)
        self.x_spinbox.setValue(0)  # 初期値は0、後で設定ファイルから読み込み
        detail_layout.addWidget(self.x_spinbox, 0, 1)
        
        detail_layout.addWidget(QLabel("Y座標:"), 0, 2)
        self.y_spinbox = QSpinBox()
        self.y_spinbox.setRange(0, 2160)
        self.y_spinbox.setValue(0)  # 初期値は0、後で設定ファイルから読み込み
        detail_layout.addWidget(self.y_spinbox, 0, 3)
        
        detail_layout.addWidget(QLabel("幅:"), 1, 0)
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(100, 800)
        self.width_spinbox.setValue(0)  # 初期値は0、後で設定ファイルから読み込み
        detail_layout.addWidget(self.width_spinbox, 1, 1)
        
        detail_layout.addWidget(QLabel("高さ:"), 1, 2)
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(50, 240)
        self.height_spinbox.setValue(0)  # 初期値は0、後で設定ファイルから読み込み
        detail_layout.addWidget(self.height_spinbox, 1, 3)
        
        self.apply_manual_btn = QPushButton("手動設定を適用")
        self.apply_manual_btn.clicked.connect(self.apply_manual_settings)
        detail_layout.addWidget(self.apply_manual_btn, 2, 0, 1, 4)
        
        layout.addWidget(detail_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "キャリブレーション")
        
        # オーバーレイウィンドウの初期化
        self.overlay_window = None
        self.area_selector = None
        
        # 解像度情報を更新
        self.update_resolution_info()
        
    def show_overlay_window(self):
        """オーバーレイウィンドウを表示"""
        try:
            if self.overlay_window is None:
                from src.features.overlay_window import OverlayWindow
                from src.features.area_selector import AreaSelector
                
                # AreaSelectorを初期化
                self.area_selector = AreaSelector()
                current_area = self.area_selector.get_flask_area()
                
                # デバッグログ: オーバーレイ作成時の座標
                self.log_message(f"[OVERLAY] オーバーレイ作成用座標: X={current_area.get('x', 245)}, Y={current_area.get('y', 850)}, W={current_area.get('width', 400)}, H={current_area.get('height', 120)}")
                
                # オーバーレイウィンドウを作成
                self.overlay_window = OverlayWindow(
                    current_area.get('x', 245),
                    current_area.get('y', 850),
                    current_area.get('width', 400),
                    current_area.get('height', 120)
                )
                
                # シグナル接続
                self.overlay_window.area_changed.connect(self.on_area_changed)
                self.overlay_window.settings_saved.connect(self.on_settings_saved)
                self.overlay_window.overlay_closed.connect(self.on_overlay_closed)
            
            self.overlay_window.show_overlay()
            self.log_message("オーバーレイウィンドウを表示しました")
            
        except Exception as e:
            self.log_message(f"オーバーレイウィンドウの表示エラー: {e}")
    
    def on_area_changed(self, x, y, width, height):
        """オーバーレイのエリアが変更された時の処理"""
        self.current_area_label.setText(f"X: {x}, Y: {y}, W: {width}, H: {height}")
        self.x_spinbox.setValue(x)
        self.y_spinbox.setValue(y)
        self.width_spinbox.setValue(width)
        self.height_spinbox.setValue(height)
        
    def on_settings_saved(self):
        """設定が保存された時の処理（包括的設定更新）"""
        try:
            if self.overlay_window and self.area_selector:
                area = self.overlay_window.get_area()
                x, y, width, height = area['x'], area['y'], area['width'], area['height']
                
                # AreaSelectorを更新
                self.area_selector.set_flask_area(x, y, width, height)
                
                # GUIの表示を更新
                self.current_area_label.setText(f"X: {x}, Y: {y}, W: {width}, H: {height}")
                self.x_spinbox.setValue(x)
                self.y_spinbox.setValue(y)
                self.width_spinbox.setValue(width)
                self.height_spinbox.setValue(height)
                
                # default_config.yamlの設定も更新
                new_area = {'x': x, 'y': y, 'width': width, 'height': height}
                
                if 'tincture' not in self.config:
                    self.config['tincture'] = {}
                
                # フラスコエリア全体検出モードに設定
                self.config['tincture']['detection_mode'] = 'full_flask_area'
                self.config['tincture']['detection_area'] = new_area
                self.config_manager.save_config(self.config)
                
                # MacroControllerのTinctureモジュールに変更を伝播
                self._update_tincture_detector_settings()
                
                self.log_message(f"検出エリア設定を保存しました: ({x}, {y}, {width}, {height})")
                self.log_message("フラスコエリア全体検出モードに切り替えました")
                
        except Exception as e:
            self.log_message(f"設定保存エラー: {e}")
            import traceback
            self.log_message(f"詳細エラー: {traceback.format_exc()}")
    
    def _update_tincture_detector_settings(self):
        """TinctureDetectorの設定を更新（必要に応じて再初期化）"""
        try:
            if self.macro_controller and hasattr(self.macro_controller, 'tincture_module'):
                tincture_module = self.macro_controller.tincture_module
                if tincture_module:
                    # 既存のDetectorの設定を更新
                    detector = tincture_module.detector
                    if detector and hasattr(detector, 'set_detection_mode'):
                        detector.set_detection_mode('full_flask_area')
                        self.log_message("TinctureDetector検出モードを更新しました")
                    
                    # AreaSelectorも更新
                    if hasattr(tincture_module, 'update_detection_area'):
                        tincture_module.update_detection_area(self.area_selector)
                        self.log_message("TinctureModule検出エリアを更新しました")
                    
                    # 設定の強制再読み込み（重要：新しい設定を確実に反映）
                    if hasattr(tincture_module, 'update_config'):
                        updated_config = self.config.get('tincture', {})
                        tincture_module.update_config(updated_config)
                        self.log_message("TinctureModule設定を強制再読み込みしました")
                    
                    # TinctureDetectorの再初期化（最も確実な方法）
                    self._reinitialize_tincture_detector()
                        
        except Exception as e:
            self.log_message(f"TinctureDetector設定更新エラー: {e}")
            import traceback
            self.log_message(f"詳細エラー: {traceback.format_exc()}")
    
    def _reinitialize_tincture_detector(self):
        """TinctureDetectorを再初期化して新しい設定を確実に適用"""
        try:
            if self.macro_controller and hasattr(self.macro_controller, 'tincture_module'):
                tincture_module = self.macro_controller.tincture_module
                if tincture_module:
                    # 現在の設定を取得
                    tincture_config = self.config.get('tincture', {})
                    
                    # TinctureDetectorを再作成
                    from src.features.image_recognition import TinctureDetector
                    
                    new_detector = TinctureDetector(
                        monitor_config=tincture_config.get('monitor_config', 'Primary'),
                        sensitivity=tincture_config.get('sensitivity', 0.7),
                        area_selector=self.area_selector,
                        config=self.config
                    )
                    
                    # 古いDetectorを新しいものに置き換え
                    tincture_module.detector = new_detector
                    
                    self.log_message("TinctureDetectorを再初期化しました")
                    self.log_message(f"新しい検出モード: {new_detector.detection_mode}")
                    
        except Exception as e:
            self.log_message(f"TinctureDetector再初期化エラー: {e}")
            import traceback
            self.log_message(f"詳細エラー: {traceback.format_exc()}")
    
    def on_overlay_closed(self):
        """オーバーレイが閉じられた時の処理"""
        self.log_message("オーバーレイウィンドウが閉じられました")
        
    def update_resolution_info(self):
        """現在の解像度情報を表示し、実際の設定ファイルから座標を読み込み"""
        try:
            if self.area_selector is None:
                from src.features.area_selector import AreaSelector
                self.area_selector = AreaSelector()
                
            resolution = self.area_selector.get_current_resolution()
            self.resolution_label.setText(f"{resolution}")
            
            # **重要**: 実際の設定ファイルから現在の座標を読み込み
            current_area = self.area_selector.get_flask_area()
            self.log_message(f"[LOAD] 設定ファイルから読み込み: X={current_area['x']}, Y={current_area['y']}, W={current_area['width']}, H={current_area['height']}")
            
            # GUI表示を実際の設定値で更新
            self.current_area_label.setText(f"X: {current_area['x']}, Y: {current_area['y']}, W: {current_area['width']}, H: {current_area['height']}")
            self.x_spinbox.setValue(current_area['x'])
            self.y_spinbox.setValue(current_area['y'])
            self.width_spinbox.setValue(current_area['width'])
            self.height_spinbox.setValue(current_area['height'])
            
            # ウルトラワイド解像度の場合の推奨座標を表示
            if resolution == "3440x1440":
                self.suggestion_label.setText("ウルトラワイド: 3番スロット推奨 X:1680, Y:1133")
            elif resolution == "2560x1080":
                self.suggestion_label.setText("ウルトラワイド: 3番スロット推奨 X:1080, Y:850")
            elif resolution == "5120x1440":
                self.suggestion_label.setText("5K ウルトラワイド: 3番スロット推奨 X:2560, Y:1133")
            else:
                self.suggestion_label.setText("")
                
            # 現在の設定プリセットを選択
            if resolution in ["1920x1080", "2560x1440", "3840x2160", "3440x1440", "2560x1080", "5120x1440"]:
                index = self.preset_combo.findText(resolution)
                if index >= 0:
                    self.preset_combo.setCurrentIndex(index)
                    
        except Exception as e:
            self.log_message(f"解像度情報の更新エラー: {e}")
            self.resolution_label.setText("取得エラー")
            # エラー時はデフォルト値を設定
            self.current_area_label.setText("エラー: 設定を確認してください")
            self.x_spinbox.setValue(245)
            self.y_spinbox.setValue(850)
            self.width_spinbox.setValue(400)
            self.height_spinbox.setValue(120)
        
    def apply_preset(self):
        """プリセットを適用"""
        try:
            if self.area_selector is None:
                from src.features.area_selector import AreaSelector
                self.area_selector = AreaSelector()
            
            selected_preset = self.preset_combo.currentText()
            if selected_preset != "カスタム":
                success = self.area_selector.apply_preset(selected_preset)
                if success:
                    area = self.area_selector.get_flask_area()
                    self.current_area_label.setText(f"X: {area['x']}, Y: {area['y']}, W: {area['width']}, H: {area['height']}")
                    self.x_spinbox.setValue(area['x'])
                    self.y_spinbox.setValue(area['y'])
                    self.width_spinbox.setValue(area['width'])
                    self.height_spinbox.setValue(area['height'])
                    
                    if self.overlay_window:
                        self.overlay_window.set_area(area['x'], area['y'], area['width'], area['height'])
                        
                    self.log_message(f"プリセット '{selected_preset}' を適用しました")
                else:
                    self.log_message(f"プリセット '{selected_preset}' の適用に失敗しました")
            
        except Exception as e:
            self.log_message(f"プリセット適用エラー: {e}")
    
    def apply_manual_settings(self):
        """手動設定を適用してモジュールを更新"""
        try:
            x = self.x_spinbox.value()
            y = self.y_spinbox.value()
            width = self.width_spinbox.value()
            height = self.height_spinbox.value()
            
            if self.area_selector is None:
                from src.features.area_selector import AreaSelector
                self.area_selector = AreaSelector()
            
            # エリア設定を更新
            self.area_selector.set_flask_area(x, y, width, height)
            self.current_area_label.setText(f"X: {x}, Y: {y}, W: {width}, H: {height}")
            
            if self.overlay_window:
                self.overlay_window.set_area(x, y, width, height)
            
            # 設定ファイルを更新
            new_area = {
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }
            
            # 設定を保存
            if 'tincture' not in self.config:
                self.config['tincture'] = {}
            
            # フラスコエリア全体検出モードに設定
            self.config['tincture']['detection_mode'] = 'full_flask_area'
            self.config['tincture']['detection_area'] = new_area
            self.config_manager.save_config(self.config)
            
            # MacroControllerのTinctureモジュールに変更を伝播
            if self.macro_controller and hasattr(self.macro_controller, 'tincture_module'):
                if self.macro_controller.tincture_module:
                    # TinctureDetectorのフラスコエリア全体検出モードに切り替え
                    detector = self.macro_controller.tincture_module.detector
                    if detector and hasattr(detector, 'set_detection_mode'):
                        detector.set_detection_mode('full_flask_area')
                        self.log_message("フラスコエリア全体検出モードに設定しました")
                    else:
                        # フォールバック: AreaSelectorを更新
                        if hasattr(self.macro_controller.tincture_module, 'update_detection_area'):
                            self.macro_controller.tincture_module.update_detection_area(self.area_selector)
                            self.log_message("検出エリアをTinctureModuleに更新しました（フォールバック）")
                
            self.log_message(f"手動設定を適用しました: ({x}, {y}, {width}, {height})")
            
        except Exception as e:
            self.log_message(f"手動設定適用エラー: {e}")
    
    def test_detection(self):
        """検出テストを実行"""
        try:
            if self.area_selector is None:
                from src.features.area_selector import AreaSelector
                self.area_selector = AreaSelector()
            
            area = self.area_selector.get_flask_area()
            
            # 検出モードに応じて適切なエリアを表示
            detection_mode = self.config.get('tincture', {}).get('detection_mode', 'auto_slot3')
            if detection_mode == 'manual':
                # 手動モード：手動設定エリア
                manual_area = self.area_selector.get_full_flask_area_for_tincture()
                self.test_result_label.setText(f"テスト結果: 手動検出モード - 手動設定エリア")
                self.log_message(f"検出テスト実行 - フラスコエリア: ({area['x']}, {area['y']}, {area['width']}, {area['height']})")
                self.log_message(f"手動Tincture検出エリア: ({manual_area['x']}, {manual_area['y']}, {manual_area['width']}, {manual_area['height']})")
            elif detection_mode == 'full_flask_area':
                # フラスコエリア全体モード
                full_area = self.area_selector.get_full_flask_area_for_tincture()
                self.test_result_label.setText(f"テスト結果: フラスコエリア全体検出モード")
                self.log_message(f"検出テスト実行 - フラスコエリア: ({area['x']}, {area['y']}, {area['width']}, {area['height']})")
                self.log_message(f"フラスコ全体Tincture検出エリア: ({full_area['x']}, {full_area['y']}, {full_area['width']}, {full_area['height']})")
            else:
                # フラスコエリア全体を使用（デフォルトモード）
                tincture_area = self.area_selector.get_full_flask_area_for_tincture()
                self.test_result_label.setText(f"テスト結果: フラスコエリア全体検出モード")
                self.log_message(f"検出テスト実行 - フラスコエリア: ({area['x']}, {area['y']}, {area['width']}, {area['height']})")
                self.log_message(f"Tincture検出エリア（フラスコ全体）: ({tincture_area['x']}, {tincture_area['y']}, {tincture_area['width']}, {tincture_area['height']})")
            
        except Exception as e:
            self.test_result_label.setText(f"テスト結果: エラー - {e}")
            self.log_message(f"検出テストエラー: {e}")
    
    def update_sensitivity_label(self, value):
        """感度ラベルを更新"""
        self.sensitivity_label.setText(f"{value}%")
    
    def start_macro(self):
        """マクロを開始"""
        try:
            if self.macro_controller:
                self.macro_controller.start()
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.statusBar().showMessage("マクロ実行中")
                self.log_message("マクロを開始しました")
            else:
                self.log_message("マクロコントローラーが初期化されていません")
            
        except Exception as e:
            self.log_message(f"マクロ開始エラー: {e}")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    def stop_macro(self):
        """マクロを停止"""
        try:
            if self.macro_controller:
                self.macro_controller.stop()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.statusBar().showMessage("Ready")
            self.log_message("マクロを停止しました")
            
        except Exception as e:
            self.log_message(f"マクロ停止エラー: {e}")
    
    def manual_use_tincture(self):
        """Tinctureを手動使用"""
        try:
            if self.macro_controller:
                self.macro_controller.manual_tincture_use()
                self.log_message("Tincture手動使用を実行しました")
            else:
                self.log_message("マクロコントローラーが初期化されていません")
            
        except Exception as e:
            self.log_message(f"Tincture手動使用エラー: {e}")
    
    def reset_tincture_stats(self):
        """Tincture統計をリセット"""
        try:
            self.tincture_uses_label.setText("使用回数: 0")
            self.detection_success_label.setText("検出成功: 0")
            self.detection_failed_label.setText("検出失敗: 0")
            self.last_use_label.setText("最後の使用: なし")
            self.log_message("Tincture統計をリセットしました")
            
        except Exception as e:
            self.log_message(f"統計リセットエラー: {e}")
    
    def update_status(self):
        """ステータスを定期更新"""
        try:
            if self.macro_controller:
                status = self.macro_controller.get_status()
                
                # Tincture統計の更新
                if 'tincture' in status and hasattr(self, 'tincture_uses_label'):
                    tincture_stats = status['tincture'].get('stats', {})
                    
                    uses = tincture_stats.get('total_uses', 0)
                    self.tincture_uses_label.setText(f"使用回数: {uses}")
                    
                    success = tincture_stats.get('detection_success', 0)
                    self.detection_success_label.setText(f"検出成功: {success}")
                    
                    failed = tincture_stats.get('detection_failed', 0)
                    self.detection_failed_label.setText(f"検出失敗: {failed}")
                    
                    last_use = tincture_stats.get('last_use')
                    if last_use:
                        import datetime
                        dt = datetime.datetime.fromtimestamp(last_use)
                        self.last_use_label.setText(f"最後の使用: {dt.strftime('%H:%M:%S')}")
                
                # ステータスバーの更新
                if status.get('running', False):
                    if not hasattr(self, '_last_running_status') or not self._last_running_status:
                        self.statusBar().showMessage("マクロ実行中")
                        self.start_btn.setEnabled(False)
                        self.stop_btn.setEnabled(True)
                        self._last_running_status = True
                else:
                    if not hasattr(self, '_last_running_status') or self._last_running_status:
                        self.statusBar().showMessage("Ready")
                        self.start_btn.setEnabled(True)
                        self.stop_btn.setEnabled(False)
                        self._last_running_status = False
            
        except Exception as e:
            logger.error(f"Status update error: {e}")
    
    def log_message(self, message):
        """ログメッセージを表示（安全性チェック付き）"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # log_textが初期化されているかチェック
        if hasattr(self, 'log_text') and self.log_text is not None:
            self.log_text.append(formatted_message)
        else:
            # log_textがまだ初期化されていない場合は、標準ログにのみ出力
            logger.warning(f"log_text not initialized yet: {formatted_message}")
        
        logger.info(message)
    
    def clear_log(self):
        """ログをクリア（安全性チェック付き）"""
        if hasattr(self, 'log_text') and self.log_text is not None:
            self.log_text.clear()
        else:
            logger.warning("log_text not initialized, cannot clear log")
    
    def closeEvent(self, event):
        """ウィンドウが閉じられる時の処理"""
        try:
            self.stop_macro()
            event.accept()
            
        except Exception as e:
            logger.error(f"Close event error: {e}")
            event.accept()

def main():
    """GUI アプリケーションのメイン関数"""
    app = QApplication(sys.argv)
    
    try:
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        window = MainWindow(config_manager, None)
        window.show()
        
        return app.exec_()
        
    except Exception as e:
        print(f"GUI起動エラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
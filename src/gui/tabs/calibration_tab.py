"""
Calibration tab for POE Macro GUI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QGridLayout, QLabel, QPushButton, QComboBox, QSpinBox)
from .base_tab import BaseTab

class CalibrationTab(BaseTab):
    """Calibration settings tab"""
    
    def create_widget(self):
        """Create calibration tab widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 検出エリア設定グループ
        area_group = QGroupBox("検出エリア設定")
        area_layout = QGridLayout(area_group)
        
        # 現在の解像度表示
        area_layout.addWidget(QLabel("検出された解像度:"), 0, 0)
        self.main_window.resolution_label = QLabel("1920x1080")
        area_layout.addWidget(self.main_window.resolution_label, 0, 1)
        
        # ウルトラワイド推奨情報
        self.main_window.suggestion_label = QLabel("")
        area_layout.addWidget(self.main_window.suggestion_label, 0, 2)
        
        # 現在の設定表示
        area_layout.addWidget(QLabel("現在の検出エリア:"), 1, 0)
        self.main_window.current_area_label = QLabel("読み込み中...")
        area_layout.addWidget(self.main_window.current_area_label, 1, 1, 1, 2)
        
        # プリセット選択
        area_layout.addWidget(QLabel("プリセット:"), 2, 0)
        self.main_window.preset_combo = QComboBox()
        self.main_window.preset_combo.addItems(["1920x1080", "2560x1440", "3840x2160", "3440x1440", "2560x1080", "5120x1440", "カスタム"])
        area_layout.addWidget(self.main_window.preset_combo, 2, 1)
        
        self.main_window.apply_preset_btn = QPushButton("プリセット適用")
        self.main_window.apply_preset_btn.clicked.connect(self.main_window.apply_preset)
        area_layout.addWidget(self.main_window.apply_preset_btn, 2, 2)
        
        # オーバーレイ表示ボタン
        self.main_window.show_overlay_btn = QPushButton("検出エリア設定を開く")
        self.main_window.show_overlay_btn.clicked.connect(self.main_window.show_overlay_window)
        area_layout.addWidget(self.main_window.show_overlay_btn, 3, 0, 1, 3)
        
        layout.addWidget(area_group)
        
        # 検出テストグループ
        test_group = QGroupBox("検出テスト")
        test_layout = QGridLayout(test_group)
        
        self.main_window.test_detection_btn = QPushButton("現在のエリアで検出テスト")
        self.main_window.test_detection_btn.clicked.connect(self.main_window.test_detection)
        test_layout.addWidget(self.main_window.test_detection_btn, 0, 0)
        
        self.main_window.test_result_label = QLabel("テスト結果: 未実行")
        test_layout.addWidget(self.main_window.test_result_label, 1, 0)
        
        layout.addWidget(test_group)
        
        # 詳細設定グループ
        detail_group = QGroupBox("詳細設定")
        detail_layout = QGridLayout(detail_group)
        
        detail_layout.addWidget(QLabel("X座標:"), 0, 0)
        self.main_window.x_spinbox = QSpinBox()
        self.main_window.x_spinbox.setRange(0, 3840)
        self.main_window.x_spinbox.setValue(0)  # 初期値は0、後で設定ファイルから読み込み
        detail_layout.addWidget(self.main_window.x_spinbox, 0, 1)
        
        detail_layout.addWidget(QLabel("Y座標:"), 0, 2)
        self.main_window.y_spinbox = QSpinBox()
        self.main_window.y_spinbox.setRange(0, 2160)
        self.main_window.y_spinbox.setValue(0)  # 初期値は0、後で設定ファイルから読み込み
        detail_layout.addWidget(self.main_window.y_spinbox, 0, 3)
        
        detail_layout.addWidget(QLabel("幅:"), 1, 0)
        self.main_window.width_spinbox = QSpinBox()
        self.main_window.width_spinbox.setRange(100, 800)
        self.main_window.width_spinbox.setValue(0)  # 初期値は0、後で設定ファイルから読み込み
        detail_layout.addWidget(self.main_window.width_spinbox, 1, 1)
        
        detail_layout.addWidget(QLabel("高さ:"), 1, 2)
        self.main_window.height_spinbox = QSpinBox()
        self.main_window.height_spinbox.setRange(50, 240)
        self.main_window.height_spinbox.setValue(0)  # 初期値は0、後で設定ファイルから読み込み
        detail_layout.addWidget(self.main_window.height_spinbox, 1, 3)
        
        self.main_window.apply_manual_btn = QPushButton("手動設定を適用")
        self.main_window.apply_manual_btn.clicked.connect(self.main_window.apply_manual_settings)
        detail_layout.addWidget(self.main_window.apply_manual_btn, 2, 0, 1, 4)
        
        layout.addWidget(detail_group)
        layout.addStretch()
        
        # オーバーレイウィンドウの初期化
        self.main_window.overlay_window = None
        self.main_window.area_selector = None
        
        return widget
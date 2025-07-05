"""
Tincture tab for POE Macro GUI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QGridLayout, QLabel, QPushButton, QCheckBox, 
                             QComboBox, QLineEdit, QSlider, QSpinBox)
from PyQt5.QtCore import Qt
from .base_tab import BaseTab

class TinctureTab(BaseTab):
    """Tincture settings tab"""
    
    def create_widget(self):
        """Create tincture tab widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tincture設定グループ
        tincture_group = QGroupBox("Tincture自動使用設定")
        tincture_layout = QGridLayout(tincture_group)
        
        self.main_window.tincture_enabled_cb = QCheckBox("Tincture自動使用を有効化")
        tincture_enabled = self.get_config_value('tincture', 'enabled', True)
        self.main_window.tincture_enabled_cb.setChecked(tincture_enabled)
        tincture_layout.addWidget(self.main_window.tincture_enabled_cb, 0, 0, 1, 2)
        
        tincture_layout.addWidget(QLabel("使用キー:"), 1, 0)
        self.main_window.tincture_key_edit = QLineEdit()
        tincture_key = self.get_config_value('tincture', 'key', '3')
        self.main_window.tincture_key_edit.setText(tincture_key)
        tincture_layout.addWidget(self.main_window.tincture_key_edit, 1, 1)
        
        tincture_layout.addWidget(QLabel("モニター設定:"), 2, 0)
        self.main_window.monitor_combo = QComboBox()
        self.main_window.monitor_combo.addItems(["Primary", "Center", "Right"])
        monitor_config = self.get_config_value('tincture', 'monitor_config', 'Primary')
        self.main_window.monitor_combo.setCurrentText(monitor_config)
        tincture_layout.addWidget(self.main_window.monitor_combo, 2, 1)
        
        tincture_layout.addWidget(QLabel("検出感度:"), 3, 0)
        self.main_window.sensitivity_slider = QSlider(Qt.Horizontal)
        self.main_window.sensitivity_slider.setRange(50, 100)
        sensitivity = int(self.get_config_value('tincture', 'sensitivity', 0.7) * 100)
        self.main_window.sensitivity_slider.setValue(sensitivity)
        self.main_window.sensitivity_slider.valueChanged.connect(self.main_window.update_sensitivity_label)
        tincture_layout.addWidget(self.main_window.sensitivity_slider, 3, 1)
        
        self.main_window.sensitivity_label = QLabel(f"{sensitivity / 100:.2f}")
        tincture_layout.addWidget(self.main_window.sensitivity_label, 3, 2)
        
        # 詳細設定
        tincture_layout.addWidget(QLabel("チェック間隔(ms):"), 4, 0)
        self.main_window.check_interval_spinbox = QSpinBox()
        self.main_window.check_interval_spinbox.setRange(50, 1000)  # 50ms～1000ms
        check_interval = int(self.get_config_value('tincture', 'check_interval', 0.1) * 1000)
        self.main_window.check_interval_spinbox.setValue(check_interval)
        tincture_layout.addWidget(self.main_window.check_interval_spinbox, 4, 1)
        
        tincture_layout.addWidget(QLabel("最小使用間隔(ms):"), 5, 0)
        self.main_window.min_use_interval_spinbox = QSpinBox()
        self.main_window.min_use_interval_spinbox.setRange(100, 5000)  # 100ms～5000ms
        min_use_interval = int(self.get_config_value('tincture', 'min_use_interval', 0.5) * 1000)
        self.main_window.min_use_interval_spinbox.setValue(min_use_interval)
        tincture_layout.addWidget(self.main_window.min_use_interval_spinbox, 5, 1)
        
        layout.addWidget(tincture_group)
        
        # 統計情報グループ
        stats_group = QGroupBox("統計情報")
        stats_layout = QGridLayout(stats_group)
        
        self.main_window.tincture_uses_label = QLabel("使用回数: 0")
        stats_layout.addWidget(self.main_window.tincture_uses_label, 0, 0)
        
        self.main_window.detection_success_label = QLabel("検出成功: 0")
        stats_layout.addWidget(self.main_window.detection_success_label, 0, 1)
        
        self.main_window.detection_failed_label = QLabel("検出失敗: 0")
        stats_layout.addWidget(self.main_window.detection_failed_label, 1, 0)
        
        self.main_window.last_use_label = QLabel("最後の使用: なし")
        stats_layout.addWidget(self.main_window.last_use_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        self.main_window.manual_use_btn = QPushButton("手動使用")
        self.main_window.manual_use_btn.clicked.connect(self.main_window.manual_use_tincture)
        button_layout.addWidget(self.main_window.manual_use_btn)
        
        self.main_window.reset_stats_btn = QPushButton("統計リセット")
        self.main_window.reset_stats_btn.clicked.connect(self.main_window.reset_tincture_stats)
        button_layout.addWidget(self.main_window.reset_stats_btn)
        
        layout.addLayout(button_layout)
        
        # 設定保存・適用ボタン
        settings_button_layout = QHBoxLayout()
        
        self.main_window.save_tincture_btn = QPushButton("設定を保存")
        self.main_window.save_tincture_btn.clicked.connect(self.main_window.save_tincture_settings)
        self.main_window.save_tincture_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        settings_button_layout.addWidget(self.main_window.save_tincture_btn)
        
        self.main_window.apply_tincture_btn = QPushButton("設定を適用（保存せずに）")
        self.main_window.apply_tincture_btn.clicked.connect(self.main_window.apply_tincture_settings)
        self.main_window.apply_tincture_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
        settings_button_layout.addWidget(self.main_window.apply_tincture_btn)
        
        layout.addLayout(settings_button_layout)
        layout.addStretch()
        
        return widget
"""
Control tab for POE Macro GUI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QGridLayout, QLabel, QPushButton, QCheckBox, 
                             QComboBox, QLineEdit)
from .base_tab import BaseTab

class ControlTab(BaseTab):
    """Main control tab for macro operations"""
    
    def create_widget(self):
        """Create control tab widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # マクロ制御グループ
        macro_group = QGroupBox("マクロ制御")
        macro_layout = QGridLayout(macro_group)
        
        self.main_window.macro_enabled_cb = QCheckBox("マクロを有効化")
        self.main_window.macro_enabled_cb.setChecked(True)
        macro_layout.addWidget(self.main_window.macro_enabled_cb, 0, 0, 1, 2)
        
        self.main_window.grace_period_cb = QCheckBox("エリア入場後のプレイヤー入力を待機 (Grace Period)")
        grace_period_enabled = self.get_config_value('grace_period', 'enabled', True)
        self.main_window.grace_period_cb.setChecked(grace_period_enabled)
        self.main_window.grace_period_cb.setToolTip("戦闘エリアに入場後、左/右/中クリックまたはQキーの入力を待ってからマクロを開始します")
        macro_layout.addWidget(self.main_window.grace_period_cb, 1, 0, 1, 2)
        
        macro_layout.addWidget(QLabel("緊急停止キー:"), 2, 0)
        self.main_window.emergency_key_edit = QLineEdit("Ctrl+Shift+F12")
        self.main_window.emergency_key_edit.setReadOnly(True)
        macro_layout.addWidget(self.main_window.emergency_key_edit, 2, 1)
        
        macro_layout.addWidget(QLabel("トグルキー:"), 3, 0)
        self.main_window.toggle_key_edit = QLineEdit("F12")
        self.main_window.toggle_key_edit.setReadOnly(True)
        macro_layout.addWidget(self.main_window.toggle_key_edit, 3, 1)
        
        layout.addWidget(macro_group)
        
        # ログ設定グループ
        log_group = QGroupBox("ログ設定")
        log_layout = QGridLayout(log_group)
        
        log_layout.addWidget(QLabel("ログレベル:"), 0, 0)
        self.main_window.log_level_combo = QComboBox()
        self.main_window.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.main_window.log_level_combo.setCurrentText("INFO")
        log_layout.addWidget(self.main_window.log_level_combo, 0, 1)
        
        layout.addWidget(log_group)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        self.main_window.start_btn = QPushButton("マクロ開始")
        self.main_window.start_btn.clicked.connect(self.main_window.start_macro)
        button_layout.addWidget(self.main_window.start_btn)
        
        self.main_window.stop_btn = QPushButton("マクロ停止")
        self.main_window.stop_btn.clicked.connect(self.main_window.stop_macro)
        self.main_window.stop_btn.setEnabled(False)
        button_layout.addWidget(self.main_window.stop_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
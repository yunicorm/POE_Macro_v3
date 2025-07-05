"""
Flask tab for POE Macro GUI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, 
                             QGridLayout, QCheckBox)
from .base_tab import BaseTab

class FlaskTab(BaseTab):
    """Flask settings tab"""
    
    def create_widget(self):
        """Create flask tab widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        flask_group = QGroupBox("Flask自動使用設定")
        flask_layout = QGridLayout(flask_group)
        
        self.main_window.flask_enabled_cb = QCheckBox("Flask自動使用を有効化")
        flask_enabled = self.get_config_value('flask', 'enabled', True)
        self.main_window.flask_enabled_cb.setChecked(flask_enabled)
        flask_layout.addWidget(self.main_window.flask_enabled_cb, 0, 0, 1, 2)
        
        layout.addWidget(flask_group)
        layout.addStretch()
        
        return widget
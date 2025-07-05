"""
Skills tab for POE Macro GUI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, 
                             QGridLayout, QCheckBox)
from .base_tab import BaseTab

class SkillsTab(BaseTab):
    """Skills settings tab"""
    
    def create_widget(self):
        """Create skills tab widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        skills_group = QGroupBox("スキル自動使用設定")
        skills_layout = QGridLayout(skills_group)
        
        self.main_window.skills_enabled_cb = QCheckBox("スキル自動使用を有効化")
        skills_enabled = self.get_config_value('skills', 'enabled', True)
        self.main_window.skills_enabled_cb.setChecked(skills_enabled)
        skills_layout.addWidget(self.main_window.skills_enabled_cb, 0, 0, 1, 2)
        
        layout.addWidget(skills_group)
        layout.addStretch()
        
        return widget
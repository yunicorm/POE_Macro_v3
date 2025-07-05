"""
Log tab for POE Macro GUI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QGroupBox, QTextEdit, QPushButton)
from PyQt5.QtGui import QFont
from .base_tab import BaseTab

class LogTab(BaseTab):
    """Log display tab"""
    
    def create_widget(self):
        """Create log tab widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        log_group = QGroupBox("ログ出力")
        log_layout = QVBoxLayout(log_group)
        
        # Create log text widget and assign to main window
        self.main_window.log_text = QTextEdit()
        self.main_window.log_text.setReadOnly(True)
        self.main_window.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.main_window.log_text)
        
        button_layout = QHBoxLayout()
        
        clear_log_btn = QPushButton("ログクリア")
        clear_log_btn.clicked.connect(self.main_window.clear_log)
        button_layout.addWidget(clear_log_btn)
        
        log_layout.addLayout(button_layout)
        layout.addWidget(log_group)
        
        return widget
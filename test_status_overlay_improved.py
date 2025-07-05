#!/usr/bin/env python3
"""
ステータスオーバーレイ改善版テストスクリプト
"""
import sys
import os
sys.path.append('src')

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from features.status_overlay import StatusOverlay
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class TestWindow(QMainWindow):
    """テスト用メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.overlay = None
        self.init_ui()
        
    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle("ステータスオーバーレイ改善版テスト")
        self.setGeometry(100, 100, 600, 500)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # レイアウト
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # タイトル
        title_label = QLabel("ステータスオーバーレイ改善版テスト")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # 状態表示
        self.status_label = QLabel("オーバーレイ: 未作成")
        layout.addWidget(self.status_label)
        
        # 位置表示
        self.position_label = QLabel("位置: 未設定")
        layout.addWidget(self.position_label)
        
        # デバッグ情報表示
        self.debug_text = QTextEdit()
        self.debug_text.setMaximumHeight(200)
        layout.addWidget(self.debug_text)
        
        # ボタン群
        button_layout = QHBoxLayout()
        
        # オーバーレイ作成/表示ボタン
        self.create_button = QPushButton("オーバーレイを作成")
        self.create_button.clicked.connect(self.create_overlay)
        button_layout.addWidget(self.create_button)
        
        # 状態切り替えボタン
        self.toggle_button = QPushButton("マクロ状態切り替え")
        self.toggle_button.clicked.connect(self.toggle_macro_status)
        self.toggle_button.setEnabled(False)
        button_layout.addWidget(self.toggle_button)
        
        # 非表示ボタン
        self.hide_button = QPushButton("オーバーレイを非表示")
        self.hide_button.clicked.connect(self.hide_overlay)
        self.hide_button.setEnabled(False)
        button_layout.addWidget(self.hide_button)
        
        # 表示ボタン
        self.show_button = QPushButton("オーバーレイを表示")
        self.show_button.clicked.connect(self.show_overlay)
        self.show_button.setEnabled(False)
        button_layout.addWidget(self.show_button)
        
        layout.addLayout(button_layout)
        
        # 情報更新ボタン
        info_button = QPushButton("情報を更新")
        info_button.clicked.connect(self.update_info)
        layout.addWidget(info_button)
        
        # 終了ボタン
        quit_button = QPushButton("終了")
        quit_button.clicked.connect(self.close)
        layout.addWidget(quit_button)
        
        # 定期的な情報更新
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)  # 1秒ごとに更新
        
        # 操作説明
        help_text = """
        操作方法:
        1. 「オーバーレイを作成」ボタンでオーバーレイを作成
        2. オーバーレイをマウスでドラッグして移動
        3. 右クリックで透明度調整やリセット
        4. 「マクロ状態切り替え」でON/OFF切り替え
        
        改善点:
        - スムーズなドラッグ操作
        - 設定の自動保存 (config/overlay_settings.yaml)
        - 右クリックメニュー
        - 透明度調整
        - 境界線の強調表示
        """
        
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc; }")
        layout.addWidget(help_label)
        
    def create_overlay(self):
        """オーバーレイを作成"""
        if self.overlay is None:
            self.overlay = StatusOverlay(font_size=16)
            self.overlay.position_changed.connect(self.on_position_changed)
            self.overlay.show()
            
            self.create_button.setText("オーバーレイ作成済み")
            self.create_button.setEnabled(False)
            self.toggle_button.setEnabled(True)
            self.hide_button.setEnabled(True)
            self.show_button.setEnabled(True)
            
            self.log_message("オーバーレイを作成しました")
            self.update_info()
        
    def toggle_macro_status(self):
        """マクロ状態を切り替え"""
        if self.overlay:
            current_status = self.overlay.is_macro_on
            new_status = not current_status
            self.overlay.set_macro_status(new_status)
            
            status_text = "ON" if new_status else "OFF"
            self.log_message(f"マクロ状態を{status_text}に切り替えました")
            
    def hide_overlay(self):
        """オーバーレイを非表示"""
        if self.overlay:
            self.overlay.hide()
            self.log_message("オーバーレイを非表示にしました")
            
    def show_overlay(self):
        """オーバーレイを表示"""
        if self.overlay:
            self.overlay.show()
            self.log_message("オーバーレイを表示しました")
            
    def on_position_changed(self, x, y):
        """位置変更イベント"""
        self.log_message(f"位置が変更されました: X={x}, Y={y}")
        self.update_info()
        
    def update_info(self):
        """情報を更新"""
        if self.overlay:
            # 基本情報
            self.status_label.setText(f"オーバーレイ: {'表示' if self.overlay.isVisible() else '非表示'}")
            self.position_label.setText(f"位置: X={self.overlay.overlay_x}, Y={self.overlay.overlay_y}")
            
            # デバッグ情報
            debug_info = self.overlay.get_debug_info()
            debug_text = "デバッグ情報:\n"
            for key, value in debug_info.items():
                debug_text += f"  {key}: {value}\n"
            
            self.debug_text.setText(debug_text)
        else:
            self.status_label.setText("オーバーレイ: 未作成")
            self.position_label.setText("位置: 未設定")
            self.debug_text.setText("デバッグ情報: オーバーレイが作成されていません")
            
    def log_message(self, message):
        """ログメッセージを表示"""
        current_text = self.debug_text.toPlainText()
        new_text = f"[LOG] {message}\n{current_text}"
        self.debug_text.setText(new_text)
        
    def closeEvent(self, event):
        """ウィンドウを閉じる時の処理"""
        if self.overlay:
            self.overlay.close()
        event.accept()

def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    
    # テストウィンドウを作成
    window = TestWindow()
    window.show()
    
    # アプリケーションを実行
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
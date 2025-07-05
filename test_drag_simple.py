#!/usr/bin/env python3
"""
シンプルなドラッグテストスクリプト - 問題の切り分け用
"""
import sys
import os
sys.path.append('src')

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import QTimer, Qt
from features.status_overlay import StatusOverlay
import logging

# ログレベルをDEBUGに設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SimpleDragTest(QMainWindow):
    """シンプルなドラッグテスト"""
    
    def __init__(self):
        super().__init__()
        self.overlay = None
        self.init_ui()
        
    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle("シンプルドラッグテスト")
        self.setGeometry(100, 100, 400, 300)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # タイトル
        title = QLabel("ステータスオーバーレイ ドラッグテスト")
        layout.addWidget(title)
        
        # ログ表示
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        # ボタン
        create_btn = QPushButton("オーバーレイ作成")
        create_btn.clicked.connect(self.create_overlay)
        layout.addWidget(create_btn)
        
        info_btn = QPushButton("デバッグ情報表示")
        info_btn.clicked.connect(self.show_debug_info)
        layout.addWidget(info_btn)
        
        quit_btn = QPushButton("終了")
        quit_btn.clicked.connect(self.close)
        layout.addWidget(quit_btn)
        
        # ログメッセージ表示
        help_text = """
テスト手順:
1. 「オーバーレイ作成」をクリック
2. 画面上部に赤い「マクロオフ」オーバーレイが表示される
3. オーバーレイにマウスをホバーさせる
4. カーソルがオープンハンドに変わることを確認
5. ドラッグして移動を試す
6. ログでイベントが正常に発生しているか確認

問題がある場合:
- ログでenterEvent/mousePressEvent/mouseMoveEventが発生しているか確認
- カーソルが変わらない場合はWA_TransparentForMouseEventsの問題
- ドラッグできない場合はmouseMoveEventが発生していない
        """
        
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; }")
        layout.addWidget(help_label)
        
    def create_overlay(self):
        """オーバーレイを作成"""
        if self.overlay is None:
            self.log_message("オーバーレイを作成します...")
            
            # デバッグ用に小さいサイズでテスト
            self.overlay = StatusOverlay(font_size=12)
            self.overlay.position_changed.connect(self.on_position_changed)
            
            # 見やすい位置に配置
            self.overlay.overlay_x = 200
            self.overlay.overlay_y = 200
            self.overlay.move(200, 200)
            
            self.overlay.show()
            
            self.log_message(f"オーバーレイ作成完了 - 位置: ({self.overlay.overlay_x}, {self.overlay.overlay_y})")
            self.log_message("オーバーレイにマウスをホバーしてください...")
            
    def on_position_changed(self, x, y):
        """位置変更イベント"""
        self.log_message(f"★ 位置変更: X={x}, Y={y}")
        
    def show_debug_info(self):
        """デバッグ情報を表示"""
        if self.overlay:
            debug_info = self.overlay.get_debug_info()
            self.log_message("=== デバッグ情報 ===")
            for key, value in debug_info.items():
                self.log_message(f"  {key}: {value}")
            self.log_message("================")
        else:
            self.log_message("オーバーレイが作成されていません")
            
    def log_message(self, message):
        """ログメッセージを表示"""
        current_text = self.log_text.toPlainText()
        new_text = f"{message}\n{current_text}"
        self.log_text.setText(new_text)
        
        # コンソールにも出力
        print(f"[TEST] {message}")
        
    def closeEvent(self, event):
        """ウィンドウを閉じる時の処理"""
        if self.overlay:
            self.overlay.close()
        event.accept()

def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    
    # テストウィンドウを作成
    window = SimpleDragTest()
    window.show()
    
    print("シンプルドラッグテストを開始しました")
    print("オーバーレイ作成後、ドラッグをテストしてください")
    
    # アプリケーションを実行
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
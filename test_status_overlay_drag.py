#!/usr/bin/env python3
"""
POE Macro v3.0 - Status Overlay Drag Test
ステータスオーバーレイのドラッグ機能テスト
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, '.')

from src.features.status_overlay import StatusOverlay

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class TestWindow(QWidget):
    """テスト用のメインウィンドウ"""
    def __init__(self):
        super().__init__()
        self.status_overlay = None
        self.init_ui()
        
    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle("Status Overlay Drag Test")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # 説明ラベル
        info_label = QLabel(
            "ステータスオーバーレイのドラッグテスト\n\n"
            "1. 「オーバーレイを表示」ボタンをクリック\n"
            "2. オーバーレイにマウスを乗せる\n"
            "3. ドラッグして移動できることを確認\n"
            "4. マウスを離すと透過状態に戻ることを確認"
        )
        info_label.setAlignment(Qt.AlignTop)
        layout.addWidget(info_label)
        
        # オーバーレイ表示ボタン
        self.show_overlay_btn = QPushButton("オーバーレイを表示")
        self.show_overlay_btn.clicked.connect(self.show_overlay)
        layout.addWidget(self.show_overlay_btn)
        
        # 状態切り替えボタン
        self.toggle_status_btn = QPushButton("マクロ状態をトグル")
        self.toggle_status_btn.clicked.connect(self.toggle_status)
        self.toggle_status_btn.setEnabled(False)
        layout.addWidget(self.toggle_status_btn)
        
        # 位置情報ラベル
        self.position_label = QLabel("位置: 未表示")
        layout.addWidget(self.position_label)
        
        # デバッグ情報ラベル
        self.debug_label = QLabel("デバッグ: -")
        layout.addWidget(self.debug_label)
        
        self.setLayout(layout)
        
    def show_overlay(self):
        """オーバーレイを表示"""
        if self.status_overlay is None:
            logger.info("Creating status overlay...")
            self.status_overlay = StatusOverlay(font_size=18)
            
            # 位置変更シグナルに接続
            self.status_overlay.position_changed.connect(self.on_position_changed)
            
            # 初期位置を画面中央に設定
            screen = QApplication.primaryScreen()
            screen_rect = screen.geometry()
            center_x = screen_rect.width() // 2 - 75  # オーバーレイ幅の半分
            center_y = screen_rect.height() // 2 - 20  # オーバーレイ高さの半分
            self.status_overlay.load_position(center_x, center_y)
            
            self.status_overlay.show()
            self.toggle_status_btn.setEnabled(True)
            self.show_overlay_btn.setText("オーバーレイを隠す")
            
            logger.info(f"Overlay shown at ({center_x}, {center_y})")
            self.position_label.setText(f"位置: X={center_x}, Y={center_y}")
            self.debug_label.setText("デバッグ: オーバーレイ作成完了")
        else:
            if self.status_overlay.isVisible():
                self.status_overlay.hide()
                self.show_overlay_btn.setText("オーバーレイを表示")
                self.debug_label.setText("デバッグ: オーバーレイ非表示")
            else:
                self.status_overlay.show()
                self.show_overlay_btn.setText("オーバーレイを隠す")
                self.debug_label.setText("デバッグ: オーバーレイ表示")
                
    def toggle_status(self):
        """マクロ状態をトグル"""
        if self.status_overlay:
            current_status = self.status_overlay.is_macro_on
            self.status_overlay.set_macro_status(not current_status)
            status_text = "ON" if not current_status else "OFF"
            logger.info(f"Macro status toggled to: {status_text}")
            self.debug_label.setText(f"デバッグ: マクロ状態を{status_text}に変更")
            
    def on_position_changed(self, x, y):
        """位置変更時のコールバック"""
        logger.info(f"Overlay position changed to: ({x}, {y})")
        self.position_label.setText(f"位置: X={x}, Y={y}")
        self.debug_label.setText(f"デバッグ: ドラッグで位置変更 ({x}, {y})")

def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    
    # テストウィンドウを作成
    test_window = TestWindow()
    test_window.show()
    
    logger.info("Status overlay drag test started")
    logger.info("Instructions:")
    logger.info("1. Click 'Show Overlay' button")
    logger.info("2. Hover mouse over the overlay")
    logger.info("3. Drag to move the overlay")
    logger.info("4. Check if dragging works smoothly")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
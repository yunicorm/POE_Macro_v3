"""
POE Macro v3.0 - Overlay Window for Flask Area Detection
半透明オーバーレイウィンドウによる検出エリア設定機能
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QKeyEvent, QMouseEvent, QWheelEvent
from pynput import keyboard
import threading
import logging

class OverlayWindow(QWidget):
    """
    半透明オーバーレイウィンドウクラス
    フラスコ検出エリアを視覚的に設定するためのウィンドウ
    """
    
    # シグナル定義
    area_changed = pyqtSignal(int, int, int, int)  # x, y, width, height
    settings_saved = pyqtSignal()
    overlay_closed = pyqtSignal()
    
    def __init__(self, initial_x=245, initial_y=850, initial_width=400, initial_height=120):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 初期位置とサイズ
        self.overlay_x = initial_x
        self.overlay_y = initial_y
        self.overlay_width = initial_width
        self.overlay_height = initial_height
        
        # 操作状態
        self.is_dragging = False
        self.is_resizing = False
        self.drag_start_pos = QPoint()
        self.resize_start_pos = QPoint()
        self.resize_start_size = QPoint()
        
        # スケール調整
        self.scale_factor = 1.0
        
        # 表示状態
        self.is_visible = False
        
        # キーボードリスナー
        self.keyboard_listener = None
        
        # ウィンドウ設定
        self.init_ui()
        self.setup_global_hotkeys()
        
    def init_ui(self):
        """UIの初期化"""
        # ウィンドウフラグ設定
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |  # Always on top
            Qt.FramelessWindowHint |   # フレームレス
            Qt.Tool |                  # タスクバーに表示しない
            Qt.WindowTransparentForInput  # 一部の入力を透過（必要に応じて削除）
        )
        
        # 削除: WindowTransparentForInputを削除して操作可能にする
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        
        # 背景を透明に
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # ウィンドウサイズと位置を設定
        self.update_geometry()
        
        # フォント設定
        self.font = QFont("Arial", 12, QFont.Bold)
        
        # キーボードフォーカスを有効にする
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.logger.info("オーバーレイウィンドウを初期化しました")
        
    def update_geometry(self):
        """ウィンドウの位置とサイズを更新"""
        scaled_width = int(self.overlay_width * self.scale_factor)
        scaled_height = int(self.overlay_height * self.scale_factor)
        
        self.setGeometry(
            self.overlay_x,
            self.overlay_y,
            scaled_width,
            scaled_height
        )
        
    def paintEvent(self, event):
        """ウィンドウの描画"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 緑色の半透明矩形を描画
        overlay_color = QColor(0, 255, 0, 128)  # 緑色、透明度50%
        painter.fillRect(self.rect(), overlay_color)
        
        # 境界線を描画
        border_color = QColor(0, 255, 0, 255)  # 不透明な緑色
        border_pen = QPen(border_color, 2)
        painter.setPen(border_pen)
        painter.drawRect(self.rect())
        
        # 座標情報を中央に表示
        painter.setPen(QPen(QColor(255, 255, 255, 255)))  # 白色
        painter.setFont(self.font)
        
        text = f"X: {self.overlay_x}, Y: {self.overlay_y}, W: {self.overlay_width}, H: {self.overlay_height}"
        text_rect = painter.fontMetrics().boundingRect(text)
        
        # テキストを中央に配置
        center_x = self.rect().center().x() - text_rect.width() // 2
        center_y = self.rect().center().y() + text_rect.height() // 2
        
        painter.drawText(center_x, center_y, text)
        
        # スケール情報を表示
        scale_text = f"Scale: {self.scale_factor:.1f}"
        scale_rect = painter.fontMetrics().boundingRect(scale_text)
        painter.drawText(
            self.rect().width() - scale_rect.width() - 10,
            self.rect().height() - 10,
            scale_text
        )
        
    def mousePressEvent(self, event):
        """マウスプレスイベント"""
        if event.button() == Qt.LeftButton:
            modifiers = QApplication.keyboardModifiers()
            
            if modifiers & Qt.ShiftModifier:
                # Shift+クリック: リサイズ開始
                self.is_resizing = True
                self.resize_start_pos = event.globalPos()
                self.resize_start_size = QPoint(self.overlay_width, self.overlay_height)
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                # 通常のクリック: ドラッグ開始
                self.is_dragging = True
                self.drag_start_pos = event.globalPos() - self.pos()
                self.setCursor(Qt.ClosedHandCursor)
                
    def mouseMoveEvent(self, event):
        """マウス移動イベント"""
        if self.is_dragging:
            # ウィンドウを移動
            new_pos = event.globalPos() - self.drag_start_pos
            self.move(new_pos)
            self.overlay_x = new_pos.x()
            self.overlay_y = new_pos.y()
            self.area_changed.emit(self.overlay_x, self.overlay_y, self.overlay_width, self.overlay_height)
            
        elif self.is_resizing:
            # ウィンドウをリサイズ
            delta = event.globalPos() - self.resize_start_pos
            new_width = max(100, self.resize_start_size.x() + delta.x())
            new_height = max(50, self.resize_start_size.y() + delta.y())
            
            self.overlay_width = new_width
            self.overlay_height = new_height
            self.update_geometry()
            self.area_changed.emit(self.overlay_x, self.overlay_y, self.overlay_width, self.overlay_height)
            
    def mouseReleaseEvent(self, event):
        """マウスリリースイベント"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.is_resizing = False
            self.setCursor(Qt.ArrowCursor)
            
    def wheelEvent(self, event):
        """マウスホイールイベント（スケール調整）"""
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor = min(2.0, self.scale_factor + 0.05)
        else:
            self.scale_factor = max(0.5, self.scale_factor - 0.05)
            
        self.update_geometry()
        self.update()
        
    def keyPressEvent(self, event):
        """キーボードイベント"""
        modifiers = QApplication.keyboardModifiers()
        
        if event.key() == Qt.Key_F10:
            # F10キーで終了（ESCはゲームメニューと衝突するため）
            event.accept()
            self.close_overlay()
            return
            
        elif event.key() == Qt.Key_S and modifiers & Qt.ControlModifier:
            # Ctrl+Sで保存
            self.save_settings()
            
        elif event.key() in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down]:
            # 矢印キーで位置調整
            self.handle_arrow_keys(event.key(), modifiers)
            
    def handle_arrow_keys(self, key, modifiers):
        """矢印キーによる位置・サイズ調整"""
        if modifiers & Qt.ShiftModifier:
            # Shift+矢印: サイズ調整
            if key == Qt.Key_Left:
                self.overlay_width = max(100, self.overlay_width - 1)
            elif key == Qt.Key_Right:
                self.overlay_width += 1
            elif key == Qt.Key_Up:
                self.overlay_height = max(50, self.overlay_height - 1)
            elif key == Qt.Key_Down:
                self.overlay_height += 1
                
            self.update_geometry()
        else:
            # 通常の矢印: 位置調整
            if key == Qt.Key_Left:
                self.overlay_x -= 1
            elif key == Qt.Key_Right:
                self.overlay_x += 1
            elif key == Qt.Key_Up:
                self.overlay_y -= 1
            elif key == Qt.Key_Down:
                self.overlay_y += 1
                
            self.move(self.overlay_x, self.overlay_y)
            
        self.area_changed.emit(self.overlay_x, self.overlay_y, self.overlay_width, self.overlay_height)
        self.update()
        
    def setup_global_hotkeys(self):
        """グローバルホットキーの設定"""
        def on_press(key):
            try:
                if key == keyboard.Key.f9:
                    self.toggle_visibility()
            except AttributeError:
                pass
                
        # キーボードリスナーを開始
        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()
        
    def toggle_visibility(self):
        """表示/非表示の切り替え"""
        if self.is_visible:
            self.hide()
            self.is_visible = False
        else:
            self.show()
            self.activateWindow()
            self.raise_()
            self.setFocus()
            self.is_visible = True
            
    def show_overlay(self):
        """オーバーレイを表示"""
        self.show()
        self.activateWindow()
        self.raise_()
        self.setFocus()
        self.is_visible = True
        self.logger.info("オーバーレイウィンドウを表示しました")
        
    def close_overlay(self):
        """オーバーレイを閉じる"""
        self.hide()
        self.is_visible = False
        self.overlay_closed.emit()
        self.logger.info("オーバーレイウィンドウを閉じました")
        
    def save_settings(self):
        """設定を保存"""
        self.settings_saved.emit()
        self.logger.info(f"設定を保存しました: ({self.overlay_x}, {self.overlay_y}, {self.overlay_width}, {self.overlay_height})")
        
    def set_area(self, x, y, width, height):
        """エリアを設定"""
        self.overlay_x = x
        self.overlay_y = y
        self.overlay_width = width
        self.overlay_height = height
        self.update_geometry()
        self.update()
        
    def get_area(self):
        """現在のエリアを取得"""
        return {
            'x': self.overlay_x,
            'y': self.overlay_y,
            'width': self.overlay_width,
            'height': self.overlay_height
        }
        
    def closeEvent(self, event):
        """ウィンドウ終了時の処理"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        event.accept()


def main():
    """テスト用のメイン関数"""
    app = QApplication(sys.argv)
    
    # ロギング設定
    logging.basicConfig(level=logging.INFO)
    
    # オーバーレイウィンドウを作成
    overlay = OverlayWindow()
    
    # シグナル接続
    overlay.area_changed.connect(lambda x, y, w, h: print(f"エリア変更: {x}, {y}, {w}, {h}"))
    overlay.settings_saved.connect(lambda: print("設定が保存されました"))
    overlay.overlay_closed.connect(lambda: print("オーバーレイが閉じられました"))
    
    # オーバーレイを表示
    overlay.show_overlay()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
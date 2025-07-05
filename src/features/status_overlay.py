"""
マクロ状態表示オーバーレイ
常時画面上にマクロのON/OFF状態を表示する半透明オーバーレイウィンドウ
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QFontDatabase
import logging

class StatusOverlay(QWidget):
    """マクロのON/OFF状態を表示するオーバーレイウィンドウ"""
    
    position_changed = pyqtSignal(int, int)
    
    def __init__(self, parent=None, font_size=16):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # フォントサイズを保存
        self.font_size = font_size
        
        # 初期位置（フラスコエリアの上部中央を想定）
        self.overlay_x = 1720  # 3440/2（中央モニター中心）
        self.overlay_y = 1050  # フラスコエリアの少し上
        
        # ステータス
        self.is_macro_on = False
        
        # ドラッグ状態
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        
        # UI初期化
        self.init_ui()
        
    def init_ui(self):
        """UIの初期化"""
        # ウィンドウフラグ設定
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |      # 常に最前面
            Qt.FramelessWindowHint |       # フレームなし
            Qt.Tool |                      # タスクバーに表示しない
            Qt.WindowTransparentForInput   # マウスクリック透過
        )
        
        # 背景を半透明に
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # ウィンドウサイズ（コンパクトに）
        self.setFixedSize(150, 40)
        
        # 初期位置
        self.move(self.overlay_x, self.overlay_y)
        
        # フォント設定（太字で見やすく）
        self.font = QFont("Arial", self.font_size, QFont.Bold)
        
        # 右クリックメニューを無効化（誤操作防止）
        self.setContextMenuPolicy(Qt.NoContextMenu)
        
        self.logger.info("ステータスオーバーレイを初期化しました")
        
    def set_macro_status(self, is_on: bool):
        """マクロの状態を設定"""
        self.is_macro_on = is_on
        self.update()  # 再描画
        self.logger.info(f"マクロステータス更新: {'ON' if is_on else 'OFF'}")
        
    def paintEvent(self, event):
        """描画イベント"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景（半透明黒）
        bg_color = QColor(0, 0, 0, 180)  # 黒、透明度70%
        painter.fillRect(self.rect(), bg_color)
        
        # 境界線とテキスト色
        if self.is_macro_on:
            border_color = QColor(0, 255, 0, 255)  # 緑
            text_color = QColor(0, 255, 0, 255)
            status_text = "マクロオン"
        else:
            border_color = QColor(255, 0, 0, 255)  # 赤
            text_color = QColor(255, 0, 0, 255)
            status_text = "マクロオフ"
            
        # 境界線描画
        painter.setPen(QPen(border_color, 2))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
        # テキスト描画
        painter.setPen(QPen(text_color))
        painter.setFont(self.font)
        painter.drawText(self.rect(), Qt.AlignCenter, status_text)
        
    def enterEvent(self, event):
        """マウスがウィンドウに入った時（ドラッグ準備）"""
        # マウスオーバー時にクリック透過を一時解除
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowTransparentForInput)
        self.show()
        self.setCursor(Qt.OpenHandCursor)
        
    def leaveEvent(self, event):
        """マウスがウィンドウから出た時（ドラッグ終了）"""
        if not self.is_dragging:
            # ドラッグ中でない場合のみクリック透過を再設定
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
            self.show()
            self.setCursor(Qt.ArrowCursor)
        
    def mousePressEvent(self, event):
        """マウス押下イベント（ドラッグ開始）"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.globalPos() - self.pos()
            self.setCursor(Qt.ClosedHandCursor)
            
    def mouseMoveEvent(self, event):
        """マウス移動イベント（ドラッグ中）"""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_start_pos
            self.move(new_pos)
            self.overlay_x = new_pos.x()
            self.overlay_y = new_pos.y()
            self.position_changed.emit(self.overlay_x, self.overlay_y)
            
    def mouseReleaseEvent(self, event):
        """マウスリリースイベント（ドラッグ終了）"""
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.setCursor(Qt.ArrowCursor)
            
            # 少し遅延してからクリック透過を再設定
            QTimer.singleShot(100, self._reset_transparency)
            
    def _reset_transparency(self):
        """クリック透過の再設定"""
        self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
        self.show()
        
    def save_position(self):
        """現在位置を保存"""
        return {'x': self.overlay_x, 'y': self.overlay_y}
        
    def load_position(self, x, y):
        """保存された位置を読み込み"""
        self.overlay_x = x
        self.overlay_y = y
        self.move(x, y)
        self.logger.info(f"オーバーレイ位置を読み込み: X={x}, Y={y}")
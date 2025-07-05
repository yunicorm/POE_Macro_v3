"""
マクロ状態表示オーバーレイ
常時画面上にマクロのON/OFF状態を表示する半透明オーバーレイウィンドウ
"""
import sys
import os
import yaml
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMenu, QAction
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QFontDatabase, QCursor
import logging

class StatusOverlay(QWidget):
    """マクロのON/OFF状態を表示するオーバーレイウィンドウ"""
    
    position_changed = pyqtSignal(int, int)
    
    def __init__(self, parent=None, font_size=16):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # 設定ファイルのパス
        self.config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'overlay_settings.yaml')
        
        # フォントサイズを保存
        self.font_size = font_size
        
        # 初期位置（フラスコエリアの上部中央を想定）
        self.overlay_x = 1720  # 3440/2（中央モニター中心）
        self.overlay_y = 1050  # フラスコエリアの少し上
        self.overlay_width = 150
        self.overlay_height = 40
        self.overlay_opacity = 0.8
        
        # ステータス
        self.is_macro_on = False
        
        # ドラッグ状態
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self.hover_active = False
        
        # 設定読み込み
        self.load_settings()
        
        # UI初期化
        self.init_ui()
        
    def init_ui(self):
        """UIの初期化"""
        # ウィンドウフラグ設定（シンプルな設定）
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |      # 常に最前面
            Qt.FramelessWindowHint |       # フレームなし
            Qt.Tool                        # タスクバーに表示しない
        )
        
        # 背景を半透明に
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 初期状態ではマウスイベントを透過
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # ウィンドウサイズ
        self.setFixedSize(self.overlay_width, self.overlay_height)
        
        # 初期位置
        self.move(self.overlay_x, self.overlay_y)
        
        # 透明度設定
        self.setWindowOpacity(self.overlay_opacity)
        
        # フォント設定（太字で見やすく）
        self.font = QFont("Arial", self.font_size, QFont.Bold)
        
        # 右クリックメニューを有効化
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.logger.info("ステータスオーバーレイを初期化しました")
        self.logger.debug(f"[INIT] Initial flags: {self.windowFlags()}")
        self.logger.debug(f"[INIT] Transparent for mouse events: {self.testAttribute(Qt.WA_TransparentForMouseEvents)}")
        
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
            
        # 境界線描画（ドラッグ中、ホバー中は強調）
        border_width = 3 if (self.is_dragging or self.hover_active) else 2
        painter.setPen(QPen(border_color, border_width))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
        # テキスト描画
        painter.setPen(QPen(text_color))
        painter.setFont(self.font)
        painter.drawText(self.rect(), Qt.AlignCenter, status_text)
        
    def enterEvent(self, event):
        """マウスオーバー時の処理を簡素化"""
        self.logger.debug("[ENTER] enterEvent triggered")
        self.hover_active = True
        
        # マウスイベントの透過を無効化（ドラッグを可能に）
        was_transparent = self.testAttribute(Qt.WA_TransparentForMouseEvents)
        self.logger.debug(f"[ENTER] Was transparent: {was_transparent}")
        
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setCursor(Qt.OpenHandCursor)
        
        self.logger.debug("[ENTER] Mouse events enabled, cursor set to OpenHandCursor")
        
        # ドラッグ中は境界線を強調
        self.update()
        self.logger.debug("[ENTER] Update called")
        
    def leaveEvent(self, event):
        """マウスアウト時の処理"""
        self.logger.debug(f"[LEAVE] leaveEvent triggered, is_dragging: {self.is_dragging}")
        self.hover_active = False
        
        if not self.is_dragging:
            # ドラッグ中でない場合のみクリック透過を再設定
            self.setCursor(Qt.ArrowCursor)
            self.logger.debug("[LEAVE] Cursor set to ArrowCursor")
            
            # 遅延なしで直接設定
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.logger.debug("[LEAVE] Mouse events disabled (transparent)")
        
        self.update()
        self.logger.debug("[LEAVE] Update called")
        
    def mousePressEvent(self, event):
        """マウス押下イベント（ドラッグ開始）"""
        self.logger.debug(f"[PRESS] mousePressEvent triggered, button: {event.button()}")
        
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.globalPos() - self.pos()
            self.setCursor(Qt.ClosedHandCursor)
            
            self.logger.debug(f"[PRESS] Drag started at global: {event.globalPos()}, widget: {self.pos()}")
            self.logger.debug(f"[PRESS] Drag start pos: {self.drag_start_pos}")
            self.logger.debug(f"[PRESS] is_dragging set to: {self.is_dragging}")
            
    def mouseMoveEvent(self, event):
        """マウス移動イベント（ドラッグ中）"""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_start_pos
            
            self.logger.debug(f"[MOVE] Dragging - Global: {event.globalPos()}, New pos: {new_pos}")
            
            self.move(new_pos)
            self.overlay_x = new_pos.x()
            self.overlay_y = new_pos.y()
            
            self.logger.debug(f"[MOVE] Moved to: X={self.overlay_x}, Y={self.overlay_y}")
            
            self.position_changed.emit(self.overlay_x, self.overlay_y)
        elif self.is_dragging:
            self.logger.debug(f"[MOVE] Dragging but wrong button state: {event.buttons()}")
            
    def mouseReleaseEvent(self, event):
        """マウスリリースイベント（ドラッグ終了）"""
        self.logger.debug(f"[RELEASE] mouseReleaseEvent triggered, button: {event.button()}, is_dragging: {self.is_dragging}")
        
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.setCursor(Qt.OpenHandCursor)  # OpenHandCursorを維持
            
            self.logger.debug(f"[RELEASE] Drag ended at position: X={self.overlay_x}, Y={self.overlay_y}")
            
            # 位置を保存
            self.save_settings()
            
            # マウスがまだウィンドウ上にあるかチェック
            mouse_in_widget = self.rect().contains(self.mapFromGlobal(event.globalPos()))
            self.logger.debug(f"[RELEASE] Mouse in widget: {mouse_in_widget}")
            
            if not mouse_in_widget:
                # マウスがウィンドウ外に移動した場合は透過を設定
                self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                self.setCursor(Qt.ArrowCursor)
                self.logger.debug("[RELEASE] Mouse events disabled (transparent)")
            
            self.update()  # 再描画で境界線を戸して更新
            
    def _reset_transparency(self):
        """クリック透過の再設定（新しい実装では使用しない）"""
        # このメソッドは新しい実装では使用しないが、互換性のために保持
        self.logger.debug("[RESET] _reset_transparency called (not used in new implementation)")
        pass
        
    def save_position(self):
        """現在位置を保存"""
        return {'x': self.overlay_x, 'y': self.overlay_y}
        
    def load_position(self, x, y):
        """保存された位置を読み込み"""
        self.overlay_x = x
        self.overlay_y = y
        self.move(x, y)
        self.logger.info(f"オーバーレイ位置を読み込み: X={x}, Y={y}")
        
    def load_settings(self):
        """設定ファイルから設定を読み込み"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    overlay_config = config.get('status_overlay', {})
                    
                    self.overlay_x = overlay_config.get('x', 1720)
                    self.overlay_y = overlay_config.get('y', 1050)
                    self.overlay_width = overlay_config.get('width', 150)
                    self.overlay_height = overlay_config.get('height', 40)
                    self.overlay_opacity = overlay_config.get('opacity', 0.8)
                    
                    self.logger.info(f"設定を読み込みました: X={self.overlay_x}, Y={self.overlay_y}")
        except Exception as e:
            self.logger.warning(f"設定読み込みエラー: {e}")
    
    def save_settings(self):
        """設定ファイルに設定を保存"""
        try:
            # 設定ディレクトリが存在しない場合は作成
            config_dir = os.path.dirname(self.config_path)
            os.makedirs(config_dir, exist_ok=True)
            
            config = {
                'status_overlay': {
                    'x': self.overlay_x,
                    'y': self.overlay_y,
                    'width': self.overlay_width,
                    'height': self.overlay_height,
                    'visible': True,
                    'opacity': self.overlay_opacity,
                    'font_size': self.font_size,
                    'always_on_top': True,
                    'click_through': True
                }
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"設定を保存しました: X={self.overlay_x}, Y={self.overlay_y}")
        except Exception as e:
            self.logger.error(f"設定保存エラー: {e}")
    
    def show_context_menu(self, position):
        """右クリックメニューを表示"""
        context_menu = QMenu(self)
        
        # 非表示アクション
        hide_action = QAction("非表示", self)
        hide_action.triggered.connect(self.hide)
        context_menu.addAction(hide_action)
        
        # 透明度調整メニュー
        opacity_menu = context_menu.addMenu("透明度調整")
        
        opacity_values = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for opacity in opacity_values:
            action = QAction(f"{int(opacity * 100)}%", self)
            action.triggered.connect(lambda checked, op=opacity: self.set_opacity(op))
            opacity_menu.addAction(action)
        
        context_menu.addSeparator()
        
        # リセットアクション
        reset_action = QAction("デフォルト位置にリセット", self)
        reset_action.triggered.connect(self.reset_position)
        context_menu.addAction(reset_action)
        
        context_menu.exec_(self.mapToGlobal(position))
    
    def set_opacity(self, opacity):
        """透明度を設定"""
        self.overlay_opacity = opacity
        self.setWindowOpacity(opacity)
        self.save_settings()
        self.logger.info(f"透明度を設定: {int(opacity * 100)}%")
    
    def reset_position(self):
        """デフォルト位置にリセット"""
        self.overlay_x = 1720
        self.overlay_y = 1050
        self.move(self.overlay_x, self.overlay_y)
        self.save_settings()
        self.logger.info("デフォルト位置にリセットしました")
    
    def get_debug_info(self):
        """デバッグ情報を取得"""
        flags = self.windowFlags()
        transparent = bool(flags & Qt.WindowTransparentForInput)
        return {
            'position': (self.overlay_x, self.overlay_y),
            'size': (self.overlay_width, self.overlay_height),
            'is_dragging': self.is_dragging,
            'hover_active': self.hover_active,
            'is_transparent': transparent,
            'is_macro_on': self.is_macro_on,
            'opacity': self.overlay_opacity,
            'window_flags': flags
        }
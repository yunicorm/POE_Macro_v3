"""
POE Macro v3.0 メインGUIウィンドウ
"""
import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QLabel, QPushButton,
                             QCheckBox, QSpinBox, QComboBox, QTextEdit,
                             QGroupBox, QGridLayout, QSlider, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """メインGUIウィンドウクラス"""
    
    def __init__(self, config_manager, macro_controller=None):
        super().__init__()
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.macro_controller = macro_controller
        
        self.setWindowTitle("POE Macro v3.0")
        self.setGeometry(100, 100, 800, 600)
        
        # UI要素の初期化
        self.init_ui()
        
        # 定期更新タイマー
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # 1秒毎
        
        logger.info("MainWindow initialized")
    
    def init_ui(self):
        """UI要素を初期化"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 各タブを作成
        self.create_general_tab()
        self.create_tincture_tab()
        self.create_flask_tab()
        self.create_skills_tab()
        self.create_log_tab()
        
        # ステータスバー
        self.statusBar().showMessage("Ready")
    
    def create_general_tab(self):
        """一般設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # マクロ制御グループ
        macro_group = QGroupBox("マクロ制御")
        macro_layout = QGridLayout(macro_group)
        
        self.macro_enabled_cb = QCheckBox("マクロを有効化")
        self.macro_enabled_cb.setChecked(True)
        macro_layout.addWidget(self.macro_enabled_cb, 0, 0)
        
        macro_layout.addWidget(QLabel("緊急停止キー:"), 1, 0)
        self.emergency_key_edit = QLineEdit("F12")
        macro_layout.addWidget(self.emergency_key_edit, 1, 1)
        
        layout.addWidget(macro_group)
        
        # ログ設定グループ
        log_group = QGroupBox("ログ設定")
        log_layout = QGridLayout(log_group)
        
        log_layout.addWidget(QLabel("ログレベル:"), 0, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        log_layout.addWidget(self.log_level_combo, 0, 1)
        
        layout.addWidget(log_group)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("マクロ開始")
        self.start_btn.clicked.connect(self.start_macro)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("マクロ停止")
        self.stop_btn.clicked.connect(self.stop_macro)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "一般")
    
    def create_tincture_tab(self):
        """Tincture設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tincture設定グループ
        tincture_group = QGroupBox("Tincture自動使用設定")
        tincture_layout = QGridLayout(tincture_group)
        
        self.tincture_enabled_cb = QCheckBox("Tincture自動使用を有効化")
        tincture_enabled = self.config.get('tincture', {}).get('enabled', True)
        self.tincture_enabled_cb.setChecked(tincture_enabled)
        tincture_layout.addWidget(self.tincture_enabled_cb, 0, 0, 1, 2)
        
        tincture_layout.addWidget(QLabel("使用キー:"), 1, 0)
        self.tincture_key_edit = QLineEdit()
        tincture_key = self.config.get('tincture', {}).get('key', '3')
        self.tincture_key_edit.setText(tincture_key)
        tincture_layout.addWidget(self.tincture_key_edit, 1, 1)
        
        tincture_layout.addWidget(QLabel("モニター設定:"), 2, 0)
        self.monitor_combo = QComboBox()
        self.monitor_combo.addItems(["Primary", "Center", "Right"])
        monitor_config = self.config.get('tincture', {}).get('monitor_config', 'Primary')
        self.monitor_combo.setCurrentText(monitor_config)
        tincture_layout.addWidget(self.monitor_combo, 2, 1)
        
        tincture_layout.addWidget(QLabel("検出感度:"), 3, 0)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(50, 100)
        sensitivity = int(self.config.get('tincture', {}).get('sensitivity', 0.7) * 100)
        self.sensitivity_slider.setValue(sensitivity)
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity_label)
        tincture_layout.addWidget(self.sensitivity_slider, 3, 1)
        
        self.sensitivity_label = QLabel(f"{sensitivity}%")
        tincture_layout.addWidget(self.sensitivity_label, 3, 2)
        
        layout.addWidget(tincture_group)
        
        # 統計情報グループ
        stats_group = QGroupBox("統計情報")
        stats_layout = QGridLayout(stats_group)
        
        self.tincture_uses_label = QLabel("使用回数: 0")
        stats_layout.addWidget(self.tincture_uses_label, 0, 0)
        
        self.detection_success_label = QLabel("検出成功: 0")
        stats_layout.addWidget(self.detection_success_label, 0, 1)
        
        self.detection_failed_label = QLabel("検出失敗: 0")
        stats_layout.addWidget(self.detection_failed_label, 1, 0)
        
        self.last_use_label = QLabel("最後の使用: なし")
        stats_layout.addWidget(self.last_use_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        self.manual_use_btn = QPushButton("手動使用")
        self.manual_use_btn.clicked.connect(self.manual_use_tincture)
        button_layout.addWidget(self.manual_use_btn)
        
        self.reset_stats_btn = QPushButton("統計リセット")
        self.reset_stats_btn.clicked.connect(self.reset_tincture_stats)
        button_layout.addWidget(self.reset_stats_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Tincture")
    
    def create_flask_tab(self):
        """Flask設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        flask_group = QGroupBox("Flask自動使用設定")
        flask_layout = QGridLayout(flask_group)
        
        self.flask_enabled_cb = QCheckBox("Flask自動使用を有効化")
        flask_enabled = self.config.get('flask', {}).get('enabled', True)
        self.flask_enabled_cb.setChecked(flask_enabled)
        flask_layout.addWidget(self.flask_enabled_cb, 0, 0, 1, 2)
        
        layout.addWidget(flask_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Flask")
    
    def create_skills_tab(self):
        """スキル設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        skills_group = QGroupBox("スキル自動使用設定")
        skills_layout = QGridLayout(skills_group)
        
        self.skills_enabled_cb = QCheckBox("スキル自動使用を有効化")
        skills_enabled = self.config.get('skills', {}).get('enabled', True)
        self.skills_enabled_cb.setChecked(skills_enabled)
        skills_layout.addWidget(self.skills_enabled_cb, 0, 0, 1, 2)
        
        layout.addWidget(skills_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "スキル")
    
    def create_log_tab(self):
        """ログタブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        log_group = QGroupBox("ログ出力")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        button_layout = QHBoxLayout()
        
        clear_log_btn = QPushButton("ログクリア")
        clear_log_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_log_btn)
        
        log_layout.addLayout(button_layout)
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(widget, "ログ")
    
    def update_sensitivity_label(self, value):
        """感度ラベルを更新"""
        self.sensitivity_label.setText(f"{value}%")
    
    def start_macro(self):
        """マクロを開始"""
        try:
            if self.macro_controller:
                self.macro_controller.start()
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.statusBar().showMessage("マクロ実行中")
                self.log_message("マクロを開始しました")
            else:
                self.log_message("マクロコントローラーが初期化されていません")
            
        except Exception as e:
            self.log_message(f"マクロ開始エラー: {e}")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    def stop_macro(self):
        """マクロを停止"""
        try:
            if self.macro_controller:
                self.macro_controller.stop()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.statusBar().showMessage("Ready")
            self.log_message("マクロを停止しました")
            
        except Exception as e:
            self.log_message(f"マクロ停止エラー: {e}")
    
    def manual_use_tincture(self):
        """Tinctureを手動使用"""
        try:
            if self.macro_controller:
                self.macro_controller.manual_tincture_use()
                self.log_message("Tincture手動使用を実行しました")
            else:
                self.log_message("マクロコントローラーが初期化されていません")
            
        except Exception as e:
            self.log_message(f"Tincture手動使用エラー: {e}")
    
    def reset_tincture_stats(self):
        """Tincture統計をリセット"""
        try:
            self.tincture_uses_label.setText("使用回数: 0")
            self.detection_success_label.setText("検出成功: 0")
            self.detection_failed_label.setText("検出失敗: 0")
            self.last_use_label.setText("最後の使用: なし")
            self.log_message("Tincture統計をリセットしました")
            
        except Exception as e:
            self.log_message(f"統計リセットエラー: {e}")
    
    def update_status(self):
        """ステータスを定期更新"""
        try:
            if self.macro_controller:
                status = self.macro_controller.get_status()
                
                # Tincture統計の更新
                if 'tincture' in status and hasattr(self, 'tincture_uses_label'):
                    tincture_stats = status['tincture'].get('stats', {})
                    
                    uses = tincture_stats.get('total_uses', 0)
                    self.tincture_uses_label.setText(f"使用回数: {uses}")
                    
                    success = tincture_stats.get('detection_success', 0)
                    self.detection_success_label.setText(f"検出成功: {success}")
                    
                    failed = tincture_stats.get('detection_failed', 0)
                    self.detection_failed_label.setText(f"検出失敗: {failed}")
                    
                    last_use = tincture_stats.get('last_use')
                    if last_use:
                        import datetime
                        dt = datetime.datetime.fromtimestamp(last_use)
                        self.last_use_label.setText(f"最後の使用: {dt.strftime('%H:%M:%S')}")
                
                # ステータスバーの更新
                if status.get('running', False):
                    if not hasattr(self, '_last_running_status') or not self._last_running_status:
                        self.statusBar().showMessage("マクロ実行中")
                        self.start_btn.setEnabled(False)
                        self.stop_btn.setEnabled(True)
                        self._last_running_status = True
                else:
                    if not hasattr(self, '_last_running_status') or self._last_running_status:
                        self.statusBar().showMessage("Ready")
                        self.start_btn.setEnabled(True)
                        self.stop_btn.setEnabled(False)
                        self._last_running_status = False
            
        except Exception as e:
            logger.error(f"Status update error: {e}")
    
    def log_message(self, message):
        """ログメッセージを表示"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        logger.info(message)
    
    def clear_log(self):
        """ログをクリア"""
        self.log_text.clear()
    
    def closeEvent(self, event):
        """ウィンドウが閉じられる時の処理"""
        try:
            self.stop_macro()
            event.accept()
            
        except Exception as e:
            logger.error(f"Close event error: {e}")
            event.accept()

def main():
    """GUI アプリケーションのメイン関数"""
    app = QApplication(sys.argv)
    
    try:
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        window = MainWindow(config_manager, None)
        window.show()
        
        return app.exec_()
        
    except Exception as e:
        print(f"GUI起動エラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
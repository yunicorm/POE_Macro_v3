"""
POE Macro v3.0 メインGUIウィンドウ（分割版）
"""
import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QTabWidget)
from PyQt5.QtCore import Qt, QTimer

# Tab imports
from .tabs.log_tab import LogTab
from .tabs.control_tab import ControlTab
from .tabs.flask_tincture_tab import FlaskTinctureTab
from .tabs.skills_tab import SkillsTab
from .tabs.calibration_tab import CalibrationTab
from .utils.calibration_helpers import CalibrationHelpers

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """メインGUIウィンドウクラス（分割版）"""
    
    def __init__(self, config_manager, macro_controller=None):
        super().__init__()
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.macro_controller = macro_controller
        
        # MacroControllerにコールバックを設定
        if self.macro_controller:
            self.macro_controller.set_status_changed_callback(self.on_macro_status_changed)
        
        self.setWindowTitle("POE Macro v3.0")
        self.setGeometry(100, 100, 800, 600)
        
        # ログテキスト要素を早期初期化（安全性のため）
        self.log_text = None
        
        # キャリブレーション関連の初期化
        self.area_selector = None
        self.overlay_window = None
        
        # キャリブレーションヘルパーの初期化
        self.calibration_helper = CalibrationHelpers(self)
        
        # UI要素の初期化
        self.init_ui()
        
        # 定期更新タイマー（高速更新）
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(250)  # 250ms毎（高速更新）
        
        # 即時フィードバック用状態管理
        self._last_running_status = False
        self._status_update_pending = False
        
        logger.info("MainWindow initialized")
        
        # ウィンドウ表示後に自動的にマクロを開始（設定により制御）
        auto_start_enabled = self.config.get('general', {}).get('auto_start_on_launch', False)
        if auto_start_enabled and self.is_config_valid():
            # 少し遅延を入れてGUIが完全に初期化されるのを待つ
            QTimer.singleShot(500, self.auto_start_macro)
        else:
            logger.info("Auto-start disabled by configuration or invalid config")
    
    def init_ui(self):
        """UI要素を初期化"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 各タブを作成（ログタブを先に作成してlog_textを初期化）
        self.create_tabs()
        
        # ステータスバー
        self.statusBar().showMessage("Ready")
        
        # キャリブレーションタブ固有の初期化
        self.calibration_helper.update_resolution_info()
    
    def create_tabs(self):
        """全タブを作成"""
        # ログタブを最初に作成（log_textの初期化のため）
        log_tab = LogTab(self)
        widget = log_tab.create_widget()
        self.tab_widget.addTab(widget, "ログ")
        
        # 他のタブを作成
        control_tab = ControlTab(self)
        widget = control_tab.create_widget()
        self.tab_widget.addTab(widget, "一般")
        
        # Flask&Tinctureタブ（統合版）
        flask_tincture_tab = FlaskTinctureTab(self)
        widget = flask_tincture_tab.create_widget()
        self.tab_widget.addTab(widget, "Flask&Tincture")
        
        skills_tab = SkillsTab(self)
        widget = skills_tab.create_widget()
        self.tab_widget.addTab(widget, "スキル")
        
        calibration_tab = CalibrationTab(self)
        widget = calibration_tab.create_widget()
        self.tab_widget.addTab(widget, "キャリブレーション")
    
    # === 保存・設定メソッド ===
    def save_general_settings(self):
        """一般設定を保存"""
        try:
            # Grace Period設定を保存
            if 'grace_period' not in self.config:
                self.config['grace_period'] = {}
            self.config['grace_period']['enabled'] = self.grace_period_cb.isChecked()
            
            # 設定を保存
            self.config_manager.save_config(self.config)
            
            # MacroControllerに反映
            if self.macro_controller:
                self.macro_controller.grace_period_enabled = self.grace_period_cb.isChecked()
            
            self.log_message("一般設定を保存しました")
            
        except Exception as e:
            self.log_message(f"一般設定保存エラー: {e}")
            logger.error(f"Error saving general settings: {e}")
    
    def save_tincture_settings(self):
        """Tincture設定を保存"""
        try:
            # UI値から設定値への変換
            sensitivity_ui = self.sensitivity_slider.value()  # 50-100の値
            sensitivity_config = sensitivity_ui / 100.0  # 0.5-1.0の値に変換
            
            check_interval_ui = self.check_interval_spinbox.value()  # msec値
            check_interval_config = check_interval_ui / 1000.0  # 秒値に変換
            
            min_use_interval_ui = self.min_use_interval_spinbox.value()  # msec値
            min_use_interval_config = min_use_interval_ui / 1000.0  # 秒値に変換
            
            # 設定を更新
            if 'tincture' not in self.config:
                self.config['tincture'] = {}
                
            self.config['tincture']['enabled'] = self.tincture_enabled_cb.isChecked()
            self.config['tincture']['key'] = self.tincture_key_edit.text()
            self.config['tincture']['sensitivity'] = sensitivity_config
            self.config['tincture']['check_interval'] = check_interval_config
            self.config['tincture']['min_use_interval'] = min_use_interval_config
            
            # 設定を保存
            self.config_manager.save_config(self.config)
            
            # MacroControllerに反映（実行中の場合）
            if self.macro_controller and hasattr(self.macro_controller, 'tincture_module'):
                tincture_config = self.config.get('tincture', {})
                self.macro_controller.tincture_module.update_config(tincture_config)
            
            self.log_message(f"Tincture設定を保存: 感度={sensitivity_config:.3f}, チェック間隔={check_interval_config:.3f}s")
            
        except Exception as e:
            self.log_message(f"Tincture設定保存エラー: {e}")
            logger.error(f"Error saving tincture settings: {e}")
    
    def apply_tincture_settings(self):
        """Tincture設定を適用（保存せずに）"""
        try:
            if not self.macro_controller or not hasattr(self.macro_controller, 'tincture_module'):
                self.log_message("Tincture設定適用: MacroControllerまたはTinctureModuleが利用できません")
                return
            
            # 一時的な設定を作成
            temp_config = {
                'enabled': self.tincture_enabled_cb.isChecked(),
                'key': self.tincture_key_edit.text(),
                'sensitivity': self.sensitivity_slider.value() / 100.0,
                'check_interval': self.check_interval_spinbox.value() / 1000.0,
                'min_use_interval': self.min_use_interval_spinbox.value() / 1000.0
            }
            
            # 実行中のモジュールに適用
            self.macro_controller.tincture_module.update_config(temp_config)
            self.log_message(f"Tincture設定を一時適用: 感度={temp_config['sensitivity']:.3f}")
            
        except Exception as e:
            self.log_message(f"Tincture設定適用エラー: {e}")
            logger.error(f"Error applying tincture settings: {e}")
    
    # === マクロ制御メソッド ===
    def start_macro_with_grace_period(self):
        """Grace Period機能付きでマクロを開始"""
        try:
            grace_period_enabled = self.grace_period_cb.isChecked()
            
            if grace_period_enabled:
                # Grace Period有効時の処理
                self.log_message("Grace Period機能が有効です。戦闘エリア入場後、プレイヤー入力を待機してマクロを開始します。")
                # Grace Period設定を有効にしてマクロ開始
                self.start_macro()
            else:
                # 通常の即座開始
                self.log_message("Grace Period機能が無効です。マクロを即座に開始します。")
                self.start_macro()
                
        except Exception as e:
            self.log_message(f"Grace Period付きマクロ開始エラー: {e}")
            logger.error(f"Error starting macro with grace period: {e}")
    
    def start_macro(self):
        """マクロを開始"""
        try:
            if not self.is_config_valid():
                self.log_message("設定が無効です。マクロを開始できません。")
                return
            
            if self.macro_controller:
                # 現在の設定を取得
                current_config = self.config_manager.load_config()
                
                # マクロ開始
                self.macro_controller.start(current_config)
                
                # UI更新
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.statusBar().showMessage("マクロ実行中...")
                
                # 即時状態更新フラグを設定
                self._status_update_pending = True
                
                self.log_message("マクロを開始しました")
            else:
                self.log_message("MacroControllerが利用できません")
                
        except Exception as e:
            self.log_message(f"マクロ開始エラー: {e}")
            logger.error(f"Error starting macro: {e}")
            
            # エラー時にボタン状態をリセット
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.statusBar().showMessage("Ready")
    
    def stop_macro(self):
        """マクロを停止"""
        try:
            if self.macro_controller:
                self.macro_controller.stop()
                
                # UI更新
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.statusBar().showMessage("Ready")
                
                # 即時状態更新フラグを設定
                self._status_update_pending = True
                
                self.log_message("マクロを停止しました")
            else:
                self.log_message("MacroControllerが利用できません")
                
        except Exception as e:
            self.log_message(f"マクロ停止エラー: {e}")
            logger.error(f"Error stopping macro: {e}")
    
    # === 統計・手動操作メソッド ===
    def manual_use_tincture(self):
        """Tinctureを手動使用"""
        try:
            if self.macro_controller and hasattr(self.macro_controller, 'tincture_module'):
                self.macro_controller.tincture_module.manual_use()
                self.log_message("Tinctureを手動使用しました")
            else:
                self.log_message("TinctureModuleが利用できません")
        except Exception as e:
            self.log_message(f"Tincture手動使用エラー: {e}")
            logger.error(f"Error in manual tincture use: {e}")
    
    def reset_tincture_stats(self):
        """Tincture統計をリセット"""
        try:
            if self.macro_controller and hasattr(self.macro_controller, 'tincture_module'):
                self.macro_controller.tincture_module.reset_stats()
                self.log_message("Tincture統計をリセットしました")
            else:
                self.log_message("TinctureModuleが利用できません")
        except Exception as e:
            self.log_message(f"Tincture統計リセットエラー: {e}")
            logger.error(f"Error resetting tincture stats: {e}")
    
    # === 状態更新・UI更新メソッド ===
    def update_sensitivity_label(self, value):
        """感度スライダーのラベルを更新"""
        sensitivity = value / 100.0
        self.sensitivity_label.setText(f"{sensitivity:.2f}")
    
    def update_status(self):
        """ステータスを更新"""
        try:
            if self.macro_controller:
                status = self.macro_controller.get_status()
                
                # 統計情報を更新
                self._update_statistics(status)
                
                # 実行状態の変化を検出
                current_running = status.get('running', False)
                if current_running != self._last_running_status or self._status_update_pending:
                    self._last_running_status = current_running
                    self._status_update_pending = False
                    
                    # ボタン状態を即座に更新
                    self.start_btn.setEnabled(not current_running)
                    self.stop_btn.setEnabled(current_running)
                    
                    # ステータスバー更新
                    status_text = "マクロ実行中..." if current_running else "Ready"
                    self.statusBar().showMessage(status_text)
                    
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    def _update_statistics(self, status):
        """統計情報を更新"""
        try:
            # Tincture統計
            tincture_stats = status.get('tincture', {})
            if hasattr(self, 'tincture_uses_label'):
                uses = tincture_stats.get('total_uses', 0)
                self.tincture_uses_label.setText(f"使用回数: {uses}")
            
            if hasattr(self, 'detection_success_label'):
                success = tincture_stats.get('successful_detections', 0)
                self.detection_success_label.setText(f"検出成功: {success}")
            
            if hasattr(self, 'detection_failed_label'):
                failed = tincture_stats.get('failed_detections', 0)
                self.detection_failed_label.setText(f"検出失敗: {failed}")
            
            if hasattr(self, 'last_use_label'):
                last_use = tincture_stats.get('last_use_time', 'なし')
                self.last_use_label.setText(f"最後の使用: {last_use}")
                
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
    
    def on_macro_status_changed(self, is_running):
        """MacroControllerからの状態変更通知"""
        self._status_update_pending = True
        logger.debug(f"Macro status changed: {is_running}")
    
    # === ユーティリティメソッド ===
    def is_config_valid(self):
        """設定が有効かどうかをチェック"""
        try:
            # 基本的な設定チェック
            if not self.config:
                return False
            
            # 必要な設定セクションの存在確認
            required_sections = ['flask', 'skills', 'tincture']
            for section in required_sections:
                if section not in self.config:
                    logger.warning(f"Missing config section: {section}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating config: {e}")
            return False
    
    def auto_start_macro(self):
        """自動開始（設定により制御）"""
        try:
            auto_start = self.config.get('general', {}).get('auto_start_on_launch', False)
            if auto_start:
                self.log_message("自動開始が有効です。マクロを開始します...")
                self.start_macro_with_grace_period()
            else:
                self.log_message("自動開始は無効です")
        except Exception as e:
            self.log_message(f"自動開始エラー: {e}")
            logger.error(f"Error in auto start: {e}")
    
    def log_message(self, message):
        """ログメッセージをGUIとファイルに出力"""
        logger.info(message)
        if self.log_text:
            self.log_text.append(f"[{logger.name}] {message}")
    
    def clear_log(self):
        """ログをクリア"""
        if self.log_text:
            self.log_text.clear()
    
    def closeEvent(self, event):
        """ウィンドウ閉じるイベント"""
        try:
            if self.macro_controller:
                self.macro_controller.stop()
            logger.info("MainWindow closed")
        except Exception as e:
            logger.error(f"Error during window close: {e}")
        event.accept()
    
    # === キャリブレーション関連メソッド（委譲）===
    def show_overlay_window(self):
        """オーバーレイウィンドウを表示"""
        self.calibration_helper.show_overlay_window()
    
    def update_resolution_info(self):
        """解像度情報を更新"""
        self.calibration_helper.update_resolution_info()
    
    def apply_preset(self):
        """プリセットを適用"""
        self.calibration_helper.apply_preset()
    
    def apply_manual_settings(self):
        """手動設定を適用"""
        self.calibration_helper.apply_manual_settings()
    
    def test_detection(self):
        """検出テスト"""
        self.calibration_helper.test_detection()
    
    def on_area_changed(self, x, y, width, height):
        """エリア変更時の処理"""
        self.calibration_helper.on_area_changed(x, y, width, height)
    
    def on_settings_saved(self):
        """設定保存時の処理"""
        self.calibration_helper.on_settings_saved()
    
    def on_overlay_closed(self):
        """オーバーレイクローズ時の処理"""
        self.calibration_helper.on_overlay_closed()

def main():
    """テスト用メイン関数"""
    app = QApplication(sys.argv)
    
    # テスト用の設定マネージャー
    class MockConfigManager:
        def load_config(self):
            return {
                'general': {'auto_start_on_launch': False},
                'grace_period': {'enabled': True},
                'tincture': {'enabled': True, 'key': '3', 'sensitivity': 0.7},
                'flask': {'enabled': True},
                'skills': {'enabled': True}
            }
        
        def save_config(self, config):
            pass
    
    config_manager = MockConfigManager()
    window = MainWindow(config_manager)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
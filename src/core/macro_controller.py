"""
マクロ統合制御モジュール
"""
import logging
import threading
from typing import Dict, Any, Optional

# pynputの条件付きインポート
try:
    import pynput
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    pynput = None

from src.modules.flask_module import FlaskModule
from src.modules.skill_module import SkillModule
from src.modules.tincture_module import TinctureModule
from src.modules.log_monitor import LogMonitor
from src.core.config_manager import ConfigManager
from src.utils.window_manager import WindowManager

logger = logging.getLogger(__name__)

class MacroController:
    """全マクロモジュールの統合制御クラス"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        
        # configが正しく読み込まれていることを確認
        logger.debug(f"MacroController init - config type: {type(self.config)}")
        if not isinstance(self.config, dict):
            logger.error(f"Invalid config type: {type(self.config)}, using fallback")
            self.config = {
                'flask': {'enabled': False},
                'skills': {'enabled': False},
                'tincture': {'enabled': False}
            }
        
        logger.debug(f"Config keys available: {list(self.config.keys())}")
        
        # モジュールの初期化（各設定を安全に取得）
        flask_config = self._convert_flask_config()
        logger.debug(f"Flask config for init: {flask_config}")
        
        skills_config = self.config.get('skills', {})
        if not isinstance(skills_config, dict):
            logger.warning(f"Skills config is not dict: {type(skills_config)}, using fallback")
            skills_config = {'enabled': False}
        logger.debug(f"Skills config for init: {skills_config}")
        
        tincture_config = self.config.get('tincture', {})
        if not isinstance(tincture_config, dict):
            logger.warning(f"Tincture config is not dict: {type(tincture_config)}, using fallback")
            tincture_config = {'enabled': False}
        logger.debug(f"Tincture config for init: {tincture_config}")
        
        # ウィンドウマネージャー
        self.window_manager = WindowManager()
        
        # モジュールの初期化（エラー処理付き、window_manager付き）
        try:
            logger.debug("Initializing FlaskModule...")
            self.flask_module = FlaskModule(flask_config, self.window_manager)
            logger.debug("FlaskModule initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize FlaskModule: {e}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise
        
        try:
            logger.debug("Initializing SkillModule...")
            self.skill_module = SkillModule(skills_config, self.window_manager)
            logger.debug("SkillModule initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SkillModule: {e}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise
        
        try:
            logger.debug("Initializing TinctureModule...")
            self.tincture_module = TinctureModule(tincture_config, self.window_manager)
            logger.debug("TinctureModule initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TinctureModule: {e}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise
        
        # LogMonitorの初期化
        try:
            logger.debug("Initializing LogMonitor...")
            log_monitor_config = self.config.get('log_monitor', {})
            self.log_monitor = LogMonitor(log_monitor_config, macro_controller=self, full_config=self.config)
            logger.debug("LogMonitor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LogMonitor: {e}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            # LogMonitorは必須ではないので、エラーでも継続
            self.log_monitor = None
        
        # 制御状態
        self.running = False
        self.emergency_stop = False
        self.waiting_for_input = False  # Grace Period待機状態
        self.grace_period_active = False  # Grace Period活性状態
        self.grace_period_enabled = self.config.get('grace_period', {}).get('enabled', True)
        
        # グローバルホットキーリスナー
        self.hotkey_listener = None
        self.toggle_listener = None  # F12トグル用リスナー
        self.alt_toggle_listener = None  # 代替トグル用リスナー
        self.input_listener = None  # Grace Period入力検知用リスナー
        
        # MainWindowとの同期用コールバック
        self.status_changed_callback = None
        
        # ステータスオーバーレイ（GUIモード時のみ）
        self.status_overlay = None
        
        # グローバルホットキーを設定（初期化時に設定）
        self._setup_global_hotkeys()
        
        # リスナー監視タイマー
        self._listener_check_timer = None
        self._start_listener_monitor()
        
        logger.info("MacroController initialized successfully")
        
    def start(self, wait_for_input=False, force=False, respect_grace_period=None):
        """全マクロモジュールを開始
        
        Args:
            wait_for_input: True の場合、Grace Period待機状態に入る
            force: True の場合、Grace Period中でも強制開始
            respect_grace_period: Grace Period設定を尊重するか（Noneの場合は設定ファイルから取得）
        """
        if self.running:
            logger.warning("MacroController already running")
            return False
        
        # 緊急停止ホットキーの設定（初回のみ）
        if self.hotkey_listener is None or self.toggle_listener is None:
            self._setup_global_hotkeys()
        
        # Grace Period中は強制指定がない限り開始を拒否
        if self.grace_period_active and not force:
            logger.info("Start request ignored - Grace Period active")
            return False
        
        # Grace Period設定確認
        if respect_grace_period is None:
            respect_grace_period = self.config.get('general', {}).get('respect_grace_period', True)
        
        # Grace Period待機が有効で、待機指定がある場合
        if self.grace_period_enabled and wait_for_input and respect_grace_period:
            logger.info("Entering Grace Period wait state...")
            self.waiting_for_input = True
            self._setup_input_listener()
            return True
            
        # 即座に状態を変更（UIの即時フィードバック用）
        self.running = True
        self.emergency_stop = False
        logger.info("Macro start signal sent (immediate)")
        
        # ステータス変更を即座通知
        self._notify_status_changed()
        
        # モジュール開始を非同期で実行
        def async_start():
            try:
                # config構造を確認
                if not isinstance(self.config, dict):
                    logger.error(f"Config is not a dict, it's {type(self.config)}: {self.config}")
                    self.config = {
                        'flask': {'enabled': False},
                        'skills': {'enabled': False},
                        'tincture': {'enabled': False}
                    }
                    logger.info("Using fallback config")
                
                # 各設定値を取得
                flask_raw = self._convert_flask_config()
                skills_raw = self.config.get('skills', {})
                tincture_raw = self.config.get('tincture', {})
                
                # デバッグ：設定値を確認
                logger.debug(f"MacroController start - skills_raw: {skills_raw}")
                logger.debug(f"MacroController start - skills enabled: {skills_raw.get('enabled', 'NOT_FOUND')}")
                
                # Path of Exileウィンドウをアクティブにする（非ブロッキング）
                def activate_window():
                    try:
                        activation_success = self.window_manager.activate_poe_window(timeout=1.0)  # タイムアウト短縮
                        if activation_success:
                            logger.info("POE window activated")
                        else:
                            logger.warning("POE window activation failed")
                    except Exception as e:
                        logger.error(f"Window activation error: {e}")
                
                # ウィンドウアクティベーションを別スレッドで実行
                threading.Thread(target=activate_window, daemon=True).start()
                
                # 各モジュールの開始を並列化
                start_threads = []
                
                def start_module(module, name, config, enabled_key='enabled'):
                    try:
                        if isinstance(config, dict):
                            enabled = config.get(enabled_key, False)
                            logger.debug(f"Starting {name} module - enabled: {enabled}, config keys: {list(config.keys())}")
                            if enabled is True or (isinstance(enabled, str) and enabled.lower() == 'true'):
                                module.start()
                                logger.info(f"✓ {name} module started successfully")
                                return True
                            else:
                                logger.info(f"- {name} module not started - disabled (enabled: {enabled})")
                                return False
                        else:
                            logger.warning(f"✗ {name} module not started - invalid config type: {type(config)}")
                            return False
                    except Exception as e:
                        logger.error(f"✗ Error starting {name} module: {e}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        return False
                
                # 並列で開始処理を実行
                start_results = {}
                for module, name, config in [
                    (self.flask_module, "Flask", flask_raw),
                    (self.skill_module, "Skill", skills_raw),
                    (self.tincture_module, "Tincture", tincture_raw)
                ]:
                    def wrapped_start_module(mod, n, cfg):
                        result = start_module(mod, n, cfg)
                        start_results[n] = result
                    
                    thread = threading.Thread(target=wrapped_start_module, args=(module, name, config), daemon=True)
                    start_threads.append(thread)
                    thread.start()
                
                # LogMonitorの開始
                log_monitor_started = False
                if self.log_monitor:
                    try:
                        self.log_monitor.start()
                        logger.info("✓ LogMonitor started successfully")
                        log_monitor_started = True
                    except Exception as e:
                        logger.error(f"✗ Failed to start LogMonitor: {e}")
                
                # 全スレッドの完了を待機（最大1.5秒）
                for thread in start_threads:
                    thread.join(timeout=0.5)
                
                # 起動サマリーをログ出力
                logger.info("=" * 50)
                logger.info("Module Startup Summary:")
                logger.info("=" * 50)
                for module_name, success in start_results.items():
                    status = "✓ STARTED" if success else "- DISABLED/FAILED"
                    logger.info(f"{module_name:<12}: {status}")
                logger.info(f"{'LogMonitor':<12}: {'✓ STARTED' if log_monitor_started else '✗ FAILED'}")
                
                successful_modules = sum(start_results.values()) + (1 if log_monitor_started else 0)
                total_modules = len(start_results) + 1
                logger.info(f"Started {successful_modules}/{total_modules} modules successfully")
                logger.info("=" * 50)
                
                logger.info("MacroController background start completed")
                
            except Exception as e:
                import traceback
                logger.error(f"Failed to start modules: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                self.running = False  # エラー時は状態を戻す
                self._notify_status_changed()
        
        # 非同期で開始処理を実行
        threading.Thread(target=async_start, daemon=True).start()
        
        return True  # 非同期開始成功
    
    def stop(self):
        """全マクロモジュールを即座停止（非同期処理）"""
        if not self.running:
            logger.warning("MacroController not running")
            return
            
        # 即座に状態を変更（UIの即時フィードバック用）
        self.running = False
        self.emergency_stop = True
        logger.info("Macro stop signal sent (immediate)")
        
        # ステータス変更を即座通知
        self._notify_status_changed()
        
        # モジュール停止を別スレッドで実行
        def async_stop():
            logger.info("Stopping macro modules...")
            
            # 各モジュールの停止（並列処理）
            stop_threads = []
            
            def stop_module(module, name):
                try:
                    module.stop()
                    logger.info(f"{name} module stopped")
                except Exception as e:
                    logger.error(f"Error stopping {name} module: {e}")
            
            # 並列で停止処理を実行
            for module, name in [
                (self.flask_module, "Flask"),
                (self.skill_module, "Skill"),
                (self.tincture_module, "Tincture")
            ]:
                thread = threading.Thread(target=stop_module, args=(module, name), daemon=True)
                stop_threads.append(thread)
                thread.start()
            
            # LogMonitorの停止
            if self.log_monitor:
                try:
                    self.log_monitor.stop()
                    logger.info("LogMonitor stopped")
                except Exception as e:
                    logger.error(f"Error stopping LogMonitor: {e}")
            
            # Grace Period関連リスナーのみ停止
            if self.input_listener:
                self.input_listener.stop()
                self.input_listener = None
            if hasattr(self, 'mouse_listener') and self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            
            # 待機状態をリセット
            self.waiting_for_input = False
            
            # 全スレッドの完了を待機（最大0.9秒）
            for thread in stop_threads:
                thread.join(timeout=0.3)
            
            logger.info("MacroController background stop completed")
        
        # 非同期で停止処理を実行
        threading.Thread(target=async_stop, daemon=True).start()
    
    def toggle(self):
        """マクロの開始/停止を高速トグル"""
        # Grace Period待機中の場合は即座に開始
        if self.waiting_for_input:
            logger.info("Toggling macro ON (ending Grace Period) - FAST")
            self._end_grace_period()
        elif self.running:
            logger.info("Toggling macro OFF - FAST")
            self.stop()
        else:
            logger.info("Toggling macro ON - FAST")
            self.start()
    
    def set_status_changed_callback(self, callback):
        """MainWindowとの同期用コールバックを設定"""
        self.status_changed_callback = callback
    
    def set_status_overlay(self, overlay):
        """ステータスオーバーレイを設定"""
        self.status_overlay = overlay
    
    def _notify_status_changed(self):
        """ステータス変更をMainWindowに通知"""
        if self.status_changed_callback:
            try:
                self.status_changed_callback(self.running)
            except Exception as e:
                logger.error(f"Error in status change callback: {e}")
        
        # ステータスオーバーレイも更新
        if self.status_overlay:
            try:
                self.status_overlay.set_macro_status(self.running)
            except Exception as e:
                logger.error(f"Error updating status overlay: {e}")
    
    def restart(self):
        """全マクロモジュールを再起動"""
        logger.info("Restarting MacroController...")
        self.stop()
        self.start()
    
    def update_config(self, config: Optional[Dict[str, Any]] = None):
        """設定を更新"""
        if config is None:
            config = self.config_manager.load_config()
        
        # configがdictでない場合の処理
        if not isinstance(config, dict):
            logger.error(f"Config is not a dict in update_config, it's {type(config)}")
            config = {
                'flask': {'enabled': False},
                'skills': {'enabled': False},
                'tincture': {'enabled': False}
            }
        
        self.config = config
        
        # 各モジュールの設定更新（安全な取得）
        flask_config = self._convert_flask_config()
        self.flask_module.update_config(flask_config)
        
        skills_config = config.get('skills', {})
        if isinstance(skills_config, dict):
            self.skill_module.update_config(skills_config)
        else:
            logger.warning(f"Skills config is not dict in update_config: {type(skills_config)}")
        
        tincture_config = config.get('tincture', {})
        if isinstance(tincture_config, dict):
            self.tincture_module.update_config(tincture_config)
        else:
            logger.warning(f"Tincture config is not dict in update_config: {type(tincture_config)}")
        
        logger.info("Configuration updated")
    
    def get_status(self) -> Dict[str, Any]:
        """全モジュールのステータスを取得"""
        try:
            # Tincture モジュールの統計情報を安全に取得
            tincture_stats = {}
            try:
                tincture_stats = self.tincture_module.get_stats()
            except Exception as e:
                logger.warning(f"Failed to get tincture stats: {e}")
                tincture_stats = {'total_uses': 0, 'stats': {}}
            
            return {
                'running': self.running,
                'waiting_for_input': self.waiting_for_input,
                'grace_period_enabled': self.grace_period_enabled,
                'emergency_stop': self.emergency_stop,
                'flask': self.flask_module.get_status(),
                'skill': {
                    'running': self.skill_module.running,
                    'threads': len(self.skill_module.threads),
                    'stats': self.skill_module.get_stats()
                },
                'tincture': {
                    'running': self.tincture_module.running,
                    'current_state': 'RUNNING' if self.tincture_module.running else 'STOPPED',
                    'stats': tincture_stats
                }
            }
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {
                'running': self.running,
                'emergency_stop': self.emergency_stop,
                'flask': {'running': False, 'enabled': False, 'flask_count': 0, 'active_flasks': []},
                'skill': {'running': False, 'threads': 0, 'stats': {}},
                'tincture': {'running': False, 'current_state': 'ERROR', 'stats': {}}
            }
    
    def _setup_global_hotkeys(self):
        """ホットキーを設定（緊急停止: Ctrl+Shift+F12, トグル: F12/F11/Pause）"""
        # 既存のリスナーを停止
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
        if self.toggle_listener:
            self.toggle_listener.stop()
            self.toggle_listener = None
        if self.alt_toggle_listener:
            self.alt_toggle_listener.stop()
            self.alt_toggle_listener = None
        
        # Ctrl+Shift+F12 緊急停止用
        def on_press_emergency(key):
            try:
                # 現在押されているキーを追跡
                current_keys = getattr(on_press_emergency, 'current_keys', set())
                
                if hasattr(key, 'char'):
                    current_keys.add(key)
                elif hasattr(key, 'name'):
                    current_keys.add(key)
                
                # Ctrl+Shift+F12の検出
                ctrl_pressed = any(k in current_keys for k in [pynput.keyboard.Key.ctrl_l, pynput.keyboard.Key.ctrl_r])
                shift_pressed = any(k in current_keys for k in [pynput.keyboard.Key.shift_l, pynput.keyboard.Key.shift_r])
                
                if ctrl_pressed and shift_pressed and key == pynput.keyboard.Key.f12:
                    logger.warning("Emergency stop triggered (Ctrl+Shift+F12)")
                    self.emergency_stop = True
                    self.stop()
                    # プログラムを終了
                    import sys
                    sys.exit(0)
                
                on_press_emergency.current_keys = current_keys
                
            except Exception as e:
                logger.error(f"Error in emergency stop handler: {e}")
        
        def on_release_emergency(key):
            try:
                current_keys = getattr(on_press_emergency, 'current_keys', set())
                current_keys.discard(key)
                on_press_emergency.current_keys = current_keys
            except Exception as e:
                logger.error(f"Error in key release handler: {e}")
        
        # F12トグル機能（リスナー継続版）
        def on_press_toggle(key):
            try:
                # デバッグログ: 検知したキーを記録
                if hasattr(key, 'name'):
                    key_name = key.name
                elif hasattr(key, 'char'):
                    key_name = f"'{key.char}'"
                else:
                    key_name = str(key)
                
                logger.debug(f"Key detected: {key_name}")
                
                # F12キーのみでトグル（シンプル化）
                if key == pynput.keyboard.Key.f12:
                    if self.running:
                        logger.info(f"Macro stopped by F12")
                        self.stop()
                        # オーバーレイ更新確認
                        if self.status_overlay:
                            logger.debug("F12: Status overlay updated to OFF")
                    else:
                        logger.info(f"Macro started by F12")
                        self.start()
                        # オーバーレイ更新確認
                        if self.status_overlay:
                            logger.debug("F12: Status overlay updated to ON")
                    # return False を削除 - リスナーを継続させる
                
            except Exception as e:
                logger.error(f"Error in toggle handler: {e}")
        
        # 代替キー検知（F11/Pauseなど）
        def on_press_alt_toggle(key):
            """代替のキー検知方法（F11/Pause用）"""
            try:
                # F11とPauseキーのトグル機能
                if key == pynput.keyboard.Key.f11 or key == pynput.keyboard.Key.pause:
                    key_name = key.name if hasattr(key, 'name') else str(key)
                    if self.running:
                        logger.info(f"Macro stopped by {key_name}")
                        self.stop()
                    else:
                        logger.info(f"Macro started by {key_name}")
                        self.start()
                    # return文なし - リスナーを継続させる
                
                # raw値による検知（仮想キー対応）
                elif hasattr(key, 'vk'):
                    # F11のVKコード: 122, PauseのVKコード: 19
                    if key.vk in [122, 19]:  # F11, Pause
                        key_names = {122: 'F11', 19: 'Pause'}
                        key_name = key_names.get(key.vk, f'VK{key.vk}')
                        if self.running:
                            logger.info(f"Macro stopped by {key_name}")
                            self.stop()
                        else:
                            logger.info(f"Macro started by {key_name}")
                            self.start()
                            
            except Exception as e:
                logger.error(f"Error in alternative toggle handler: {e}")
        
        # 緊急停止リスナー（suppress=False で仮想キーも検知）
        self.hotkey_listener = pynput.keyboard.Listener(
            on_press=on_press_emergency,
            on_release=on_release_emergency,
            suppress=False  # 仮想キー入力も検知
        )
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()
        
        # メイントグルリスナー（suppress=False で仮想キーも検知）
        self.toggle_listener = pynput.keyboard.Listener(
            on_press=on_press_toggle,
            suppress=False  # 仮想キー入力も検知
        )
        self.toggle_listener.daemon = True
        self.toggle_listener.start()
        
        # 代替トグルリスナー（より低レベルな検知）
        try:
            self.alt_toggle_listener = pynput.keyboard.Listener(
                on_press=on_press_alt_toggle,
                suppress=False,
                win32_event_filter=lambda msg, data: True  # Windowsイベントフィルターを無効化
            )
            self.alt_toggle_listener.daemon = True
            self.alt_toggle_listener.start()
            logger.info("Alternative toggle listener started")
        except Exception as e:
            logger.warning(f"Alternative toggle listener failed to start: {e}")
        
        logger.info("Hotkeys registered - Toggle: F12/F11/Pause, Emergency stop: Ctrl+Shift+F12")
    
    def _start_listener_monitor(self):
        """リスナーの健全性を監視し、必要に応じて再起動"""
        def check_listeners():
            try:
                # リスナーの状態をチェック
                listeners_ok = True
                
                if self.toggle_listener and not self.toggle_listener.running:
                    logger.warning("Toggle listener has stopped, restarting...")
                    listeners_ok = False
                
                if self.alt_toggle_listener and not self.alt_toggle_listener.running:
                    logger.warning("Alternative toggle listener has stopped, restarting...")
                    listeners_ok = False
                
                if self.hotkey_listener and not self.hotkey_listener.running:
                    logger.warning("Hotkey listener has stopped, restarting...")
                    listeners_ok = False
                
                # リスナーが停止している場合は再起動
                if not listeners_ok:
                    logger.info("Restarting stopped listeners...")
                    self._setup_global_hotkeys()
                
                # 次回チェックをスケジュール（10秒後）
                if not self.emergency_stop:
                    self._listener_check_timer = threading.Timer(10.0, check_listeners)
                    self._listener_check_timer.daemon = True
                    self._listener_check_timer.start()
                    
            except Exception as e:
                logger.error(f"Error in listener monitor: {e}")
                # エラーが発生してもチェックを継続
                if not self.emergency_stop:
                    self._listener_check_timer = threading.Timer(10.0, check_listeners)
                    self._listener_check_timer.daemon = True
                    self._listener_check_timer.start()
        
        # 初回チェックを10秒後に開始
        self._listener_check_timer = threading.Timer(10.0, check_listeners)
        self._listener_check_timer.daemon = True
        self._listener_check_timer.start()
        logger.debug("Listener monitor started")
    
    def _setup_input_listener(self):
        """Grace Period入力検知リスナーを設定"""
        if self.input_listener:
            self.input_listener.stop()
            self.input_listener = None
        
        logger.info("Setting up Grace Period input listener...")
        self.grace_period_active = True
        
        def on_click(x, y, button, pressed):
            """マウスクリック検知"""
            if not pressed or not self.waiting_for_input:
                return
            
            # 左、右、中央クリックを検知
            if button in [pynput.mouse.Button.left, pynput.mouse.Button.right, pynput.mouse.Button.middle]:
                logger.info(f"Grace Period ended by {button.name} click")
                self._end_grace_period()
                # return Falseを削除 - リスナーは_end_grace_period()で管理
        
        def on_press(key):
            """キーボード入力検知"""
            if not self.waiting_for_input:
                return
            
            # Qキーを検知
            try:
                if hasattr(key, 'char') and key.char and key.char.lower() == 'q':
                    logger.info("Grace Period ended by Q key")
                    self._end_grace_period()
                    # return Falseを削除 - リスナーは_end_grace_period()で管理
            except Exception as e:
                logger.error(f"Error in key detection: {e}")
        
        # マウスリスナー
        self.mouse_listener = pynput.mouse.Listener(on_click=on_click)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()
        
        # キーボードリスナー
        self.input_listener = pynput.keyboard.Listener(on_press=on_press)
        self.input_listener.daemon = True
        self.input_listener.start()
        
        logger.info("Grace Period input listener started - waiting for left/right/middle click or Q key")
    
    def _end_grace_period(self):
        """Grace Period待機を終了して通常のマクロ開始"""
        self.waiting_for_input = False
        self.grace_period_active = False
        
        # 入力リスナーを停止
        if hasattr(self, 'mouse_listener') and self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        if self.input_listener:
            self.input_listener.stop()
            self.input_listener = None
        
        # 通常のマクロ開始
        logger.info("Grace Period ended, starting macro normally")
        self.start(wait_for_input=False)
    
    def manual_flask_use(self, slot: str):
        """手動でフラスコを使用"""
        try:
            logger.debug(f"Manual flask use requested for slot: {slot}")
            logger.debug(f"Config type: {type(self.config)}")
            
            if not isinstance(self.config, dict):
                logger.warning("Configuration is not valid for manual flask use")
                return
                
            # 新しい設定形式を使用
            flask_slots = self.config.get('flask_slots', {})
            
            # 旧形式との互換性チェック
            if not flask_slots and 'flask' in self.config:
                flask_config = self.config.get('flask', {})
                slot_config = flask_config.get(slot, {})
                logger.debug(f"Using old format - Slot {slot} config: {slot_config}")
                
                if isinstance(slot_config, dict):
                    key = slot_config.get('key')
                    if key:
                        self.flask_module.keyboard.press_key(key)
                        logger.info(f"Manual flask use (old format): {slot} -> {key}")
                    else:
                        logger.warning(f"No key configured for flask slot: {slot}")
                else:
                    logger.warning(f"Invalid configuration for flask slot: {slot} - {type(slot_config)}")
                return
            
            # 新形式での処理
            slot_config = flask_slots.get(slot, {})
            logger.debug(f"Slot {slot} config: {slot_config}")
            
            if isinstance(slot_config, dict):
                # Tinctureスロットはスキップ
                if slot_config.get('is_tincture', False):
                    logger.info(f"Slot {slot} is configured as Tincture, skipping flask use")
                    return
                
                key = slot_config.get('key')
                if key:
                    self.flask_module.keyboard.press_key(key)
                    logger.info(f"Manual flask use: {slot} -> {key}")
                else:
                    logger.warning(f"No key configured for flask slot: {slot}")
            else:
                logger.warning(f"Invalid configuration for flask slot: {slot} - {type(slot_config)}")
                
        except Exception as e:
            logger.error(f"Error in manual flask use: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def manual_skill_use(self, skill_name: str):
        """手動でスキルを使用"""
        self.skill_module.manual_use(skill_name)
    
    def manual_tincture_use(self):
        """手動でTinctureを使用"""
        self.tincture_module.manual_use()
    
    def check_poe_window_status(self) -> dict:
        """Path of Exileウィンドウの状態をチェック"""
        try:
            is_process_running = self.window_manager.find_poe_process() is not None
            is_window_active = self.window_manager.is_poe_active()
            window_info = self.window_manager.get_poe_window_info()
            
            return {
                'process_running': is_process_running,
                'window_active': is_window_active,
                'window_info': window_info
            }
        except Exception as e:
            logger.error(f"Error checking POE window status: {e}")
            return {
                'process_running': False,
                'window_active': False,
                'window_info': None,
                'error': str(e)
            }
    
    def activate_poe_window(self) -> bool:
        """手動でPath of Exileウィンドウをアクティブにする"""
        try:
            return self.window_manager.activate_poe_window()
        except Exception as e:
            logger.error(f"Error activating POE window: {e}")
            return False
    
    def restart_hotkey_listeners(self):
        """ホットキーリスナーを手動で再起動"""
        logger.info("Manually restarting hotkey listeners...")
        self._setup_global_hotkeys()
        logger.info("Hotkey listeners restarted")
    
    def get_listener_status(self) -> dict:
        """リスナーの状態を取得"""
        return {
            'hotkey_listener': self.hotkey_listener.running if self.hotkey_listener else False,
            'toggle_listener': self.toggle_listener.running if self.toggle_listener else False,
            'alt_toggle_listener': self.alt_toggle_listener.running if self.alt_toggle_listener else False,
            'input_listener': self.input_listener.running if self.input_listener else False,
            'mouse_listener': self.mouse_listener.running if hasattr(self, 'mouse_listener') and self.mouse_listener else False
        }
    
    def __enter__(self):
        """コンテキストマネージャーとして使用"""
        self.start()
        return self
    
    def shutdown(self):
        """完全にシャットダウン（ホットキーリスナーも含む）"""
        self.stop()
        
        # ホットキーリスナーの停止
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
            logger.info("Hotkey listener stopped")
        if self.toggle_listener:
            self.toggle_listener.stop()
            self.toggle_listener = None
            logger.info("Toggle listener stopped")
        if self.alt_toggle_listener:
            self.alt_toggle_listener.stop()
            self.alt_toggle_listener = None
            logger.info("Alt toggle listener stopped")
        
        # リスナー監視タイマーの停止
        if self._listener_check_timer:
            self._listener_check_timer.cancel()
            self._listener_check_timer = None
            logger.info("Listener monitor stopped")
        
        logger.info("MacroController completely shut down")
    
    def _convert_flask_config(self):
        """新しい設定形式に変換"""
        flask_config = {
            'enabled': self.config.get('flask', {}).get('enabled', False),
            'flask_slots': {}
        }
        
        # Flask&Tinctureタブの設定を読み込み
        flask_slots = self.config.get('flask_slots', {})
        
        # 旧形式との互換性維持
        if not flask_slots and 'flask' in self.config:
            # 旧形式から変換
            old_flask = self.config['flask']
            for slot_key in ['slot_1', 'slot_2', 'slot_3', 'slot_4', 'slot_5']:
                if slot_key in old_flask:
                    slot_config = old_flask[slot_key]
                    if slot_config.get('enabled', False):
                        flask_slots[slot_key] = {
                            'key': slot_config.get('key', ''),
                            'duration_ms': int(slot_config.get('duration', 5) * 1000),
                            'use_when_full': False,
                            'is_tincture': False
                        }
        
        flask_config['flask_slots'] = flask_slots
        return flask_config
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーとして使用"""
        self.shutdown()
"""
マクロ統合制御モジュール
"""
import logging
import pynput
import threading
from typing import Dict, Any, Optional

from modules.flask_module import FlaskModule
from modules.skill_module import SkillModule
from modules.tincture_module import TinctureModule
from core.config_manager import ConfigManager
from utils.window_manager import WindowManager

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
        flask_config = self.config.get('flask', {})
        if not isinstance(flask_config, dict):
            logger.warning(f"Flask config is not dict: {type(flask_config)}, using fallback")
            flask_config = {'enabled': False}
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
        
        # 制御状態
        self.running = False
        self.emergency_stop = False
        self.waiting_for_input = False  # Grace Period待機状態
        self.grace_period_enabled = config.get('grace_period', {}).get('enabled', True)
        
        # グローバルホットキーリスナー
        self.hotkey_listener = None
        self.toggle_listener = None  # F12トグル用リスナー
        self.input_listener = None  # Grace Period入力検知用リスナー
        
        # MainWindowとの同期用コールバック
        self.status_changed_callback = None
        
        # グローバルホットキーを設定（初期化時に設定）
        self._setup_global_hotkeys()
        
        logger.info("MacroController initialized successfully")
        
    def start(self, wait_for_input=False):
        """全マクロモジュールを開始
        
        Args:
            wait_for_input: True の場合、Grace Period待機状態に入る
        """
        if self.running:
            logger.warning("MacroController already running")
            return
        
        # Grace Period待機が有効で、待機指定がある場合
        if self.grace_period_enabled and wait_for_input:
            logger.info("Entering Grace Period wait state...")
            self.waiting_for_input = True
            self._setup_input_listener()
            return
            
        try:
            # デバッグ: config構造を確認
            logger.debug(f"Start - Config type: {type(self.config)}")
            logger.debug(f"Start - Config keys: {self.config.keys() if isinstance(self.config, dict) else 'Not a dict'}")
            
            # configがdictでない場合の処理
            if not isinstance(self.config, dict):
                logger.error(f"Config is not a dict, it's {type(self.config)}: {self.config}")
                self.config = {
                    'flask': {'enabled': False},
                    'skills': {'enabled': False},
                    'tincture': {'enabled': False}
                }
                logger.info("Using fallback config")
            
            # 各設定値のタイプと内容をデバッグ出力
            flask_raw = self.config.get('flask', {})
            skills_raw = self.config.get('skills', {})
            tincture_raw = self.config.get('tincture', {})
            
            logger.debug(f"Start - Flask config raw: {flask_raw} (type: {type(flask_raw)})")
            logger.debug(f"Start - Skills config raw: {skills_raw} (type: {type(skills_raw)})")
            logger.debug(f"Start - Tincture config raw: {tincture_raw} (type: {type(tincture_raw)})")
            
            self.running = True
            self.emergency_stop = False
            
            # Path of Exileウィンドウをアクティブにする
            logger.info("Attempting to activate Path of Exile window...")
            try:
                activation_success = self.window_manager.activate_poe_window(timeout=3.0)
                if activation_success:
                    logger.info("Successfully activated Path of Exile window")
                    # ウィンドウ切り替え後の安定化のため少し待機
                    import time
                    time.sleep(0.5)
                else:
                    logger.warning("Failed to activate Path of Exile window - macro will start anyway")
                    logger.warning("Please manually focus on Path of Exile window for optimal performance")
            except Exception as e:
                logger.error(f"Error during window activation: {e}")
                logger.warning("Continuing with macro startup despite window activation failure")
            
            # 各モジュールの開始
            logger.info("Starting macro modules...")
            
            # flask設定の安全な取得
            flask_config = flask_raw if isinstance(flask_raw, dict) else {}
            if flask_config:
                # enabledキーがbool値の場合の対応
                flask_enabled = flask_config.get('enabled', False)
                if flask_enabled is True or (isinstance(flask_enabled, str) and flask_enabled.lower() == 'true'):
                    self.flask_module.start()
                    logger.info("Flask module started")
                else:
                    logger.info(f"Flask module not started - enabled: {flask_enabled}")
            else:
                logger.info("Flask module not started - no valid config")
            
            # skills設定の安全な取得
            skills_config = skills_raw if isinstance(skills_raw, dict) else {}
            if skills_config:
                skills_enabled = skills_config.get('enabled', False)
                if skills_enabled is True or (isinstance(skills_enabled, str) and skills_enabled.lower() == 'true'):
                    self.skill_module.start()
                    logger.info("Skill module started")
                else:
                    logger.info(f"Skill module not started - enabled: {skills_enabled}")
            else:
                logger.info("Skill module not started - no valid config")
            
            # tincture設定の安全な取得
            tincture_config = tincture_raw if isinstance(tincture_raw, dict) else {}
            if tincture_config:
                tincture_enabled = tincture_config.get('enabled', False)
                if tincture_enabled is True or (isinstance(tincture_enabled, str) and tincture_enabled.lower() == 'true'):
                    self.tincture_module.start()
                    logger.info("Tincture module started")
                else:
                    logger.info(f"Tincture module not started - enabled: {tincture_enabled}")
            else:
                logger.info("Tincture module not started - no valid config")
            
            # ホットキーは初期化時に設定済み
            
            logger.info("MacroController started successfully")
            
            # ステータス変更を通知
            self._notify_status_changed()
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to start MacroController: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            self.stop()
            raise
    
    def stop(self):
        """全マクロモジュールを停止"""
        if not self.running:
            logger.warning("MacroController not running")
            return
            
        self.running = False
        self.emergency_stop = True
        
        logger.info("Stopping macro modules...")
        
        # 各モジュールの停止
        try:
            self.flask_module.stop()
            logger.info("Flask module stopped")
        except Exception as e:
            logger.error(f"Error stopping flask module: {e}")
        
        try:
            self.skill_module.stop()
            logger.info("Skill module stopped")
        except Exception as e:
            logger.error(f"Error stopping skill module: {e}")
        
        try:
            self.tincture_module.stop()
            logger.info("Tincture module stopped")
        except Exception as e:
            logger.error(f"Error stopping tincture module: {e}")
        
        # ホットキーリスナーの停止
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
        if self.toggle_listener:
            self.toggle_listener.stop()
            self.toggle_listener = None
        if self.input_listener:
            self.input_listener.stop()
            self.input_listener = None
        if hasattr(self, 'mouse_listener') and self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        # 待機状態をリセット
        self.waiting_for_input = False
        
        logger.info("MacroController stopped")
        
        # ステータス変更を通知
        self._notify_status_changed()
    
    def toggle(self):
        """マクロの開始/停止をトグル"""
        # Grace Period待機中の場合は即座に開始
        if self.waiting_for_input:
            logger.info("Toggling macro ON (ending Grace Period)")
            self._end_grace_period()
        elif self.running:
            logger.info("Toggling macro OFF")
            self.stop()
        else:
            logger.info("Toggling macro ON")
            self.start()
    
    def set_status_changed_callback(self, callback):
        """MainWindowとの同期用コールバックを設定"""
        self.status_changed_callback = callback
    
    def _notify_status_changed(self):
        """ステータス変更をMainWindowに通知"""
        if self.status_changed_callback:
            try:
                self.status_changed_callback(self.running)
            except Exception as e:
                logger.error(f"Error in status change callback: {e}")
    
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
        flask_config = config.get('flask', {})
        if isinstance(flask_config, dict):
            self.flask_module.update_config(flask_config)
        else:
            logger.warning(f"Flask config is not dict in update_config: {type(flask_config)}")
        
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
                'flask': {
                    'running': self.flask_module.running,
                    'threads': len(self.flask_module.threads)
                },
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
                'flask': {'running': False, 'threads': 0},
                'skill': {'running': False, 'threads': 0, 'stats': {}},
                'tincture': {'running': False, 'current_state': 'ERROR', 'stats': {}}
            }
    
    def _setup_global_hotkeys(self):
        """ホットキーを設定（緊急停止: Ctrl+Shift+F12, トグル: F12）"""
        # 既存のリスナーを停止
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
        if self.toggle_listener:
            self.toggle_listener.stop()
            self.toggle_listener = None
        
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
        
        # F12トグル用
        def on_press_toggle(key):
            try:
                if key == pynput.keyboard.Key.f12:
                    logger.info("Toggle triggered (F12)")
                    self.toggle()
            except Exception as e:
                logger.error(f"Error in toggle handler: {e}")
        
        # 緊急停止リスナー
        self.hotkey_listener = pynput.keyboard.Listener(
            on_press=on_press_emergency,
            on_release=on_release_emergency
        )
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()
        
        # トグルリスナー
        self.toggle_listener = pynput.keyboard.Listener(on_press=on_press_toggle)
        self.toggle_listener.daemon = True
        self.toggle_listener.start()
        
        logger.info("Hotkeys registered - Toggle: F12, Emergency stop: Ctrl+Shift+F12")
    
    def _setup_input_listener(self):
        """Grace Period入力検知リスナーを設定"""
        if self.input_listener:
            self.input_listener.stop()
            self.input_listener = None
        
        logger.info("Setting up Grace Period input listener...")
        
        def on_click(x, y, button, pressed):
            """マウスクリック検知"""
            if not pressed or not self.waiting_for_input:
                return
            
            # 左、右、中央クリックを検知
            if button in [pynput.mouse.Button.left, pynput.mouse.Button.right, pynput.mouse.Button.middle]:
                logger.info(f"Grace Period ended by {button.name} click")
                self._end_grace_period()
                return False  # リスナーを停止
        
        def on_press(key):
            """キーボード入力検知"""
            if not self.waiting_for_input:
                return
            
            # Qキーを検知
            try:
                if hasattr(key, 'char') and key.char and key.char.lower() == 'q':
                    logger.info("Grace Period ended by Q key")
                    self._end_grace_period()
                    return False  # リスナーを停止
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
                
            flask_config = self.config.get('flask', {})
            logger.debug(f"Flask config type: {type(flask_config)}")
            
            if not isinstance(flask_config, dict):
                logger.warning(f"Flask configuration is not valid: {type(flask_config)}")
                return
                
            slot_config = flask_config.get(slot, {})
            logger.debug(f"Slot {slot} config: {slot_config}")
            
            if isinstance(slot_config, dict):
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
    
    def __enter__(self):
        """コンテキストマネージャーとして使用"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーとして使用"""
        self.stop()
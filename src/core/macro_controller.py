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
        
        self.flask_module = FlaskModule(flask_config)
        self.skill_module = SkillModule(skills_config)
        self.tincture_module = TinctureModule(tincture_config)
        
        # 制御状態
        self.running = False
        self.emergency_stop = False
        
        # グローバルホットキーリスナー
        self.hotkey_listener = None
        
        logger.info("MacroController initialized successfully")
        
    def start(self):
        """全マクロモジュールを開始"""
        if self.running:
            logger.warning("MacroController already running")
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
            
            # 緊急停止ホットキーの設定
            self._setup_emergency_stop()
            
            logger.info("MacroController started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start MacroController: {e}")
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
        
        logger.info("MacroController stopped")
    
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
    
    def _setup_emergency_stop(self):
        """緊急停止ホットキー（F12）を設定"""
        def on_press(key):
            try:
                if key == pynput.keyboard.Key.f12:
                    logger.warning("Emergency stop triggered (F12)")
                    self.stop()
                    return False  # リスナーを停止
            except Exception as e:
                logger.error(f"Error in emergency stop handler: {e}")
        
        self.hotkey_listener = pynput.keyboard.Listener(on_press=on_press)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()
        logger.info("Emergency stop hotkey (F12) registered")
    
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
    
    def __enter__(self):
        """コンテキストマネージャーとして使用"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーとして使用"""
        self.stop()
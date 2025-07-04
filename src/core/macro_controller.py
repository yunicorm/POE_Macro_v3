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
        
        # モジュールの初期化
        self.flask_module = FlaskModule(self.config.get('flask', {}))
        self.skill_module = SkillModule(self.config.get('skills', {}))
        self.tincture_module = TinctureModule(self.config.get('tincture', {}))
        
        # 制御状態
        self.running = False
        self.emergency_stop = False
        
        # グローバルホットキーリスナー
        self.hotkey_listener = None
        
    def start(self):
        """全マクロモジュールを開始"""
        if self.running:
            logger.warning("MacroController already running")
            return
            
        try:
            self.running = True
            self.emergency_stop = False
            
            # 各モジュールの開始
            logger.info("Starting macro modules...")
            
            if self.config.get('flask', {}).get('enabled', False):
                self.flask_module.start()
                logger.info("Flask module started")
            
            if self.config.get('skills', {}).get('enabled', False):
                self.skill_module.start()
                logger.info("Skill module started")
            
            if self.config.get('tincture', {}).get('enabled', False):
                self.tincture_module.start()
                logger.info("Tincture module started")
            
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
        
        self.config = config
        
        # 各モジュールの設定更新
        self.flask_module.update_config(config.get('flask', {}))
        self.skill_module.update_config(config.get('skills', {}))
        self.tincture_module.update_config(config.get('tincture', {}))
        
        logger.info("Configuration updated")
    
    def get_status(self) -> Dict[str, Any]:
        """全モジュールのステータスを取得"""
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
                'detection_active': self.tincture_module.detection_active,
                'current_state': self.tincture_module.current_state.name if hasattr(self.tincture_module, 'current_state') else 'UNKNOWN',
                'stats': self.tincture_module.get_stats()
            }
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
        key = self.config.get('flask', {}).get(slot, {}).get('key')
        if key:
            self.flask_module.keyboard.press_key(key)
            logger.info(f"Manual flask use: {slot}")
    
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
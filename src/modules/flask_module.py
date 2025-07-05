"""
フラスコ自動使用モジュール
"""
import threading
import time
import random
import logging
from typing import Dict, Any

from src.utils.keyboard_input import KeyboardController
from src.utils.flask_timer_manager import FlaskTimerManager

logger = logging.getLogger(__name__)

class FlaskModule:
    """フラスコ自動使用を制御するクラス"""
    
    def __init__(self, config: Dict[str, Any], window_manager=None):
        # 設定の型チェック
        if not isinstance(config, dict):
            logger.error(f"FlaskModule.__init__ received non-dict config: {type(config)} - {config}")
            config = {'enabled': False}  # フォールバック設定
        
        self.config = config
        self.window_manager = window_manager
        self.keyboard = KeyboardController()
        self.running = False
        
        # FlaskTimerManagerを使用
        self.timer_manager = FlaskTimerManager(key_press_callback=self._use_flask)
        
        logger.info("FlaskModule initialized with timer manager")
        
    def start(self):
        """フラスコ自動使用を開始"""
        if not self.config.get('enabled', False):
            logger.info("Flask module is disabled")
            return
        
        if self.running:
            logger.warning("Flask module already running")
            return
            
        self.running = True
        
        # 設定をタイマーマネージャーに反映
        self.timer_manager.update_config(self.config)
        
        logger.info("Flask module started with timer manager")
    
    def stop(self):
        """フラスコ自動使用を停止"""
        self.running = False
        self.timer_manager.stop_all_timers()
        logger.info("Flask module stopped")
    
    def _use_flask(self, key: str):
        """フラスコ使用時の処理"""
        if not self.running:
            return
            
        # POEアクティブチェック
        if self.window_manager and hasattr(self.window_manager, 'is_poe_active'):
            if not self.window_manager.is_poe_active():
                logger.debug(f"Flask use skipped - POE not active (key: {key})")
                return
        
        try:
            self.keyboard.press_key(key)
            logger.debug(f"Flask used (key: {key})")
        except Exception as e:
            logger.error(f"Error using flask: {e}")
    
    def update_config(self, new_config: Dict[str, Any]):
        """設定を更新"""
        self.config = new_config
        if self.running:
            self.timer_manager.update_config(new_config)
    
    def get_status(self) -> Dict[str, Any]:
        """モジュールのステータスを取得"""
        status = {
            'enabled': self.config.get('enabled', False),
            'running': self.running,
            'flask_count': 0,
            'active_flasks': []
        }
        
        if hasattr(self, 'timer_manager'):
            # タイマーマネージャーから情報を取得
            status['flask_count'] = self.timer_manager.get_timer_count()
            
            # アクティブなフラスコの情報を取得
            all_stats = self.timer_manager.get_all_stats()
            for slot_num, stats in all_stats.items():
                if stats.get('is_running', False):
                    status['active_flasks'].append({
                        'slot': slot_num,
                        'total_uses': stats.get('total_uses', 0)
                    })
        
        return status
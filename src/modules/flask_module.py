"""
フラスコ自動使用モジュール
"""
import threading
import time
import random
import logging
from typing import Dict, Any

from utils.keyboard_input import KeyboardController

logger = logging.getLogger(__name__)

class FlaskModule:
    """フラスコ自動使用を制御するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        # 設定の型チェック
        if not isinstance(config, dict):
            logger.error(f"FlaskModule.__init__ received non-dict config: {type(config)} - {config}")
            config = {'enabled': False}  # フォールバック設定
        
        self.config = config
        self.keyboard = KeyboardController()
        self.running = False
        self.threads = []
        
    def start(self):
        """フラスコ自動使用を開始"""
        if self.running:
            logger.warning("Flask module already running")
            return
            
        self.running = True
        
        # フラスコスロットごとに自動使用を開始
        for slot_name, slot_config in self.config.items():
            if slot_config.get('enabled', False):
                thread = threading.Thread(
                    target=self._flask_loop,
                    args=(slot_name, slot_config),
                    daemon=True
                )
                thread.start()
                self.threads.append(thread)
                logger.info(f"Started flask loop for {slot_name}")
    
    def stop(self):
        """フラスコ自動使用を停止"""
        self.running = False
        for thread in self.threads:
            thread.join(timeout=1.0)
        self.threads.clear()
        logger.info("Flask module stopped")
    
    def _flask_loop(self, slot_name: str, config: Dict[str, Any]):
        """個別フラスコのループ処理"""
        key = config['key']
        loop_delay = config['loop_delay']
        
        # 初回使用
        self.keyboard.press_key(key)
        
        while self.running:
            # ランダム遅延
            delay = random.uniform(loop_delay[0], loop_delay[1])
            logger.debug(f"{slot_name}: Waiting {delay:.3f}s before next use")
            
            # 短時間間隔でチェックして停止要求に迅速に対応
            for _ in range(int(delay * 10)):
                if not self.running:
                    break
                time.sleep(0.1)
            
            if self.running:
                self.keyboard.press_key(key)
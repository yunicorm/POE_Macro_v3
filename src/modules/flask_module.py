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
    
    def __init__(self, config: Dict[str, Any], window_manager=None):
        # 設定の型チェック
        if not isinstance(config, dict):
            logger.error(f"FlaskModule.__init__ received non-dict config: {type(config)} - {config}")
            config = {'enabled': False}  # フォールバック設定
        
        self.config = config
        self.keyboard = KeyboardController()
        self.running = False
        self.threads = []
        self.window_manager = window_manager
        
    def start(self):
        """フラスコ自動使用を高速開始"""
        if self.running:
            logger.warning("Flask module already running")
            return
            
        self.running = True
        logger.info("Flask module start signal sent")
        
        # フラスコスロットごとに自動使用を開始
        for slot_name, slot_config in self.config.items():
            # 'enabled'キーや辞書でない項目をスキップ
            if slot_name == 'enabled' or not isinstance(slot_config, dict):
                continue
                
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
        """フラスコ自動使用を即座停止"""
        self.running = False
        logger.info("Flask module stop signal sent")
        
        # 短いタイムアウトでスレッド終了を待機（高速チェックで早期終了）
        for thread in self.threads:
            thread.join(timeout=0.2)  # 1.0 -> 0.2に短縮
        self.threads.clear()
        logger.info("Flask module stopped")
    
    def _use_flask(self, key: str, slot_name: str):
        """フラスコを使用（POEウィンドウアクティブチェック付き）"""
        # Path of Exileがアクティブでない場合はスキップ
        if hasattr(self, 'window_manager') and self.window_manager:
            try:
                if not self.window_manager.is_poe_active():
                    logger.debug(f"{slot_name}: Path of Exile is not active, skipping flask use")
                    return
            except Exception as e:
                logger.debug(f"{slot_name}: Error checking POE window status: {e}")
                # エラーが発生してもキー入力を継続
        
        # POEがアクティブの場合のみキー入力を実行
        try:
            self.keyboard.press_key(key)
            logger.debug(f"{slot_name}: Flask used (key: {key})")
        except Exception as e:
            logger.error(f"{slot_name}: Error using flask: {e}")
    
    def set_window_manager(self, window_manager):
        """WindowManagerの参照を設定"""
        self.window_manager = window_manager
        logger.debug("FlaskModule: WindowManager reference set")
    
    def _flask_loop(self, slot_name: str, config: Dict[str, Any]):
        """個別フラスコのループ処理（即座停止対応）"""
        key = config['key']
        loop_delay = config['loop_delay']
        
        # 初回使用
        self._use_flask(key, slot_name)
        
        while self.running:
            # ランダム遅延
            delay = random.uniform(loop_delay[0], loop_delay[1])
            logger.debug(f"{slot_name}: Waiting {delay:.3f}s before next use")
            
            # より短い間隔（25ms）でチェックして即座に反応
            for _ in range(int(delay * 40)):  # 10 -> 40に変更（25ms間隔）
                if not self.running:
                    logger.debug(f"{slot_name}: Fast stop detected")
                    break
                time.sleep(0.025)  # 0.1 -> 0.025に変更（高速チェック）
            
            if self.running:
                self._use_flask(key, slot_name)
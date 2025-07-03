"""
�鹳��(����
"""
import threading
import time
import random
import logging
from typing import Dict, Any

from ..utils.keyboard_input import KeyboardController

logger = logging.getLogger(__name__)

class FlaskModule:
    """�鹳��(��Y���"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.keyboard = KeyboardController()
        self.running = False
        self.threads = []
        
    def start(self):
        """�鹳��ג��"""
        if self.running:
            logger.warning("Flask module already running")
            return
            
        self.running = True
        
        # �鹳����n��ג��
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
        """�鹳��ג\b"""
        self.running = False
        for thread in self.threads:
            thread.join(timeout=1.0)
        self.threads.clear()
        logger.info("Flask module stopped")
    
    def _flask_loop(self, slot_name: str, config: Dict[str, Any]):
        """%�鹳n����"""
        key = config['key']
        loop_delay = config['loop_delay']
        
        # ޟL
        self.keyboard.press_key(key)
        
        while self.running:
            # ����jE�
            delay = random.uniform(loop_delay[0], loop_delay[1])
            logger.debug(f"{slot_name}: Waiting {delay:.3f}s before next use")
            
            # 0KD��g��ïWf\b�Bk �O��
            for _ in range(int(delay * 10)):
                if not self.running:
                    break
                time.sleep(0.1)
            
            if self.running:
                self.keyboard.press_key(key)
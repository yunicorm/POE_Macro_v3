"""
キーボード入力制御モジュール
アンチチート対策のためランダム性を導入
"""
import time
import random
import logging
from typing import Tuple, Optional
import pyautogui
import pynput.keyboard as keyboard

logger = logging.getLogger(__name__)

class KeyboardController:
    """キーボード入力を制御するクラス"""
    
    def __init__(self):
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
        self._controller = keyboard.Controller()
        logger.info("KeyboardController initialized")
        
    def press_key(self, key: str, delay_range: Tuple[float, float] = (0.05, 0.1)) -> None:
        """
        指定されたキーを押下する（人間らしい遅延付き）
        
        Args:
            key: 押下するキー
            delay_range: キー押下時間の範囲（秒）
        """
        try:
            # 押下前の微小遅延（0-50ms）
            pre_delay = random.uniform(0, 0.05)
            time.sleep(pre_delay)
            
            # キー押下時間
            press_duration = random.uniform(*delay_range)
            
            logger.debug(f"Pressing key: {key} for {press_duration:.3f}s")
            pyautogui.keyDown(key)
            time.sleep(press_duration)
            pyautogui.keyUp(key)
            
            # 押下後の微小遅延（0-30ms）
            post_delay = random.uniform(0, 0.03)
            time.sleep(post_delay)
            
        except Exception as e:
            logger.error(f"Failed to press key {key}: {e}")
            raise

    def press_key_combination(self, keys: list[str]) -> None:
        """
        複数キーの組み合わせを押下（例：Ctrl+Shift+F1）
        
        Args:
            keys: 押下するキーのリスト
        """
        try:
            logger.debug(f"Pressing key combination: {'+'.join(keys)}")
            
            # 全てのキーを押下
            for key in keys:
                pyautogui.keyDown(key)
                time.sleep(random.uniform(0.01, 0.03))
            
            # 短い保持時間
            time.sleep(random.uniform(0.05, 0.1))
            
            # 逆順でキーを離す
            for key in reversed(keys):
                pyautogui.keyUp(key)
                time.sleep(random.uniform(0.01, 0.03))
                
        except Exception as e:
            logger.error(f"Failed to press key combination {keys}: {e}")
            raise
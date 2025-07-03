"""
�����e�6�����
�������Vn_�����'�e
"""
import time
import random
import logging
from typing import Tuple, Optional
import pyautogui
import pynput.keyboard as keyboard

logger = logging.getLogger(__name__)

class KeyboardController:
    """�����e��6�Y���"""
    
    def __init__(self):
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
        self._controller = keyboard.Controller()
        
    def press_key(self, key: str, delay_range: Tuple[float, float] = (0.05, 0.1)) -> None:
        """
        �U�_����Y����WDE��M	
        
        Args:
            key: �Y���
            delay_range: ���B�n���	
        """
        try:
            # �Mn�E�0-50ms	
            pre_delay = random.uniform(0, 0.05)
            time.sleep(pre_delay)
            
            # ���B�
            press_duration = random.uniform(*delay_range)
            
            logger.debug(f"Pressing key: {key} for {press_duration:.3f}s")
            pyautogui.keyDown(key)
            time.sleep(press_duration)
            pyautogui.keyUp(key)
            
            # ��n�E�0-30ms	
            post_delay = random.uniform(0, 0.03)
            time.sleep(post_delay)
            
        except Exception as e:
            logger.error(f"Failed to press key {key}: {e}")
            raise
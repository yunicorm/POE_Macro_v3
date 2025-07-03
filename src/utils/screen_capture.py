"""
;b���������
����˿�����
"""
import numpy as np
import cv2
import pyautogui
import logging
from typing import Optional, Tuple
import mss

logger = logging.getLogger(__name__)

class ScreenCapture:
    """;b����㒡Y���"""
    
    def __init__(self, monitor_index: int = 1):
        """
        Args:
            monitor_index: �˿�j�0: ����, 1: -.�˿�	
        """
        self.sct = mss.mss()
        self.monitor_index = monitor_index + 1  # msso1-indexed
        self.monitor = self.sct.monitors[self.monitor_index]
        logger.info(f"Screen capture initialized for monitor {monitor_index}: {self.monitor}")
        
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        �ߒ�����
        
        Args:
            x, y: ������n�
�
            width, height: ������n���
            
        Returns:
            �����W_;�numpyM	
        """
        try:
            region = {
                "left": self.monitor["left"] + x,
                "top": self.monitor["top"] + y,
                "width": width,
                "height": height
            }
            
            screenshot = self.sct.grab(region)
            img = np.array(screenshot)
            # BGRAK�BGRk	�
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
            
        except Exception as e:
            logger.error(f"Failed to capture screen region: {e}")
            raise
    
    def capture_full_screen(self) -> np.ndarray:
        """-.�˿�hS������"""
        return self.capture_region(0, 0, self.monitor["width"], self.monitor["height"])
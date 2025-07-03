"""
画面キャプチャモジュール
マルチモニター環境対応
"""
import numpy as np
import cv2
import logging
from typing import Optional, Tuple
import mss
import mss.tools

logger = logging.getLogger(__name__)

class ScreenCapture:
    """画面キャプチャを管理するクラス"""
    
    def __init__(self, monitor_index: int = 1):
        """
        Args:
            monitor_index: モニター番号（0: プライマリ, 1: 中央モニター）
        """
        self.sct = mss.mss()
        self.monitor_index = monitor_index + 1  # mssは1-indexed
        
        # モニター情報の取得
        if self.monitor_index >= len(self.sct.monitors):
            logger.warning(f"Monitor index {monitor_index} not found, using primary monitor")
            self.monitor_index = 1
            
        self.monitor = self.sct.monitors[self.monitor_index]
        logger.info(f"Screen capture initialized for monitor {monitor_index}: {self.monitor}")
        
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        指定領域をキャプチャ
        
        Args:
            x, y: キャプチャ領域の左上座標（モニター相対）
            width, height: キャプチャ領域のサイズ
            
        Returns:
            キャプチャした画像（numpy配列、BGR形式）
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
            # BGRAからBGRに変換
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
            
        except Exception as e:
            logger.error(f"Failed to capture screen region: {e}")
            raise
    
    def capture_full_screen(self) -> np.ndarray:
        """中央モニター全体をキャプチャ"""
        return self.capture_region(0, 0, self.monitor["width"], self.monitor["height"])
    
    def save_screenshot(self, img: np.ndarray, filename: str) -> None:
        """スクリーンショットを保存（デバッグ用）"""
        try:
            cv2.imwrite(filename, img)
            logger.debug(f"Screenshot saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            
    def get_monitor_info(self) -> dict:
        """現在のモニター情報を取得"""
        return {
            "index": self.monitor_index - 1,
            "left": self.monitor["left"],
            "top": self.monitor["top"],
            "width": self.monitor["width"],
            "height": self.monitor["height"]
        }
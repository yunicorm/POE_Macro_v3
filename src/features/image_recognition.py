"""
Tincture検出用画像認識モジュール
OpenCVによるテンプレートマッチング機能
"""
import cv2
import numpy as np
import logging
from typing import Optional, Tuple, Dict
from pathlib import Path
import mss

logger = logging.getLogger(__name__)

class TinctureDetector:
    """Tincture アイコンの検出を行うクラス（簡略化版）"""
    
    # モニター設定
    MONITOR_CONFIGS = {
        "Primary": 0,
        "Center": 1,
        "Right": 2
    }
    
    def __init__(self, monitor_config: str = "Primary", sensitivity: float = 0.7, area_selector=None):
        """
        TinctureDetector の初期化
        
        Args:
            monitor_config: モニター設定 ("Primary", "Center", "Right")
            sensitivity: 検出感度 (0.5-1.0)
            area_selector: AreaSelectorインスタンス（オプション）
        """
        self.monitor_config = monitor_config
        self.sensitivity = max(0.5, min(1.0, sensitivity))
        self.sct = mss.mss()
        self.area_selector = area_selector
        
        # モニター設定の検証
        if monitor_config not in self.MONITOR_CONFIGS:
            raise ValueError(f"Invalid monitor_config: {monitor_config}. Must be one of {list(self.MONITOR_CONFIGS.keys())}")
        
        # AreaSelectorを初期化（提供されていない場合）
        if self.area_selector is None:
            try:
                from features.area_selector import AreaSelector
                self.area_selector = AreaSelector()
            except ImportError:
                logger.warning("AreaSelector not available, using fallback detection area")
                self.area_selector = None
        
        # テンプレート画像を読み込み（解像度別は不要）
        self.template_path = Path("assets/images/tincture/sap_of_the_seasons/idle/sap_of_the_seasons_idle.png")
        self.template = None
        self._load_template()
        
        logger.info(f"TinctureDetector initialized: monitor={monitor_config}, sensitivity={sensitivity}")
    
    def _load_template(self):
        """Idle状態のテンプレート画像を読み込み"""
        try:
            if not self.template_path.exists():
                raise FileNotFoundError(f"Template not found: {self.template_path}")
            
            self.template = cv2.imread(str(self.template_path))
            if self.template is None:
                raise ValueError(f"Failed to load template: {self.template_path}")
                
            logger.info(f"Loaded template: {self.template_path}")
            
        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            raise
    
    def _capture_screen(self) -> np.ndarray:
        """画面をキャプチャ（検出エリア限定）"""
        try:
            # AreaSelectorから検出エリアを取得
            if self.area_selector:
                try:
                    tincture_area = self.area_selector.get_absolute_tincture_area()
                    capture_area = {
                        'top': tincture_area['y'],
                        'left': tincture_area['x'],
                        'width': tincture_area['width'],
                        'height': tincture_area['height']
                    }
                    logger.debug(f"Using configured tincture detection area: {capture_area}")
                except Exception as e:
                    logger.warning(f"Failed to get configured area, using fallback: {e}")
                    capture_area = self._get_fallback_area()
            else:
                capture_area = self._get_fallback_area()
            
            # スクリーンショットを撮影
            screenshot = self.sct.grab(capture_area)
            
            # numpy配列に変換
            img_array = np.array(screenshot)
            
            # BGRに変換（OpenCV形式）
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
            
            return img_bgr
            
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            raise
    
    def _get_fallback_area(self) -> Dict[str, int]:
        """フォールバック用の検出エリアを取得"""
        try:
            # モニターを選択
            monitor_index = self.MONITOR_CONFIGS[self.monitor_config]
            if monitor_index >= len(self.sct.monitors) - 1:
                monitor_index = 0  # プライマリモニターにフォールバック
            
            monitor = self.sct.monitors[monitor_index + 1]  # monitors[0]は全画面
            
            # 画面右上部分のみキャプチャ（Tinctureアイコンの位置）
            width = monitor['width']
            height = monitor['height']
            
            # 右上の約1/4エリアをキャプチャ（従来の方式）
            return {
                'top': monitor['top'],
                'left': monitor['left'] + width // 2,
                'width': width // 2,
                'height': height // 4
            }
            
        except Exception as e:
            logger.error(f"Failed to get fallback area: {e}")
            # 最後の手段として固定値を返す
            return {
                'top': 0,
                'left': 960,  # 1920x1080の右半分
                'width': 960,
                'height': 270
            }
    
    def detect_tincture_icon(self) -> bool:
        """Tincture Idle状態を検出"""
        try:
            # 画面をキャプチャ
            screen = self._capture_screen()
            
            # テンプレートマッチング
            result = cv2.matchTemplate(screen, self.template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 検出判定
            detected = max_val >= self.sensitivity
            
            if detected:
                logger.debug(f"Tincture idle state detected (confidence: {max_val:.3f})")
            
            return detected
            
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return False
    
    def get_detection_area_info(self) -> Dict[str, any]:
        """検出エリアの情報を取得（デバッグ用）"""
        try:
            info = {
                'monitor_config': self.monitor_config,
                'template_path': str(self.template_path),
                'sensitivity': self.sensitivity,
                'area_selector_available': self.area_selector is not None
            }
            
            # AreaSelectorから情報を取得
            if self.area_selector:
                try:
                    flask_area = self.area_selector.get_flask_area()
                    tincture_area = self.area_selector.get_absolute_tincture_area()
                    
                    info.update({
                        'flask_area': flask_area,
                        'tincture_detection_area': tincture_area,
                        'detection_method': 'configured_area'
                    })
                except Exception as e:
                    logger.warning(f"Failed to get area selector info: {e}")
                    info.update({
                        'detection_method': 'fallback_area',
                        'fallback_reason': str(e)
                    })
            else:
                # フォールバック情報を取得
                fallback_area = self._get_fallback_area()
                info.update({
                    'detection_area': fallback_area,
                    'detection_method': 'fallback_area'
                })
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get detection area info: {e}")
            return {}
    
    def update_sensitivity(self, new_sensitivity: float) -> None:
        """検出感度を更新"""
        self.sensitivity = max(0.5, min(1.0, new_sensitivity))
        logger.info(f"Sensitivity updated to: {self.sensitivity}")
    
    def reload_template(self) -> None:
        """テンプレートを再読み込み"""
        self._load_template()
        logger.info("Template reloaded")
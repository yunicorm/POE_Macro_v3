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
import platform

logger = logging.getLogger(__name__)

class TinctureDetector:
    """Tincture アイコンの検出を行うクラス"""
    
    # サポートされる解像度
    SUPPORTED_RESOLUTIONS = ["1920x1080", "2560x1440", "3840x2160"]
    
    # モニター設定
    MONITOR_CONFIGS = {
        "Primary": 0,
        "Center": 1,
        "Right": 2
    }
    
    def __init__(self, monitor_config: str = "Primary", sensitivity: float = 0.7):
        """
        TinctureDetector の初期化
        
        Args:
            monitor_config: モニター設定 ("Primary", "Center", "Right")
            sensitivity: 検出感度 (0.5-1.0)
        """
        self.monitor_config = monitor_config
        self.sensitivity = max(0.5, min(1.0, sensitivity))
        self.assets_path = Path("assets/images/tincture")
        self.templates: Dict[str, np.ndarray] = {}
        self.current_resolution = None
        self.sct = mss.mss()
        
        # モニター設定の検証
        if monitor_config not in self.MONITOR_CONFIGS:
            raise ValueError(f"Invalid monitor_config: {monitor_config}. Must be one of {list(self.MONITOR_CONFIGS.keys())}")
        
        # 現在の解像度を取得
        self._detect_resolution()
        
        # テンプレート画像の読み込み
        self._load_templates()
        
        logger.info(f"TinctureDetector initialized: monitor={monitor_config}, sensitivity={sensitivity}, resolution={self.current_resolution}")
    
    def _detect_resolution(self) -> None:
        """現在の画面解像度を検出"""
        try:
            # プライマリモニターの情報を取得
            monitor = self.sct.monitors[1]  # monitors[0]は全画面、monitors[1]はプライマリ
            width = monitor['width']
            height = monitor['height']
            
            resolution = f"{width}x{height}"
            
            # サポートされている解像度かチェック
            if resolution in self.SUPPORTED_RESOLUTIONS:
                self.current_resolution = resolution
            else:
                # 最も近い解像度を選択
                logger.warning(f"Unsupported resolution {resolution}, using closest match")
                self.current_resolution = self._get_closest_resolution(width, height)
            
            logger.info(f"Detected resolution: {resolution} -> Using: {self.current_resolution}")
            
        except Exception as e:
            logger.error(f"Failed to detect resolution: {e}")
            self.current_resolution = "1920x1080"  # デフォルト
    
    def _get_closest_resolution(self, width: int, height: int) -> str:
        """最も近い解像度を取得"""
        resolutions = {
            "1920x1080": (1920, 1080),
            "2560x1440": (2560, 1440),
            "3840x2160": (3840, 2160)
        }
        
        min_distance = float('inf')
        closest_resolution = "1920x1080"
        
        for res_name, (res_w, res_h) in resolutions.items():
            distance = abs(width - res_w) + abs(height - res_h)
            if distance < min_distance:
                min_distance = distance
                closest_resolution = res_name
        
        return closest_resolution
    
    def _load_templates(self) -> None:
        """テンプレート画像を読み込み"""
        template_file = f"sap_of_the_seasons_{self.current_resolution}.png"
        template_path = self.assets_path / template_file
        
        try:
            if not template_path.exists():
                raise FileNotFoundError(f"Template file not found: {template_path}")
            
            template = cv2.imread(str(template_path))
            if template is None:
                raise ValueError(f"Failed to load template image: {template_path}")
            
            self.templates['sap_of_the_seasons'] = template
            logger.info(f"Loaded template: {template_file}")
            
        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            raise
    
    def _capture_screen(self) -> np.ndarray:
        """画面をキャプチャ（検出エリア限定）"""
        try:
            # モニターを選択
            monitor_index = self.MONITOR_CONFIGS[self.monitor_config]
            if monitor_index >= len(self.sct.monitors) - 1:
                monitor_index = 0  # プライマリモニターにフォールバック
            
            monitor = self.sct.monitors[monitor_index + 1]  # monitors[0]は全画面
            
            # 画面右上部分のみキャプチャ（Tinctureアイコンの位置）
            # 解像度に応じて調整
            width = monitor['width']
            height = monitor['height']
            
            # 右上の約1/4エリアをキャプチャ
            capture_area = {
                'top': monitor['top'],
                'left': monitor['left'] + width // 2,
                'width': width // 2,
                'height': height // 4
            }
            
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
    
    def _load_template(self) -> np.ndarray:
        """テンプレート画像を取得"""
        if 'sap_of_the_seasons' not in self.templates:
            self._load_templates()
        
        return self.templates['sap_of_the_seasons']
    
    def _match_template(self, screen: np.ndarray, template: np.ndarray) -> float:
        """テンプレートマッチングを実行"""
        try:
            # テンプレートマッチング実行
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            
            # 最大値を取得
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            logger.debug(f"Template match confidence: {max_val:.3f} at position {max_loc}")
            
            return max_val
            
        except Exception as e:
            logger.error(f"Template matching failed: {e}")
            return 0.0
    
    def detect_tincture_icon(self) -> bool:
        """
        Tincture アイコンを検出
        
        Returns:
            bool: アイコンが検出された場合True
        """
        try:
            # 画面をキャプチャ
            screen = self._capture_screen()
            
            # テンプレートを取得
            template = self._load_template()
            
            # テンプレートマッチング実行
            confidence = self._match_template(screen, template)
            
            # 検出判定
            detected = confidence >= self.sensitivity
            
            if detected:
                logger.info(f"Tincture icon detected with confidence: {confidence:.3f}")
            else:
                logger.debug(f"Tincture icon not detected (confidence: {confidence:.3f}, threshold: {self.sensitivity})")
            
            return detected
            
        except Exception as e:
            logger.error(f"Tincture detection failed: {e}")
            return False
    
    def get_detection_area_info(self) -> Dict[str, any]:
        """検出エリアの情報を取得（デバッグ用）"""
        try:
            monitor_index = self.MONITOR_CONFIGS[self.monitor_config]
            if monitor_index >= len(self.sct.monitors) - 1:
                monitor_index = 0
            
            monitor = self.sct.monitors[monitor_index + 1]
            width = monitor['width']
            height = monitor['height']
            
            return {
                'monitor_config': self.monitor_config,
                'monitor_index': monitor_index,
                'full_resolution': f"{width}x{height}",
                'detection_area': {
                    'top': monitor['top'],
                    'left': monitor['left'] + width // 2,
                    'width': width // 2,
                    'height': height // 4
                },
                'template_resolution': self.current_resolution,
                'sensitivity': self.sensitivity
            }
            
        except Exception as e:
            logger.error(f"Failed to get detection area info: {e}")
            return {}
    
    def update_sensitivity(self, new_sensitivity: float) -> None:
        """検出感度を更新"""
        self.sensitivity = max(0.5, min(1.0, new_sensitivity))
        logger.info(f"Sensitivity updated to: {self.sensitivity}")
    
    def reload_templates(self) -> None:
        """テンプレートを再読み込み"""
        self.templates.clear()
        self._load_templates()
        logger.info("Templates reloaded")
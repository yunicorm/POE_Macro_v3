"""
画像認識モジュール
OpenCVによるテンプレートマッチング
"""
import cv2
import numpy as np
import logging
from typing import Optional, Tuple, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageRecognition:
    """画像認識を行うクラス"""
    
    def __init__(self, assets_path: str = "assets/images"):
        self.assets_path = Path(assets_path)
        self.templates: Dict[str, np.ndarray] = {}
        
        # 画像が存在することを確認
        if not self.assets_path.exists():
            logger.warning(f"Assets path does not exist: {assets_path}")
            self.assets_path.mkdir(parents=True, exist_ok=True)
            
    def load_template(self, name: str, path: str) -> None:
        """
        テンプレート画像を読み込み
        
        Args:
            name: テンプレートの識別名
            path: 画像ファイルの相対パス（assets_pathからの相対）
        """
        try:
            full_path = self.assets_path / path
            template = cv2.imread(str(full_path))
            if template is None:
                raise ValueError(f"Failed to load image: {full_path}")
                
            self.templates[name] = template
            logger.info(f"Loaded template '{name}' from {full_path}")
            
        except Exception as e:
            logger.error(f"Failed to load template {name}: {e}")
            raise
    
    def find_template(self, screenshot: np.ndarray, template_name: str, 
                     threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        スクリーンショット内でテンプレートを検索
        
        Args:
            screenshot: 検索対象の画像
            template_name: テンプレート名
            threshold: マッチング閾値（0.0-1.0）
            
        Returns:
            見つかった場合は(x, y)座標、見つからない場合はNone
        """
        if template_name not in self.templates:
            logger.error(f"Template '{template_name}' not loaded")
            return None
            
        template = self.templates[template_name]
        
        try:
            # テンプレートマッチング
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                logger.debug(f"Template '{template_name}' found at {max_loc} with confidence {max_val:.3f}")
                return max_loc
            else:
                logger.debug(f"Template '{template_name}' not found (max confidence: {max_val:.3f})")
                return None
                
        except Exception as e:
            logger.error(f"Template matching failed: {e}")
            return None
    
    def find_all_templates(self, screenshot: np.ndarray, template_name: str,
                          threshold: float = 0.8) -> List[Tuple[int, int]]:
        """
        スクリーンショット内で全ての一致するテンプレートを検索
        
        Returns:
            見つかった全ての(x, y)座標のリスト
        """
        if template_name not in self.templates:
            logger.error(f"Template '{template_name}' not loaded")
            return []
            
        template = self.templates[template_name]
        locations = []
        
        try:
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= threshold)
            
            # 座標を(x, y)のタプルに変換
            for pt in zip(*loc[::-1]):
                locations.append(pt)
                
            logger.debug(f"Found {len(locations)} instances of template '{template_name}'")
            return locations
            
        except Exception as e:
            logger.error(f"Template matching failed: {e}")
            return []
    
    def load_tincture_templates(self):
        """Tincture関連のテンプレートを一括読み込み"""
        tincture_templates = {
            "sap_idle": "tincture/sap_of_the_seasons/idle/sap_of_the_seasons_idle.png",
            "sap_active": "tincture/sap_of_the_seasons/active/sap_of_the_seasons_active.png",
            "sap_cooldown": "tincture/sap_of_the_seasons/cooldown/sap_of_the_seasons_cooldown_p050.png"
        }
        
        for name, path in tincture_templates.items():
            try:
                self.load_template(name, path)
            except Exception as e:
                logger.warning(f"Failed to load tincture template {name}: {e}")
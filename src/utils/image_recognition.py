"""
;ÏXâ¸åüë
OpenCVkˆ‹Æó×ìüÈÞÃÁó°
"""
import cv2
import numpy as np
import logging
from typing import Optional, Tuple, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageRecognition:
    """;ÏX’LF¯é¹"""
    
    def __init__(self, assets_path: str = "assets/images"):
        self.assets_path = Path(assets_path)
        self.templates = {}
        
    def load_template(self, name: str, path: str) -> None:
        """Æó×ìüÈ;Ï’­¼"""
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
        ¹¯êüó·çÃÈ…gÆó×ìüÈ’"
        
        Args:
            screenshot: "þan;Ï
            template_name: Æó×ìüÈ
            threshold: ÞÃÁó°¾$
            
        Returns:
            ‹dKc_4o(x, y)§‹dK‰jD4oNone
        """
        if template_name not in self.templates:
            logger.error(f"Template '{template_name}' not loaded")
            return None
            
        template = self.templates[template_name]
        
        try:
            # Æó×ìüÈÞÃÁó°
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
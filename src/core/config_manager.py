"""
-š¡â¸åüë
"""
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """-šÕ¡¤ë’¡Y‹¯é¹"""
    
    def __init__(self, config_path: str = "config/default_config.yaml"):
        self.config_path = Path(config_path)
        self.config = {}
        self.user_config_path = Path("config/user_config.yaml")
        
    def load_config(self) -> Dict[str, Any]:
        """-šÕ¡¤ë’­¼€"""
        try:
            # ÇÕ©ëÈ-š’­¼
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Loaded default config from {self.config_path}")
            
            # æü¶ü-šLBŒp
øM
            if self.user_config_path.exists():
                with open(self.user_config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    self._merge_config(self.config, user_config)
                logger.info(f"Loaded user config from {self.user_config_path}")
                
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def save_user_config(self) -> None:
        """þ(n-š’æü¶ü-šhWfÝX"""
        try:
            self.user_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved user config to {self.user_config_path}")
        except Exception as e:
            logger.error(f"Failed to save user config: {e}")
            raise
    
    def _merge_config(self, base: Dict, override: Dict) -> None:
        """-š’0„kÞü¸"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        ÉÃÈ:Šn­üÑ¹g-š$’Ö—
        ‹: get("flasks.slot_1.key") -> "1"
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
"""
設定管理モジュール
"""
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """設定ファイルを管理するクラス"""
    
    def __init__(self, config_path: str = "config/default_config.yaml"):
        self.config_path = Path(config_path)
        self.config = {}
        self.user_config_path = Path("config/user_config.yaml")
        
    def load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        try:
            # デフォルト設定を読み込み
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Loaded default config from {self.config_path}")
            
            # デバッグ: 読み込んだ設定の型と構造を確認
            logger.debug(f"Config type after loading: {type(self.config)}")
            if isinstance(self.config, dict):
                logger.debug(f"Config keys: {list(self.config.keys())}")
                
                # Flask設定の詳細デバッグ
                flask_config = self.config.get('flask')
                logger.debug(f"Flask config type: {type(flask_config)}")
                logger.debug(f"Flask config value: {flask_config}")
                if isinstance(flask_config, dict):
                    logger.debug(f"Flask config keys: {list(flask_config.keys())}")
                
                # Skills設定の詳細デバッグ
                skills_config = self.config.get('skills')
                logger.debug(f"Skills config type: {type(skills_config)}")
                logger.debug(f"Skills config value: {skills_config}")
                if isinstance(skills_config, dict):
                    logger.debug(f"Skills config keys: {list(skills_config.keys())}")
                
                # Tincture設定の詳細デバッグ
                tincture_config = self.config.get('tincture')
                logger.debug(f"Tincture config type: {type(tincture_config)}")
                logger.debug(f"Tincture config value: {tincture_config}")
                if isinstance(tincture_config, dict):
                    logger.debug(f"Tincture config keys: {list(tincture_config.keys())}")
            else:
                logger.error(f"Config is not a dictionary: {self.config}")
            
            # ユーザー設定があれば上書き
            if self.user_config_path.exists():
                logger.debug(f"User config file exists: {self.user_config_path}")
                with open(self.user_config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    logger.debug(f"User config type: {type(user_config)}")
                    logger.debug(f"User config value: {user_config}")
                    if isinstance(user_config, dict):
                        logger.debug(f"Merging user config...")
                        self._merge_config(self.config, user_config)
                        logger.info(f"Loaded user config from {self.user_config_path}")
                    else:
                        logger.warning(f"User config is not a dictionary, skipping: {type(user_config)}")
            
            # 最終的な設定構造をデバッグ
            logger.debug(f"Final config type: {type(self.config)}")
            logger.debug(f"Returning config with keys: {list(self.config.keys()) if isinstance(self.config, dict) else 'Not a dict'}")
            
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # フォールバック設定を返す
            fallback_config = {
                'flask': {'enabled': False},
                'skills': {'enabled': False},
                'tincture': {'enabled': False}
            }
            logger.warning(f"Using fallback config: {fallback_config}")
            self.config = fallback_config
            return self.config
    
    def save_user_config(self) -> None:
        """現在の設定をユーザー設定として保存"""
        try:
            self.user_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved user config to {self.user_config_path}")
        except Exception as e:
            logger.error(f"Failed to save user config: {e}")
            raise
    
    def _merge_config(self, base: Dict, override: Dict) -> None:
        """設定を再帰的にマージ"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        ドット区切りのキーパスで設定値を取得
        例: get("flasks.slot_1.key") -> "1"
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """
        ドット区切りのキーパスで設定値を設定
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        config[keys[-1]] = value
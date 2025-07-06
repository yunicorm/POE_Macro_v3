"""
設定管理モジュール
"""
import yaml
import logging
import os
from pathlib import Path
from typing import Dict, Any
from src.utils.resource_path import get_config_path, get_user_config_path, ensure_directory_exists

logger = logging.getLogger(__name__)

class ConfigManager:
    """設定ファイルを管理するクラス"""
    
    def __init__(self, config_path: str = "default_config.yaml"):
        self.config_filename = config_path
        self.config_path = get_config_path(config_path)
        self.config = {}
        self.user_config_path = Path(get_user_config_path("user_config.yaml"))
        
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
                        # flask_slotsの確認を追加
                        if 'flask_slots' in user_config:
                            logger.debug(f"User config has flask_slots: {user_config['flask_slots'].keys()}")
                        logger.debug(f"Merging user config...")
                        self._merge_config(self.config, user_config)
                        logger.info(f"Loaded user config from {self.user_config_path}")
                        # マージ後のflask_slots確認
                        if 'flask_slots' in self.config:
                            logger.debug(f"After merge - flask_slots keys: {self.config['flask_slots'].keys()}")
                        else:
                            logger.warning("After merge - flask_slots not found in config")
                    else:
                        logger.warning(f"User config is not a dictionary, skipping: {type(user_config)}")
            
            # 最終的な設定構造をデバッグ
            logger.debug(f"Final config type: {type(self.config)}")
            logger.debug(f"Returning config with keys: {list(self.config.keys()) if isinstance(self.config, dict) else 'Not a dict'}")
            
            # デバッグ: load_config完了時の最終config確認
            print(f"[DEBUG] ConfigManager.load_config - 最終config keys: {list(self.config.keys())}")
            if 'flask_slots' in self.config:
                print(f"[DEBUG] ConfigManager.load_config - 最終flask_slots: {list(self.config['flask_slots'].keys())}")
                for slot_name, slot_data in self.config['flask_slots'].items():
                    print(f"[DEBUG]   {slot_name}: key={slot_data.get('key')}, type={slot_data.get('flask_type')}")
            else:
                print(f"[DEBUG] ConfigManager.load_config - flask_slotsが存在しません")
            
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
            ensure_directory_exists(self.user_config_path)
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved user config to {self.user_config_path}")
        except Exception as e:
            logger.error(f"Failed to save user config: {e}")
            raise
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """設定を保存（内部設定を更新してユーザー設定として保存）"""
        try:
            # デバッグ: 保存するconfig全体を出力
            print(f"[DEBUG] ConfigManager.save_config - 保存するconfig keys: {list(config.keys())}")
            if 'flask_slots' in config:
                print(f"[DEBUG] ConfigManager.save_config - flask_slots: {list(config['flask_slots'].keys())}")
            
            # デバッグ: user_config.yamlのフルパスを出力
            print(f"[DEBUG] ConfigManager.save_config - user_config_path: {self.user_config_path}")
            
            self.config = config
            self.save_user_config()
            
            # デバッグ: ファイル書き込み後、ファイルを読み直して内容を確認
            if self.user_config_path.exists():
                with open(self.user_config_path, 'r', encoding='utf-8') as f:
                    saved_content = yaml.safe_load(f)
                    if 'flask_slots' in saved_content:
                        print(f"[DEBUG] ファイル書き込み後確認 - flask_slots存在: {list(saved_content['flask_slots'].keys())}")
                    else:
                        print(f"[DEBUG] ファイル書き込み後確認 - flask_slotsが存在しません")
            else:
                print(f"[DEBUG] user_config.yamlファイルが存在しません")
                
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            print(f"[DEBUG] ConfigManager.save_config エラー: {e}")
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
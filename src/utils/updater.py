"""
POE Macro v3 Auto-Updater
GitHubのリリースから最新バージョンをチェックして更新
"""

import os
import sys
import json
import logging
import requests
import tempfile
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path
from src.version import VERSION

logger = logging.getLogger(__name__)

class Updater:
    """自動更新機能を提供するクラス"""
    
    GITHUB_REPO = "your-username/poe-macro-v3"  # 実際のリポジトリに変更してください
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    
    def __init__(self):
        self.current_version = VERSION
        self.update_available = False
        self.latest_version = None
        self.download_url = None
        
    def check_for_updates(self) -> bool:
        """
        GitHubから最新バージョンをチェック
        
        Returns:
            bool: 更新が利用可能な場合True
        """
        try:
            logger.info("Checking for updates...")
            
            # GitHub APIから最新リリース情報を取得
            response = requests.get(
                self.GITHUB_API_URL,
                headers={'Accept': 'application/vnd.github.v3+json'},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to check updates: HTTP {response.status_code}")
                return False
            
            release_data = response.json()
            
            # バージョン情報を取得
            self.latest_version = release_data.get('tag_name', '').lstrip('v')
            
            # アセット（実行ファイル）のURLを取得
            assets = release_data.get('assets', [])
            for asset in assets:
                if asset['name'].endswith('.exe'):
                    self.download_url = asset['browser_download_url']
                    break
            
            # バージョン比較
            if self._compare_versions(self.latest_version, self.current_version) > 0:
                self.update_available = True
                logger.info(f"Update available: {self.current_version} -> {self.latest_version}")
                return True
            else:
                logger.info("No updates available")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error checking for updates: {e}")
            return False
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return False
    
    def download_update(self) -> Optional[str]:
        """
        最新バージョンをダウンロード
        
        Returns:
            Optional[str]: ダウンロードしたファイルのパス
        """
        if not self.download_url:
            logger.error("No download URL available")
            return None
        
        try:
            logger.info(f"Downloading update from {self.download_url}")
            
            # 一時ファイルにダウンロード
            with tempfile.NamedTemporaryFile(delete=False, suffix='.exe') as tmp_file:
                response = requests.get(self.download_url, stream=True, timeout=60)
                response.raise_for_status()
                
                # プログレスバー表示用
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.info(f"Download progress: {progress:.1f}%")
                
                logger.info(f"Download completed: {tmp_file.name}")
                return tmp_file.name
                
        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            return None
    
    def install_update(self, downloaded_file: str) -> bool:
        """
        ダウンロードした更新をインストール
        
        Args:
            downloaded_file: ダウンロードしたファイルのパス
            
        Returns:
            bool: 成功した場合True
        """
        try:
            # 現在の実行ファイルのパス
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                logger.warning("Not running from executable, cannot auto-update")
                return False
            
            # バックアップを作成
            backup_path = f"{current_exe}.backup"
            os.rename(current_exe, backup_path)
            
            # 新しいバージョンを配置
            os.rename(downloaded_file, current_exe)
            
            logger.info("Update installed successfully")
            
            # アップデートスクリプトを作成して実行
            update_script = f"""
import os
import time
import subprocess

# 少し待機（現在のプロセスが終了するまで）
time.sleep(2)

# 新しいバージョンを起動
subprocess.Popen([r'{current_exe}'])

# バックアップを削除
try:
    os.remove(r'{backup_path}')
except:
    pass
"""
            
            script_path = "update_helper.py"
            with open(script_path, 'w') as f:
                f.write(update_script)
            
            # アップデートヘルパーを起動
            subprocess.Popen([sys.executable, script_path])
            
            return True
            
        except Exception as e:
            logger.error(f"Error installing update: {e}")
            
            # エラーが発生した場合、バックアップから復元
            if os.path.exists(backup_path):
                try:
                    os.remove(current_exe)
                    os.rename(backup_path, current_exe)
                except:
                    pass
            
            return False
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        バージョン番号を比較
        
        Args:
            version1: 比較するバージョン1
            version2: 比較するバージョン2
            
        Returns:
            int: version1 > version2 なら 1, 等しければ 0, 小さければ -1
        """
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # バージョン番号の長さを揃える
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            
            return 0
            
        except Exception:
            return 0
    
    def get_update_info(self) -> Dict[str, Any]:
        """
        更新情報を取得
        
        Returns:
            Dict[str, Any]: 更新情報
        """
        return {
            'current_version': self.current_version,
            'latest_version': self.latest_version,
            'update_available': self.update_available,
            'download_url': self.download_url
        }
"""
Path of Exile ログ監視モジュール
Client.txtを監視してエリア入退場を検出し、マクロを自動制御
"""
import os
import time
import threading
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class LogMonitor:
    """POEログファイルを監視してマクロを自動制御するクラス"""
    
    def __init__(self, config: Dict[str, Any], macro_controller=None):
        self.config = config
        self.macro_controller = macro_controller
        
        # ログファイルパス
        self.log_file_path = Path(config.get('log_path', 
            r'C:\Program Files (x86)\Steam\steamapps\common\Path of Exile\logs\Client.txt'))
        
        # 監視設定
        self.check_interval = config.get('check_interval', 0.5)  # 0.5秒間隔
        self.enabled = config.get('enabled', False)
        
        # 監視状態
        self.running = False
        self.monitor_thread = None
        self.last_position = 0
        
        # エリア状態
        self.in_area = False
        self.current_area = None
        
        # ログパターン
        self.area_enter_pattern = re.compile(
            r'.*Entering area.*|.*You have entered.*|.*Entered area.*', 
            re.IGNORECASE
        )
        self.area_exit_pattern = re.compile(
            r'.*Leaving area.*|.*You have left.*|.*Left area.*', 
            re.IGNORECASE
        )
        self.hideout_pattern = re.compile(
            r'.*hideout.*|.*Hideout.*', 
            re.IGNORECASE
        )
        self.town_pattern = re.compile(
            r'.*town.*|.*Town.*|.*Lioneye.*|.*Highgate.*|.*Oriath.*', 
            re.IGNORECASE
        )
        
        # 統計情報
        self.stats = {
            'areas_entered': 0,
            'areas_exited': 0,
            'macro_activations': 0,
            'macro_deactivations': 0,
            'last_area_change': None
        }
        
        # コールバック
        self.on_area_enter = None
        self.on_area_exit = None
        
    def start(self):
        """ログ監視を開始"""
        if not self.enabled:
            logger.info("Log monitor is disabled in config")
            return
            
        if self.running:
            logger.warning("Log monitor already running")
            return
            
        if not self.log_file_path.exists():
            logger.error(f"Log file not found: {self.log_file_path}")
            return
            
        self.running = True
        
        # 現在のファイル位置を記録（末尾から監視開始）
        try:
            with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(0, 2)  # ファイル末尾へ
                self.last_position = f.tell()
        except Exception as e:
            logger.error(f"Failed to initialize log position: {e}")
            return
            
        # 監視スレッドを開始
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info(f"Log monitor started, watching: {self.log_file_path}")
        
    def stop(self):
        """ログ監視を停止"""
        if not self.running:
            return
            
        self.running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            self.monitor_thread = None
            
        logger.info("Log monitor stopped")
        
    def update_config(self, config: Dict[str, Any]):
        """設定を更新"""
        self.config = config
        self.enabled = config.get('enabled', False)
        self.check_interval = config.get('check_interval', 0.5)
        
        # ログファイルパスが変更された場合は再起動
        new_log_path = Path(config.get('log_path', self.log_file_path))
        if new_log_path != self.log_file_path:
            self.log_file_path = new_log_path
            if self.running:
                self.stop()
                self.start()
                
        logger.info("Log monitor configuration updated")
        
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            **self.stats,
            'running': self.running,
            'in_area': self.in_area,
            'current_area': self.current_area,
            'log_file_exists': self.log_file_path.exists()
        }
        
    def set_callbacks(self, on_area_enter: Callable = None, on_area_exit: Callable = None):
        """コールバック関数を設定"""
        self.on_area_enter = on_area_enter
        self.on_area_exit = on_area_exit
        
    def _monitor_loop(self):
        """ログファイル監視のメインループ"""
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        while self.running:
            try:
                # ファイルサイズをチェック
                if not self.log_file_path.exists():
                    logger.warning(f"Log file disappeared: {self.log_file_path}")
                    time.sleep(self.check_interval)
                    continue
                    
                current_size = self.log_file_path.stat().st_size
                
                # ファイルが小さくなった場合（ローテーション）
                if current_size < self.last_position:
                    logger.info("Log file rotated, resetting position")
                    self.last_position = 0
                    
                # 新しいデータがある場合
                if current_size > self.last_position:
                    self._read_new_lines()
                    
                consecutive_errors = 0
                time.sleep(self.check_interval)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in log monitor loop: {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive errors, stopping log monitor")
                    break
                    
                time.sleep(self.check_interval * 2)  # エラー時は少し長く待つ
                
    def _read_new_lines(self):
        """新しい行を読み込んで解析"""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()
                
                for line in new_lines:
                    line = line.strip()
                    if line:
                        self._parse_log_entry(line)
                        
        except Exception as e:
            logger.error(f"Error reading log file: {e}")
            
    def _parse_log_entry(self, line: str):
        """ログエントリを解析してエリア入退場を検出"""
        try:
            # エリア入場の検出
            if self.area_enter_pattern.search(line):
                self._handle_area_enter(line)
                return
                
            # エリア退場の検出
            if self.area_exit_pattern.search(line):
                self._handle_area_exit(line)
                return
                
        except Exception as e:
            logger.error(f"Error parsing log entry: {e}")
            
    def _handle_area_enter(self, line: str):
        """エリア入場時の処理"""
        if self.in_area:
            return  # 既にエリア内
            
        self.in_area = True
        self.current_area = self._extract_area_name(line)
        self.stats['areas_entered'] += 1
        self.stats['last_area_change'] = time.time()
        
        logger.info(f"Entered area: {self.current_area}")
        
        # 安全なエリア（町・隠れ家）以外でマクロを有効化
        if not self._is_safe_area(line):
            self._activate_macro()
            
        # コールバック実行
        if self.on_area_enter:
            try:
                self.on_area_enter(self.current_area)
            except Exception as e:
                logger.error(f"Error in area enter callback: {e}")
                
    def _handle_area_exit(self, line: str):
        """エリア退場時の処理"""
        if not self.in_area:
            return  # 既にエリア外
            
        self.in_area = False
        old_area = self.current_area
        self.current_area = None
        self.stats['areas_exited'] += 1
        self.stats['last_area_change'] = time.time()
        
        logger.info(f"Left area: {old_area}")
        
        # マクロを無効化
        self._deactivate_macro()
        
        # コールバック実行
        if self.on_area_exit:
            try:
                self.on_area_exit(old_area)
            except Exception as e:
                logger.error(f"Error in area exit callback: {e}")
                
    def _extract_area_name(self, line: str) -> str:
        """ログ行からエリア名を抽出"""
        # 簡単な抽出ロジック（実際のログ形式に応じて調整）
        try:
            if '"' in line:
                # "エリア名" 形式
                start = line.find('"') + 1
                end = line.find('"', start)
                if end > start:
                    return line[start:end]
            
            # その他の形式
            words = line.split()
            for i, word in enumerate(words):
                if word.lower() in ['area', 'entering', 'entered']:
                    if i + 1 < len(words):
                        return words[i + 1]
                        
        except Exception as e:
            logger.error(f"Error extracting area name: {e}")
            
        return "Unknown Area"
        
    def _is_safe_area(self, line: str) -> bool:
        """安全なエリア（町・隠れ家）かどうかを判定"""
        return (self.hideout_pattern.search(line) or 
                self.town_pattern.search(line))
                
    def _activate_macro(self):
        """マクロを有効化"""
        if self.macro_controller and not self.macro_controller.running:
            try:
                self.macro_controller.start()
                self.stats['macro_activations'] += 1
                logger.info("Macro activated by log monitor")
            except Exception as e:
                logger.error(f"Failed to activate macro: {e}")
                
    def _deactivate_macro(self):
        """マクロを無効化"""
        if self.macro_controller and self.macro_controller.running:
            try:
                self.macro_controller.stop()
                self.stats['macro_deactivations'] += 1
                logger.info("Macro deactivated by log monitor")
            except Exception as e:
                logger.error(f"Failed to deactivate macro: {e}")
                
    def manual_test_area_enter(self, area_name: str = "Test Area"):
        """手動でエリア入場をテスト"""
        test_line = f'Entering area "{area_name}"'
        self._parse_log_entry(test_line)
        
    def manual_test_area_exit(self, area_name: str = "Test Area"):
        """手動でエリア退場をテスト"""
        test_line = f'Leaving area "{area_name}"'
        self._parse_log_entry(test_line)
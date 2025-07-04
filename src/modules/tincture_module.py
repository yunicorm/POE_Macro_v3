"""
Tincture自動使用モジュール
Path of Exile の Tincture アイテムを自動で使用する機能
"""
import time
import threading
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from features.image_recognition import TinctureDetector
from utils.keyboard_input import KeyboardController
from core.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class TinctureModule:
    """Tincture自動使用モジュール"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        TinctureModule の初期化
        
        Args:
            config: 設定辞書
        """
        # 設定の型チェック
        if not isinstance(config, dict):
            logger.error(f"TinctureModule.__init__ received non-dict config: {type(config)} - {config}")
            config = {'enabled': False}  # フォールバック設定
        
        self.config = config
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_use_time = 0
        
        # 設定の読み込み
        self.enabled = config.get('enabled', True)
        self.key = config.get('key', '3')
        self.monitor_config = config.get('monitor_config', 'Primary')
        self.sensitivity = config.get('sensitivity', 0.7)
        self.check_interval = config.get('check_interval', 0.1)  # 100ms
        self.min_use_interval = config.get('min_use_interval', 0.5)  # 500ms
        
        # AreaSelectorを初期化
        try:
            from features.area_selector import AreaSelector
            self.area_selector = AreaSelector()
        except ImportError:
            logger.warning("AreaSelector not available")
            self.area_selector = None
        
        # 単一の検出器のみ初期化（AreaSelectorを渡す）
        self.detector = TinctureDetector(
            monitor_config=self.monitor_config,
            sensitivity=self.sensitivity,
            area_selector=self.area_selector
        )
        
        # キーボード制御
        self.keyboard = KeyboardController()
        
        # 統計情報
        self.stats = {
            'total_uses': 0,
            'successful_detections': 0,
            'failed_detections': 0,
            'last_use_timestamp': None
        }
        
        logger.info(f"TinctureModule initialized: enabled={self.enabled}, key={self.key}")
    
    
    def start(self) -> None:
        """Tincture モジュールを開始"""
        if not self.enabled:
            logger.info("Tincture module is disabled")
            return
        
        if self.running:
            logger.warning("Tincture module is already running")
            return
        
        try:
            self.running = True
            self.thread = threading.Thread(target=self._tincture_loop, daemon=True)
            self.thread.start()
            logger.info("Tincture module started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start tincture module: {e}")
            self.running = False
            raise
    
    def stop(self) -> None:
        """Tincture モジュールを停止"""
        if not self.running:
            logger.info("Tincture module is not running")
            return
        
        try:
            self.running = False
            
            # スレッドの終了を待機
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2.0)
                if self.thread.is_alive():
                    logger.warning("Tincture thread did not terminate gracefully")
            
            logger.info("Tincture module stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping tincture module: {e}")
    
    def _tincture_loop(self) -> None:
        """簡略化されたループ - Idle状態のみ検出"""
        logger.info("Tincture monitoring started")
        
        while self.running:
            try:
                # Idle状態を検出
                if self.detector.detect_tincture_icon():
                    # 最小使用間隔をチェック
                    current_time = time.time()
                    if current_time - self.last_use_time >= self.min_use_interval:
                        # Tinctureを使用
                        logger.info(f"Using tincture (key: {self.key})")
                        self.keyboard.press_key(self.key)
                        
                        # 統計を更新
                        self.last_use_time = current_time
                        self.stats['total_uses'] += 1
                        self.stats['last_use_timestamp'] = current_time
                        
                        # 使用後は一定時間待機（アクティブ時間を考慮）
                        time.sleep(5.0)  # Tinctureが有効になるまで待機
                
                # 検出間隔
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in tincture loop: {e}")
                time.sleep(self.check_interval * 2)
        
        logger.info("Tincture monitoring ended")
    
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """設定を更新"""
        try:
            # 設定の型チェック
            if not isinstance(new_config, dict):
                logger.error(f"TinctureModule.update_config received non-dict config: {type(new_config)} - {new_config}")
                return
            
            # 設定の更新
            old_enabled = self.enabled
            self.config = new_config
            self.enabled = new_config.get('enabled', True)
            self.key = new_config.get('key', '3')
            self.monitor_config = new_config.get('monitor_config', 'Primary')
            self.sensitivity = new_config.get('sensitivity', 0.7)
            self.check_interval = new_config.get('check_interval', 0.1)
            self.min_use_interval = new_config.get('min_use_interval', 0.5)
            
            # 検出器の感度を更新
            self.detector.update_sensitivity(self.sensitivity)
            
            # 有効/無効の状態変化に応じて起動/停止
            if old_enabled != self.enabled:
                if self.enabled:
                    self.start()
                else:
                    self.stop()
            
            logger.info("Tincture module configuration updated")
            
        except Exception as e:
            logger.error(f"Failed to update tincture configuration: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            'enabled': self.enabled,
            'running': self.running,
            'key': self.key,
            'monitor_config': self.monitor_config,
            'sensitivity': self.sensitivity,
            'stats': self.stats.copy()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """現在のステータスを取得"""
        return {
            'enabled': self.enabled,
            'running': self.running,
            'last_use_time': self.last_use_time,
            'total_uses': self.stats['total_uses']
        }
    
    def manual_use(self) -> bool:
        """手動でTinctureを使用"""
        try:
            if not self.enabled:
                logger.warning("Cannot use tincture manually: module is disabled")
                return False
            
            current_time = time.time()
            
            # 最小使用間隔のチェック
            if current_time - self.last_use_time < self.min_use_interval:
                logger.warning("Cannot use tincture manually: minimum interval not met")
                return False
            
            # キーを入力
            logger.info(f"Manual tincture use (key: {self.key})")
            self.keyboard.press_key(self.key)
            
            # 使用時刻と統計の更新
            self.last_use_time = current_time
            self.stats['total_uses'] += 1
            self.stats['last_use_timestamp'] = current_time
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to use tincture manually: {e}")
            return False
    
    def reset_stats(self) -> None:
        """統計情報をリセット"""
        self.stats = {
            'total_uses': 0,
            'successful_detections': 0,
            'failed_detections': 0,
            'last_use_timestamp': None
        }
        logger.info("Tincture statistics reset")
    
    def __del__(self):
        """デストラクタ：リソースのクリーンアップ"""
        try:
            self.stop()
        except:
            pass
"""
Tincture自動使用モジュール
Path of Exile の Tincture アイテムを自動で使用する機能
"""
import time
import threading
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from src.features.image_recognition import TinctureDetector
from src.utils.keyboard_input import KeyboardController
from src.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class TinctureModule:
    """Tincture自動使用モジュール"""
    
    def __init__(self, config: Dict[str, Any], window_manager=None):
        """
        TinctureModule の初期化
        
        Args:
            config: 設定辞書
            window_manager: ウィンドウマネージャー
        """
        # 設定の型チェック
        if not isinstance(config, dict):
            logger.error(f"TinctureModule.__init__ received non-dict config: {type(config)} - {config}")
            config = {'enabled': False}  # フォールバック設定
        
        self.config = config
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_use_time = 0
        self.window_manager = window_manager
        
        # 設定の読み込み
        self.enabled = config.get('enabled', True)
        self.key = config.get('key', '3')
        self.monitor_config = config.get('monitor_config', 'Primary')
        # 設定ファイルからデフォルト値を取得
        default_sensitivity = self._get_default_sensitivity()
        self.sensitivity = config.get('sensitivity', default_sensitivity)
        self.check_interval = config.get('check_interval', 0.1)  # 100ms
        self.min_use_interval = config.get('min_use_interval', 0.5)  # 500ms
        
        # AreaSelectorを初期化
        try:
            from src.features.area_selector import AreaSelector
            self.area_selector = AreaSelector()
        except ImportError:
            logger.warning("AreaSelector not available")
            self.area_selector = None
        
        # 単一の検出器のみ初期化（設定とAreaSelectorを渡す）
        # TinctureDetectorに全設定を渡して検出モードを適用
        full_config = {'tincture': config}
        self.detector = TinctureDetector(
            monitor_config=self.monitor_config,
            sensitivity=self.sensitivity,
            area_selector=self.area_selector,
            config=full_config
        )
        
        # キーボード制御
        self.keyboard = KeyboardController()
        
        # 統計情報
        self.stats = {
            'total_uses': 0,
            'successful_detections': 0,
            'failed_detections': 0,
            'active_detections': 0,
            'idle_detections': 0,
            'unknown_detections': 0,
            'last_use_timestamp': None
        }
        
        logger.info(f"TinctureModule initialized: enabled={self.enabled}, key={self.key}, active_detection={self.detector.template_active is not None}")
    
    
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
        """Active状態を考慮したTincture管理ループ"""
        logger.info("Tincture monitoring started (with Active state detection)")
        logger.debug(f"Detection interval: {self.check_interval}s, Min use interval: {self.min_use_interval}s")
        
        while self.running:
            try:
                # 現在の状態を取得
                current_state = self.detector.get_tincture_state()
                logger.debug(f"Current Tincture state: {current_state}")
                
                if current_state == "ACTIVE":
                    # Active状態の場合は何もしない（維持する）
                    logger.debug("Tincture is ACTIVE - maintaining state")
                    self.stats['active_detections'] += 1
                    
                elif current_state == "IDLE":
                    # Idle状態でかつ最小使用間隔を満たしている場合のみ使用
                    current_time = time.time()
                    time_since_last_use = current_time - self.last_use_time
                    
                    if time_since_last_use >= self.min_use_interval:
                        logger.info(f"Tincture IDLE detected! Using tincture (key: {self.key})")
                        success = self._use_tincture()
                        
                        if success:
                            # 統計を更新
                            self.last_use_time = current_time
                            self.stats['total_uses'] += 1
                            self.stats['successful_detections'] += 1
                            self.stats['idle_detections'] += 1
                            self.stats['last_use_timestamp'] = current_time
                            
                            logger.info(f"Tincture used successfully. Total uses: {self.stats['total_uses']}")
                        
                        # 使用後は少し長めに待機（Active状態になるまで）
                        logger.debug("Waiting 2 seconds for tincture to become active...")
                        time.sleep(2.0)  # Active状態への移行待ち
                    else:
                        logger.debug(f"Skipping use - minimum interval not met ({time_since_last_use:.2f}s < {self.min_use_interval}s)")
                        self.stats['idle_detections'] += 1
                        
                elif current_state == "UNKNOWN":
                    # UNKNOWN状態
                    self.stats['failed_detections'] += 1
                    self.stats['unknown_detections'] += 1
                    logger.debug("Tincture state unknown")
                    
                else:
                    # ERROR状態など
                    self.stats['failed_detections'] += 1
                    logger.debug(f"Tincture state error or unexpected: {current_state}")
                
                # 検出間隔
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in tincture loop: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
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
            # 現在の感度をデフォルトとして使用（設定ファイルからの初期値を保持）
            old_sensitivity = self.sensitivity
            self.sensitivity = new_config.get('sensitivity', self.sensitivity)
            self.check_interval = new_config.get('check_interval', 0.1)
            self.min_use_interval = new_config.get('min_use_interval', 0.5)
            
            # 検出器の感度を更新
            if old_sensitivity != self.sensitivity:
                logger.info(f"TinctureModule sensitivity updated: {old_sensitivity:.3f} -> {self.sensitivity:.3f}")
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
    
    def update_detection_area(self, new_area_selector):
        """検出エリアを動的に更新"""
        try:
            self.area_selector = new_area_selector
            
            # TinctureDetectorのarea_selectorを更新
            if self.detector:
                self.detector.area_selector = new_area_selector
                logger.info("Detection area updated successfully in TinctureModule")
            else:
                logger.warning("TinctureDetector not available for area update")
                
        except Exception as e:
            logger.error(f"Error updating detection area: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            'enabled': self.enabled,
            'running': self.running,
            'key': self.key,
            'monitor_config': self.monitor_config,
            'sensitivity': self.sensitivity,
            'stats': {
                **self.stats,
                'active_detections': self.stats.get('active_detections', 0),
                'idle_detections': self.stats.get('idle_detections', 0),
                'unknown_detections': self.stats.get('unknown_detections', 0)
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """現在のステータスを取得"""
        # 現在の状態を取得（ステータスチェック時のみ）
        current_state = "N/A"
        try:
            if self.running and self.detector:
                current_state = self.detector.get_tincture_state()
        except Exception as e:
            logger.debug(f"Failed to get current state in get_status: {e}")
        
        return {
            'enabled': self.enabled,
            'running': self.running,
            'current_state': current_state,
            'last_use_time': self.last_use_time,
            'total_uses': self.stats['total_uses'],
            'active_detections': self.stats.get('active_detections', 0),
            'idle_detections': self.stats.get('idle_detections', 0),
            'unknown_detections': self.stats.get('unknown_detections', 0)
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
            success = self._use_tincture()
            
            if success:
                # 使用時刻と統計の更新
                self.last_use_time = current_time
                self.stats['total_uses'] += 1
                self.stats['last_use_timestamp'] = current_time
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to use tincture manually: {e}")
            return False
    
    def reset_stats(self) -> None:
        """統計情報をリセット"""
        self.stats = {
            'total_uses': 0,
            'successful_detections': 0,
            'failed_detections': 0,
            'active_detections': 0,
            'idle_detections': 0,
            'unknown_detections': 0,
            'last_use_timestamp': None
        }
        logger.info("Tincture statistics reset")
    
    def _get_default_sensitivity(self) -> float:
        """設定ファイルからデフォルト感度を取得"""
        try:
            config_manager = ConfigManager()
            default_config = config_manager.load_config()
            return default_config.get('tincture', {}).get('sensitivity', 0.7)
        except Exception as e:
            logger.warning(f"Failed to load default sensitivity from config: {e}")
            return 0.7  # フォールバック値
    
    def _use_tincture(self) -> bool:
        """Tinctureを使用（POEウィンドウアクティブチェック付き）"""
        # Path of Exileがアクティブでない場合はスキップ
        if hasattr(self, 'window_manager') and self.window_manager:
            try:
                if not self.window_manager.is_poe_active():
                    logger.debug("Path of Exile is not active, skipping tincture use")
                    return False
            except Exception as e:
                logger.debug(f"Error checking POE window status: {e}")
                # エラーが発生してもキー入力を継続
        
        # POEがアクティブの場合のみキー入力を実行
        try:
            self.keyboard.press_key(self.key)
            logger.debug(f"Tincture used (key: {self.key})")
            return True
        except Exception as e:
            logger.error(f"Error using tincture: {e}")
            return False
    
    def set_window_manager(self, window_manager):
        """WindowManagerの参照を設定"""
        self.window_manager = window_manager
        logger.debug("TinctureModule: WindowManager reference set")
    
    def __del__(self):
        """デストラクタ：リソースのクリーンアップ"""
        try:
            self.stop()
        except:
            pass
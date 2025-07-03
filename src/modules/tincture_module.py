"""
Tincture自動使用モジュール
Path of Exile の Tincture アイテムを自動で使用する機能
"""
import time
import threading
import logging
from enum import Enum
from typing import Dict, Any, Optional
from pathlib import Path

from ..features.image_recognition import TinctureDetector
from ..utils.keyboard_input import KeyboardController
from ..core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class TinctureState(Enum):
    """Tincture の状態を表す列挙型"""
    IDLE = "idle"           # 使用可能状態
    ACTIVE = "active"       # 使用中状態
    COOLDOWN = "cooldown"   # クールダウン中状態
    UNKNOWN = "unknown"     # 不明状態

class TinctureModule:
    """Tincture自動使用モジュール"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        TinctureModule の初期化
        
        Args:
            config: 設定辞書
        """
        self.config = config
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.current_state = TinctureState.UNKNOWN
        self.last_use_time = 0
        
        # 設定の読み込み
        self.enabled = config.get('tincture', {}).get('enabled', True)
        self.key = config.get('tincture', {}).get('key', '3')
        self.monitor_config = config.get('tincture', {}).get('monitor_config', 'Primary')
        self.sensitivity = config.get('tincture', {}).get('sensitivity', 0.7)
        self.check_interval = config.get('tincture', {}).get('check_interval', 0.1)  # 100ms
        self.min_use_interval = config.get('tincture', {}).get('min_use_interval', 0.5)  # 500ms
        
        # 各状態の検出器を初期化
        self.detectors = {}
        self._init_detectors()
        
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
    
    def _init_detectors(self) -> None:
        """各状態の検出器を初期化"""
        try:
            # 各状態用の検出器を作成
            for state in [TinctureState.IDLE, TinctureState.ACTIVE, TinctureState.COOLDOWN]:
                detector = TinctureDetector(
                    monitor_config=self.monitor_config,
                    sensitivity=self.sensitivity
                )
                # 状態に応じたテンプレートパスを設定
                detector.template_path = self._get_template_path(state)
                self.detectors[state] = detector
                
            logger.info("All tincture detectors initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize tincture detectors: {e}")
            raise
    
    def _get_template_path(self, state: TinctureState) -> str:
        """状態に応じたテンプレートパスを取得"""
        base_path = "assets/images/tincture/sap_of_the_seasons"
        
        if state == TinctureState.IDLE:
            return f"{base_path}/idle"
        elif state == TinctureState.ACTIVE:
            return f"{base_path}/active"
        elif state == TinctureState.COOLDOWN:
            return f"{base_path}/cooldown"
        else:
            return base_path
    
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
        """Tincture の状態監視と自動使用のメインループ"""
        logger.info("Tincture monitoring loop started")
        
        while self.running:
            try:
                # 現在の状態を検出
                detected_state = self._detect_state()
                
                # 状態変化の記録
                if detected_state != self.current_state:
                    logger.debug(f"Tincture state changed: {self.current_state.value} -> {detected_state.value}")
                    self.current_state = detected_state
                
                # 状態に応じた処理
                self._handle_state(detected_state)
                
                # 検出間隔の待機
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in tincture loop: {e}")
                self.stats['failed_detections'] += 1
                # エラー時は少し長めに待機
                time.sleep(self.check_interval * 2)
        
        logger.info("Tincture monitoring loop ended")
    
    def _detect_state(self) -> TinctureState:
        """現在の Tincture 状態を検出"""
        try:
            # 各状態を優先度順に検出
            detection_order = [
                TinctureState.ACTIVE,    # アクティブ状態を最優先
                TinctureState.COOLDOWN,  # クールダウン状態
                TinctureState.IDLE       # アイドル状態
            ]
            
            for state in detection_order:
                if state in self.detectors:
                    detector = self.detectors[state]
                    
                    # 状態に応じた検出メソッドを呼び出し
                    if self._detect_state_specific(detector, state):
                        self.stats['successful_detections'] += 1
                        return state
            
            # どの状態も検出されなかった場合
            logger.debug("No tincture state detected")
            return TinctureState.UNKNOWN
            
        except Exception as e:
            logger.error(f"State detection failed: {e}")
            return TinctureState.UNKNOWN
    
    def _detect_state_specific(self, detector: TinctureDetector, state: TinctureState) -> bool:
        """特定の状態の検出を実行"""
        try:
            # 状態に応じたテンプレートパターンを設定
            if state == TinctureState.COOLDOWN:
                # クールダウン状態は複数のテンプレートをチェック
                return self._detect_cooldown_state(detector)
            else:
                # その他の状態は単一テンプレートで検出
                return detector.detect_tincture_icon()
                
        except Exception as e:
            logger.error(f"Failed to detect {state.value} state: {e}")
            return False
    
    def _detect_cooldown_state(self, detector: TinctureDetector) -> bool:
        """クールダウン状態の検出（複数のテンプレートパターン）"""
        try:
            # クールダウンのパーセンテージテンプレートを順番にチェック
            cooldown_patterns = [
                'sap_of_the_seasons_cooldown_p000.png',
                'sap_of_the_seasons_cooldown_p050.png',
                'sap_of_the_seasons_cooldown_p100.png'
            ]
            
            for pattern in cooldown_patterns:
                # 各パターンで検出を試行
                if detector.detect_tincture_icon():
                    logger.debug(f"Detected cooldown pattern: {pattern}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Cooldown detection failed: {e}")
            return False
    
    def _handle_state(self, state: TinctureState) -> None:
        """検出された状態に応じた処理を実行"""
        try:
            if state == TinctureState.IDLE:
                self._handle_idle_state()
            elif state == TinctureState.ACTIVE:
                self._handle_active_state()
            elif state == TinctureState.COOLDOWN:
                self._handle_cooldown_state()
            else:
                self._handle_unknown_state()
                
        except Exception as e:
            logger.error(f"Error handling state {state.value}: {e}")
    
    def _handle_idle_state(self) -> None:
        """アイドル状態の処理：即座にキーを入力"""
        try:
            current_time = time.time()
            
            # 最小使用間隔のチェック
            if current_time - self.last_use_time < self.min_use_interval:
                logger.debug("Skipping tincture use due to minimum interval")
                return
            
            # キーを入力
            logger.info(f"Using tincture (key: {self.key})")
            self.keyboard.press_key(self.key)
            
            # 使用時刻と統計の更新
            self.last_use_time = current_time
            self.stats['total_uses'] += 1
            self.stats['last_use_timestamp'] = current_time
            
        except Exception as e:
            logger.error(f"Failed to use tincture: {e}")
    
    def _handle_active_state(self) -> None:
        """アクティブ状態の処理：何もしない"""
        logger.debug("Tincture is active, waiting...")
    
    def _handle_cooldown_state(self) -> None:
        """クールダウン状態の処理：待機"""
        logger.debug("Tincture is in cooldown, waiting...")
    
    def _handle_unknown_state(self) -> None:
        """不明状態の処理：何もしない"""
        logger.debug("Tincture state is unknown, waiting...")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """設定を更新"""
        try:
            # 設定の更新
            old_enabled = self.enabled
            self.config = new_config
            self.enabled = new_config.get('tincture', {}).get('enabled', True)
            self.key = new_config.get('tincture', {}).get('key', '3')
            self.monitor_config = new_config.get('tincture', {}).get('monitor_config', 'Primary')
            self.sensitivity = new_config.get('tincture', {}).get('sensitivity', 0.7)
            self.check_interval = new_config.get('tincture', {}).get('check_interval', 0.1)
            self.min_use_interval = new_config.get('tincture', {}).get('min_use_interval', 0.5)
            
            # 検出器の感度を更新
            for detector in self.detectors.values():
                detector.update_sensitivity(self.sensitivity)
            
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
            'current_state': self.current_state.value,
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
            'current_state': self.current_state.value,
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
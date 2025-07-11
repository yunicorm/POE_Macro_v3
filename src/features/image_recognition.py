"""
Tincture検出用画像認識モジュール
OpenCVによるテンプレートマッチング機能
"""
import cv2
import numpy as np
import logging
from typing import Optional, Tuple, Dict
from pathlib import Path
import mss
from src.utils.resource_path import get_asset_path

logger = logging.getLogger(__name__)

class TinctureDetector:
    """Tincture アイコンの検出を行うクラス（簡略化版）"""
    
    # モニター設定
    MONITOR_CONFIGS = {
        "Primary": 0,
        "Center": 1,
        "Right": 2
    }
    
    def __init__(self, monitor_config: str = "Primary", sensitivity: float = None, area_selector=None, config=None):
        """
        TinctureDetector の初期化
        
        Args:
            monitor_config: モニター設定 ("Primary", "Center", "Right")
            sensitivity: 検出感度 (0.5-1.0)
            area_selector: AreaSelectorインスタンス（オプション）
            config: 設定辞書（検出モード設定含む）
        """
        self.monitor_config = monitor_config
        self.area_selector = area_selector
        self.config = config or {}
        
        # 感度の設定（設定ファイルから取得またはデフォルト値）
        if sensitivity is None:
            # 設定ファイルから感度を取得
            default_sensitivity = self._get_default_sensitivity()
            self.sensitivity = max(0.5, min(1.0, default_sensitivity))
        else:
            self.sensitivity = max(0.5, min(1.0, sensitivity))
        
        # 検出モードの設定（詳細ログ付き）
        tincture_config = self.config.get('tincture', {})
        self.detection_mode = tincture_config.get('detection_mode', 'full_flask_area')
        
        logger.info(f"[INIT] TinctureDetector初期化開始")
        logger.info(f"[INIT] 設定された検出モード: {self.detection_mode}")
        logger.info(f"[INIT] 検出感度: {self.sensitivity}")
        logger.info(f"[INIT] モニター設定: {monitor_config}")
        
        # 設定構造のデバッグ出力
        if tincture_config:
            logger.debug(f"[INIT] Tincture設定内容: {tincture_config}")
        else:
            logger.warning(f"[INIT] Tincture設定が見つかりません。デフォルト値を使用します")
        
        # 手動検出エリアの設定
        self.manual_detection_area = None
        if self.detection_mode == 'manual':
            manual_area = tincture_config.get('detection_area', {})
            if manual_area:
                self.manual_detection_area = {
                    'top': manual_area.get('y', 1133),
                    'left': manual_area.get('x', 1680),
                    'width': manual_area.get('width', 80),
                    'height': manual_area.get('height', 120)
                }
                logger.info(f"[INIT] 手動検出エリアを設定: X={self.manual_detection_area['left']}, Y={self.manual_detection_area['top']}, W={self.manual_detection_area['width']}, H={self.manual_detection_area['height']}")
            else:
                logger.warning(f"[INIT] 手動モードですが検出エリア設定が見つかりません")
        
        # モニター設定の検証
        if monitor_config not in self.MONITOR_CONFIGS:
            raise ValueError(f"Invalid monitor_config: {monitor_config}. Must be one of {list(self.MONITOR_CONFIGS.keys())}")
        
        # AreaSelectorを初期化（提供されていない場合）
        if self.area_selector is None:
            try:
                from src.features.area_selector import AreaSelector
                self.area_selector = AreaSelector()
                logger.info(f"[INIT] AreaSelectorを新規作成しました")
            except ImportError:
                logger.warning("AreaSelector not available, using fallback detection area")
                self.area_selector = None
        else:
            logger.info(f"[INIT] 既存のAreaSelectorを使用します")
        
        # 初期化時の検出エリア情報をログ出力
        if self.area_selector:
            try:
                if self.detection_mode == 'full_flask_area':
                    area_info = self.area_selector.get_full_flask_area_for_tincture()
                    logger.info(f"[INIT] フラスコエリア全体検出: X={area_info['x']}, Y={area_info['y']}, W={area_info['width']}, H={area_info['height']}")
            except Exception as e:
                logger.warning(f"[INIT] 検出エリア情報の取得に失敗: {e}")
        
        # テンプレート画像を読み込み（Idle + Active状態）
        self.template_idle_path = Path(get_asset_path("images/tincture/sap_of_the_seasons/idle/sap_of_the_seasons_idle.png"))
        self.template_active_path = Path(get_asset_path("images/tincture/sap_of_the_seasons/active/sap_of_the_seasons_active.png"))
        
        self.template_idle = None
        self.template_active = None
        self._load_templates()
        
        logger.info(f"TinctureDetector initialized: monitor={monitor_config}, sensitivity={sensitivity}, mode={self.detection_mode}")
    
    def _load_templates(self):
        """Idle状態とActive状態のテンプレート画像を読み込み"""
        try:
            # Idle状態テンプレート
            if not self.template_idle_path.exists():
                raise FileNotFoundError(f"Idle template not found: {self.template_idle_path}")
            
            self.template_idle = cv2.imread(str(self.template_idle_path))
            if self.template_idle is None:
                raise ValueError(f"Failed to load idle template: {self.template_idle_path}")
                
            logger.info(f"Loaded idle template: {self.template_idle_path}")
            
            # Active状態テンプレート
            if self.template_active_path.exists():
                self.template_active = cv2.imread(str(self.template_active_path))
                if self.template_active is not None:
                    logger.info(f"Loaded active template: {self.template_active_path}")
                else:
                    logger.warning(f"Active template file exists but failed to load: {self.template_active_path}")
            else:
                logger.warning(f"Active template not found: {self.template_active_path}")
                logger.warning("Active state detection will be disabled")
            
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            raise
    
    def _capture_screen(self) -> np.ndarray:
        """画面をキャプチャ（検出エリア限定）"""
        try:
            # 検出モードに応じてエリアを決定
            if self.detection_mode == 'manual' and self.manual_detection_area:
                # 手動設定エリアを使用
                capture_area = self.manual_detection_area.copy()
                logger.info(f"[DETECTION] モード: manual - 手動設定エリア使用")
                logger.info(f"[DETECTION] エリア座標: X={capture_area['left']}, Y={capture_area['top']}, W={capture_area['width']}, H={capture_area['height']}")
                logger.debug(f"Manual detection area raw data: {capture_area}")
            elif self.detection_mode == 'full_flask_area' and self.area_selector:
                # フラスコエリア全体を使用（新しいモード）
                try:
                    full_area = self.area_selector.get_full_flask_area_for_tincture()
                    capture_area = {
                        'top': full_area['y'],
                        'left': full_area['x'],
                        'width': full_area['width'],
                        'height': full_area['height']
                    }
                    logger.info(f"[DETECTION] モード: full_flask_area - フラスコエリア全体使用")
                    logger.info(f"[DETECTION] エリア座標: X={full_area['x']}, Y={full_area['y']}, W={full_area['width']}, H={full_area['height']}")
                    logger.info(f"[DETECTION] 検出範囲面積: {full_area['width'] * full_area['height']}px^2")
                    logger.debug(f"Full flask area raw data: {full_area}")
                except Exception as e:
                    logger.warning(f"Failed to get full flask area, using fallback: {e}")
                    capture_area = self._get_fallback_area()
                    logger.info(f"[DETECTION] モード: fallback - フォールバックエリア使用")
            elif self.area_selector:
                # AreaSelectorから検出エリアを取得（従来の3番スロット方法）
                try:
                    # Legacy mode removed - fallback to full flask area
                    tincture_area = self.area_selector.get_full_flask_area_for_tincture()
                    capture_area = {
                        'top': tincture_area['y'],
                        'left': tincture_area['x'],
                        'width': tincture_area['width'],
                        'height': tincture_area['height']
                    }
                    logger.info(f"[DETECTION] モード: auto_slot3 - 3番スロット自動計算")
                    logger.info(f"[DETECTION] エリア座標: X={tincture_area['x']}, Y={tincture_area['y']}, W={tincture_area['width']}, H={tincture_area['height']}")
                    logger.debug(f"3rd slot area raw data: {tincture_area}")
                except Exception as e:
                    logger.warning(f"Failed to get configured area, using fallback: {e}")
                    capture_area = self._get_fallback_area()
                    logger.info(f"[DETECTION] モード: fallback - フォールバックエリア使用")
            else:
                capture_area = self._get_fallback_area()
                logger.info(f"[DETECTION] モード: fallback - AreaSelector未設定")
            
            # スクリーンショットを撮影（新しいmssインスタンスを使用）
            with mss.mss() as sct:
                screenshot = sct.grab(capture_area)
                
                # numpy配列に変換
                img_array = np.array(screenshot)
                
                # BGRに変換（OpenCV形式）
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
                
                return img_bgr
            
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            raise
    
    def _get_fallback_area(self) -> Dict[str, int]:
        """フォールバック用の検出エリアを取得"""
        try:
            # モニター情報を取得（新しいmssインスタンスを使用）
            with mss.mss() as sct:
                # モニターを選択
                monitor_index = self.MONITOR_CONFIGS[self.monitor_config]
                if monitor_index >= len(sct.monitors) - 1:
                    monitor_index = 0  # プライマリモニターにフォールバック
                    logger.warning(f"指定されたモニター({self.monitor_config})が見つかりません。プライマリモニターを使用します")
                
                monitor = sct.monitors[monitor_index + 1]  # monitors[0]は全画面
                
                # 画面右上部分のみキャプチャ（Tinctureアイコンの位置）
                width = monitor['width']
                height = monitor['height']
                
                # 右上の約1/4エリアをキャプチャ（従来の方式）
                fallback_area = {
                    'top': monitor['top'],
                    'left': monitor['left'] + width // 2,
                    'width': width // 2,
                    'height': height // 4
                }
                
                logger.info(f"[FALLBACK] モニター解像度: {width}x{height}")
                logger.info(f"[FALLBACK] エリア座標: X={fallback_area['left']}, Y={fallback_area['top']}, W={fallback_area['width']}, H={fallback_area['height']}")
                logger.info(f"[FALLBACK] 検出範囲面積: {fallback_area['width'] * fallback_area['height']}px^2")
                
                return fallback_area
            
        except Exception as e:
            logger.error(f"Failed to get fallback area: {e}")
            # 最後の手段として固定値を返す
            emergency_area = {
                'top': 0,
                'left': 960,  # 1920x1080の右半分
                'width': 960,
                'height': 270
            }
            logger.warning(f"[EMERGENCY] 緊急フォールバック: X={emergency_area['left']}, Y={emergency_area['top']}, W={emergency_area['width']}, H={emergency_area['height']}")
            return emergency_area
    
    def detect_tincture_icon(self) -> bool:
        """Tincture Idle状態を検出（下位互換性のため）"""
        return self.detect_tincture_idle()
    
    def detect_tincture_idle(self) -> bool:
        """Tincture Idle状態を検出"""
        try:
            logger.debug("Starting Tincture IDLE detection...")
            
            # 現在の検出エリア設定を出力
            if self.area_selector:
                try:
                    # Legacy mode removed - fallback to full flask area
                    tincture_area = self.area_selector.get_full_flask_area_for_tincture()
                    logger.debug(f"Current detection area: X:{tincture_area['x']}, Y:{tincture_area['y']}, W:{tincture_area['width']}, H:{tincture_area['height']}")
                except Exception as e:
                    logger.warning(f"Failed to get current detection area: {e}")
            else:
                logger.debug("Using fallback detection area (no area_selector)")
            
            # テンプレートの検証
            if self.template_idle is None:
                logger.error("Idle template not loaded!")
                return False
            
            logger.debug(f"Idle template shape: {self.template_idle.shape}")
            
            # 画面をキャプチャ
            logger.debug("Capturing screen...")
            screen = self._capture_screen()
            logger.debug(f"Screen captured, shape: {screen.shape}")
            
            # テンプレートマッチング
            logger.debug(f"Current sensitivity setting: {self.sensitivity}")
            logger.debug(f"Running idle template matching with sensitivity: {self.sensitivity}")
            result = cv2.matchTemplate(screen, self.template_idle, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            logger.debug(f"Idle template matching result: min={min_val:.3f}, max={max_val:.3f}, location={max_loc}")
            
            # 検出判定
            detected = max_val >= self.sensitivity
            comparison_symbol = '>=' if detected else '<'
            logger.debug(f"Tincture IDLE {'detected' if detected else 'NOT detected'} (confidence: {max_val:.3f} {comparison_symbol} {self.sensitivity})")
            
            if detected:
                logger.info(f"Tincture IDLE detected! (confidence: {max_val:.3f} >= {self.sensitivity})")
            else:
                logger.debug(f"Tincture IDLE NOT detected (confidence: {max_val:.3f} < {self.sensitivity})")
            
            return detected
            
        except Exception as e:
            logger.error(f"Idle detection failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def detect_tincture_active(self) -> bool:
        """Tincture Active状態を検出"""
        try:
            logger.debug("Starting Tincture ACTIVE detection...")
            
            # Active テンプレートの検証
            if self.template_active is None:
                logger.debug("Active template not loaded - Active detection disabled")
                return False
            
            logger.debug(f"Active template shape: {self.template_active.shape}")
            
            # 画面をキャプチャ
            logger.debug("Capturing screen for active detection...")
            screen = self._capture_screen()
            logger.debug(f"Screen captured, shape: {screen.shape}")
            
            # テンプレートマッチング
            logger.debug(f"Running active template matching with sensitivity: {self.sensitivity}")
            result = cv2.matchTemplate(screen, self.template_active, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            logger.debug(f"Active template matching result: min={min_val:.3f}, max={max_val:.3f}, location={max_loc}")
            
            # 検出判定
            detected = max_val >= self.sensitivity
            comparison_symbol = '>=' if detected else '<'
            logger.debug(f"Tincture ACTIVE {'detected' if detected else 'NOT detected'} (confidence: {max_val:.3f} {comparison_symbol} {self.sensitivity})")
            
            if detected:
                logger.info(f"Tincture ACTIVE detected! (confidence: {max_val:.3f} >= {self.sensitivity})")
            else:
                logger.debug(f"Tincture ACTIVE NOT detected (confidence: {max_val:.3f} < {self.sensitivity})")
            
            return detected
            
        except Exception as e:
            logger.error(f"Active detection failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def get_tincture_state(self) -> str:
        """Tincture の現在の状態を取得（詳細ログ付き）"""
        try:
            logger.debug("=== Starting Tincture State Detection ===")
            
            # テンプレートの状態を確認
            active_available = self.template_active is not None
            idle_available = self.template_idle is not None
            
            logger.debug(f"Template availability: Active={active_available}, Idle={idle_available}")
            
            if not idle_available:
                logger.error("Idle template not available - cannot perform detection")
                return "ERROR"
            
            # Active状態をチェック（優先）
            if active_available:
                logger.debug("Checking ACTIVE state first (priority detection)...")
                active_detected = self.detect_tincture_active()
                if active_detected:
                    logger.info("Tincture state determined: ACTIVE (priority check successful)")
                    return "ACTIVE"
                else:
                    logger.debug("ACTIVE state not detected, proceeding to IDLE check")
            else:
                logger.warning("Active template not available - skipping ACTIVE detection")
            
            # Idle状態をチェック
            logger.debug("Checking IDLE state...")
            idle_detected = self.detect_tincture_idle()
            if idle_detected:
                logger.info("Tincture state determined: IDLE")
                return "IDLE"
            else:
                logger.debug("IDLE state not detected")
            
            # どちらも検出されない場合
            logger.debug("Tincture state determined: UNKNOWN (no templates matched)")
            return "UNKNOWN"
            
        except Exception as e:
            logger.error(f"Error determining tincture state: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "ERROR"
    
    def get_detection_area_info(self) -> Dict[str, any]:
        """検出エリアの情報を取得（デバッグ用）"""
        try:
            info = {
                'monitor_config': self.monitor_config,
                'template_path': str(self.template_path),
                'sensitivity': self.sensitivity,
                'area_selector_available': self.area_selector is not None
            }
            
            # AreaSelectorから情報を取得
            if self.area_selector:
                try:
                    flask_area = self.area_selector.get_flask_area()
                    # Legacy mode removed - fallback to full flask area
                    tincture_area = self.area_selector.get_full_flask_area_for_tincture()
                    
                    info.update({
                        'flask_area': flask_area,
                        'tincture_detection_area': tincture_area,
                        'detection_method': 'configured_area'
                    })
                except Exception as e:
                    logger.warning(f"Failed to get area selector info: {e}")
                    info.update({
                        'detection_method': 'fallback_area',
                        'fallback_reason': str(e)
                    })
            else:
                # フォールバック情報を取得
                fallback_area = self._get_fallback_area()
                info.update({
                    'detection_area': fallback_area,
                    'detection_method': 'fallback_area'
                })
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get detection area info: {e}")
            return {}
    
    def update_sensitivity(self, new_sensitivity: float) -> None:
        """検出感度を更新"""
        self.sensitivity = max(0.5, min(1.0, new_sensitivity))
        logger.info(f"Sensitivity updated to: {self.sensitivity}")
    
    def update_manual_detection_area(self, area_dict: dict):
        """手動検出エリアを更新"""
        try:
            if self.detection_mode == 'manual':
                self.manual_detection_area = {
                    'top': area_dict.get('y', area_dict.get('top', 1133)),
                    'left': area_dict.get('x', area_dict.get('left', 1680)),
                    'width': area_dict.get('width', 80),
                    'height': area_dict.get('height', 120)
                }
                logger.info(f"Updated manual detection area: {self.manual_detection_area}")
            else:
                logger.warning("Cannot update manual detection area: detection mode is not manual")
        except Exception as e:
            logger.error(f"Failed to update manual detection area: {e}")
            raise
    
    def set_detection_mode(self, mode: str, area_dict: dict = None):
        """検出モードを設定"""
        try:
            if mode in ['manual', 'auto_slot3', 'full_flask_area']:
                self.detection_mode = mode
                if mode == 'manual' and area_dict:
                    self.update_manual_detection_area(area_dict)
                logger.info(f"Detection mode set to: {mode}")
            else:
                raise ValueError(f"Invalid detection mode: {mode}. Supported modes: manual, auto_slot3, full_flask_area")
        except Exception as e:
            logger.error(f"Failed to set detection mode: {e}")
            raise
    
    def reload_templates(self) -> None:
        """テンプレートを再読み込み"""
        self._load_templates()
        logger.info("Templates reloaded")
    
    def reload_template(self) -> None:
        """テンプレートを再読み込み（下位互換性のため）"""
        self.reload_templates()
    
    def update_sensitivity(self, new_sensitivity: float):
        """感度を動的に更新"""
        old_sensitivity = self.sensitivity
        self.sensitivity = max(0.5, min(1.0, new_sensitivity))
        logger.info(f"TinctureDetector sensitivity updated: {old_sensitivity:.3f} -> {self.sensitivity:.3f}")
        
        # 設定辞書も更新（存在する場合）
        if self.config and 'tincture' in self.config:
            self.config['tincture']['sensitivity'] = self.sensitivity
            logger.debug("Config dictionary updated with new sensitivity")
    
    def _get_default_sensitivity(self) -> float:
        """設定ファイルからデフォルト感度を取得"""
        try:
            from src.core.config_manager import ConfigManager
            config_manager = ConfigManager()
            default_config = config_manager.load_config()
            return default_config.get('tincture', {}).get('sensitivity', 0.7)
        except Exception as e:
            logger.warning(f"Failed to load default sensitivity from config: {e}")
            return 0.7  # フォールバック値
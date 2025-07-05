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

# Grace Period機能用インポート
try:
    from pynput import mouse, keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    mouse, keyboard = None, None

logger = logging.getLogger(__name__)

class LogMonitor:
    """POEログファイルを監視してマクロを自動制御するクラス"""
    
    def __init__(self, config: Dict[str, Any], macro_controller=None, full_config: Dict[str, Any] = None):
        self.config = config
        self.macro_controller = macro_controller
        self.full_config = full_config or {}
        
        # ログファイルパス（Steam版優先で自動検出）
        self.log_file_path = Path(config.get('log_path', self._find_client_log_path()))
        
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
        
        # ログパターン（実際のClient.txtの形式に合わせて修正）
        self.area_enter_pattern = re.compile(
            r'.*You have entered (.+)\.$', 
            re.IGNORECASE
        )
        self.area_exit_pattern = re.compile(
            r'.*You have left (.+)\.$', 
            re.IGNORECASE
        )
        
        # 安全エリア（マクロを自動ONにしない）リスト
        self.safe_areas = {
            # Act拠点（実際のエリア名）
            "lioneye's watch",  # Act1 & Act6
            "the forest encampment",  # Act2
            "the sarn encampment",  # Act3 & Act8
            "highgate",  # Act4 & Act9
            "overseer's tower",  # Act5
            "the bridge encampment",  # Act7
            "oriath docks",  # Act10
            
            # エンドゲーム拠点
            "karui shore",
            "kingsmarch",
        }
        
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
        
        # Grace Period設定（全体設定から取得）
        self.grace_period_config = self.full_config.get('grace_period', {})
        self.grace_period_enabled = self.grace_period_config.get('enabled', False)
        self.wait_for_input = self.grace_period_config.get('wait_for_input', True)
        self.trigger_inputs = self.grace_period_config.get('trigger_inputs', ['mouse_left', 'mouse_right', 'mouse_middle', 'q'])
        
        # Grace Period設定デバッグログ
        logger.info(f"Grace Period settings: enabled={self.grace_period_enabled}, wait_for_input={self.wait_for_input}")
        logger.info(f"Grace Period trigger inputs: {self.trigger_inputs}")
        logger.info(f"pynput available: {PYNPUT_AVAILABLE}")
        
        # Grace Period状態管理
        self.grace_period_active = False
        self.input_listeners = []
        self.current_area_needs_grace = False
        
    def _find_client_log_path(self) -> str:
        """POE Client.txtファイルのパスを自動検出"""
        # 検索対象のパス（Steam版優先）
        potential_paths = [
            r'C:\Program Files (x86)\Steam\steamapps\common\Path of Exile\logs\Client.txt',
            r'C:\Program Files\Steam\steamapps\common\Path of Exile\logs\Client.txt',
            r'C:\Program Files (x86)\Grinding Gear Games\Path of Exile\logs\Client.txt',
            r'C:\Program Files\Grinding Gear Games\Path of Exile\logs\Client.txt'
        ]
        
        for path in potential_paths:
            if Path(path).exists():
                logger.info(f"Found POE Client.txt at: {path}")
                return path
                
        # どれも見つからない場合はSteam版のデフォルトを返す
        logger.warning("POE Client.txt not found, using default Steam path")
        return potential_paths[0]
        
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
        if not self._is_safe_area(self.current_area):
            # Grace Period機能が有効かチェック
            if self.grace_period_enabled and self.wait_for_input:
                # 毎回入力待機（キャッシュ機能削除）
                logger.info(f"Entering grace period - waiting for player input...")
                self.current_area_needs_grace = True
                self._start_grace_period()
            else:
                self._activate_macro()
                logger.info(f"Macro activated for area: {self.current_area}")
        else:
            logger.info(f"Safe area detected, macro not activated: {self.current_area}")
            
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
        
        # Grace Period状態をリセット
        self._stop_grace_period()
        
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
        try:
            # "You have entered [エリア名]." 形式から抽出
            match = self.area_enter_pattern.search(line)
            if match:
                return match.group(1).strip()
            
            # "You have left [エリア名]." 形式から抽出
            match = self.area_exit_pattern.search(line)
            if match:
                return match.group(1).strip()
                
        except Exception as e:
            logger.error(f"Error extracting area name: {e}")
            
        return "Unknown Area"
        
    def _is_safe_area(self, area_name: str) -> bool:
        """安全なエリア（町・隠れ家）かどうかを判定"""
        if not area_name:
            return False
            
        area_lower = area_name.lower()
        
        # Hideoutは部分一致で判定
        if "hideout" in area_lower:
            return True
            
        # その他の安全エリアは完全一致で判定
        return area_lower in self.safe_areas
                
    def _activate_macro(self):
        """マクロを有効化"""
        if self.macro_controller and not self.macro_controller.running:
            try:
                self.macro_controller.start()
                self.stats['macro_activations'] += 1
                logger.info("Macro activation initiated by log monitor")
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
        """手動でエリア入場をテスト（実際のログ形式）"""
        test_line = f'2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have entered {area_name}.'
        self._parse_log_entry(test_line)
        
    def manual_test_area_exit(self, area_name: str = "Test Area"):
        """手動でエリア退場をテスト（実際のログ形式）"""
        test_line = f'2025/07/05 06:07:24 113538687 cff945b9 [INFO Client 14940] : You have left {area_name}.'
        self._parse_log_entry(test_line)
        
    def _start_grace_period(self):
        """Grace Period（入力待機）を開始"""
        if not PYNPUT_AVAILABLE:
            logger.warning("pynput not available, Grace Period disabled")
            self._activate_macro()
            return
            
        if self.grace_period_active:
            return  # 既に待機中
            
        self.grace_period_active = True
        
        try:
            # 入力監視開始
            self._start_input_monitoring()
            logger.info("Grace Period started - waiting for player input...")
            
        except Exception as e:
            logger.error(f"Error starting Grace Period: {e}")
            self.grace_period_active = False
            self._activate_macro()  # フォールバック
    
    def _stop_grace_period(self):
        """Grace Period（入力待機）を停止"""
        if not self.grace_period_active:
            return
            
        self.grace_period_active = False
        self.current_area_needs_grace = False
        
        # 入力監視を停止
        self._stop_input_monitoring()
        
        logger.info("Grace Period stopped")
    
    def _start_input_monitoring(self):
        """入力監視を開始"""
        if not PYNPUT_AVAILABLE:
            return
            
        try:
            # マウス監視
            if any(trigger in ['mouse_left', 'mouse_right', 'mouse_middle'] for trigger in self.trigger_inputs):
                mouse_listener = mouse.Listener(
                    on_click=self._on_mouse_click
                )
                mouse_listener.start()
                self.input_listeners.append(mouse_listener)
                logger.debug("Mouse input monitoring started")
            
            # キーボード監視
            keyboard_triggers = [trigger for trigger in self.trigger_inputs if trigger not in ['mouse_left', 'mouse_right', 'mouse_middle']]
            if keyboard_triggers:
                keyboard_listener = keyboard.Listener(
                    on_press=self._on_key_press
                )
                keyboard_listener.start()
                self.input_listeners.append(keyboard_listener)
                logger.debug(f"Keyboard input monitoring started for keys: {keyboard_triggers}")
                
        except Exception as e:
            logger.error(f"Error starting input monitoring: {e}")
    
    def _stop_input_monitoring(self):
        """入力監視を停止"""
        for listener in self.input_listeners:
            try:
                listener.stop()
            except Exception as e:
                logger.error(f"Error stopping input listener: {e}")
                
        self.input_listeners.clear()
        logger.debug("Input monitoring stopped")
    
    def _on_mouse_click(self, x, y, button, pressed):
        """マウスクリック時の処理"""
        if not pressed or not self.grace_period_active:
            return
            
        try:
            button_name = button.name if hasattr(button, 'name') else str(button)
            input_type = f"mouse_{button_name}"
            
            if input_type in self.trigger_inputs:
                self._on_grace_period_input(input_type)
                
        except Exception as e:
            logger.error(f"Error handling mouse click: {e}")
    
    def _on_key_press(self, key):
        """キー押下時の処理"""
        if not self.grace_period_active:
            return
            
        try:
            # キーの文字列表現を取得
            if hasattr(key, 'char') and key.char:
                key_str = key.char.lower()
            elif hasattr(key, 'name'):
                key_str = key.name.lower()
            else:
                key_str = str(key).lower()
            
            if key_str in self.trigger_inputs:
                self._on_grace_period_input(key_str)
                
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
    
    def _on_grace_period_input(self, input_type: str):
        """Grace Period中の入力検知時の処理"""
        if not self.grace_period_active:
            return
            
        logger.info(f"Player input detected ({input_type}) - starting macro")
        
        # Grace Period終了
        self._stop_grace_period()
        
        # マクロ開始
        self._activate_macro()
    
    def manual_test_grace_period(self):
        """Grace Period機能の手動テスト"""
        logger.info("=== Grace Period Manual Test ===")
        logger.info(f"Grace Period enabled: {self.grace_period_enabled}")
        logger.info(f"Wait for input: {self.wait_for_input}")
        logger.info(f"Trigger inputs: {self.trigger_inputs}")
        logger.info(f"pynput available: {PYNPUT_AVAILABLE}")
        
        if not PYNPUT_AVAILABLE:
            logger.warning("pynput not available - Grace Period will be disabled")
            return
            
        # テスト用エリア入場
        self.manual_test_area_enter("Test Combat Area")
        
        if self.grace_period_active:
            logger.info("Grace Period is active - waiting for input...")
            logger.info(f"Trigger any of these inputs: {self.trigger_inputs}")
        else:
            logger.info("Grace Period not activated (check configuration)")
    
    def test_safe_area_detection(self):
        """安全エリア検出のテスト"""
        test_areas = [
            "Lioneye's Watch",  # 安全エリア
            "The Sarn Encampment",  # 安全エリア
            "Highgate",  # 安全エリア
            "My Hideout",  # 安全エリア（Hideout）
            "The Twilight Strand",  # 通常エリア
            "Aspirants' Plaza",  # 通常エリア
        ]
        
        logger.info("Testing safe area detection:")
        for area in test_areas:
            is_safe = self._is_safe_area(area)
            logger.info(f"  {area}: {'SAFE' if is_safe else 'NORMAL'}")
            
        return test_areas
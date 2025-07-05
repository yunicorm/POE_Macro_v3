"""
Flask timer manager for independent flask timers
"""
import time
import threading
import logging
from typing import Dict, Optional, Callable

logger = logging.getLogger(__name__)

class FlaskTimer:
    """個別のフラスコタイマー"""
    
    def __init__(self, slot_num: int, key: str, duration_ms: int, 
                 use_callback: Callable, use_when_full: bool = False):
        """
        初期化
        
        Args:
            slot_num: スロット番号
            key: 使用キー
            duration_ms: 持続時間（ミリ秒）
            use_callback: 使用時のコールバック関数
            use_when_full: チャージフル時のみ使用するか
        """
        self.slot_num = slot_num
        self.key = key
        self.duration_ms = duration_ms
        self.use_callback = use_callback
        self.use_when_full = use_when_full
        
        self.last_use_time = 0
        self.is_running = False
        self.timer_thread = None
        
        # 統計情報
        self.total_uses = 0
        self.total_skips = 0  # チャージフル待ちでスキップした回数
    
    def start(self):
        """タイマーを開始"""
        if self.is_running:
            return
        
        self.is_running = True
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        logger.info(f"Flask timer started for slot {self.slot_num} (key: {self.key})")
    
    def stop(self):
        """タイマーを停止"""
        self.is_running = False
        if self.timer_thread:
            self.timer_thread.join(timeout=1.0)
        logger.info(f"Flask timer stopped for slot {self.slot_num}")
    
    def _timer_loop(self):
        """タイマーループ"""
        while self.is_running:
            try:
                current_time = time.time() * 1000  # ミリ秒
                
                # 持続時間が経過したかチェック
                if current_time - self.last_use_time >= self.duration_ms:
                    # フラスコを使用
                    if self._should_use_flask():
                        if self.use_callback:
                            self.use_callback(self.key)
                        self.last_use_time = current_time
                        self.total_uses += 1
                        logger.debug(f"Flask used: slot {self.slot_num}, key {self.key}")
                    else:
                        self.total_skips += 1
                        logger.debug(f"Flask skipped: slot {self.slot_num} (waiting for full charge)")
                
                # 100ms待機
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in flask timer loop for slot {self.slot_num}: {e}")
                time.sleep(1.0)  # エラー時は長めに待機
    
    def _should_use_flask(self) -> bool:
        """フラスコを使用すべきかどうかを判断"""
        if not self.use_when_full:
            return True
        
        # TODO: チャージフル判定の実装
        # 現在は常にTrueを返す（将来的に画像認識で判定）
        return True
    
    def force_use(self):
        """強制的にフラスコを使用"""
        if self.use_callback:
            self.use_callback(self.key)
        self.last_use_time = time.time() * 1000
        self.total_uses += 1
        logger.info(f"Flask force used: slot {self.slot_num}, key {self.key}")
    
    def reset_stats(self):
        """統計情報をリセット"""
        self.total_uses = 0
        self.total_skips = 0
        logger.info(f"Stats reset for slot {self.slot_num}")
    
    def get_stats(self) -> Dict:
        """統計情報を取得"""
        return {
            'total_uses': self.total_uses,
            'total_skips': self.total_skips,
            'last_use_time': self.last_use_time,
            'duration_ms': self.duration_ms,
            'is_running': self.is_running
        }

class FlaskTimerManager:
    """フラスコタイマー管理クラス"""
    
    def __init__(self, key_press_callback: Optional[Callable] = None):
        """
        初期化
        
        Args:
            key_press_callback: キー押下時のコールバック関数
        """
        self.key_press_callback = key_press_callback
        self.timers: Dict[int, FlaskTimer] = {}
        self.is_enabled = False
    
    def set_key_press_callback(self, callback: Callable):
        """キー押下コールバックを設定"""
        self.key_press_callback = callback
    
    def add_flask_timer(self, slot_num: int, key: str, duration_ms: int, 
                       use_when_full: bool = False):
        """
        フラスコタイマーを追加
        
        Args:
            slot_num: スロット番号
            key: 使用キー
            duration_ms: 持続時間（ミリ秒）
            use_when_full: チャージフル時のみ使用するか
        """
        # 既存のタイマーがあれば停止
        if slot_num in self.timers:
            self.remove_flask_timer(slot_num)
        
        # 新しいタイマーを作成
        timer = FlaskTimer(
            slot_num=slot_num,
            key=key,
            duration_ms=duration_ms,
            use_callback=self._use_flask,
            use_when_full=use_when_full
        )
        
        self.timers[slot_num] = timer
        
        # タイマーが有効な場合は開始
        if self.is_enabled:
            timer.start()
        
        logger.info(f"Flask timer added: slot {slot_num}, key {key}, duration {duration_ms}ms")
    
    def remove_flask_timer(self, slot_num: int):
        """
        フラスコタイマーを削除
        
        Args:
            slot_num: スロット番号
        """
        if slot_num in self.timers:
            self.timers[slot_num].stop()
            del self.timers[slot_num]
            logger.info(f"Flask timer removed: slot {slot_num}")
    
    def start_all_timers(self):
        """全てのタイマーを開始"""
        self.is_enabled = True
        for timer in self.timers.values():
            timer.start()
        logger.info(f"All flask timers started ({len(self.timers)} timers)")
    
    def stop_all_timers(self):
        """全てのタイマーを停止"""
        self.is_enabled = False
        for timer in self.timers.values():
            timer.stop()
        logger.info("All flask timers stopped")
    
    def clear_all_timers(self):
        """全てのタイマーを削除"""
        self.stop_all_timers()
        self.timers.clear()
        logger.info("All flask timers cleared")
    
    def force_use_flask(self, slot_num: int):
        """
        指定スロットのフラスコを強制使用
        
        Args:
            slot_num: スロット番号
        """
        if slot_num in self.timers:
            self.timers[slot_num].force_use()
    
    def force_use_all_flasks(self):
        """全てのフラスコを強制使用"""
        for timer in self.timers.values():
            timer.force_use()
        logger.info("All flasks force used")
    
    def reset_stats(self, slot_num: Optional[int] = None):
        """
        統計情報をリセット
        
        Args:
            slot_num: スロット番号（Noneの場合は全て）
        """
        if slot_num is not None:
            if slot_num in self.timers:
                self.timers[slot_num].reset_stats()
        else:
            for timer in self.timers.values():
                timer.reset_stats()
            logger.info("All flask stats reset")
    
    def get_stats(self, slot_num: Optional[int] = None) -> Dict:
        """
        統計情報を取得
        
        Args:
            slot_num: スロット番号（Noneの場合は全て）
            
        Returns:
            統計情報の辞書
        """
        if slot_num is not None:
            if slot_num in self.timers:
                return {f'slot_{slot_num}': self.timers[slot_num].get_stats()}
            else:
                return {}
        else:
            stats = {}
            for slot_num, timer in self.timers.items():
                stats[f'slot_{slot_num}'] = timer.get_stats()
            return stats
    
    def get_timer_count(self) -> int:
        """アクティブなタイマー数を取得"""
        return len(self.timers)
    
    def is_timer_running(self, slot_num: int) -> bool:
        """指定スロットのタイマーが動作中かチェック"""
        if slot_num in self.timers:
            return self.timers[slot_num].is_running
        return False
    
    def _use_flask(self, key: str):
        """フラスコ使用時の内部処理"""
        if self.key_press_callback:
            try:
                self.key_press_callback(key)
            except Exception as e:
                logger.error(f"Error in key press callback for key {key}: {e}")
        else:
            logger.warning(f"No key press callback set, cannot use flask key: {key}")
    
    def update_config(self, flask_config: Dict):
        """
        設定を更新
        
        Args:
            flask_config: フラスコ設定の辞書
        """
        # 現在のタイマーを停止・削除
        self.clear_all_timers()
        
        # 新しい設定でタイマーを作成
        flask_slots = flask_config.get('flask_slots', {})
        
        for slot_key, slot_config in flask_slots.items():
            if slot_key.startswith('slot_'):
                try:
                    slot_num = int(slot_key.split('_')[1])
                    
                    # Tinctureスロットはスキップ
                    if slot_config.get('is_tincture', False):
                        continue
                    
                    key = slot_config.get('key', '')
                    duration_ms = slot_config.get('duration_ms', 5000)
                    use_when_full = slot_config.get('use_when_full', False)
                    
                    if key.strip():
                        self.add_flask_timer(slot_num, key, duration_ms, use_when_full)
                    
                except (ValueError, KeyError) as e:
                    logger.error(f"Error parsing flask slot config {slot_key}: {e}")
        
        # フラスコが有効な場合はタイマーを開始
        if flask_config.get('enabled', False):
            self.start_all_timers()
        
        logger.info(f"Flask timer config updated: {self.get_timer_count()} timers loaded")
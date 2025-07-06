"""
スキル自動使用モジュール
"""
import threading
import time
import random
import logging
from typing import Dict, Any

from src.utils.keyboard_input import KeyboardController

logger = logging.getLogger(__name__)

class SkillModule:
    """スキル自動使用を制御するクラス"""
    
    def __init__(self, config: Dict[str, Any], window_manager=None):
        # 設定の型チェック
        if not isinstance(config, dict):
            logger.error(f"SkillModule.__init__ received non-dict config: {type(config)} - {config}")
            config = {'enabled': False}  # フォールバック設定
        
        self.config = config
        logger.debug(f"SkillModule initialized with config: {config}")
        logger.debug(f"Config 'enabled' value: {config.get('enabled', 'NOT FOUND')}")
        self.keyboard = KeyboardController()
        self.running = False
        self.threads = []
        self.window_manager = window_manager
        self.stats = {
            'berserk': {'count': 0, 'last_used': None},
            'molten_shell': {'count': 0, 'last_used': None},
            'order_to_me': {'count': 0, 'last_used': None}
        }
        
    def start(self):
        """スキル自動使用を高速開始"""
        logger.debug(f"SkillModule.start() - config: {self.config}")
        logger.debug(f"SkillModule.start() - enabled: {self.config.get('enabled', False)}")
        
        if self.running:
            logger.warning("Skill module already running")
            return
        
        # スキルモジュール全体が無効の場合は開始しない
        if not self.config.get('enabled', False):
            logger.info("Skill module is disabled, not starting")
            return
            
        self.running = True
        logger.info("Skill module start signal sent")
        
        # スキルごとに自動使用を開始
        for skill_name, skill_config in self.config.items():
            # 'enabled'キーや辞書でない項目をスキップ
            if skill_name == 'enabled' or not isinstance(skill_config, dict):
                continue
                
            if skill_config.get('enabled', False):
                thread = threading.Thread(
                    target=self._skill_loop,
                    args=(skill_name, skill_config),
                    daemon=True
                )
                thread.start()
                self.threads.append(thread)
                logger.info(f"Started skill loop for {skill_name}")
        
        if not self.threads:
            logger.info("No skills are enabled for automation")
    
    def stop(self):
        """スキル自動使用を即座停止"""
        self.running = False
        logger.info("Skill module stop signal sent")
        
        # 短いタイムアウトでスレッド終了を待機（高速チェックで早期終了）
        for thread in self.threads:
            thread.join(timeout=0.15)  # 1.0 -> 0.15に短縮
        self.threads.clear()
        logger.info("Skill module stopped")
    
    def update_config(self, config: Dict[str, Any]):
        """設定の更新"""
        # 設定の型チェック
        if not isinstance(config, dict):
            logger.error(f"SkillModule.update_config received non-dict config: {type(config)} - {config}")
            return
        
        self.config = config
        logger.info("Skill module configuration updated")
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return self.stats.copy()
    
    def manual_use(self, skill_name: str):
        """手動でスキルを使用"""
        if skill_name in self.config:
            key = self.config[skill_name]['key']
            self._use_skill(key, skill_name)
            logger.info(f"Manual use of {skill_name}")
    
    def _use_skill(self, key: str, skill_name: str):
        """スキルを使用（POEウィンドウアクティブチェック付き）"""
        # Path of Exileがアクティブでない場合はスキップ
        if hasattr(self, 'window_manager') and self.window_manager:
            try:
                if not self.window_manager.is_poe_active():
                    logger.debug(f"{skill_name}: Path of Exile is not active, skipping skill use")
                    return
            except Exception as e:
                logger.debug(f"{skill_name}: Error checking POE window status: {e}")
                # エラーが発生してもキー入力を継続
        
        # POEがアクティブの場合のみキー入力を実行
        try:
            self.keyboard.press_key(key)
            self.stats[skill_name]['count'] += 1
            self.stats[skill_name]['last_used'] = time.time()
            logger.debug(f"{skill_name}: Skill used (key: {key}, count: {self.stats[skill_name]['count']})")
        except Exception as e:
            logger.error(f"{skill_name}: Error using skill: {e}")
    
    def set_window_manager(self, window_manager):
        """WindowManagerの参照を設定"""
        self.window_manager = window_manager
        logger.debug("SkillModule: WindowManager reference set")
    
    def _skill_loop(self, skill_name: str, config: Dict[str, Any]):
        """個別スキルのループ処理（即座停止対応）"""
        key = config['key']
        interval = config['interval']
        
        # 初回使用
        self._use_skill(key, skill_name)
        
        while self.running:
            # ランダム遅延（アンチチート対策）
            delay = random.uniform(interval[0], interval[1])
            logger.debug(f"{skill_name}: Waiting {delay:.3f}s before next use")
            
            # より短い間隔（20ms）でチェックして即座に反応
            for _ in range(int(delay * 50)):  # 10 -> 50に変更（20ms間隔）
                if not self.running:
                    logger.debug(f"{skill_name}: Fast stop detected")
                    break
                time.sleep(0.02)  # 0.1 -> 0.02に変更（高速チェック）
            
            if self.running:
                self._use_skill(key, skill_name)
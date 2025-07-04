"""
スキル自動使用モジュール
"""
import threading
import time
import random
import logging
from typing import Dict, Any

from utils.keyboard_input import KeyboardController

logger = logging.getLogger(__name__)

class SkillModule:
    """スキル自動使用を制御するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        # 設定の型チェック
        if not isinstance(config, dict):
            logger.error(f"SkillModule.__init__ received non-dict config: {type(config)} - {config}")
            config = {'enabled': False}  # フォールバック設定
        
        self.config = config
        self.keyboard = KeyboardController()
        self.running = False
        self.threads = []
        self.stats = {
            'berserk': {'count': 0, 'last_used': None},
            'molten_shell': {'count': 0, 'last_used': None},
            'order_to_me': {'count': 0, 'last_used': None}
        }
        
    def start(self):
        """スキル自動使用を開始"""
        if self.running:
            logger.warning("Skill module already running")
            return
            
        self.running = True
        
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
    
    def stop(self):
        """スキル自動使用を停止"""
        self.running = False
        for thread in self.threads:
            thread.join(timeout=1.0)
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
            self.keyboard.press_key(key)
            self.stats[skill_name]['count'] += 1
            self.stats[skill_name]['last_used'] = time.time()
            logger.info(f"Manual use of {skill_name}")
    
    def _skill_loop(self, skill_name: str, config: Dict[str, Any]):
        """個別スキルのループ処理"""
        key = config['key']
        interval = config['interval']
        
        # 初回使用
        self.keyboard.press_key(key)
        self.stats[skill_name]['count'] += 1
        self.stats[skill_name]['last_used'] = time.time()
        logger.debug(f"{skill_name}: Initial use")
        
        while self.running:
            # ランダム遅延（アンチチート対策）
            delay = random.uniform(interval[0], interval[1])
            logger.debug(f"{skill_name}: Waiting {delay:.3f}s before next use")
            
            # 短時間間隔でチェックして停止要求に迅速に対応
            for _ in range(int(delay * 10)):
                if not self.running:
                    break
                time.sleep(0.1)
            
            if self.running:
                self.keyboard.press_key(key)
                self.stats[skill_name]['count'] += 1
                self.stats[skill_name]['last_used'] = time.time()
                logger.debug(f"{skill_name}: Used (count: {self.stats[skill_name]['count']})")
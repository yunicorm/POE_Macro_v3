# POE Macro v3.0 スキルシステム リファクタリング詳細設計書

## 概要
本ドキュメントは、POE Macro v3.0のスキルシステムを、ハードコーディングされた実装から完全に動的な管理システムへリファクタリングするための詳細設計を記述します。

## 1. システムアーキテクチャ

### 1.1 現在のアーキテクチャ（問題点）
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ default_config  │    │  SkillModule    │    │   SkillsTab     │
│    .yaml        │───▶│ (Hardcoded)     │◀───│ (Limited GUI)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Three Fixed     │
                       │ Threads         │
                       └─────────────────┘
```

**問題点:**
- スキル名がハードコーディング（berserk, molten_shell, order_to_me）
- 新規スキル追加にコード変更が必要
- GUI側での個別スキル管理不可

### 1.2 新しいアーキテクチャ
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Enhanced YAML   │    │  SkillManager   │    │ Dynamic GUI     │
│ Configuration   │───▶│ (Central Hub)   │◀───│ (Full Control)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                     │                       │
         ▼                     ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ SkillConfig     │    │ DynamicSkill    │    │ SkillTableWidget│
│ (Data Model)    │    │ Thread Pool     │    │ SkillEditDialog │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ SkillValidator  │
                       │ & ErrorHandler  │
                       └─────────────────┘
```

## 2. クラス設計

### 2.1 データモデル

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

@dataclass
class SkillConfig:
    """個別スキルの設定を管理するデータクラス"""
    id: str  # 一意識別子（UUID）
    name: str  # スキル名（ユーザー定義）
    key: str  # キーバインド
    min_interval: float  # 最小間隔（秒）
    max_interval: float  # 最大間隔（秒）
    enabled: bool = True
    priority: int = 1  # 実行優先度（1が最高）
    created_at: datetime = None
    modified_at: datetime = None
    
    # 統計情報
    use_count: int = 0
    last_used: Optional[float] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
        self.modified_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """YAML保存用の辞書形式に変換"""
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key,
            'min_interval': self.min_interval,
            'max_interval': self.max_interval,
            'enabled': self.enabled,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'stats': {
                'use_count': self.use_count,
                'last_used': self.last_used
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillConfig':
        """辞書形式から復元"""
        # 統計情報の分離
        stats = data.pop('stats', {})
        
        # 日時文字列をdatetimeオブジェクトに変換
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('modified_at'), str):
            data['modified_at'] = datetime.fromisoformat(data['modified_at'])
        
        # インスタンス作成
        config = cls(**data)
        config.use_count = stats.get('use_count', 0)
        config.last_used = stats.get('last_used')
        
        return config
```

### 2.2 中央管理システム

```python
import threading
from typing import Dict, List, Optional, Callable
import logging

class SkillManager:
    """すべてのスキルを管理する中央コントローラー"""
    
    def __init__(self, config_manager, window_manager=None):
        self.config_manager = config_manager
        self.window_manager = window_manager
        self.keyboard = KeyboardController()
        
        # スキル設定の管理
        self.skills: Dict[str, SkillConfig] = {}
        self.skill_threads: Dict[str, DynamicSkillThread] = {}
        
        # 状態管理
        self.running = False
        self._lock = threading.RLock()
        
        # イベントコールバック
        self.on_skill_added: Optional[Callable] = None
        self.on_skill_removed: Optional[Callable] = None
        self.on_skill_updated: Optional[Callable] = None
        self.on_skill_used: Optional[Callable] = None
        
        # バリデータ
        self.validator = SkillValidator()
        
        # ロガー
        self.logger = logging.getLogger(__name__)
        
        # 設定の読み込み
        self.load_skills()
    
    def load_skills(self):
        """設定ファイルからスキルを読み込み"""
        config = self.config_manager.load_config()
        skills_config = config.get('skills', {})
        
        # 新形式の設定を読み込み
        if 'skill_list' in skills_config:
            for skill_data in skills_config['skill_list']:
                try:
                    skill = SkillConfig.from_dict(skill_data)
                    self.skills[skill.id] = skill
                except Exception as e:
                    self.logger.error(f"Failed to load skill: {e}")
        
        # 旧形式からの移行（後方互換性）
        elif any(key in skills_config for key in ['berserk', 'molten_shell', 'order_to_me']):
            self._migrate_legacy_config(skills_config)
    
    def add_skill(self, skill: SkillConfig) -> bool:
        """新しいスキルを追加"""
        with self._lock:
            # バリデーション
            errors = self.validator.validate_skill(skill, self.skills.values())
            if errors:
                self.logger.error(f"Skill validation failed: {errors}")
                return False
            
            # スキルを追加
            self.skills[skill.id] = skill
            
            # 実行中の場合はスレッドを起動
            if self.running and skill.enabled:
                self._start_skill_thread(skill)
            
            # 設定を保存
            self._save_skills()
            
            # コールバック実行
            if self.on_skill_added:
                self.on_skill_added(skill)
            
            return True
    
    def remove_skill(self, skill_id: str) -> bool:
        """スキルを削除"""
        with self._lock:
            if skill_id not in self.skills:
                return False
            
            # スレッドを停止
            if skill_id in self.skill_threads:
                self._stop_skill_thread(skill_id)
            
            # スキルを削除
            skill = self.skills.pop(skill_id)
            
            # 設定を保存
            self._save_skills()
            
            # コールバック実行
            if self.on_skill_removed:
                self.on_skill_removed(skill)
            
            return True
    
    def update_skill(self, skill_id: str, updates: Dict[str, Any]) -> bool:
        """スキルを更新"""
        with self._lock:
            if skill_id not in self.skills:
                return False
            
            skill = self.skills[skill_id]
            
            # 更新内容を適用
            for key, value in updates.items():
                if hasattr(skill, key):
                    setattr(skill, key, value)
            
            skill.modified_at = datetime.now()
            
            # バリデーション
            other_skills = [s for s in self.skills.values() if s.id != skill_id]
            errors = self.validator.validate_skill(skill, other_skills)
            if errors:
                self.logger.error(f"Skill validation failed: {errors}")
                return False
            
            # スレッドの再起動が必要か判断
            if self.running:
                if skill.enabled and skill_id not in self.skill_threads:
                    self._start_skill_thread(skill)
                elif not skill.enabled and skill_id in self.skill_threads:
                    self._stop_skill_thread(skill_id)
                elif skill_id in self.skill_threads:
                    # 設定が変更された場合は再起動
                    self._restart_skill_thread(skill)
            
            # 設定を保存
            self._save_skills()
            
            # コールバック実行
            if self.on_skill_updated:
                self.on_skill_updated(skill)
            
            return True
    
    def start(self):
        """スキル自動使用を開始"""
        with self._lock:
            if self.running:
                return
            
            self.running = True
            
            # 有効なスキルのスレッドを起動
            for skill in self.skills.values():
                if skill.enabled:
                    self._start_skill_thread(skill)
            
            self.logger.info("SkillManager started")
    
    def stop(self):
        """スキル自動使用を停止"""
        with self._lock:
            if not self.running:
                return
            
            self.running = False
            
            # すべてのスレッドを停止
            for skill_id in list(self.skill_threads.keys()):
                self._stop_skill_thread(skill_id)
            
            self.logger.info("SkillManager stopped")
    
    def get_skills(self) -> List[SkillConfig]:
        """すべてのスキルを取得（優先度順）"""
        return sorted(self.skills.values(), key=lambda s: s.priority)
    
    def get_skill(self, skill_id: str) -> Optional[SkillConfig]:
        """特定のスキルを取得"""
        return self.skills.get(skill_id)
    
    def _start_skill_thread(self, skill: SkillConfig):
        """スキル用スレッドを起動"""
        thread = DynamicSkillThread(skill, self)
        thread.start()
        self.skill_threads[skill.id] = thread
    
    def _stop_skill_thread(self, skill_id: str):
        """スキル用スレッドを停止"""
        if skill_id in self.skill_threads:
            thread = self.skill_threads.pop(skill_id)
            thread.stop()
    
    def _restart_skill_thread(self, skill: SkillConfig):
        """スキル用スレッドを再起動"""
        self._stop_skill_thread(skill.id)
        self._start_skill_thread(skill)
    
    def _save_skills(self):
        """スキル設定を保存"""
        config = self.config_manager.load_config()
        
        if 'skills' not in config:
            config['skills'] = {}
        
        # 新形式で保存
        config['skills']['enabled'] = True  # 全体の有効/無効
        config['skills']['skill_list'] = [
            skill.to_dict() for skill in self.skills.values()
        ]
        
        self.config_manager.save_config(config)
    
    def _migrate_legacy_config(self, legacy_config: Dict[str, Any]):
        """旧形式の設定を新形式に移行"""
        migration_map = {
            'berserk': {'name': 'Berserk', 'key': 'e', 'interval': [0.3, 1.0]},
            'molten_shell': {'name': 'Molten Shell', 'key': 'r', 'interval': [0.3, 1.0]},
            'order_to_me': {'name': 'Order! To Me!', 'key': 't', 'interval': [3.5, 4.0]}
        }
        
        for old_key, defaults in migration_map.items():
            if old_key in legacy_config:
                old_data = legacy_config[old_key]
                if isinstance(old_data, dict) and old_data.get('enabled', False):
                    skill = SkillConfig(
                        id=f"legacy_{old_key}",
                        name=defaults['name'],
                        key=old_data.get('key', defaults['key']),
                        min_interval=old_data.get('interval', defaults['interval'])[0],
                        max_interval=old_data.get('interval', defaults['interval'])[1],
                        enabled=old_data.get('enabled', True)
                    )
                    self.skills[skill.id] = skill
        
        # 移行完了後、新形式で保存
        self._save_skills()
        self.logger.info("Migrated legacy skill configuration to new format")
```

### 2.3 動的スレッド管理

```python
import time
import random

class DynamicSkillThread(threading.Thread):
    """動的に生成されるスキル実行スレッド"""
    
    def __init__(self, skill: SkillConfig, manager: SkillManager):
        super().__init__(daemon=True, name=f"SkillThread-{skill.name}")
        self.skill = skill
        self.manager = manager
        self._stop_event = threading.Event()
        self.logger = logging.getLogger(f"{__name__}.{skill.name}")
    
    def run(self):
        """スキル実行ループ"""
        self.logger.info(f"Skill thread started: {self.skill.name}")
        
        # 初回実行
        self._use_skill()
        
        while not self._stop_event.is_set():
            # ランダム遅延
            delay = random.uniform(self.skill.min_interval, self.skill.max_interval)
            
            # 高頻度チェックで即座に停止可能
            for _ in range(int(delay * 50)):
                if self._stop_event.is_set():
                    break
                time.sleep(0.02)
            
            if not self._stop_event.is_set():
                self._use_skill()
        
        self.logger.info(f"Skill thread stopped: {self.skill.name}")
    
    def stop(self):
        """スレッドを停止"""
        self._stop_event.set()
        self.join(timeout=0.5)
    
    def _use_skill(self):
        """スキルを使用"""
        # POEウィンドウチェック
        if self.manager.window_manager:
            try:
                if not self.manager.window_manager.is_poe_active():
                    return
            except Exception as e:
                self.logger.debug(f"Window check error: {e}")
        
        # キー入力実行
        try:
            self.manager.keyboard.press_key(self.skill.key)
            
            # 統計情報更新
            self.skill.use_count += 1
            self.skill.last_used = time.time()
            
            # コールバック実行
            if self.manager.on_skill_used:
                self.manager.on_skill_used(self.skill)
            
            self.logger.debug(f"Skill used: {self.skill.name} (count: {self.skill.use_count})")
            
        except Exception as e:
            self.logger.error(f"Error using skill: {e}")
```

### 2.4 バリデーション

```python
from typing import List, Optional

class SkillValidator:
    """スキル設定の検証"""
    
    VALID_KEYS = set('abcdefghijklmnopqrstuvwxyz0123456789')
    RESERVED_KEYS = {'f1', 'f12', '1', '2', '3', '4', '5'}  # フラスコ用等
    
    def validate_skill(self, skill: SkillConfig, existing_skills: List[SkillConfig]) -> List[str]:
        """スキル設定を検証し、エラーのリストを返す"""
        errors = []
        
        # 名前の検証
        if not skill.name or len(skill.name.strip()) == 0:
            errors.append("スキル名は必須です")
        elif len(skill.name) > 50:
            errors.append("スキル名は50文字以内にしてください")
        
        # キーの検証
        if not skill.key:
            errors.append("キーバインドは必須です")
        elif skill.key.lower() not in self.VALID_KEYS:
            errors.append(f"無効なキー: {skill.key}")
        elif skill.key.lower() in self.RESERVED_KEYS:
            errors.append(f"予約済みのキー: {skill.key}")
        
        # 重複チェック
        for other in existing_skills:
            if other.id != skill.id:
                if other.key.lower() == skill.key.lower():
                    errors.append(f"キー '{skill.key}' は既に {other.name} で使用されています")
                if other.name.lower() == skill.name.lower():
                    errors.append(f"スキル名 '{skill.name}' は既に使用されています")
        
        # 間隔の検証
        if skill.min_interval < 0.1:
            errors.append("最小間隔は0.1秒以上にしてください")
        if skill.max_interval > 60:
            errors.append("最大間隔は60秒以下にしてください")
        if skill.min_interval > skill.max_interval:
            errors.append("最小間隔は最大間隔以下にしてください")
        
        # 優先度の検証
        if skill.priority < 1 or skill.priority > 10:
            errors.append("優先度は1〜10の範囲で設定してください")
        
        return errors
```

## 3. データフロー

### 3.1 スキル追加フロー
```
User Input (GUI)
    │
    ▼
SkillEditDialog
    │
    ├─▶ Input Validation
    │
    ▼
SkillManager.add_skill()
    │
    ├─▶ SkillValidator.validate()
    │
    ├─▶ Update internal state
    │
    ├─▶ Start DynamicSkillThread (if running)
    │
    ├─▶ Save to YAML
    │
    └─▶ Trigger callbacks (GUI update)
```

### 3.2 スキル実行フロー
```
DynamicSkillThread
    │
    ├─▶ Check POE window active
    │
    ├─▶ Random delay calculation
    │
    ├─▶ KeyboardController.press_key()
    │
    ├─▶ Update statistics
    │
    └─▶ Trigger on_skill_used callback
```

## 4. 状態遷移

### 4.1 スキルマネージャー状態
```
          ┌─────────┐
          │ Stopped │
          └────┬────┘
               │ start()
               ▼
          ┌─────────┐
          │ Running │
          └────┬────┘
               │ stop()
               ▼
          ┌─────────┐
          │ Stopped │
          └─────────┘
```

### 4.2 個別スキル状態
```
┌───────────┐    add_skill()    ┌──────────┐
│   New     │ ────────────────▶ │ Disabled │
└───────────┘                   └────┬─────┘
                                     │ enable
                                     ▼
                               ┌──────────┐
                               │ Enabled  │◀─┐
                               └────┬─────┘  │
                                    │ disable │
                                    ▼         │
                               ┌──────────┐   │
                               │ Disabled │───┘
                               └────┬─────┘ update
                                    │ remove_skill()
                                    ▼
                               ┌──────────┐
                               │ Deleted  │
                               └──────────┘
```

## 5. エラーハンドリング

### 5.1 エラーケース一覧
1. **設定エラー**
   - 無効なキー設定
   - 重複するキー割り当て
   - 不正な間隔設定

2. **実行時エラー**
   - スレッド生成失敗
   - キーボード入力エラー
   - ウィンドウマネージャーエラー

3. **永続化エラー**
   - ファイル書き込み失敗
   - 設定ファイル破損

### 5.2 エラー処理戦略
```python
class ErrorHandler:
    """エラー処理の統一インターフェース"""
    
    @staticmethod
    def handle_validation_error(errors: List[str], context: str):
        """バリデーションエラーの処理"""
        logger.error(f"Validation error in {context}: {', '.join(errors)}")
        # GUIに通知
        return False
    
    @staticmethod
    def handle_runtime_error(error: Exception, skill: SkillConfig):
        """実行時エラーの処理"""
        logger.error(f"Runtime error for skill {skill.name}: {error}")
        # 統計情報に記録
        # 必要に応じて再試行またはスキップ
    
    @staticmethod
    def handle_persistence_error(error: Exception, operation: str):
        """永続化エラーの処理"""
        logger.error(f"Persistence error during {operation}: {error}")
        # バックアップから復元を試行
        # ユーザーに通知
```

## 6. パフォーマンス考慮事項

### 6.1 最適化ポイント
1. **スレッドプール管理**
   - 最大スレッド数の制限（デフォルト: 20）
   - アイドルスレッドの自動クリーンアップ

2. **メモリ管理**
   - 統計情報の定期的なクリーンアップ
   - 弱参照を使用したコールバック管理

3. **CPU使用率**
   - 高頻度チェックの最適化（20ms間隔）
   - バッチ処理による設定保存

### 6.2 ベンチマーク目標
- スキル追加/削除: < 50ms
- 設定保存: < 100ms
- スレッド起動: < 10ms
- メモリ使用量: < 50MB（100スキル時）

## 7. 拡張性考慮事項

### 7.1 将来の拡張ポイント
1. **条件付きスキル実行**
   - HP/MP閾値による制御
   - バフ/デバフ状態による制御

2. **スキルグループ化**
   - 複数スキルの連携実行
   - グループ単位での有効/無効切り替え

3. **プロファイル機能**
   - キャラクター別設定
   - シチュエーション別プロファイル

4. **高度な統計**
   - 使用頻度グラフ
   - パフォーマンス分析

### 7.2 インターフェース設計
```python
# 将来の拡張用インターフェース
class ISkillCondition(ABC):
    """スキル実行条件のインターフェース"""
    @abstractmethod
    def is_satisfied(self) -> bool:
        pass

class ISkillGroup(ABC):
    """スキルグループのインターフェース"""
    @abstractmethod
    def execute(self):
        pass
```

## 8. セキュリティ考慮事項

1. **入力検証**
   - SQLインジェクション対策（設定名）
   - パストラバーサル対策（ファイルパス）

2. **権限管理**
   - 設定ファイルの適切な権限設定
   - キーロガー対策

3. **アンチチート対策**
   - ランダム遅延の維持
   - 人間的な操作パターンの模倣
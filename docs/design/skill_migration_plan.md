# POE Macro v3.0 スキルシステム移行計画書

## 概要
この文書は、現在のハードコーディングされたスキルシステムから、動的管理システムへの移行を安全かつ効率的に行うための詳細な計画を記述します。

## 1. 移行戦略

### 1.1 段階的移行アプローチ
```
Phase 1: 新システム実装
    ├─ 新しいクラス・インターフェース作成
    ├─ 旧システムと並行動作
    └─ 内部テスト

Phase 2: 自動移行機能
    ├─ 設定ファイル移行ツール
    ├─ バックアップ機能
    └─ ロールバック機能

Phase 3: 完全移行
    ├─ 旧システムの無効化
    ├─ 新システムの本格稼働
    └─ 旧コードの削除
```

### 1.2 移行原則
1. **ゼロダウンタイム**: ユーザーの利用を中断させない
2. **データ保護**: 既存設定の完全保持
3. **自動化**: 手動操作を最小限に抑制
4. **可逆性**: 問題発生時の即座なロールバック

## 2. 既存設定の分析

### 2.1 現在の設定形式
```yaml
# 現在の設定（旧形式）
skills:
  enabled: true
  berserk:
    enabled: true
    key: "e"
    interval: [0.3, 1.0]
  molten_shell:
    enabled: true
    key: "r"
    interval: [0.3, 1.0]
  order_to_me:
    enabled: true
    key: "t"
    interval: [3.5, 4.0]
```

### 2.2 新設定形式
```yaml
# 新しい設定（新形式）
skills:
  enabled: true
  skill_list:
    - id: "legacy_berserk"
      name: "Berserk"
      key: "e"
      min_interval: 0.3
      max_interval: 1.0
      enabled: true
      priority: 1
      created_at: "2025-07-12T10:00:00"
      modified_at: "2025-07-12T10:00:00"
      stats:
        use_count: 0
        last_used: null
    - id: "legacy_molten_shell"
      name: "Molten Shell"
      key: "r"
      min_interval: 0.3
      max_interval: 1.0
      enabled: true
      priority: 2
      created_at: "2025-07-12T10:00:00"
      modified_at: "2025-07-12T10:00:00"
      stats:
        use_count: 0
        last_used: null
    - id: "legacy_order_to_me"
      name: "Order! To Me!"
      key: "t"
      min_interval: 3.5
      max_interval: 4.0
      enabled: true
      priority: 3
      created_at: "2025-07-12T10:00:00"
      modified_at: "2025-07-12T10:00:00"
      stats:
        use_count: 0
        last_used: null
```

## 3. 自動移行アルゴリズム

### 3.1 移行処理フロー
```python
class ConfigMigrator:
    """設定移行を処理するクラス"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.backup_path = None
    
    def migrate_skill_config(self) -> MigrationResult:
        """スキル設定を移行"""
        try:
            # 1. 現在の設定を読み込み
            current_config = self.config_manager.load_config()
            
            # 2. バックアップを作成
            self.backup_path = self._create_backup(current_config)
            
            # 3. 移行が必要かチェック
            if not self._needs_migration(current_config):
                return MigrationResult.NO_MIGRATION_NEEDED
            
            # 4. 新形式に変換
            migrated_config = self._convert_to_new_format(current_config)
            
            # 5. 検証
            if not self._validate_migrated_config(migrated_config):
                return MigrationResult.VALIDATION_FAILED
            
            # 6. 保存
            self.config_manager.save_config(migrated_config)
            
            # 7. 検証のため再読み込み
            verification_config = self.config_manager.load_config()
            if not self._verify_migration(verification_config):
                self._rollback()
                return MigrationResult.VERIFICATION_FAILED
            
            self.logger.info("Skill configuration migrated successfully")
            return MigrationResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            if self.backup_path:
                self._rollback()
            return MigrationResult.ERROR
    
    def _create_backup(self, config: Dict) -> str:
        """設定のバックアップを作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"config_backup_{timestamp}.yaml"
        backup_path = os.path.join(os.path.dirname(self.config_manager.config_path), backup_filename)
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, ensure_ascii=False)
        
        self.logger.info(f"Backup created: {backup_path}")
        return backup_path
    
    def _needs_migration(self, config: Dict) -> bool:
        """移行が必要かチェック"""
        skills_config = config.get('skills', {})
        
        # 新形式が既に存在する場合は移行不要
        if 'skill_list' in skills_config:
            return False
        
        # 旧形式のスキルが存在する場合は移行必要
        legacy_skills = ['berserk', 'molten_shell', 'order_to_me']
        return any(skill in skills_config for skill in legacy_skills)
    
    def _convert_to_new_format(self, config: Dict) -> Dict:
        """旧形式から新形式に変換"""
        new_config = config.copy()
        skills_config = new_config.setdefault('skills', {})
        
        # 移行マッピング
        migration_mapping = {
            'berserk': {
                'name': 'Berserk',
                'default_key': 'e',
                'default_interval': [0.3, 1.0],
                'priority': 1
            },
            'molten_shell': {
                'name': 'Molten Shell',
                'default_key': 'r',
                'default_interval': [0.3, 1.0],
                'priority': 2
            },
            'order_to_me': {
                'name': 'Order! To Me!',
                'default_key': 't',
                'default_interval': [3.5, 4.0],
                'priority': 3
            }
        }
        
        skill_list = []
        current_time = datetime.now().isoformat()
        
        for legacy_key, mapping in migration_mapping.items():
            if legacy_key in skills_config:
                legacy_skill = skills_config[legacy_key]
                
                # 旧設定が辞書形式でない場合はスキップ
                if not isinstance(legacy_skill, dict):
                    continue
                
                # 新形式のスキル設定を作成
                new_skill = {
                    'id': f"legacy_{legacy_key}",
                    'name': mapping['name'],
                    'key': legacy_skill.get('key', mapping['default_key']),
                    'min_interval': legacy_skill.get('interval', mapping['default_interval'])[0],
                    'max_interval': legacy_skill.get('interval', mapping['default_interval'])[1],
                    'enabled': legacy_skill.get('enabled', True),
                    'priority': mapping['priority'],
                    'created_at': current_time,
                    'modified_at': current_time,
                    'stats': {
                        'use_count': 0,
                        'last_used': None
                    }
                }
                
                skill_list.append(new_skill)
                
                # 旧設定を削除
                del skills_config[legacy_key]
        
        # 新形式で保存
        skills_config['skill_list'] = skill_list
        
        return new_config
    
    def _validate_migrated_config(self, config: Dict) -> bool:
        """移行された設定を検証"""
        try:
            skills_config = config.get('skills', {})
            skill_list = skills_config.get('skill_list', [])
            
            # 基本的な構造チェック
            if not isinstance(skill_list, list):
                return False
            
            # 各スキルの必須フィールドチェック
            required_fields = ['id', 'name', 'key', 'min_interval', 'max_interval', 'enabled', 'priority']
            for skill in skill_list:
                if not isinstance(skill, dict):
                    return False
                
                for field in required_fields:
                    if field not in skill:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False
    
    def _verify_migration(self, config: Dict) -> bool:
        """移行結果の検証"""
        try:
            # SkillManagerで正常に読み込めるかテスト
            from src.modules.skill_manager import SkillManager
            
            # 一時的なSkillManagerインスタンスで検証
            temp_manager = SkillManager(self.config_manager)
            skills = temp_manager.get_skills()
            
            # 移行されたスキルが正しく読み込まれているかチェック
            expected_skills = ['Berserk', 'Molten Shell', 'Order! To Me!']
            loaded_skill_names = [skill.name for skill in skills]
            
            return all(name in loaded_skill_names for name in expected_skills)
            
        except Exception as e:
            self.logger.error(f"Verification error: {e}")
            return False
    
    def _rollback(self):
        """バックアップからロールバック"""
        if self.backup_path and os.path.exists(self.backup_path):
            try:
                # バックアップファイルを現在の設定ファイルに復元
                shutil.copy2(self.backup_path, self.config_manager.config_path)
                self.logger.info("Configuration rolled back successfully")
            except Exception as e:
                self.logger.error(f"Rollback failed: {e}")


class MigrationResult(Enum):
    """移行結果の列挙型"""
    SUCCESS = "success"
    NO_MIGRATION_NEEDED = "no_migration_needed"
    VALIDATION_FAILED = "validation_failed"
    VERIFICATION_FAILED = "verification_failed"
    ERROR = "error"
```

## 4. エラーハンドリング戦略

### 4.1 エラーケース分析
```python
ERROR_SCENARIOS = {
    "BACKUP_CREATION_FAILED": {
        "description": "バックアップファイルの作成に失敗",
        "recovery": "手動バックアップの作成を促す",
        "severity": "HIGH"
    },
    "CONFIG_PARSE_ERROR": {
        "description": "設定ファイルの解析に失敗",
        "recovery": "デフォルト設定での復旧",
        "severity": "MEDIUM"
    },
    "MIGRATION_VALIDATION_FAILED": {
        "description": "移行後の設定が不正",
        "recovery": "自動ロールバック",
        "severity": "HIGH"
    },
    "SAVE_PERMISSION_DENIED": {
        "description": "設定ファイルの保存権限がない",
        "recovery": "権限の確認と修正を促す",
        "severity": "HIGH"
    },
    "DISK_SPACE_INSUFFICIENT": {
        "description": "ディスク容量不足",
        "recovery": "容量確保を促す",
        "severity": "MEDIUM"
    }
}
```

### 4.2 フォールバック機能
```python
class FallbackManager:
    """フォールバック機能を管理"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
    
    def create_emergency_config(self) -> Dict:
        """緊急時の最小設定を作成"""
        return {
            'skills': {
                'enabled': False,  # 安全のため無効化
                'skill_list': []
            },
            'general': {
                'debug_mode': True,  # デバッグモードを有効
                'log_level': 'DEBUG'
            }
        }
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """バックアップから復元"""
        try:
            if not os.path.exists(backup_path):
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_config = yaml.safe_load(f)
            
            self.config_manager.save_config(backup_config)
            self.logger.info(f"Configuration restored from backup: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup restoration failed: {e}")
            return False
    
    def get_available_backups(self) -> List[str]:
        """利用可能なバックアップファイルを取得"""
        config_dir = os.path.dirname(self.config_manager.config_path)
        backup_pattern = os.path.join(config_dir, "config_backup_*.yaml")
        
        backups = glob.glob(backup_pattern)
        return sorted(backups, reverse=True)  # 新しい順
```

## 5. ユーザー通知システム

### 5.1 通知レベル
```python
class NotificationLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class MigrationNotifier:
    """移行関連の通知を管理"""
    
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.logger = logging.getLogger(__name__)
    
    def notify_migration_start(self):
        """移行開始の通知"""
        message = "スキルシステムの設定を新形式に移行しています..."
        self._notify(message, NotificationLevel.INFO)
    
    def notify_migration_success(self, backup_path: str):
        """移行成功の通知"""
        message = f"スキル設定の移行が完了しました。\nバックアップ: {backup_path}"
        self._notify(message, NotificationLevel.SUCCESS)
    
    def notify_migration_failure(self, error: str):
        """移行失敗の通知"""
        message = f"スキル設定の移行に失敗しました: {error}\n旧設定で動作を継続します。"
        self._notify(message, NotificationLevel.ERROR)
    
    def notify_rollback(self):
        """ロールバック実行の通知"""
        message = "問題が発生したため、設定を元に戻しました。"
        self._notify(message, NotificationLevel.WARNING)
    
    def _notify(self, message: str, level: NotificationLevel):
        """通知を送信"""
        # ログに記録
        log_method = getattr(self.logger, level.value)
        log_method(message)
        
        # GUI通知
        if self.gui_callback:
            self.gui_callback(message, level)
```

### 5.2 GUI通知ダイアログ
```python
class MigrationDialog(QDialog):
    """移行進捗を表示するダイアログ"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定移行")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # 進捗表示
        self.progress_label = QLabel("移行処理を開始しています...")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不確定進捗
        layout.addWidget(self.progress_bar)
        
        # ボタン
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def update_progress(self, message: str, finished: bool = False):
        """進捗を更新"""
        self.progress_label.setText(message)
        
        if finished:
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(1)
            self.ok_button.setEnabled(True)
```

## 6. 実行計画とスケジュール

### 6.1 実装フェーズ
```
Day 2: 新システム実装
├─ 07:00-09:00: SkillManager, SkillConfig実装
├─ 09:00-11:00: DynamicSkillThread, バリデータ実装
├─ 11:00-13:00: 移行機能実装
├─ 13:00-15:00: GUI統合
└─ 15:00-17:00: 初期テスト

Day 3: 統合とテスト
├─ 07:00-09:00: 統合テスト
├─ 09:00-11:00: エラーハンドリング強化
├─ 11:00-13:00: パフォーマンス調整
├─ 13:00-15:00: 実機テスト
└─ 15:00-17:00: 最終調整とドキュメント更新
```

### 6.2 テストケース
```python
TEST_CASES = {
    "MIGRATION_BASIC": {
        "description": "基本的な移行テスト",
        "input": "標準的な3スキル設定",
        "expected": "正常な新形式への変換"
    },
    "MIGRATION_EMPTY": {
        "description": "空設定の移行テスト",
        "input": "スキル設定なし",
        "expected": "空のskill_listを作成"
    },
    "MIGRATION_PARTIAL": {
        "description": "一部スキルのみの移行",
        "input": "一部スキルが無効",
        "expected": "有効なスキルのみ移行"
    },
    "MIGRATION_INVALID": {
        "description": "不正設定の移行",
        "input": "不正なキー設定",
        "expected": "エラーハンドリングと修正"
    },
    "ROLLBACK_TEST": {
        "description": "ロールバック機能",
        "input": "移行失敗時",
        "expected": "元の設定に復元"
    }
}
```

## 7. 品質保証

### 7.1 チェックリスト
- [ ] バックアップ作成機能の動作確認
- [ ] 移行アルゴリズムの正確性確認
- [ ] エラーハンドリングの網羅性確認
- [ ] ロールバック機能の動作確認
- [ ] GUI通知機能の動作確認
- [ ] パフォーマンス影響の測定
- [ ] メモリリークの確認
- [ ] 複数回実行の安全性確認

### 7.2 承認基準
1. **機能要件**
   - すべてのテストケースが成功
   - 既存データの100%保持
   - エラー時の自動復旧

2. **非機能要件**
   - 移行処理時間 < 5秒
   - 追加メモリ使用量 < 10MB
   - CPU使用率増加 < 5%

3. **ユーザビリティ**
   - 明確な進捗表示
   - 分かりやすいエラーメッセージ
   - 手動介入の最小化

## 8. 緊急対応計画

### 8.1 移行失敗時の対応
```
1. 自動ロールバック実行
2. エラーログの詳細記録
3. ユーザーへの状況説明
4. 手動復旧手順の提供
5. 緊急パッチの準備
```

### 8.2 データ損失防止
```python
class DataProtector:
    """データ保護機能"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.backup_retention = 30  # 30日間保持
    
    def create_multiple_backups(self):
        """複数のバックアップを作成"""
        backups = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. メイン設定のバックアップ
        main_backup = f"config_backup_{timestamp}.yaml"
        self._create_backup(main_backup)
        backups.append(main_backup)
        
        # 2. 圧縮バックアップ
        compressed_backup = f"config_backup_{timestamp}.tar.gz"
        self._create_compressed_backup(compressed_backup)
        backups.append(compressed_backup)
        
        # 3. 古いバックアップのクリーンアップ
        self._cleanup_old_backups()
        
        return backups
    
    def verify_backup_integrity(self, backup_path: str) -> bool:
        """バックアップの整合性を検証"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 基本的な構造チェック
            required_sections = ['skills', 'general']
            return all(section in config for section in required_sections)
            
        except Exception:
            return False
```

この移行計画により、既存ユーザーの設定を安全に新システムに移行し、問題発生時の迅速な復旧を保証します。
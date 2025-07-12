# POE Macro v3.0 スキルシステム GUI設計モックアップ

## 概要
この文書は、動的スキル管理システムのGUI設計を詳細に記述します。現在のシンプルなチェックボックスベースの設計から、フル機能のスキル管理インターフェースへの進化を目指します。

## 1. 現在のGUI分析

### 1.1 現在の制限事項
```
[現在のスキルタブ]
┌─────────────────────────────────────────────────────────────────┐
│ スキル自動使用設定                                                │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ☑ スキル自動使用を有効化                                        │ │
│ │                                                             │ │
│ │ [設定を保存]  [設定を適用（保存せずに）]                         │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ (大きな余白)                                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**問題点:**
- 個別スキルの管理不可
- 設定の可視性が低い
- スキルの追加/削除不可
- 統計情報の表示なし

## 2. 新しいGUI設計

### 2.1 新しいスキルタブ全体レイアウト
```
[新しいスキルタブ - 800x600]
┌─────────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ スキル自動使用設定                                            │ │
│ │ ☑ スキル自動使用を有効化    [🔄 リロード] [💾 すべて保存]      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ アクションバー                                                │ │
│ │ [➕ 新規スキル] [📋 プリセット] [📤 エクスポート] [📥 インポート] │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ スキル一覧テーブル                                            │ │
│ │┌───┬────────────┬───┬──────────┬──────────┬───┬────────────┐│ │
│ ││☑ │ スキル名     │キー│ 間隔(秒)  │ 優先度    │統計│ アクション    ││ │
│ │├───┼────────────┼───┼──────────┼──────────┼───┼────────────┤│ │
│ ││☑ │ Berserk    │ E │ 0.3-1.0  │ 1 (高)   │ 42 │[✏️][🔄][❌]││ │
│ ││☑ │ Molten Shell│ R │ 0.3-1.0  │ 2 (高)   │ 38 │[✏️][🔄][❌]││ │
│ ││☑ │ Order! To Me│ T │ 3.5-4.0  │ 3 (中)   │ 15 │[✏️][🔄][❌]││ │
│ ││☐ │ Blood Rage  │ B │ 15.0-16.0│ 4 (低)   │ 8  │[✏️][🔄][❌]││ │
│ │└───┴────────────┴───┴──────────┴──────────┴───┴────────────┘│ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ リアルタイム統計                                              │ │
│ │ 📊 総実行回数: 103  ⏱️ 平均間隔: 2.1秒  🎯 成功率: 99.2%     │ │
│ │ 📈 最後の実行: Berserk (2秒前)  ⚠️ エラー: 0                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 スキル編集ダイアログ
```
[スキル編集ダイアログ - 500x400]
┌─────────────────────────────────────────────────────────────────┐
│ ✏️ スキル設定 - Berserk                                         │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 基本設定                                                     │ │
│ │ スキル名: [Berserk                         ]                 │ │
│ │ キー:     [E] [🎯 キー記録]                                  │ │
│ │ 有効:     ☑ スキルを有効化                                   │ │
│ │ 優先度:   [1] (1=最高, 10=最低)                              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 実行間隔設定                                                 │ │
│ │ 最小間隔: [0.3] 秒                                           │ │
│ │ 最大間隔: [1.0] 秒                                           │ │
│ │ プリセット: [🎮 通常戦闘] [⚔️ ボス戦] [🏃 移動中] [カスタム]   │ │
│ │                                                             │ │
│ │ プレビュー: 0.3〜1.0秒でランダムに実行                        │ │
│ │           (平均: 0.65秒, 時間あたり: 約92回)                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 統計情報                                                     │ │
│ │ 作成日時: 2025-07-12 10:30:15                                │ │
│ │ 最終更新: 2025-07-12 15:45:22                                │ │
│ │ 総実行回数: 42回                                             │ │
│ │ 最後の実行: 5秒前                                            │ │
│ │ 平均間隔: 0.67秒                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ │ [🔄 プレビュー] [💾 保存] [❌ キャンセル] [🗑️ 削除]             │ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 キー記録ダイアログ
```
[キー記録ダイアログ - 300x200]
┌─────────────────────────────────────────────────────────────────┐
│ 🎯 キー記録                                                     │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                                                             │ │
│ │             使用するキーを押してください                       │ │
│ │                                                             │ │
│ │            現在の設定: [E]                                   │ │
│ │                                                             │ │
│ │        ⏱️ 30秒でタイムアウトします                            │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [❌ キャンセル]                                                │ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 スキルプリセットダイアログ
```
[スキルプリセットダイアログ - 400x300]
┌─────────────────────────────────────────────────────────────────┐
│ 📋 スキルプリセット                                             │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ プリセット一覧                                               │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ ⚔️ 標準戦闘セット (3スキル)                              │ │ │
│ │ │ 🏹 レンジャー向け (4スキル)                               │ │ │
│ │ │ 🔮 カスター向け (5スキル)                                 │ │ │
│ │ │ 🛡️ タンク向け (2スキル)                                  │ │ │
│ │ │ 🎯 カスタム1 (6スキル)                                   │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ プリセット詳細                                               │ │
│ │ 名前: 標準戦闘セット                                        │ │
│ │ 説明: 一般的な戦闘に適したスキル構成                          │ │
│ │ スキル: Berserk, Molten Shell, Order! To Me!                │ │
│ │ 作成日: 2025-07-12                                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [📤 適用] [➕ 新規] [✏️ 編集] [🗑️ 削除] [❌ 閉じる]             │ │
└─────────────────────────────────────────────────────────────────┘
```

## 3. コンポーネント設計

### 3.1 SkillTableWidget
```python
class SkillTableWidget(QTableWidget):
    """スキル一覧テーブルウィジェット"""
    
    skill_changed = pyqtSignal(str)  # スキルID
    skill_deleted = pyqtSignal(str)  # スキルID
    skill_toggled = pyqtSignal(str, bool)  # スキルID, 有効状態
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.skill_manager = None
        self.setup_table()
        self.setup_context_menu()
    
    def setup_table(self):
        """テーブルの初期設定"""
        # カラム設定
        self.setColumnCount(7)
        headers = ["有効", "スキル名", "キー", "間隔", "優先度", "統計", "アクション"]
        self.setHorizontalHeaderLabels(headers)
        
        # カラム幅の調整
        self.setColumnWidth(0, 50)   # チェックボックス
        self.setColumnWidth(1, 150)  # スキル名
        self.setColumnWidth(2, 50)   # キー
        self.setColumnWidth(3, 100)  # 間隔
        self.setColumnWidth(4, 80)   # 優先度
        self.setColumnWidth(5, 70)   # 統計
        self.setColumnWidth(6, 120)  # アクション
        
        # テーブル設定
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        
        # スタイル設定
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: #fafafa;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3daee9;
                color: white;
            }
        """)
    
    def setup_context_menu(self):
        """コンテキストメニューの設定"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.context_menu = QMenu(self)
        
        # メニューアイテム
        self.edit_action = QAction("✏️ 編集", self)
        self.edit_action.triggered.connect(self.edit_selected_skill)
        self.context_menu.addAction(self.edit_action)
        
        self.duplicate_action = QAction("📋 複製", self)
        self.duplicate_action.triggered.connect(self.duplicate_selected_skill)
        self.context_menu.addAction(self.duplicate_action)
        
        self.context_menu.addSeparator()
        
        self.delete_action = QAction("🗑️ 削除", self)
        self.delete_action.triggered.connect(self.delete_selected_skill)
        self.context_menu.addAction(self.delete_action)
    
    def set_skill_manager(self, skill_manager):
        """スキルマネージャーを設定"""
        self.skill_manager = skill_manager
        self.refresh_table()
    
    def refresh_table(self):
        """テーブルを更新"""
        if not self.skill_manager:
            return
        
        skills = self.skill_manager.get_skills()
        self.setRowCount(len(skills))
        
        for row, skill in enumerate(skills):
            self.populate_row(row, skill)
    
    def populate_row(self, row: int, skill: SkillConfig):
        """行にスキルデータを設定"""
        # 有効チェックボックス
        checkbox = QCheckBox()
        checkbox.setChecked(skill.enabled)
        checkbox.stateChanged.connect(lambda state, s=skill: self.on_skill_toggled(s, state))
        self.setCellWidget(row, 0, checkbox)
        
        # スキル名
        name_item = QTableWidgetItem(skill.name)
        name_item.setData(Qt.UserRole, skill.id)
        self.setItem(row, 1, name_item)
        
        # キー
        key_item = QTableWidgetItem(skill.key.upper())
        key_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 2, key_item)
        
        # 間隔
        interval_text = f"{skill.min_interval}-{skill.max_interval}"
        interval_item = QTableWidgetItem(interval_text)
        interval_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 3, interval_item)
        
        # 優先度
        priority_text = f"{skill.priority} ({self.get_priority_text(skill.priority)})"
        priority_item = QTableWidgetItem(priority_text)
        priority_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 4, priority_item)
        
        # 統計
        stats_text = str(skill.use_count)
        stats_item = QTableWidgetItem(stats_text)
        stats_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 5, stats_item)
        
        # アクションボタン
        action_widget = self.create_action_widget(skill)
        self.setCellWidget(row, 6, action_widget)
    
    def create_action_widget(self, skill: SkillConfig) -> QWidget:
        """アクションボタンウィジェットを作成"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # 編集ボタン
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(25, 25)
        edit_btn.setToolTip("編集")
        edit_btn.clicked.connect(lambda: self.edit_skill(skill))
        layout.addWidget(edit_btn)
        
        # 手動実行ボタン
        manual_btn = QPushButton("🔄")
        manual_btn.setFixedSize(25, 25)
        manual_btn.setToolTip("手動実行")
        manual_btn.clicked.connect(lambda: self.manual_execute(skill))
        layout.addWidget(manual_btn)
        
        # 削除ボタン
        delete_btn = QPushButton("❌")
        delete_btn.setFixedSize(25, 25)
        delete_btn.setToolTip("削除")
        delete_btn.clicked.connect(lambda: self.delete_skill(skill))
        layout.addWidget(delete_btn)
        
        return widget
    
    def get_priority_text(self, priority: int) -> str:
        """優先度のテキスト表現を取得"""
        if priority <= 2:
            return "高"
        elif priority <= 5:
            return "中"
        else:
            return "低"
    
    def on_skill_toggled(self, skill: SkillConfig, state: int):
        """スキルの有効/無効切り替え"""
        enabled = state == Qt.Checked
        self.skill_toggled.emit(skill.id, enabled)
```

### 3.2 SkillEditDialog
```python
class SkillEditDialog(QDialog):
    """スキル編集ダイアログ"""
    
    def __init__(self, skill: SkillConfig = None, parent=None):
        super().__init__(parent)
        self.skill = skill
        self.is_new = skill is None
        self.setup_ui()
        self.setup_validation()
        
        if skill:
            self.load_skill_data()
    
    def setup_ui(self):
        """UIの設定"""
        self.setWindowTitle("✏️ スキル設定" + (f" - {self.skill.name}" if self.skill else " - 新規"))
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # 基本設定グループ
        basic_group = QGroupBox("基本設定")
        basic_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(50)
        basic_layout.addRow("スキル名:", self.name_edit)
        
        key_layout = QHBoxLayout()
        self.key_edit = QLineEdit()
        self.key_edit.setMaxLength(1)
        self.key_edit.setFixedWidth(50)
        self.key_record_btn = QPushButton("🎯 キー記録")
        self.key_record_btn.clicked.connect(self.record_key)
        key_layout.addWidget(self.key_edit)
        key_layout.addWidget(self.key_record_btn)
        key_layout.addStretch()
        basic_layout.addRow("キー:", key_layout)
        
        self.enabled_cb = QCheckBox("スキルを有効化")
        basic_layout.addRow("有効:", self.enabled_cb)
        
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 10)
        self.priority_spin.setToolTip("1=最高, 10=最低")
        basic_layout.addRow("優先度:", self.priority_spin)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 間隔設定グループ
        interval_group = QGroupBox("実行間隔設定")
        interval_layout = QFormLayout()
        
        self.min_interval_spin = QDoubleSpinBox()
        self.min_interval_spin.setRange(0.1, 60.0)
        self.min_interval_spin.setDecimals(1)
        self.min_interval_spin.setSuffix(" 秒")
        self.min_interval_spin.valueChanged.connect(self.update_preview)
        interval_layout.addRow("最小間隔:", self.min_interval_spin)
        
        self.max_interval_spin = QDoubleSpinBox()
        self.max_interval_spin.setRange(0.1, 60.0)
        self.max_interval_spin.setDecimals(1)
        self.max_interval_spin.setSuffix(" 秒")
        self.max_interval_spin.valueChanged.connect(self.update_preview)
        interval_layout.addRow("最大間隔:", self.max_interval_spin)
        
        # プリセットボタン
        preset_layout = QHBoxLayout()
        presets = [
            ("🎮 通常戦闘", 0.3, 1.0),
            ("⚔️ ボス戦", 0.5, 1.5),
            ("🏃 移動中", 2.0, 3.0),
            ("カスタム", None, None)
        ]
        
        for name, min_val, max_val in presets:
            btn = QPushButton(name)
            if min_val is not None:
                btn.clicked.connect(lambda checked, m=min_val, x=max_val: self.apply_preset(m, x))
            preset_layout.addWidget(btn)
        
        interval_layout.addRow("プリセット:", preset_layout)
        
        # プレビュー
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        interval_layout.addRow("プレビュー:", self.preview_label)
        
        interval_group.setLayout(interval_layout)
        layout.addWidget(interval_group)
        
        # 統計情報グループ（既存スキルのみ）
        if not self.is_new:
            stats_group = QGroupBox("統計情報")
            stats_layout = QFormLayout()
            
            self.created_label = QLabel()
            stats_layout.addRow("作成日時:", self.created_label)
            
            self.modified_label = QLabel()
            stats_layout.addRow("最終更新:", self.modified_label)
            
            self.use_count_label = QLabel()
            stats_layout.addRow("総実行回数:", self.use_count_label)
            
            self.last_used_label = QLabel()
            stats_layout.addRow("最後の実行:", self.last_used_label)
            
            stats_group.setLayout(stats_layout)
            layout.addWidget(stats_group)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("🔄 プレビュー")
        self.preview_btn.clicked.connect(self.show_preview)
        button_layout.addWidget(self.preview_btn)
        
        button_layout.addStretch()
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self.save_skill)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("❌ キャンセル")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        if not self.is_new:
            self.delete_btn = QPushButton("🗑️ 削除")
            self.delete_btn.clicked.connect(self.delete_skill)
            self.delete_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
            button_layout.addWidget(self.delete_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def setup_validation(self):
        """バリデーションの設定"""
        # リアルタイム入力検証
        self.name_edit.textChanged.connect(self.validate_input)
        self.key_edit.textChanged.connect(self.validate_input)
        self.min_interval_spin.valueChanged.connect(self.validate_input)
        self.max_interval_spin.valueChanged.connect(self.validate_input)
    
    def validate_input(self):
        """入力検証"""
        errors = []
        
        # スキル名チェック
        if not self.name_edit.text().strip():
            errors.append("スキル名は必須です")
        
        # キーチェック
        if not self.key_edit.text().strip():
            errors.append("キーは必須です")
        
        # 間隔チェック
        if self.min_interval_spin.value() > self.max_interval_spin.value():
            errors.append("最小間隔は最大間隔以下である必要があります")
        
        # UIの更新
        self.save_btn.setEnabled(len(errors) == 0)
        
        if errors:
            self.setStyleSheet("QDialog { border: 2px solid #f44336; }")
            self.setWindowTitle("❌ エラー - スキル設定")
        else:
            self.setStyleSheet("")
            title = "✏️ スキル設定" + (f" - {self.skill.name}" if self.skill else " - 新規")
            self.setWindowTitle(title)
    
    def update_preview(self):
        """プレビュー更新"""
        min_val = self.min_interval_spin.value()
        max_val = self.max_interval_spin.value()
        
        if min_val <= max_val:
            avg = (min_val + max_val) / 2
            per_hour = 3600 / avg
            preview_text = f"{min_val}〜{max_val}秒でランダムに実行\n(平均: {avg:.2f}秒, 時間あたり: 約{per_hour:.0f}回)"
        else:
            preview_text = "⚠️ 最小間隔が最大間隔を超えています"
        
        self.preview_label.setText(preview_text)
    
    def record_key(self):
        """キー記録ダイアログを表示"""
        dialog = KeyRecordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.key_edit.setText(dialog.recorded_key)
    
    def apply_preset(self, min_val: float, max_val: float):
        """プリセットを適用"""
        self.min_interval_spin.setValue(min_val)
        self.max_interval_spin.setValue(max_val)
    
    def load_skill_data(self):
        """スキルデータを読み込み"""
        self.name_edit.setText(self.skill.name)
        self.key_edit.setText(self.skill.key)
        self.enabled_cb.setChecked(self.skill.enabled)
        self.priority_spin.setValue(self.skill.priority)
        self.min_interval_spin.setValue(self.skill.min_interval)
        self.max_interval_spin.setValue(self.skill.max_interval)
        
        # 統計情報の更新
        if not self.is_new:
            self.created_label.setText(self.skill.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            self.modified_label.setText(self.skill.modified_at.strftime("%Y-%m-%d %H:%M:%S"))
            self.use_count_label.setText(f"{self.skill.use_count}回")
            
            if self.skill.last_used:
                last_used = datetime.fromtimestamp(self.skill.last_used)
                elapsed = datetime.now() - last_used
                self.last_used_label.setText(f"{self.format_elapsed(elapsed)}前")
            else:
                self.last_used_label.setText("未実行")
    
    def format_elapsed(self, elapsed: timedelta) -> str:
        """経過時間のフォーマット"""
        seconds = elapsed.total_seconds()
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            return f"{int(seconds/60)}分"
        else:
            return f"{int(seconds/3600)}時間"
    
    def save_skill(self):
        """スキルを保存"""
        # データの収集
        skill_data = {
            'name': self.name_edit.text().strip(),
            'key': self.key_edit.text().strip().lower(),
            'enabled': self.enabled_cb.isChecked(),
            'priority': self.priority_spin.value(),
            'min_interval': self.min_interval_spin.value(),
            'max_interval': self.max_interval_spin.value()
        }
        
        # 新規または更新
        if self.is_new:
            self.skill = SkillConfig(**skill_data)
        else:
            for key, value in skill_data.items():
                setattr(self.skill, key, value)
            self.skill.modified_at = datetime.now()
        
        self.accept()
    
    def delete_skill(self):
        """スキルを削除"""
        reply = QMessageBox.question(
            self, 
            "削除確認",
            f"スキル '{self.skill.name}' を削除しますか？\n\nこの操作は取り消せません。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.skill = None  # 削除マーカー
            self.accept()
```

### 3.3 KeyRecordDialog
```python
class KeyRecordDialog(QDialog):
    """キー記録ダイアログ"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recorded_key = None
        self.setup_ui()
        self.setup_key_listener()
    
    def setup_ui(self):
        """UIの設定"""
        self.setWindowTitle("🎯 キー記録")
        self.setModal(True)
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # 指示テキスト
        instruction_label = QLabel("使用するキーを押してください")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(instruction_label)
        
        # 現在のキー表示
        self.current_key_label = QLabel("現在の設定: [未設定]")
        self.current_key_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.current_key_label)
        
        # タイムアウト表示
        self.timeout_label = QLabel("⏱️ 30秒でタイムアウトします")
        self.timeout_label.setAlignment(Qt.AlignCenter)
        self.timeout_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.timeout_label)
        
        layout.addStretch()
        
        # キャンセルボタン
        self.cancel_btn = QPushButton("❌ キャンセル")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        self.setLayout(layout)
        
        # タイマー設定
        self.timeout_timer = QTimer()
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self.timeout_reached)
        self.timeout_timer.start(30000)  # 30秒
    
    def setup_key_listener(self):
        """キーリスナーの設定"""
        self.key_listener = pynput.keyboard.Listener(
            on_press=self.on_key_press,
            suppress=True
        )
        self.key_listener.start()
    
    def on_key_press(self, key):
        """キー押下時の処理"""
        try:
            # 特殊キーの処理
            if hasattr(key, 'char') and key.char:
                if key.char.isalnum():
                    self.recorded_key = key.char.lower()
                    self.key_recorded()
            elif key == pynput.keyboard.Key.esc:
                self.reject()
        except Exception as e:
            print(f"Key recording error: {e}")
    
    def key_recorded(self):
        """キーが記録された時の処理"""
        self.timeout_timer.stop()
        self.key_listener.stop()
        
        self.current_key_label.setText(f"記録されたキー: [{self.recorded_key.upper()}]")
        self.timeout_label.setText("✅ キーが記録されました")
        
        # 少し待ってから閉じる
        QTimer.singleShot(1000, self.accept)
    
    def timeout_reached(self):
        """タイムアウト時の処理"""
        self.key_listener.stop()
        self.timeout_label.setText("⏰ タイムアウトしました")
        QTimer.singleShot(2000, self.reject)
    
    def closeEvent(self, event):
        """ダイアログが閉じられる時の処理"""
        if hasattr(self, 'key_listener'):
            self.key_listener.stop()
        if hasattr(self, 'timeout_timer'):
            self.timeout_timer.stop()
        super().closeEvent(event)
```

## 4. ユーザーインタラクションフロー

### 4.1 スキル追加フロー
```
1. [➕ 新規スキル] クリック
2. SkillEditDialog (新規モード) 表示
3. スキル名入力
4. [🎯 キー記録] クリック
5. KeyRecordDialog でキー記録
6. 間隔設定（プリセット利用可）
7. [💾 保存] クリック
8. バリデーション実行
9. SkillManager.add_skill() 呼び出し
10. テーブル更新
11. 成功メッセージ表示
```

### 4.2 スキル編集フロー
```
1. テーブル行の [✏️] クリック
2. SkillEditDialog (編集モード) 表示
3. 既存データの表示
4. 設定変更
5. リアルタイム入力検証
6. [💾 保存] クリック
7. SkillManager.update_skill() 呼び出し
8. テーブル更新
9. 成功メッセージ表示
```

### 4.3 スキル削除フロー
```
1. テーブル行の [❌] クリック
2. 削除確認ダイアログ表示
3. [はい] クリック
4. SkillManager.remove_skill() 呼び出し
5. テーブルから行削除
6. 成功メッセージ表示
```

## 5. 応答性とフィードバック

### 5.1 リアルタイム更新
- 統計情報の自動更新（1秒間隔）
- スキル実行時の即座な反映
- 設定変更時の即座な適用

### 5.2 視覚的フィードバック
- 有効/無効状態の色分け
- 実行中スキルのハイライト
- エラー状態の明確な表示
- 成功時のアニメーション

### 5.3 パフォーマンス考慮
- 遅延読み込み
- 効率的な差分更新
- UI応答性の維持

この設計により、ユーザーはスキルを直感的に管理し、リアルタイムで状態を確認できる高度なインターフェースを実現できます。
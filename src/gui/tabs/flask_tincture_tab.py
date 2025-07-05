"""
Flask & Tincture integrated tab for POE Macro GUI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QGridLayout, QLabel, QPushButton, QCheckBox, 
                             QComboBox, QLineEdit, QSlider, QSpinBox,
                             QDoubleSpinBox, QScrollArea, QFrame, QFileDialog)
from PyQt5.QtCore import Qt
from .base_tab import BaseTab
from src.utils.flask_data_manager import FlaskDataManager
from src.gui.widgets.searchable_combobox import SearchableComboBox

class FlaskTinctureTab(BaseTab):
    """Flask & Tincture integrated settings tab"""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.flask_slot_widgets = {}  # フラスコスロットのウィジェットを保存
        self.flask_data_manager = FlaskDataManager()  # フラスコデータマネージャー
        self.is_initializing = False  # 初期化中フラグを追加
        
    def create_widget(self):
        """Create flask & tincture tab widget"""
        # スクロール可能なウィジェットを作成
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # フラスコスロット設定グループ
        flask_group = self.create_flask_slots_group()
        main_layout.addWidget(flask_group)
        
        # 全体設定保存と検証ボタン
        save_button_layout = QHBoxLayout()
        
        validate_btn = QPushButton("設定を検証")
        validate_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-weight: bold; padding: 8px; }")
        validate_btn.clicked.connect(self.validate_and_show_results)
        save_button_layout.addWidget(validate_btn)
        
        save_all_btn = QPushButton("すべての設定を保存")
        save_all_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
        save_all_btn.clicked.connect(self.save_all_settings)
        save_button_layout.addWidget(save_all_btn)
        
        main_layout.addLayout(save_button_layout)
        
        # セパレーター
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Tincture設定グループ（既存のTinctureタブから移植）
        tincture_group = self.create_tincture_group()
        main_layout.addWidget(tincture_group)
        
        # 統計情報グループ
        stats_group = self.create_stats_group()
        main_layout.addWidget(stats_group)
        
        # ボタングループ
        button_layout = self.create_button_layout()
        main_layout.addLayout(button_layout)
        
        # 設定保存・適用ボタン
        settings_button_layout = self.create_settings_button_layout()
        main_layout.addLayout(settings_button_layout)
        
        main_layout.addStretch()
        
        scroll_area.setWidget(main_widget)
        return scroll_area
    
    def create_flask_slots_group(self):
        """フラスコスロット設定グループを作成"""
        group = QGroupBox("フラスコスロット設定")
        layout = QVBoxLayout(group)
        
        # Flask自動使用を有効化チェックボックス（既存のコードとの互換性のため）
        self.main_window.flask_enabled_cb = QCheckBox("Flask自動使用を有効化")
        flask_enabled = self.get_config_value('flask', 'enabled', True)
        self.main_window.flask_enabled_cb.setChecked(flask_enabled)
        layout.addWidget(self.main_window.flask_enabled_cb)
        
        # 5つのフラスコスロットを作成
        for slot_num in range(1, 6):
            slot_widget = self.create_flask_slot_widget(slot_num)
            layout.addWidget(slot_widget)
        
        # 全スロット作成後にTinctureキー割り当てを更新
        # (遅延実行でウィジェットが確実に存在するようにする)
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.update_tincture_key_assignment)
            
        return group
    
    def create_flask_slot_widget(self, slot_num):
        """個別のフラスコスロットウィジェットを作成"""
        # 初期化開始
        self.is_initializing = True
        
        slot_group = QGroupBox(f"スロット {slot_num}")
        layout = QGridLayout(slot_group)
        
        # ウィジェットを保存するディクショナリ
        slot_widgets = {}
        
        # 保存された設定を読み込み
        slot_config = self.config.get('flask_slots', {}).get(f'slot_{slot_num}', {})
        
        # 保存された持続時間を記録
        saved_duration = slot_config.get('duration_seconds', 5.0)
        
        # 割り当てキー
        layout.addWidget(QLabel("割り当てキー:"), 0, 0)
        key_edit = QLineEdit()
        key_edit.setMaximumWidth(50)
        # 保存された値があれば使用、なければデフォルト
        key_edit.setText(slot_config.get('key', str(slot_num)))
        slot_widgets['key'] = key_edit
        layout.addWidget(key_edit, 0, 1)
        
        # Tinctureチェックボックス
        tincture_cb = QCheckBox("Tincture")
        tincture_cb.setChecked(slot_config.get('is_tincture', False))
        tincture_cb.stateChanged.connect(lambda state: self.on_tincture_checked(slot_num, state))
        slot_widgets['is_tincture'] = tincture_cb
        layout.addWidget(tincture_cb, 0, 2)
        
        # フラスコ属性プルダウン
        layout.addWidget(QLabel("フラスコ属性:"), 1, 0)
        flask_type_combo = QComboBox()
        flask_type_combo.addItems(self.flask_data_manager.get_all_flask_types())
        # 保存された値を設定
        saved_flask_type = slot_config.get('flask_type', '')
        if saved_flask_type:
            index = flask_type_combo.findText(saved_flask_type)
            if index >= 0:
                flask_type_combo.setCurrentIndex(index)
        flask_type_combo.currentTextChanged.connect(lambda text: self.on_flask_type_changed(slot_num, text))
        slot_widgets['flask_type'] = flask_type_combo
        layout.addWidget(flask_type_combo, 1, 1, 1, 2)
        
        # レアリティプルダウン（Wine以外で表示）
        rarity_label = QLabel("レアリティ:")
        layout.addWidget(rarity_label, 2, 0)
        slot_widgets['rarity_label'] = rarity_label
        
        rarity_combo = QComboBox()
        rarity_combo.addItems(self.flask_data_manager.get_all_rarities())
        # 保存された値を設定
        saved_rarity = slot_config.get('rarity', '')
        if saved_rarity:
            index = rarity_combo.findText(saved_rarity)
            if index >= 0:
                rarity_combo.setCurrentIndex(index)
        rarity_combo.currentTextChanged.connect(lambda text: self.on_rarity_changed(slot_num, text))
        slot_widgets['rarity'] = rarity_combo
        layout.addWidget(rarity_combo, 2, 1, 1, 2)
        
        # ★順序変更：詳細プルダウン（ユニーク名/ベースタイプ）を先に（行3）
        detail_label = QLabel("詳細:")
        layout.addWidget(detail_label, 3, 0)  # 行3に移動
        slot_widgets['detail_label'] = detail_label
        detail_label.hide()
        
        # ★ ここが重要：SearchableComboBoxを使用
        from src.gui.widgets.searchable_combobox import SearchableComboBox
        detail_combo = SearchableComboBox()  # QComboBox()ではなくSearchableComboBox()
        detail_combo.currentTextChanged.connect(lambda text: self.on_detail_changed(slot_num, text))
        detail_combo.hide()
        slot_widgets['detail'] = detail_combo
        layout.addWidget(detail_combo, 3, 1, 1, 2)  # 行3に移動
        
        # ★順序変更：ユーティリティベース選択を後に（行4）
        base_label = QLabel("ベース:")
        layout.addWidget(base_label, 4, 0)  # 行4に移動
        slot_widgets['base_label'] = base_label
        base_label.hide()  # 初期状態では非表示
        
        base_combo = SearchableComboBox()  # SearchableComboBoxに変更
        base_combo.addItems(self.flask_data_manager.get_utility_bases())
        # 保存された値を設定
        saved_base = slot_config.get('base', '')
        if saved_base:
            index = base_combo.findText(saved_base)
            if index >= 0:
                base_combo.setCurrentIndex(index)
        base_combo.currentTextChanged.connect(lambda text: self.on_base_changed(slot_num, text))
        base_combo.hide()  # 初期状態では非表示
        slot_widgets['base'] = base_combo
        layout.addWidget(base_combo, 4, 1, 1, 2)  # 行4に移動
        # 保存された詳細値は後で設定（プルダウンが更新された後）
        
        # 持続時間入力
        layout.addWidget(QLabel("持続時間(秒):"), 5, 0)
        duration_spinbox = QDoubleSpinBox()
        duration_spinbox.setRange(0.0, 30.0)
        duration_spinbox.setDecimals(2)
        duration_spinbox.setSingleStep(0.1)
        duration_spinbox.setValue(saved_duration)
        slot_widgets['duration'] = duration_spinbox
        layout.addWidget(duration_spinbox, 5, 1, 1, 2)
        
        # チャージフル使用チェックボックス
        charge_full_cb = QCheckBox("チャージがフルの時のみ使用")
        charge_full_cb.setChecked(slot_config.get('use_when_full', False))
        slot_widgets['use_when_full'] = charge_full_cb
        layout.addWidget(charge_full_cb, 6, 0, 1, 3)
        
        # スロット設定保存ボタン
        save_slot_btn = QPushButton(f"スロット{slot_num}設定を保存")
        save_slot_btn.clicked.connect(lambda: self.save_slot_settings(slot_num))
        layout.addWidget(save_slot_btn, 7, 0, 1, 3)
        
        # ウィジェットを保存
        self.flask_slot_widgets[slot_num] = slot_widgets
        
        # 初期状態でプルダウンの表示/非表示を設定
        if saved_flask_type:
            self.on_flask_type_changed(slot_num, saved_flask_type)
            if saved_rarity:
                self.on_rarity_changed(slot_num, saved_rarity)
                # 詳細値を設定する
                saved_detail = slot_config.get('detail', '')
                if saved_detail and not detail_combo.isHidden():
                    index = detail_combo.findText(saved_detail)
                    if index >= 0:
                        detail_combo.setCurrentIndex(index)
        
        # 初期化完了後、保存された持続時間を再設定（上書きを防ぐため）
        self.is_initializing = False
        duration_spinbox.setValue(saved_duration)
        
        # Tinctureスロットの場合はキー割り当て更新
        if slot_config.get('is_tincture', False):
            # 他のスロット作成後にキー割り当てを更新するため、後で呼び出す
            pass
        
        return slot_group
    
    def create_tincture_group(self):
        """Tincture設定グループを作成（既存のTinctureタブから移植）"""
        tincture_group = QGroupBox("Tincture設定")
        tincture_layout = QGridLayout(tincture_group)
        
        # Tincture自動使用を有効化チェックボックス
        self.main_window.tincture_enabled_cb = QCheckBox("Tincture自動使用を有効化")
        tincture_enabled = self.get_config_value('tincture', 'enabled', True)
        self.main_window.tincture_enabled_cb.setChecked(tincture_enabled)
        tincture_layout.addWidget(self.main_window.tincture_enabled_cb, 0, 0, 1, 3)
        
        # Experienced Herbalistチェックボックス
        self.main_window.experienced_herbalist_cb = QCheckBox("Experienced Herbalist (2つのTincture装備可能)")
        experienced_herbalist = self.get_config_value('tincture', 'experienced_herbalist', False)
        self.main_window.experienced_herbalist_cb.setChecked(experienced_herbalist)
        self.main_window.experienced_herbalist_cb.stateChanged.connect(self.on_experienced_herbalist_changed)
        tincture_layout.addWidget(self.main_window.experienced_herbalist_cb, 1, 0, 1, 3)
        
        # 使用キー設定（既存コードとの互換性のため）
        tincture_layout.addWidget(QLabel("使用キー:"), 2, 0)
        self.main_window.tincture_key_edit = QLineEdit()
        tincture_key = self.get_config_value('tincture', 'key', '3')
        self.main_window.tincture_key_edit.setText(tincture_key)
        tincture_layout.addWidget(self.main_window.tincture_key_edit, 2, 1)
        
        # Tincture設定1
        tincture_layout.addWidget(QLabel("Tincture 1:"), 3, 0)
        self.create_tincture_settings(tincture_layout, 1, 3)
        
        # Tincture設定2（初期状態では非表示）
        self.tincture2_label = QLabel("Tincture 2:")
        self.tincture2_label.hide()
        tincture_layout.addWidget(self.tincture2_label, 4, 0)
        self.create_tincture_settings(tincture_layout, 2, 4)
        
        # モニター設定（共通）
        tincture_layout.addWidget(QLabel("モニター設定:"), 5, 0)
        self.main_window.monitor_combo = QComboBox()
        self.main_window.monitor_combo.addItems(["Primary", "Center", "Right"])
        monitor_config = self.get_config_value('tincture', 'monitor_config', 'Primary')
        self.main_window.monitor_combo.setCurrentText(monitor_config)
        tincture_layout.addWidget(self.main_window.monitor_combo, 5, 1)
        
        # 検出感度
        tincture_layout.addWidget(QLabel("検出感度:"), 6, 0)
        self.main_window.sensitivity_slider = QSlider(Qt.Horizontal)
        self.main_window.sensitivity_slider.setRange(50, 100)
        sensitivity = int(self.get_config_value('tincture', 'sensitivity', 0.7) * 100)
        self.main_window.sensitivity_slider.setValue(sensitivity)
        self.main_window.sensitivity_slider.valueChanged.connect(self.main_window.update_sensitivity_label)
        tincture_layout.addWidget(self.main_window.sensitivity_slider, 6, 1)
        
        self.main_window.sensitivity_label = QLabel(f"{sensitivity / 100:.2f}")
        tincture_layout.addWidget(self.main_window.sensitivity_label, 6, 2)
        
        # 詳細設定
        tincture_layout.addWidget(QLabel("チェック間隔(ms):"), 7, 0)
        self.main_window.check_interval_spinbox = QSpinBox()
        self.main_window.check_interval_spinbox.setRange(50, 1000)
        check_interval = int(self.get_config_value('tincture', 'check_interval', 0.1) * 1000)
        self.main_window.check_interval_spinbox.setValue(check_interval)
        tincture_layout.addWidget(self.main_window.check_interval_spinbox, 7, 1)
        
        tincture_layout.addWidget(QLabel("最小使用間隔(ms):"), 8, 0)
        self.main_window.min_use_interval_spinbox = QSpinBox()
        self.main_window.min_use_interval_spinbox.setRange(100, 5000)
        min_use_interval = int(self.get_config_value('tincture', 'min_use_interval', 0.5) * 1000)
        self.main_window.min_use_interval_spinbox.setValue(min_use_interval)
        tincture_layout.addWidget(self.main_window.min_use_interval_spinbox, 8, 1)
        
        # 初期状態でExperienced Herbalistの表示/非表示を適用
        if experienced_herbalist:
            self.on_experienced_herbalist_changed(Qt.Checked)
        
        return tincture_group
    
    def create_tincture_settings(self, layout, tincture_num, row):
        """個別のTincture設定を作成"""
        # 保存されたTincture設定を読み込み
        tincture_configs = self.get_config_value('tincture', 'tinctures', {})
        tincture_key = f'tincture{tincture_num}'
        tincture_config = tincture_configs.get(tincture_key, {})
        
        # 割り当てキー表示（読み取り専用）
        key_label = QLabel("キー: 未設定")
        if tincture_num == 1:
            self.main_window.tincture1_key_label = key_label
        else:
            self.main_window.tincture2_key_label = key_label
            key_label.hide()
        layout.addWidget(key_label, row, 1)
        
        # フォルダ選択ボタン
        folder_btn = QPushButton("フォルダ選択")
        folder_btn.clicked.connect(lambda: self.select_tincture_folder(tincture_num))
        if tincture_num == 1:
            self.main_window.tincture1_folder_btn = folder_btn
        else:
            self.main_window.tincture2_folder_btn = folder_btn
            folder_btn.hide()
        layout.addWidget(folder_btn, row, 2)
        
        # 選択されたフォルダパス表示
        saved_folder_path = tincture_config.get('folder_path', '未選択')
        folder_path_label = QLabel(saved_folder_path)
        if saved_folder_path != '未選択':
            folder_path_label.setStyleSheet("color: black; font-size: 10px;")
        else:
            folder_path_label.setStyleSheet("color: gray; font-size: 10px;")
        if tincture_num == 1:
            self.main_window.tincture1_folder_path_label = folder_path_label
        else:
            self.main_window.tincture2_folder_path_label = folder_path_label
            folder_path_label.hide()
        layout.addWidget(folder_path_label, row + 1, 1, 1, 2)
        
        # しきい値設定
        threshold_label = QLabel("しきい値:")
        if tincture_num == 1:
            self.main_window.tincture1_threshold_label = threshold_label
        else:
            self.main_window.tincture2_threshold_label = threshold_label
            threshold_label.hide()
        layout.addWidget(threshold_label, row + 2, 1)
        
        threshold_spinbox = QDoubleSpinBox()
        threshold_spinbox.setRange(0.1, 1.0)
        threshold_spinbox.setDecimals(2)
        threshold_spinbox.setSingleStep(0.05)
        # 保存された値を使用、なければデフォルト値
        saved_threshold = tincture_config.get('threshold', 0.8)
        threshold_spinbox.setValue(saved_threshold)
        if tincture_num == 1:
            self.main_window.tincture1_threshold_spinbox = threshold_spinbox
        else:
            self.main_window.tincture2_threshold_spinbox = threshold_spinbox
            threshold_spinbox.hide()
        layout.addWidget(threshold_spinbox, row + 2, 2)
        
    def create_stats_group(self):
        """統計情報グループを作成"""
        stats_group = QGroupBox("統計情報")
        stats_layout = QGridLayout(stats_group)
        
        self.main_window.tincture_uses_label = QLabel("使用回数: 0")
        stats_layout.addWidget(self.main_window.tincture_uses_label, 0, 0)
        
        self.main_window.detection_success_label = QLabel("検出成功: 0")
        stats_layout.addWidget(self.main_window.detection_success_label, 0, 1)
        
        self.main_window.detection_failed_label = QLabel("検出失敗: 0")
        stats_layout.addWidget(self.main_window.detection_failed_label, 1, 0)
        
        self.main_window.last_use_label = QLabel("最後の使用: なし")
        stats_layout.addWidget(self.main_window.last_use_label, 1, 1)
        
        return stats_group
    
    def create_button_layout(self):
        """ボタンレイアウトを作成"""
        button_layout = QHBoxLayout()
        
        self.main_window.manual_use_btn = QPushButton("手動使用")
        self.main_window.manual_use_btn.clicked.connect(self.main_window.manual_use_tincture)
        button_layout.addWidget(self.main_window.manual_use_btn)
        
        self.main_window.reset_stats_btn = QPushButton("統計リセット")
        self.main_window.reset_stats_btn.clicked.connect(self.main_window.reset_tincture_stats)
        button_layout.addWidget(self.main_window.reset_stats_btn)
        
        return button_layout
    
    def create_settings_button_layout(self):
        """設定保存・適用ボタンレイアウトを作成"""
        settings_button_layout = QHBoxLayout()
        
        self.main_window.save_tincture_btn = QPushButton("設定を保存")
        self.main_window.save_tincture_btn.clicked.connect(self.main_window.save_tincture_settings)
        self.main_window.save_tincture_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        settings_button_layout.addWidget(self.main_window.save_tincture_btn)
        
        self.main_window.apply_tincture_btn = QPushButton("設定を適用（保存せずに）")
        self.main_window.apply_tincture_btn.clicked.connect(self.main_window.apply_tincture_settings)
        self.main_window.apply_tincture_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
        settings_button_layout.addWidget(self.main_window.apply_tincture_btn)
        
        return settings_button_layout
    
    # イベントハンドラー
    def on_tincture_checked(self, slot_num, state):
        """Tinctureチェックボックスの状態変更時の処理"""
        is_checked = state == Qt.Checked
        widgets = self.flask_slot_widgets[slot_num]
        
        # フラスコ設定項目の有効/無効を切り替え
        widgets['flask_type'].setEnabled(not is_checked)
        widgets['rarity'].setEnabled(not is_checked)
        widgets['detail'].setEnabled(not is_checked)
        widgets['base'].setEnabled(not is_checked)
        widgets['duration'].setEnabled(not is_checked)
        widgets['use_when_full'].setEnabled(not is_checked)
        
        if is_checked:
            # Tinctureチェック時の処理
            self.update_tincture_key_assignment()
        
    def on_flask_type_changed(self, slot_num, flask_type):
        """フラスコ属性変更時の処理"""
        widgets = self.flask_slot_widgets[slot_num]
        
        if flask_type == "Wine":
            # Wineの場合はレアリティ選択を非表示
            widgets['rarity_label'].hide()
            widgets['rarity'].hide()
            widgets['detail_label'].hide()
            widgets['detail'].hide()
            widgets['base_label'].hide()
            widgets['base'].hide()
            # Wineのデフォルト持続時間を設定
            widgets['duration'].setValue(self.flask_data_manager.get_magic_flask_duration("wine"))
        else:
            # Wine以外はレアリティ選択を表示
            widgets['rarity_label'].show()
            widgets['rarity'].show()
            self.on_rarity_changed(slot_num, widgets['rarity'].currentText())
    
    def on_rarity_changed(self, slot_num, rarity):
        """レアリティ変更時の処理"""
        widgets = self.flask_slot_widgets[slot_num]
        flask_type = widgets['flask_type'].currentText()
        
        # デバッグログ
        print(f"[DEBUG] on_rarity_changed: slot={slot_num}, rarity={rarity}, flask_type={flask_type}")
        print(f"[DEBUG] detail widget type: {type(widgets['detail'])}")
        
        if rarity == "Magic":
            if flask_type == "Utility":
                # Utility + Magicの場合はベースタイプ選択を表示
                widgets['base_label'].hide()
                widgets['base'].hide()
                widgets['detail_label'].show()
                widgets['detail_label'].setText("ベースタイプ:")  # Magicの場合はベースタイプ
                widgets['detail'].show()
                
                # ユーティリティベースタイプをdetailに設定
                base_types = self.flask_data_manager.get_utility_base_types()
                widgets['detail'].clear()
                widgets['detail'].addItems(base_types)
                
                # 検索ヒントを設定
                if hasattr(widgets['detail'], 'lineEdit'):
                    widgets['detail'].lineEdit().setPlaceholderText("タイプして検索...")
                
                # 最初のアイテムが選択された場合の持続時間を設定
                if base_types:
                    self.on_detail_changed(slot_num, base_types[0])
            else:
                # その他のMagicフラスコ
                widgets['detail_label'].hide()
                widgets['detail'].hide()
                widgets['base_label'].hide()
                widgets['base'].hide()
                # Magicフラスコのデフォルト持続時間を設定
                widgets['duration'].setValue(self.flask_data_manager.get_magic_flask_duration(flask_type.lower()))
        else:  # Unique
            if flask_type == "Utility":
                # Utility+Uniqueの場合：ユニーク名を先に選択、ベースは自動設定
                widgets['detail_label'].show()
                widgets['detail_label'].setText("ユニーク名:")  # ★ラベルを変更
                widgets['detail'].show()
                
                # すべてのユーティリティユニークフラスコを表示
                unique_flasks = self.flask_data_manager.get_all_utility_uniques()
                widgets['detail'].clear()
                widgets['detail'].addItems(unique_flasks)
                
                # 検索ヒントを設定
                if hasattr(widgets['detail'], 'lineEdit'):
                    widgets['detail'].lineEdit().setPlaceholderText("ユニーク名を検索...")
                
                # ベースラベルは表示するが、ユーザーは選択不可（自動設定）
                widgets['base_label'].show()
                widgets['base_label'].setText("ベース（自動）:")
                widgets['base'].show()
                widgets['base'].setEnabled(False)  # 自動設定なので無効化
                
                # 最初のアイテムが選択された場合の処理
                if unique_flasks:
                    self.on_detail_changed(slot_num, unique_flasks[0])
            else:
                # その他のUnique（Life, Mana, Hybrid）
                widgets['base_label'].hide()
                widgets['base'].hide()
                widgets['detail_label'].show()
                widgets['detail_label'].setText("ユニーク名:")  # ★ラベルを変更
                widgets['detail'].show()
                
                # フラスコタイプに応じたユニーク名をdetailに設定
                unique_flasks = self.flask_data_manager.get_unique_flasks(flask_type.lower())
                widgets['detail'].clear()
                widgets['detail'].addItems(unique_flasks)
                
                # 検索ヒントを設定
                if hasattr(widgets['detail'], 'lineEdit'):
                    widgets['detail'].lineEdit().setPlaceholderText("ユニーク名を検索...")
                
                # 最初のアイテムが選択された場合の持続時間を設定
                if unique_flasks:
                    self.on_detail_changed(slot_num, unique_flasks[0])
    
    def on_base_changed(self, slot_num, base):
        """ベース変更時の処理（Utility+Uniqueでは使用されない）"""
        # Utility+Uniqueの場合はベースが自動設定されるため、この処理は不要
        # 将来の拡張のために残しておく
        pass
    
    def on_detail_changed(self, slot_num, detail):
        """詳細選択変更時の処理"""
        widgets = self.flask_slot_widgets[slot_num]
        flask_type = widgets['flask_type'].currentText()
        rarity = widgets['rarity'].currentText()
        
        if not detail:
            return
        
        # Utility + Uniqueの場合、選択されたユニーク名からベースを自動設定
        if flask_type == "Utility" and rarity == "Unique":
            base = self.flask_data_manager.get_base_for_utility_unique(detail)
            if base:
                # ベースを自動設定（ユーザーは変更不可）
                widgets['base'].clear()
                widgets['base'].addItem(base)
                widgets['base'].setCurrentText(base)
                
                # 持続時間を取得
                duration = self.flask_data_manager.get_flask_duration("utility", detail, base)
                if duration is not None:
                    widgets['duration'].setValue(duration)
        elif flask_type == "Utility" and rarity == "Magic":
            # Magicユーティリティの場合はベースタイプから持続時間を取得
            duration = self.flask_data_manager.get_utility_base_duration(detail)
            if duration is not None:
                widgets['duration'].setValue(duration)
        else:
            # その他のフラスコ
            duration = self.flask_data_manager.get_flask_duration(flask_type.lower(), detail)
            if duration is not None:
                widgets['duration'].setValue(duration)
    
    def on_experienced_herbalist_changed(self, state):
        """Experienced Herbalistチェックボックスの状態変更時の処理"""
        is_checked = state == Qt.Checked
        
        # Tincture 2の表示/非表示を切り替え
        self.tincture2_label.setVisible(is_checked)
        self.main_window.tincture2_key_label.setVisible(is_checked)
        self.main_window.tincture2_folder_btn.setVisible(is_checked)
        self.main_window.tincture2_folder_path_label.setVisible(is_checked)
        self.main_window.tincture2_threshold_label.setVisible(is_checked)
        self.main_window.tincture2_threshold_spinbox.setVisible(is_checked)
        
        if is_checked:
            # Tinctureチェック数の検証
            self.validate_tincture_count()
        else:
            # Tincture 2が無効になった場合、関連するスロットのチェックを外す
            self.uncheck_excess_tinctures(1)
    
    def update_tincture_key_assignment(self):
        """Tinctureのキー割り当てを更新"""
        tincture_slots = []
        
        # Tinctureにチェックされたスロットを収集
        for slot_num, widgets in self.flask_slot_widgets.items():
            if widgets['is_tincture'].isChecked():
                key = widgets['key'].text()
                tincture_slots.append((slot_num, key))
        
        # キー割り当てを更新
        if len(tincture_slots) >= 1:
            self.main_window.tincture1_key_label.setText(f"キー: {tincture_slots[0][1]}")
        else:
            self.main_window.tincture1_key_label.setText("キー: 未設定")
            
        if len(tincture_slots) >= 2 and self.main_window.experienced_herbalist_cb.isChecked():
            self.main_window.tincture2_key_label.setText(f"キー: {tincture_slots[1][1]}")
        else:
            self.main_window.tincture2_key_label.setText("キー: 未設定")
    
    def validate_tincture_count(self):
        """Tinctureチェック数の検証"""
        tincture_count = sum(1 for widgets in self.flask_slot_widgets.values() 
                           if widgets['is_tincture'].isChecked())
        
        max_tinctures = 2 if self.main_window.experienced_herbalist_cb.isChecked() else 1
        
        if tincture_count > max_tinctures:
            # TODO: 警告メッセージを表示
            self.log_info(f"警告: Tinctureは最大{max_tinctures}個まで装備可能です")
    
    def save_slot_settings(self, slot_num):
        """個別スロットの設定を保存"""
        try:
            widgets = self.flask_slot_widgets[slot_num]
            
            # スロット設定を収集
            slot_config = {
                'key': widgets['key'].text(),
                'is_tincture': widgets['is_tincture'].isChecked(),
                'flask_type': widgets['flask_type'].currentText(),
                'rarity': widgets['rarity'].currentText(),
                'detail': widgets['detail'].currentText() if widgets['detail'].isVisible() else '',
                'base': widgets['base'].currentText() if widgets['base'].isVisible() else '',
                'duration_seconds': widgets['duration'].value(),
                'duration_ms': self.convert_duration_to_ms(widgets['duration'].value()),
                'use_when_full': widgets['use_when_full'].isChecked()
            }
            
            # 設定の検証
            is_valid, error_msg = self.validate_slot_config(slot_config)
            if not is_valid:
                self.log_info(f"スロット{slot_num}設定エラー: {error_msg}")
                return False
            
            # 設定を保存
            if 'flask_slots' not in self.config:
                self.config['flask_slots'] = {}
            
            self.config['flask_slots'][f'slot_{slot_num}'] = slot_config
            self.config_manager.save_config(self.config)
            
            self.log_info(f"スロット{slot_num}の設定を保存しました")
            return True
            
        except Exception as e:
            self.log_info(f"スロット{slot_num}設定保存エラー: {e}")
            return False
    
    def save_all_settings(self):
        """すべての設定を保存"""
        try:
            # 保存前に検証を実行
            errors, warnings = self.validate_all_settings()
            
            if errors:
                # エラーがある場合は保存を停止
                self.show_validation_results(errors, warnings)
                return False
            
            saved_count = 0
            
            # 全スロットの設定を保存
            for slot_num in range(1, 6):
                if self.save_slot_settings(slot_num):
                    saved_count += 1
            
            # Flask全体の有効/無効設定を保存
            if 'flask' not in self.config:
                self.config['flask'] = {}
            self.config['flask']['enabled'] = self.main_window.flask_enabled_cb.isChecked()
            
            # Tincture設定を保存
            self.save_tincture_config()
            
            self.config_manager.save_config(self.config)
            
            # 警告がある場合は表示
            if warnings:
                self.show_validation_results([], warnings)
            
            self.log_info(f"すべての設定を保存しました ({saved_count}/5 スロット)")
            return True
            
        except Exception as e:
            self.log_info(f"設定保存エラー: {e}")
            return False
    
    def validate_and_show_results(self):
        """設定を検証して結果を表示"""
        errors, warnings = self.validate_all_settings()
        self.show_validation_results(errors, warnings)
    
    def save_tincture_config(self):
        """Tincture設定を保存"""
        if 'tincture' not in self.config:
            self.config['tincture'] = {}
        
        # Tincture有効/無効
        self.config['tincture']['enabled'] = self.main_window.tincture_enabled_cb.isChecked()
        
        # 基本キー設定（互換性のため）
        self.config['tincture']['key'] = self.main_window.tincture_key_edit.text()
        
        # Experienced Herbalist設定
        self.config['tincture']['experienced_herbalist'] = self.main_window.experienced_herbalist_cb.isChecked()
        
        # モニター設定
        self.config['tincture']['monitor_config'] = self.main_window.monitor_combo.currentText()
        
        # 感度設定
        sensitivity_ui = self.main_window.sensitivity_slider.value()
        self.config['tincture']['sensitivity'] = sensitivity_ui / 100.0
        
        # チェック間隔
        check_interval_ui = self.main_window.check_interval_spinbox.value()
        self.config['tincture']['check_interval'] = check_interval_ui / 1000.0
        
        # 最小使用間隔
        min_use_interval_ui = self.main_window.min_use_interval_spinbox.value()
        self.config['tincture']['min_use_interval'] = min_use_interval_ui / 1000.0
        
        # 個別Tincture設定
        tincture_configs = {}
        
        # Tincture 1
        tincture_configs['tincture1'] = {
            'folder_path': self.main_window.tincture1_folder_path_label.text(),
            'threshold': self.main_window.tincture1_threshold_spinbox.value()
        }
        
        # Tincture 2 (Experienced Herbalistの場合のみ)
        if self.main_window.experienced_herbalist_cb.isChecked():
            tincture_configs['tincture2'] = {
                'folder_path': self.main_window.tincture2_folder_path_label.text(),
                'threshold': self.main_window.tincture2_threshold_spinbox.value()
            }
        
        self.config['tincture']['tinctures'] = tincture_configs
    
    def convert_duration_to_ms(self, duration_seconds):
        """
        持続時間を秒からミリ秒に変換し、ランダム化を適用
        
        Args:
            duration_seconds: 持続時間（秒）
            
        Returns:
            ミリ秒単位の持続時間（-100ms～0msのランダム減算）
        """
        import random
        
        # 秒をミリ秒に変換
        duration_ms = duration_seconds * 1000
        
        # -100ms～0msのランダム減算を適用
        random_offset = random.randint(-100, 0)
        final_duration = int(duration_ms + random_offset)
        
        # 最小値を100msに制限
        return max(final_duration, 100)
    
    def validate_slot_config(self, config):
        """
        スロット設定の妥当性を検証
        
        Args:
            config: スロット設定の辞書
            
        Returns:
            (有効かどうか, エラーメッセージ)
        """
        # キーが設定されているかチェック
        if not config['key'].strip():
            return False, "割り当てキーが設定されていません"
        
        # Tinctureの場合は追加の検証をスキップ
        if config['is_tincture']:
            return True, ""
        
        # フラスコ設定の検証
        flask_type = config['flask_type']
        rarity = config['rarity']
        detail = config['detail']
        base = config['base']
        
        # FlaskDataManagerを使用した検証
        is_valid, error_msg = self.flask_data_manager.validate_flask_selection(
            flask_type, rarity, detail, base
        )
        
        if not is_valid:
            return False, error_msg
        
        # 持続時間の検証
        if config['duration_seconds'] <= 0:
            return False, "持続時間は0より大きい値を設定してください"
        
        return True, ""
    
    def select_tincture_folder(self, tincture_num):
        """Tinctureフォルダを選択"""
        folder_path = QFileDialog.getExistingDirectory(
            self.main_window,
            f"Tincture {tincture_num}のフォルダを選択",
            "assets/images/tincture/"
        )
        
        if folder_path:
            # パス表示ラベルを更新
            if tincture_num == 1:
                self.main_window.tincture1_folder_path_label.setText(folder_path)
                self.main_window.tincture1_folder_path_label.setStyleSheet("color: black; font-size: 10px;")
            else:
                self.main_window.tincture2_folder_path_label.setText(folder_path)
                self.main_window.tincture2_folder_path_label.setStyleSheet("color: black; font-size: 10px;")
            
            # フォルダ内のファイルを検証
            self.validate_tincture_folder(tincture_num, folder_path)
            
            self.log_info(f"Tincture {tincture_num}フォルダを選択: {folder_path}")
    
    def validate_tincture_folder(self, tincture_num, folder_path):
        """Tinctureフォルダの構造を検証"""
        import os
        
        required_files = ['active', 'idle']
        missing_files = []
        
        for file_type in required_files:
            file_dir = os.path.join(folder_path, file_type)
            if not os.path.exists(file_dir):
                missing_files.append(file_type)
        
        if missing_files:
            self.log_info(f"警告: Tincture {tincture_num}フォルダに必要なサブフォルダが不足: {', '.join(missing_files)}")
        else:
            self.log_info(f"Tincture {tincture_num}フォルダの構造が正常です")
    
    def uncheck_excess_tinctures(self, max_tinctures):
        """制限を超えたTinctureチェックを外す"""
        tincture_slots = []
        
        # Tinctureにチェックされたスロットを収集
        for slot_num, widgets in self.flask_slot_widgets.items():
            if widgets['is_tincture'].isChecked():
                tincture_slots.append(slot_num)
        
        # 制限を超えた場合、後ろから順にチェックを外す
        if len(tincture_slots) > max_tinctures:
            excess_count = len(tincture_slots) - max_tinctures
            for i in range(excess_count):
                slot_num = tincture_slots[-(i+1)]  # 後ろから
                self.flask_slot_widgets[slot_num]['is_tincture'].setChecked(False)
            
            self.log_info(f"Tincture制限により{excess_count}個のスロットのチェックを外しました")
        
        # キー割り当てを更新
        self.update_tincture_key_assignment()
    
    def check_duplicate_unique_flasks(self):
        """重複ユニークフラスコをチェック"""
        unique_flasks = {}
        duplicates = []
        
        for slot_num, widgets in self.flask_slot_widgets.items():
            # Tinctureスロットはスキップ
            if widgets['is_tincture'].isChecked():
                continue
            
            # Uniqueフラスコのみチェック
            if widgets['rarity'].currentText() != "Unique":
                continue
            
            flask_type = widgets['flask_type'].currentText()
            detail = widgets['detail'].currentText() if widgets['detail'].isVisible() else ''
            base = widgets['base'].currentText() if widgets['base'].isVisible() else ''
            
            if not detail:
                continue
            
            # フラスコの識別子を作成
            if flask_type == "Utility":
                flask_id = f"{flask_type}:{base}:{detail}"
            else:
                flask_id = f"{flask_type}:{detail}"
            
            # 重複チェック
            if flask_id in unique_flasks:
                duplicates.append({
                    'flask_id': flask_id,
                    'slot1': unique_flasks[flask_id],
                    'slot2': slot_num
                })
            else:
                unique_flasks[flask_id] = slot_num
        
        return duplicates
    
    def validate_all_settings(self):
        """全設定の包括的な検証"""
        validation_errors = []
        warnings = []
        
        # 1. 重複ユニークフラスコのチェック
        duplicates = self.check_duplicate_unique_flasks()
        for dup in duplicates:
            validation_errors.append(
                f"重複ユニークフラスコ: {dup['flask_id']} (スロット{dup['slot1']} と スロット{dup['slot2']})"
            )
        
        # 2. Tinctureチェック数の検証
        tincture_count = sum(1 for widgets in self.flask_slot_widgets.values() 
                           if widgets['is_tincture'].isChecked())
        max_tinctures = 2 if self.main_window.experienced_herbalist_cb.isChecked() else 1
        
        if tincture_count > max_tinctures:
            validation_errors.append(
                f"Tincture数制限超過: {tincture_count}個設定済み (最大{max_tinctures}個)"
            )
        
        # 3. 各スロットの設定検証
        for slot_num, widgets in self.flask_slot_widgets.items():
            key = widgets['key'].text().strip()
            if not key:
                validation_errors.append(f"スロット{slot_num}: 割り当てキーが未設定")
                continue
            
            # Tinctureスロットの場合
            if widgets['is_tincture'].isChecked():
                # Tinctureフォルダの検証
                if tincture_count >= 1 and slot_num <= tincture_count:
                    tincture_num = 1 if tincture_count == 1 else (1 if slot_num <= tincture_count/2 else 2)
                    folder_path = self.get_tincture_folder_path(tincture_num)
                    if not folder_path or folder_path == "未選択":
                        warnings.append(f"スロット{slot_num}: Tinctureフォルダが未選択")
            else:
                # フラスコスロットの場合
                slot_config = {
                    'key': key,
                    'is_tincture': False,
                    'flask_type': widgets['flask_type'].currentText(),
                    'rarity': widgets['rarity'].currentText(),
                    'detail': widgets['detail'].currentText() if widgets['detail'].isVisible() else '',
                    'base': widgets['base'].currentText() if widgets['base'].isVisible() else '',
                    'duration_seconds': widgets['duration'].value(),
                    'use_when_full': widgets['use_when_full'].isChecked()
                }
                
                is_valid, error_msg = self.validate_slot_config(slot_config)
                if not is_valid:
                    validation_errors.append(f"スロット{slot_num}: {error_msg}")
        
        # 4. キーの重複チェック
        used_keys = {}
        for slot_num, widgets in self.flask_slot_widgets.items():
            key = widgets['key'].text().strip().lower()
            if key:
                if key in used_keys:
                    validation_errors.append(
                        f"キーの重複: '{key}' (スロット{used_keys[key]} と スロット{slot_num})"
                    )
                else:
                    used_keys[key] = slot_num
        
        return validation_errors, warnings
    
    def get_tincture_folder_path(self, tincture_num):
        """Tinctureフォルダパスを取得"""
        if tincture_num == 1:
            return self.main_window.tincture1_folder_path_label.text()
        else:
            return self.main_window.tincture2_folder_path_label.text()
    
    def show_validation_results(self, errors, warnings):
        """検証結果を表示"""
        from PyQt5.QtWidgets import QMessageBox
        
        if not errors and not warnings:
            QMessageBox.information(
                self.main_window,
                "設定検証",
                "すべての設定が正常です。"
            )
            return True
        
        message = ""
        
        if errors:
            message += "以下のエラーが見つかりました:\n\n"
            for i, error in enumerate(errors, 1):
                message += f"{i}. {error}\n"
        
        if warnings:
            if errors:
                message += "\n"
            message += "以下の警告があります:\n\n"
            for i, warning in enumerate(warnings, 1):
                message += f"{i}. {warning}\n"
        
        if errors:
            QMessageBox.critical(
                self.main_window,
                "設定エラー",
                message
            )
            return False
        else:
            QMessageBox.warning(
                self.main_window,
                "設定警告",
                message
            )
            return True
"""
Skills tab for POE Macro GUI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, 
                             QGridLayout, QCheckBox, QPushButton, QHBoxLayout)
from .base_tab import BaseTab

class SkillsTab(BaseTab):
    """Skills settings tab"""
    
    def create_widget(self):
        """Create skills tab widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        skills_group = QGroupBox("スキル自動使用設定")
        skills_layout = QGridLayout(skills_group)
        
        self.main_window.skills_enabled_cb = QCheckBox("スキル自動使用を有効化")
        skills_enabled = self.get_config_value('skills', 'enabled', True)
        
        # デバッグログ追加
        self.logger.debug(f"Skills tab - loaded enabled value: {skills_enabled}")
        
        self.main_window.skills_enabled_cb.setChecked(skills_enabled)
        self.main_window.skills_enabled_cb.stateChanged.connect(self.on_skills_enabled_changed)
        self.main_window.skills_enabled_cb.stateChanged.connect(self.save_skills_settings)  # 自動保存を追加
        skills_layout.addWidget(self.main_window.skills_enabled_cb, 0, 0, 1, 2)
        
        # 設定保存ボタン
        button_layout = QHBoxLayout()
        save_btn = QPushButton("設定を保存")
        save_btn.clicked.connect(self.save_skills_settings)
        save_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        button_layout.addWidget(save_btn)
        
        apply_btn = QPushButton("設定を適用（保存せずに）")
        apply_btn.clicked.connect(self.apply_skills_settings)
        apply_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
        button_layout.addWidget(apply_btn)
        
        skills_layout.addLayout(button_layout, 1, 0, 1, 2)
        
        layout.addWidget(skills_group)
        layout.addStretch()
        
        return widget
    
    def on_skills_enabled_changed(self, state):
        """スキル有効化チェックボックスの状態変更時の処理"""
        try:
            self.log_info(f"スキル自動使用: {'有効' if state else '無効'}")
        except Exception as e:
            self.logger.error(f"Error in on_skills_enabled_changed: {e}")
    
    def save_skills_settings(self):
        """スキル設定を保存"""
        try:
            # スキル有効/無効設定を更新
            if 'skills' not in self.config:
                self.config['skills'] = {}
            
            checkbox_state = self.main_window.skills_enabled_cb.isChecked()
            self.config['skills']['enabled'] = checkbox_state
            
            # デバッグログ追加
            self.logger.debug(f"Saving skills settings - checkbox state: {checkbox_state}")
            self.logger.debug(f"Skills config before save: {self.config.get('skills', {})}")
            
            # 設定を保存
            self.config_manager.save_config(self.config)
            
            # 保存後の確認
            saved_config = self.config_manager.load_config()
            saved_enabled = saved_config.get('skills', {}).get('enabled', 'NOT_FOUND')
            self.logger.debug(f"Skills config after save: {saved_enabled}")
            
            # MacroControllerに反映
            if self.main_window.macro_controller:
                skills_config = self.config.get('skills', {})
                if hasattr(self.main_window.macro_controller, 'skill_module'):
                    self.main_window.macro_controller.skill_module.update_config(skills_config)
                    self.log_info("スキル設定をMacroControllerに反映しました")
            
            self.log_info(f"スキル設定を保存しました (enabled: {checkbox_state})")
            
        except Exception as e:
            self.log_error(f"スキル設定保存エラー: {e}")
            self.logger.error(f"Error saving skills settings: {e}")
    
    def apply_skills_settings(self):
        """スキル設定を適用（保存せずに）"""
        try:
            if not self.main_window.macro_controller:
                self.log_info("スキル設定適用: MacroControllerが利用できません")
                return
            
            # 一時的な設定を作成
            temp_config = self.config.get('skills', {}).copy()
            temp_config['enabled'] = self.main_window.skills_enabled_cb.isChecked()
            
            # 実行中のモジュールに適用
            if hasattr(self.main_window.macro_controller, 'skill_module'):
                self.main_window.macro_controller.skill_module.update_config(temp_config)
                self.log_info("スキル設定を一時適用しました")
            else:
                self.log_info("スキル設定適用: SkillModuleが利用できません")
                
        except Exception as e:
            self.log_error(f"スキル設定適用エラー: {e}")
            self.logger.error(f"Error applying skills settings: {e}")
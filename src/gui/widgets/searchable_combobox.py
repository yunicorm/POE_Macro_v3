"""
Searchable ComboBox widget for POE Macro GUI
"""
from PyQt5.QtWidgets import QComboBox, QCompleter, QLineEdit
from PyQt5.QtCore import Qt

class SearchableComboBox(QComboBox):
    """検索可能なコンボボックス"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 編集可能にする
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        
        # コンプリーター設定
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.setCompleter(self.completer)
        
    def addItems(self, items):
        """アイテムを追加（オーバーライド）"""
        super().addItems(items)
        # コンプリーターのモデルを更新
        self.completer.setModel(self.model())
        
    def focusInEvent(self, event):
        """フォーカスイン時の処理"""
        super().focusInEvent(event)
        # テキストを全選択
        self.lineEdit().selectAll()
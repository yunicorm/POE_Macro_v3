"""
Searchable ComboBox widget for POE Macro GUI
"""
from PyQt5.QtWidgets import QComboBox, QCompleter, QLineEdit
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QStringListModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class SearchableComboBox(QComboBox):
    """検索可能なコンボボックス"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        
        # フィルタリング用のプロキシモデル
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        
        # コンプリーター設定
        self.completer = QCompleter(self)
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        
        # モデル設定
        self.source_model = QStandardItemModel(self)
        self.proxy_model.setSourceModel(self.source_model)
        self.setModel(self.proxy_model)
        self.completer.setModel(self.proxy_model)
        self.setCompleter(self.completer)
        
        # テキスト変更時のフィルタリング
        self.lineEdit().textChanged.connect(self.filter_items)
        
        # フォーカスイン時の処理
        self.lineEdit().installEventFilter(self)
        
        # 元のアイテムリストを保持
        self._items = []
        
    def addItems(self, items):
        """アイテムを追加（オーバーライド）"""
        self._items = items
        self.source_model.clear()
        for item in items:
            self.source_model.appendRow(QStandardItem(item))
        
    def clear(self):
        """アイテムをクリア（オーバーライド）"""
        self._items = []
        self.source_model.clear()
        
    def filter_items(self, text):
        """アイテムをフィルタリング"""
        if not text:
            # テキストが空の場合は全て表示
            self.proxy_model.setFilterFixedString("")
        else:
            # 部分一致でフィルタリング
            self.proxy_model.setFilterRegExp(text)
            
    def eventFilter(self, obj, event):
        """イベントフィルター"""
        if obj == self.lineEdit():
            if event.type() == event.FocusIn:
                # フォーカスイン時にポップアップを表示
                self.showPopup()
                # テキストを全選択
                self.lineEdit().selectAll()
        return super().eventFilter(obj, event)
    
    def showPopup(self):
        """ポップアップ表示（オーバーライド）"""
        # 現在のフィルタをクリアして全アイテムを表示
        self.proxy_model.setFilterFixedString("")
        super().showPopup()
        
    def setCurrentText(self, text):
        """現在のテキストを設定（オーバーライド）"""
        # 正確なアイテムを選択
        index = self.findText(text, Qt.MatchExactly)
        if index >= 0:
            self.setCurrentIndex(index)
        else:
            self.lineEdit().setText(text)
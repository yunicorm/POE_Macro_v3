# 画像認識システム

## 概要
OpenCVテンプレートマッチングを使用した高精度な画像認識システム。Tinctureのアイコン状態（Active/Idle）を検出し、自動使用機能を支援します。

## 主要機能

### TinctureDetectorクラス
- **複数状態検出**: Active・Idle状態の両方を検出
- **統一状態取得**: get_tincture_state()による状態統合
- **高速キャプチャ**: mssライブラリによる最適化
- **感度調整**: 0.0-1.0の範囲での検出感度設定

### 検出モード
- **manual**: 手動設定エリアでの検出
- **auto_slot3**: 従来の3番スロット自動計算（60x100）
- **full_flask_area**: フラスコエリア全体検出（398x130）

### テンプレート管理
- **Idle状態**: sap_of_the_seasons_idle.png
- **Active状態**: sap_of_the_seasons_active.png
- **フォールバック**: テンプレート読み込み失敗時の安全な処理
- **下位互換性**: 既存のdetect_tincture_icon()維持

## 技術仕様

### 画像処理
- **OpenCVテンプレートマッチング**: cv2.matchTemplate使用
- **グレースケール変換**: 処理速度向上
- **信頼度評価**: min/max値による検出判定
- **エリア限定**: 指定された検出エリアでの処理

### 最適化技術
- **単一テンプレート方式**: 複雑な解像度別対応から簡略化
- **メモリ効率**: 不要なオブジェクト生成削減
- **CPU最適化**: 検出ロジックの軽量化
- **キャッシュ活用**: テンプレート読み込みの最適化

### 座標変換
- **スクリーン座標**: グローバル座標系
- **モニター相対**: 各モニターでの相対座標
- **解像度対応**: 複数解像度での適切な座標変換
- **エリア計算**: フラスコエリアからの座標算出

## 検出エリア拡張

### 検出範囲比較
- **従来（3番スロット）**: 60x100 (6,000 px²)
- **新機能（フラスコ全体）**: 398x130 (51,740 px²)
- **改善率**: 8.6倍の検出範囲拡大

### AreaSelector統合
- **フラスコエリア設定**: オーバーレイによる視覚的設定
- **自動座標計算**: 設定エリアからの検出範囲算出
- **設定永続化**: detection_areas.yamlでの保存
- **GUI連携**: 設定変更の即座反映

## 状態検出ロジック

### 優先順位制御
```python
def get_tincture_state(self) -> str:
    # 優先順位: Active > Idle > Unknown
    if self.detect_tincture_active():
        return "ACTIVE"
    elif self.detect_tincture_idle():
        return "IDLE"
    else:
        return "UNKNOWN"
```

### 検出結果
- **ACTIVE**: Tincture効果が発動中
- **IDLE**: Tincture使用可能状態
- **UNKNOWN**: 検出不可・エラー状態

## パフォーマンス

### 処理速度
- **CPU使用率**: 5%以下（100ms間隔での検出）
- **検出遅延**: 最大100ms
- **メモリ使用量**: 最適化済み
- **スレッドセーフ**: 完全対応

### エラーハンドリング
- **テンプレート読み込み失敗**: フォールバック処理
- **画面キャプチャエラー**: 安全な継続動作
- **座標エラー**: デフォルトエリアでの処理
- **感度設定エラー**: フォールバック値使用

## 実装ファイル
- **src/features/image_recognition.py**: メイン実装
- **src/features/area_selector.py**: エリア選択機能
- **assets/images/tincture/**: テンプレート画像
- **config/detection_areas.yaml**: エリア設定

## 設定例
```yaml
tincture:
  sensitivity: 0.65
  detection_mode: "full_flask_area"
  check_interval: 100
  min_use_interval: 1000
```

## テスト
- **test_active_detection.py**: Active状態検出テスト
- **test_detection_area_update.py**: エリア更新テスト
- **test_manual_detection_mode.py**: 手動モードテスト

## 効果
- **検出精度向上**: フラスコエリア全体での検出により見逃し大幅減少
- **柔軟性向上**: 画面解像度・UIレイアウト変更に対応
- **設定簡便性**: オーバーレイ視覚設定が検出エリアに直接反映
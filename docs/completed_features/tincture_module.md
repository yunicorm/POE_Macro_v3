# Tincture自動使用モジュール

## 概要
Path of ExileのTincture（ポーション強化アイテム）を自動的に使用するモジュール。画像認識技術を使用してTinctureのアイコン状態を監視し、適切なタイミングで自動使用を行います。

## 主要機能

### Active状態検出機能
- **detect_tincture_active()**: Active状態の検出機能
- **get_tincture_state()**: 統一状態取得（ACTIVE/IDLE/UNKNOWN）
- **下位互換性**: 既存コードとの完全互換性維持

### スマート状態管理
- **Active状態時**: 使用せず効果維持
- **Idle状態時**: 新たに使用して効果発動
- **状態遷移ログ**: 詳細な状態変化追跡
- **統計情報拡張**: active_detections、idle_detections、unknown_detections

### 検出エリア拡張
- **3つの検出モード**:
  - `manual`: 手動設定エリア使用
  - `auto_slot3`: 従来の3番スロット自動計算
  - `full_flask_area`: フラスコエリア全体使用（推奨）
- **検出範囲**: 8.6倍拡大（60x100 → 398x130）

### 感度設定
- **動的感度更新**: リアルタイムでの感度調整
- **ハードコーディング除去**: 設定ファイルからの動的読み込み
- **GUI保存機能**: スライダー変更の永続化

## 技術仕様

### 画像認識
- **テンプレートマッチング**: OpenCV使用
- **複数テンプレート対応**: Idle + Active両方
- **高速画面キャプチャ**: mssライブラリ使用
- **感度調整**: 0.0-1.0の範囲で設定可能

### スレッド処理
- **非同期監視**: 独立スレッドでの動作
- **統計管理**: スレッドセーフな統計情報
- **適切なクリーンアップ**: 停止時の安全な処理

### 設定管理
- **YAML設定**: default_config.yamlでの統一管理
- **動的更新**: 実行中の設定変更対応
- **フォールバック**: 設定エラー時の安全な動作

## 使用効果

### パフォーマンス向上
- **無駄な再使用防止**: Active状態中は使用しない
- **CPU軽減**: 効率的な検出ループ
- **メモリ最適化**: 不要なオブジェクト生成削減

### 使用パターン
```
従来: Idle検出→使用→即座に再検出→無駄な再使用
改良: Idle検出→使用→Active維持→効果終了→Idle→再使用
```

### 統計情報
- **total_uses**: 使用回数
- **active_detections**: Active状態検出回数
- **idle_detections**: Idle状態検出回数
- **unknown_detections**: 不明状態検出回数

## 実装ファイル
- **src/modules/tincture_module.py**: メインモジュール
- **src/features/image_recognition.py**: 画像認識エンジン
- **config/default_config.yaml**: 設定ファイル
- **assets/images/tincture/**: テンプレート画像

## テスト
- **test_active_detection.py**: Active状態検出テスト
- **test_tincture_settings_save.py**: GUI保存機能テスト
- **test_tincture_complete_workflow.py**: 包括的動作確認
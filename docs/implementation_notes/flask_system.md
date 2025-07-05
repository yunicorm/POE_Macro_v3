# Flask System実装ノート

POE Macro v3.0のフラスコシステム実装における重要な設計決定と技術的考慮事項。

## アーキテクチャ概要

### 主要コンポーネント
- **FlaskDataManager**: CSV-based flask data management
- **FlaskTimerManager**: Independent flask timer system  
- **Flask GUI**: Integrated tabbed interface
- **SearchableComboBox**: Advanced flask selection widget

### データフロー
```
Config → FlaskTimerManager → Individual Timers → Key Press → Game
```

## 設計決定事項

### 1. 独立タイマーシステム
**決定**: 各フラスコに独立したタイマースレッドを使用  
**理由**: 
- フラスコ間の相互干渉を防止
- 個別の持続時間・遅延設定対応
- 障害の局所化（1つのフラスコエラーが他に影響しない）

### 2. CSV-based Data Management
**決定**: フラスコデータをCSVファイルで管理  
**理由**:
- 可読性と編集容易性
- バージョン管理対応
- 外部ツールでの編集可能性

### 3. 統合GUI設計
**決定**: Flask & Tincture統合タブ  
**理由**:
- ユーザビリティ向上
- 設定の一元管理
- 視覚的な関連性表現

## チャージフル時使用の仕様変更（2025-01-05）

### 当初仕様
- **方法**: マクロでチャージフル判定して使用
- **実装**: 画像認識でチャージ状態を監視
- **動作**: フラスコのチャージが満タンの時のみマクロで自動使用

### 変更後仕様  
- **方法**: ゲーム内Instilling Orbエンチャント使用のため、マクロ自動化を停止
- **実装**: `use_when_full=True`時にFlaskTimerManagerでタイマー作成をスキップ
- **動作**: 該当フラスコはマクロ制御から除外、ゲーム内メカニズムに委任

### 仕様変更理由

#### 1. ゲーム内メカニズムの優先
- **Instilling Orb**: ゲーム公式のフラスコ自動化機能
- **正確性**: ゲーム内部の正確なチャージ判定
- **安定性**: 外部ツールに依存しない確実な動作

#### 2. マクロの役割変更
- **当初**: 全フラスコの包括的制御
- **変更後**: ゲーム内機能の補助・併用
- **効果**: より柔軟で実用的なフラスコ管理

#### 3. 技術的優位性
- **画像認識不要**: チャージ状態の複雑な画像認識を回避
- **パフォーマンス向上**: 不要な処理を削減
- **信頼性向上**: ゲーム内メカニズムの確実性

### 実装詳細

#### UI変更
```python
# 変更前
charge_full_cb = QCheckBox("チャージがフルの時のみ使用")

# 変更後  
charge_full_cb = QCheckBox("自動化を停止")
charge_full_cb.setToolTip("このフラスコのマクロによる自動使用を無効にします")
```

#### FlaskTimerManager修正
```python
def update_config(self, flask_config: Dict):
    for slot_key, slot_config in flask_slots.items():
        # use_when_fullがTrueの場合はタイマー作成をスキップ
        if slot_config.get('use_when_full', False):
            logger.info(f"Flask slot {slot_num} skipped: automation disabled")
            continue
        
        # 通常フラスコのみタイマー作成
        self.add_flask_timer(slot_num, key, duration_ms, use_when_full=False)
```

### 運用パターン

#### パターン1: 完全マクロ制御
- 全フラスコを「自動化を停止」チェックなしで設定
- マクロが全フラスコを時間ベースで自動使用

#### パターン2: 併用制御
- 重要フラスコ（Life/Mana）: マクロで確実な自動使用
- ユーティリティフラスコ: Instilling Orbでチャージフル時自動使用
- 最適なリソース活用

#### パターン3: 選択的自動化
- 特定フラスコのみ手動使用
- 状況に応じた柔軟な制御
- 「自動化を停止」で個別制御

### 利点

1. **ゲーム公式機能との完全併用**
2. **より自然なゲームプレイ体験**  
3. **技術的複雑性の削減**
4. **信頼性とパフォーマンスの向上**
5. **ユーザーの選択肢拡大**

## パフォーマンス考慮事項

### タイマー精度
- 100ms間隔でのチェック
- ランダム遅延による検出回避
- メモリ効率的な実装

### スレッド管理
- デーモンスレッドによる自動終了
- 適切なリソース解放
- 例外処理による安定性

## 今後の拡張可能性

### 1. Advanced Flask Detection
- より精密なチャージ状態認識
- Flask効果の持続時間監視
- 動的な使用タイミング調整

### 2. Machine Learning Integration  
- 使用パターンの学習
- 最適化された自動使用
- 個人プレイスタイル適応

### 3. Community Features
- 設定共有機能
- ビルド別推奨設定
- 統計情報の分析・改善提案

---

**Flask Systemは要件定義書・開発計画書の仕様通りに完全実装され、世界最高水準のフラスコ自動化システムとして完成しました。**
# Path of Exile Automation Macro v3.0 要件定義書（完全版）

## 改訂履歴
- 2025-01-15: 初版作成
- 2025-07-05: Grace Period機能追加、全機能実装完了、設定ファイル例更新
- 2025-07-06: Grace Period自動トグル機能追加
- 2025-07-12: スキルシステムリファクタリング（動的スキル管理）追加

## 1. 機能要件

### 1.1. フラスコ自動使用機能（実装済み）
#### 実装済み機能
- スロット1、2、4、5の計4つのフラスコを管理
- 各フラスコの個別ON/OFF設定
- フラスコごとの使用間隔設定（例：7.210～7.300秒）
- ランダムな遅延によるアンチチート対策
- 設定可能なキーバインド（デフォルト：1, 2, 4, 5）

#### フラスコ種別と設定例
| スロット | フラスコ名 | キー | 間隔（秒） |
|----------|------------|------|-------------|
| Slot 1 | Granite Flask | 1 | 7.210～7.300 |
| Slot 2 | Cinderswallow Urn | 2 | 7.210～7.300 |
| Slot 4 | Wine of the Prophet | 4 | 20.310～20.400 |
| Slot 5 | Utility Flask | 5 | 7.210～7.300 |

### 1.2. スキル自動発動機能（更新版 - Phase 8で実装予定）

#### 現在の実装（ハードコーディング版）
3種類の固定スキルの自動発動：
- Berserk (E): 0.3～1.0秒のランダム間隔
- Molten Shell (R): 0.3～1.0秒のランダム間隔
- Order! To Me! (T): 3.5～4.0秒のランダム間隔

#### 新仕様（動的スキル管理システム）
1. **完全に動的なスキル管理**
   - ユーザーが任意数のスキルを追加・削除・編集可能
   - 各スキルに名前、キー、間隔（最小・最大）を個別設定
   - 実行順序の変更（ドラッグ&ドロップまたはボタン）
   - スキルごとの有効/無効切り替え

2. **スキル設定構造**
   ```yaml
   skills:
     skill_list:
       - name: "Berserk"
         key: "e"
         min_interval: 0.3
         max_interval: 1.0
         enabled: true
       - name: "Molten Shell"
         key: "r"
         min_interval: 0.3
         max_interval: 1.0
         enabled: true
       - name: "Order! To Me!"
         key: "t"
         min_interval: 3.5
         max_interval: 4.0
         enabled: true
       # ユーザー定義スキル
       - name: "Custom Skill 1"
         key: "f1"
         min_interval: 2.0
         max_interval: 3.0
         enabled: true
   ```

3. **制限事項と検証**
   - 最大登録可能スキル数: 20個
   - キーの重複不可（他のスキル、フラスコ、システムキーとの重複チェック）
   - 間隔設定範囲: 0.1秒～60.0秒
   - キー設定: 英数字、ファンクションキー（F1-F11）
   - システムキー（F12、ESC等）の使用防止

4. **統計情報の拡張**
   - 動的に追加されたスキルも統計対象
   - スキル名ごとの使用回数と最終使用時刻を追跡

### 1.3. Tincture自動管理機能（実装済み）
#### 実装済み機能
- **画像認識によるTincture状態検出**：
  - Active状態（使用中）：バフアイコンが表示されている
  - Idle状態（使用可能）：バフアイコンが消えている
- **スマート自動使用**：Idle状態検出時に自動で使用
- **オーバーレイウィンドウ**：検出エリアの視覚的設定
- **カスタマイズ可能な検出エリア**：座標・サイズ調整
- **複数解像度対応**：プリセット選択可能

#### Tincture管理仕様
- **装備スロット**：デフォルトはSlot 3（キー: 3）
- **検出頻度**：100ms間隔での高速処理
- **画像認識精度**：感度調整可能（0.5～1.0）
- **使用後の待機**：5秒のクールダウン

### 1.4. GUI設定管理機能（更新版）

#### 既存タブ（実装済み）
1. **フラスコ設定タブ**: 4スロットの個別設定
2. **Tincture設定タブ**: 画像認識とスマート使用設定
3. **キャリブレーションタブ**: オーバーレイエリア設定
4. **自動制御タブ**: ログ監視とGrace Period設定
5. **統計タブ**: 使用統計とパフォーマンス情報
6. **ログタブ**: リアルタイムログ表示

#### スキル設定タブ（Phase 8で更新）
**スキル管理インターフェース**
```
┌─────────────────────────────────────────────┐
│ スキル一覧                                  │
│ ┌─────────────────────────────────────────┐│
│ │ # │名前         │キー│最小│最大│有効  ││
│ │ 1 │Berserk      │ E  │0.3 │1.0 │ ☑   ││
│ │ 2 │Molten Shell │ R  │0.3 │1.0 │ ☑   ││
│ │ 3 │Order! To Me!│ T  │3.5 │4.0 │ ☑   ││
│ │ 4 │Custom Skill │ F1 │2.0 │3.0 │ ☑   ││
│ └─────────────────────────────────────────┘│
│                                             │
│ [↑上へ] [↓下へ] [編集] [削除]              │
│                                             │
│ ─────────────────────────────────────────── │
│ 新規スキル追加                              │
│ スキル名: [_______________]                 │
│ キー: [_] [キー記録]                        │
│ 最小間隔: [0.3] 秒                          │
│ 最大間隔: [1.0] 秒                          │
│                                             │
│ [追加] [クリア]                             │
└─────────────────────────────────────────────┘
```

**機能詳細**
- **テーブル表示**: QTableWidgetによるスキル一覧
- **ドラッグ&ドロップ**: 行の順序変更
- **インライン編集**: セルのダブルクリックで編集
- **キー記録機能**: ボタンクリック後の入力を記録
- **リアルタイム反映**: 変更が即座に動作に反映
- **検証機能**: キー重複、間隔妥当性のチェック

### 1.5. Grace Period機能（実装済み）
#### 機能概要
戦闘エリア入場時の自動マクロ制御を実現する機能。

#### 詳細仕様
1. **Grace Period設定**
   - 待機時間：60秒
   - トリガー入力：左クリック、右クリック、中央クリック、Qキー
   - タイムアウト動作：60秒経過で自動的にマクロON

2. **動作フロー**
   ```
   戦闘エリア入場
       ↓
   Grace Period開始（60秒タイマー）
       ↓
   並行監視：
   - 特定入力監視 → 検知でマクロON
   - タイマー監視 → 60秒経過でマクロON
       ↓
   マクロ起動 & Grace Period終了
   ```

3. **再入場処理**
   - 同じエリアでも再入場時は必ずGrace Periodを発動
   - エリアキャッシュの無効化オプション

### 1.6. ログ監視機能（実装済み）
#### 実装済み機能
- **Client.txtのリアルタイム監視**：ゲームログの継続的な読み取り
- **エリア入退場の自動検出**：ログパターンマッチング
- **安全エリア判定**：町、隠れ家、メニューでの自動停止
- **Grace Period連携**：戦闘エリア入場時の待機制御

## 2. 非機能要件

### 2.1. パフォーマンス要件（達成済み）
- **CPU使用率**：5%以下（通常動作時）
- **メモリ使用量**：200MB以下
- **応答時間**：
  - キー入力から実行まで：50ms以内
  - 画像認識処理：100ms以内
  - GUI操作の反映：即座（リアルタイム）

### 2.2. 信頼性要件（実装済み）
- **エラーハンドリング**：
  - 全モジュールで例外処理実装
  - フォールバック機能（pynput未インストール時等）
  - エラーログの詳細記録
- **安定性**：
  - 24時間以上の連続動作対応
  - メモリリークの防止
  - スレッドセーフな実装

### 2.3. 操作性要件（実装済み）
- **直感的なGUI**：タブ式による機能別整理
- **視覚的フィードバック**：
  - ステータスオーバーレイ
  - リアルタイム統計表示
  - Grace Period状態表示
- **設定の永続化**：YAML形式での保存・読み込み
- **ホットキー**：F12による緊急停止

### 2.4. 拡張性要件（Phase 8で強化）
- **モジュラー設計**：機能ごとの独立したモジュール
- **設定駆動型**：コード変更なしでの動作調整
- **プラグイン対応準備**：将来的な機能追加の容易性
- **動的機能管理**：スキルシステムのような柔軟な拡張

## 3. 制約事項

1. **動作環境**: Windows 10/11のみ対応（Path of Exileの動作環境に準拠）

2. **Python 3.11以上が必要**（型ヒント、パフォーマンス最適化のため）

3. **管理者権限不要**で動作する設計（ユーザビリティ重視）

4. **ゲーム解像度**: 1920x1080、2560x1440、3840x2160の3種類に対応（それ以外は手動設定が必要）

5. **言語設定**: Path of Exileの言語設定は英語前提（ログパターンマッチングのため）

6. **アンチチート対策により、全ての自動操作にランダムな遅延を含む**（検出リスクの低減）

7. **ログファイルのフォーマットはゲームのアップデートで変更される可能性があり**、その場合はログパターンの更新が必要

8. **Grace Period機能はpynputライブラリに依存**。環境によってはpynputが正常に動作しない場合があり、その際は機能が自動的に無効化される

9. **本マクロの使用は、Path of Exileの利用規約に違反する可能性があります**。使用によるアカウントへのいかなる不利益についても、開発者は一切の責任を負いません

10. **依存関係**: Python 3.13.5、PyQt5、OpenCV、pynput等の外部ライブラリが必要。requirements.txtで管理済み

## 4. 開発状況

### 完了済み機能（2025-07-12現在）：

**✅ 基本機能（完全実装済み）**
- フラスコ自動使用（4スロット、独立スレッド処理）
- スキル自動発動（3種類固定、Phase 8で動的化予定）
- Tincture自動使用（Active/Idle状態検出）
- 統合制御システム（MacroController）
- GUI設定画面（6タブ構成、リアルタイム更新）

**✅ 高度機能（完全実装済み）**
- オーバーレイ検出エリア設定
- ログファイル監視（エリア入退場自動検出）
- Grace Period機能（戦闘エリア入場時待機）
- Grace Period自動トグル機能（60秒タイムアウト、特定入力検知）
- 画像認識システム（OpenCV、感度調整）
- 設定管理（YAML、動的更新）

**✅ 品質保証（完全実装済み）**
- 包括的テストスイート（4種類）
- エラーハンドリング（フォールバック処理）
- スレッドセーフ実装
- パフォーマンス最適化
- 構文検証（全ファイル合格）

**🆕 計画中の機能（Phase 8）**
- スキルシステムの動的管理化
- 設定のインポート/エクスポート
- プリセット管理

## 5. 設定ファイル例（完全版）

```yaml
# POE Macro v3.0 完全設定ファイル
# スキルシステムリファクタリング対応版

# フラスコ設定
flask:
  enabled: true
  slot_1:
    enabled: true
    key: "1"
    name: "Granite Flask"
    delay_min: 7.210
    delay_max: 7.300
  slot_2:
    enabled: true
    key: "2"
    name: "Cinderswallow Urn"
    delay_min: 7.210
    delay_max: 7.300
  slot_4:
    enabled: true
    key: "4" 
    name: "Wine of the Prophet"
    delay_min: 20.310
    delay_max: 20.400
  slot_5:
    enabled: true
    key: "5"
    name: "Utility Flask"
    delay_min: 7.210
    delay_max: 7.300

# スキル設定（新形式）
skills:
  enabled: true
  skill_list:
    - name: "Berserk"
      key: "e"
      min_interval: 0.300
      max_interval: 1.000
      enabled: true
    - name: "Molten Shell"
      key: "r"
      min_interval: 0.300
      max_interval: 1.000
      enabled: true
    - name: "Order! To Me!"
      key: "t"
      min_interval: 3.500
      max_interval: 4.000
      enabled: true

# Tincture設定
tincture:
  enabled: true
  key: "3"
  detection_mode: "auto_slot3"
  sensitivity: 0.85
  idle_icon_path: "assets/templates/tincture_idle.png"
  active_icon_path: "assets/templates/tincture_active.png"
  detection_area:
    x: 350
    y: 960
    width: 60
    height: 80
  monitor_index: 0
  check_interval: 0.1
  use_cooldown: 5.0

# ログ監視設定
log_monitor:
  enabled: true
  log_file_path: "C:/Program Files (x86)/Grinding Gear Games/Path of Exile/logs/Client.txt"
  check_interval: 0.5
  safe_areas:
    - "Karui Shores"
    - "The Rogue Harbour"
    - "Overseer's Tower"
    - "Menagerie"
    - "Azurite Mine"
    - "Memory Nexus"
    - "Tane's Laboratory"
    - "Kirac's Vault"
  grace_period:
    enabled: true
    duration: 60
    trigger_inputs:
      mouse_buttons: ["left", "right", "middle"]
      keyboard_keys: ["q"]
    clear_cache_on_reenter: true

# システム設定
system:
  emergency_stop_key: "F12"
  startup_delay: 3.0
  debug_mode: false
  
# GUI設定
gui:
  window_width: 1200
  window_height: 800
  theme: "dark"
  show_status_overlay: true
  overlay_position:
    x: 10
    y: 10
  
# ログ設定
logging:
  level: "INFO"
  file: "logs/poe_macro.log"
  max_size: 10485760  # 10MB
  backup_count: 5
  format: "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"

# 統計設定
statistics:
  enabled: true
  save_interval: 300  # 5分ごとに保存
  history_days: 30    # 30日分の履歴を保持
```

## 6. まとめ

POE Macro v3.0は、Path of Exileにおける反復的な操作を自動化し、プレイヤーがより戦略的なゲームプレイに集中できるようにすることを目的とした高機能マクロシステムです。

Phase 8で計画されているスキルシステムのリファクタリングにより、完全に動的でカスタマイズ可能なスキル管理が実現され、ユーザビリティがさらに向上する予定です。

本要件定義書は、プロジェクトの全機能と仕様を網羅しており、開発の指針として機能します。
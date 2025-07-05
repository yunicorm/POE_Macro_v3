# Path of Exile Automation Macro v3.0 要件定義書（完全版）

## 改訂履歴
- 2025-01-15: 初版作成
- 2025-07-05: Grace Period機能追加、全機能実装完了、設定ファイル例更新
- 2025-07-06: Grace Period自動トグル機能追加

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

### 1.2. スキル自動発動機能（実装済み）
#### 実装済み機能
- 3種類のスキルの自動発動
- 個別のON/OFF設定
- ランダムな使用間隔設定
- 独立したスレッドによる非同期処理

#### スキル設定例
| スキル名 | キー | 間隔（秒） | 説明 |
|----------|------|-------------|------|
| Berserk | E | 0.3～1.0 | 攻撃スキル、高頻度 |
| Molten Shell | R | 0.3～1.0 | 防御スキル、高頻度 |
| Order! To Me! | T | 3.5～4.0 | ミニオンコマンド、低頻度 |

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

### 1.4. Grace Period自動トグル機能（新規追加）
#### 機能概要
戦闘エリア入場時の自動マクロ制御を実現する機能。既存のGrace Period機能を拡張。

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
   - エリアキャッシュの無効化

4. **設定例**
   ```yaml
   log_monitor:
     grace_period:
       enabled: true
       duration: 60
       trigger_inputs:
         mouse_buttons: ["left", "right", "middle"]
         keyboard_keys: ["q"]
       clear_cache_on_reenter: true
   ```

### 1.5. 画像認識システム（実装済み）
#### TinctureDetectorクラス仕様
- **画像認識エンジン**：OpenCV テンプレートマッチング
- **対応解像度**：1920x1080、2560x1440、3840x2160
- **モニター設定**：Primary、Center、Right
- **検出モード**：
  - Manual（手動設定エリア）
  - Auto Slot 3（自動計算位置）
  - Full Flask Area（フラスコエリア全体）

#### 実装詳細
- テンプレート画像による状態検出
- リアルタイム画面キャプチャ（mssライブラリ使用）
- マルチスレッド対応による非ブロッキング処理
- 設定ファイルによる座標管理

### 1.6. GUI設定管理機能（実装済み）
#### 実装済み機能
- **タブ式インターフェース**: PyQt5による6タブ構成
- **リアルタイム設定変更**: GUI変更の即座反映
- **統計情報表示**: 各モジュールの使用統計
- **手動操作機能**: テスト・デバッグ用手動実行
- **設定永続化**: YAML設定ファイル自動保存
- **MacroController統合**: 実際のマクロ制御連携

#### タブ構成

**1. フラスコ設定タブ**

| 設定項目 | 内容 |
|----------|------|
| スロット番号 | 1～5のフラスコスロット |
| フラスコ名称 | ドロップダウンまたはテキスト入力（例：Granite Flask, Cinderswallow Urn, Wine of the Prophet等） |
| 割り当てキー | キーバインド設定（デフォルト：1, 2, 4, 5） |
| ループ間隔 | 最小値～最大値の範囲設定（例：7.210～7.300秒） |
| 有効/無効 | 各スロットの自動使用ON/OFF |

**2. Tincture設定タブ**

| 設定項目 | 内容 |
|----------|------|
| Tincture名称 | 使用するTinctureの選択（例：Sap of the Seasons） |
| 装備スロット | キーバインド設定（デフォルト：3） |
| 検出感度 | 画像認識の閾値調整 |
| 有効/無効 | Tincture自動使用のON/OFF |

**3. スキル設定タブ**

| 設定項目 | 内容 |
|----------|------|
| スキル名称 | スキル名の入力（例：Berserk, Molten Shell, Order! To Me!） |
| 割り当てキー | キーバインド設定（デフォルト：E, R, T） |
| 使用間隔 | 最小値～最大値の範囲設定（例：0.3～1.0秒） |
| 有効/無効 | 各スキルの自動使用ON/OFF |

**4. 全般設定タブ**

| 設定項目 | 内容 |
|----------|------|
| マクロ開始/停止キー | グローバルホットキーの設定（デフォルト：F12） |
| 緊急停止キー | 緊急停止用キーの設定（デフォルト：Ctrl+Shift+F12） |
| ログレベル | デバッグ情報の出力レベル |
| 画面解像度 | ゲーム画面の解像度確認・調整 |
| デバッグモード | 画像認識結果の可視化、マッチング精度の表示 |
| テストモード | 各機能の個別テスト実行 |

**5. 自動制御タブ**

| 設定項目 | 内容 |
|----------|------|
| ログ監視 | ログファイル監視機能のON/OFF |
| ログファイルパス | Client.txtの場所（デフォルトパスから変更可能） |
| 自動ON/OFF | エリア入退場での自動制御有効/無効 |
| Grace Period | 戦闘エリア入場時の待機機能ON/OFF |
| 待機時間 | Grace Period の待機時間（デフォルト：60秒） |
| トリガー入力設定 | Grace Periodを解除する入力の選択 |
| 除外エリア | 自動制御を適用しないエリアのリスト（例：町など） |
| ログパターン | エリア入退場を検出するための正規表現パターン |

**6. キャリブレーションタブ（実装済み）**

| 設定項目 | 内容 |
|----------|------|
| 検出エリア設定 | オーバーレイウィンドウ表示 |
| プリセット選択 | 解像度別初期座標（3種類） |
| 検出テスト | リアルタイムTincture検出確認 |
| エリア情報表示 | 現在の座標・サイズ（動的更新） |
| 詳細設定 | X,Y,幅,高さの手動調整 |
| 設定保存 | detection_areas.yaml保存 |

### 1.7. ログファイル監視機能（実装済み）
#### 実装済み仕様
- **監視対象**: Client.txtのリアルタイム監視
- **検出パターン**: "You have entered [エリア名]." 形式
- **エリア分類**: 安全エリア（町・隠れ家）と戦闘エリアの自動判定
- **Grace Period統合**: 戦闘エリア入場時の自動待機
- **再入場対応**: エリアキャッシュ制御

#### 動作フロー（Grace Period自動トグル対応）:
1. **戦闘エリア入場**: 
   - Grace Period開始（60秒）
   - 特定入力検知またはタイムアウトでマクロON
2. **安全エリア入場**: 即座にマクロ停止
3. **エリア退場**: マクロ自動停止
4. **再入場**: 同じエリアでもGrace Period再発動

#### ログパターン例
```
-- 入場パターン例
2025/01/15 12:34:56 You have entered Crimson Temple.
2025/01/15 12:35:12 You have entered Hideout.
2025/01/15 12:35:45 You have entered Crimson Temple.

-- 退場パターン例
2025/01/15 12:40:23 You have left Crimson Temple.
```

## 2. 非機能要件

| 項目 | 要件 |
|------|------|
| 実行環境 | ・OS: Windows 10/11<br>・Python: 3.13.5対応<br>・ディスプレイ構成: マルチモニター対応（Primary/Center/Right）<br>・解像度対応: 1920x1080, 2560x1440, 3840x2160<br>・ゲーム設定: Windowed Fullscreen推奨 |
| パフォーマンス | ・CPU使用率: 5%以下（達成済み）<br>・画像認識処理: 100ms以内（達成済み）<br>・メモリ使用量: 200MB以下（最適化済み）<br>・Tincture検出: 100ms間隔での高速処理<br>・Grace Period入力検知: 100ms以内 |
| 信頼性 | 長時間のゲームプレイセッション（数時間）において、エラーなく安定して動作すること。 |
| 操作性 | ユーザーが単一の操作（特定のキーの組み合わせなど）でマクロ全体の開始と停止を切り替えられること。<br>Grace Period中でも手動操作を優先できること。 |
| アンチチート対策 | 全てのキー入力タイミングにミリ秒単位のランダムな揺らぎを持たせ、機械的なパターンを排除する。 |
| ユーザビリティ | 直感的なGUI操作。設定変更が即座に反映され、マクロの再起動が不要。<br>Grace Period待機中の状態表示。 |
| 設定の検証 | 不正な値（負の数値、空欄等）の入力を防ぐバリデーション機能。 |
| 拡張性 | 新しいフラスコ、スキル、バフの追加が容易な設計。画像ファイルと設定ファイルの追加/修正のみで対応可能。 |
| 保守性 | アセット（画像ファイル）の体系的な管理。READMEによる各ディレクトリの説明文書化。 |
| リアルタイム性 | ・ログファイル監視: 0.5秒間隔（設定可能）<br>・Grace Period入力検知: 100ms以内（pynput使用）<br>・Tincture検出: 100ms間隔での連続処理<br>・GUI更新: リアルタイム統計表示 |
| 耐障害性 | ・ログファイルアクセス失敗の独立処理<br>・pynput未インストール時の自動フォールバック<br>・個別モジュールエラーの分離処理<br>・スレッドセーフな実装による安定性<br>・設定ファイル破損時のデフォルト値復旧 |
| エラー処理 | ・画像認識失敗時の再試行機構<br>・ゲーム画面が見つからない場合の適切な通知<br>・設定ファイル破損時のデフォルト値での起動 |

## 3. 制約事項

1. **本マクロは、指定された解像度およびUIスケールでのみ正常な動作を保証する。** 解像度やUI設定が異なる場合、画像認識の精度が低下し、意図しない動作をする可能性がある。

2. **ゲームクライアントのアップデートにより、UI要素（フラスコやTinctureの表示位置、デザイン）が変更された場合、マクロの修正が必要となる。** 特に画像認識部分は影響を受けやすい。

3. **初期バージョンでは、フラスコは固定間隔での自動使用のみ対応。** チャージ量やプログレスバーの状態は考慮しない。

4. **Wine of the Prophetは初期実装では固定間隔（約20秒）での使用となり、Divination Cardバフの状態は考慮しない。**

5. **Divination Cardバフは同時に1つのみ適用されるゲーム仕様に基づいて将来の拡張を設計。**

6. **ログファイルの場所はSteam版のデフォルトパスを想定。** スタンドアロン版やEpic Games版では異なるパスになる可能性があり、手動での設定が必要。

7. **ログファイルのフォーマットはゲームのアップデートで変更される可能性があり、その場合はログパターンの更新が必要。**

8. **Grace Period機能はpynputライブラリに依存。** 環境によってはpynputが正常に動作しない場合があり、その際は機能が自動的に無効化される。（実装済みの自動フォールバック機能）

9. **Grace Period自動トグル機能の入力検知は、左クリック、右クリック、中央クリック、Qキーに限定。** その他の入力ではGrace Periodは解除されない。

10. **本マクロの使用は、Path of Exileの利用規約に違反する可能性があります。使用によるアカウントへのいかなる不利益（アカウント停止等）についても、開発者は一切の責任を負いません。利用は完全に自己責任で行うものとします。**

11. **依存関係**: Python 3.13.5、PyQt5、OpenCV、pynput等の外部ライブラリが必要。requirements.txtで管理済み。

## 4. 開発状況

### 完了済み機能（2025-07-06現在）：

**✅ 基本機能（完全実装済み）**
- フラスコ自動使用（4スロット、独立スレッド処理）
- スキル自動発動（Berserk/Molten Shell/Order! To Me!）
- Tincture自動使用（Active/Idle状態検出）
- 統合制御システム（MacroController）
- GUI設定画面（6タブ構成、リアルタイム更新）

**✅ 高度機能（完全実装済み）**
- オーバーレイ検出エリア設定（PyQt5、pynput統合）
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

**📋 将来の拡張機能**
- Divination Cardバフ検出
- フラスコチャージ・プログレスバー検出
- 機械学習による動的制御

## 5. 設定ファイル例（完全版）

```yaml
# POE Macro v3.0 完全設定ファイル
# Grace Period自動トグル機能対応版

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

# スキル設定
skill:
  enabled: true
  berserk:
    enabled: true
    key: "e"
    name: "Berserk"
    delay_min: 0.300
    delay_max: 1.000
  molten_shell:
    enabled: true
    key: "r"
    name: "Molten Shell"
    delay_min: 0.300
    delay_max: 1.000
  order_to_me:
    enabled: true
    key: "t"
    name: "Order! To Me!"
    delay_min: 3.500
    delay_max: 4.000

# Tincture設定
tincture:
  enabled: true
  key: "3"
  name: "Sap of the Seasons"
  detection:
    sensitivity: 0.7
    interval: 0.1
    cooldown: 5.0
    mode: "manual"  # manual, auto_slot3, full_flask_area

# ログ監視設定
log_monitor:
  enabled: true
  log_file_path: "C:/Program Files (x86)/Steam/steamapps/common/Path of Exile/logs/Client.txt"
  check_interval: 0.5
  safe_areas:
    - "Hideout"
    - "The Rogue Harbour"
    - "Lioneye's Watch"
    - "The Forest Encampment"
    - "The Sarn Encampment"
    - "Highgate"
    - "Overseer's Tower"
    - "The Bridge Encampment"
    - "Oriath"
    - "The Karui Shores"
  grace_period:
    enabled: true
    duration: 60
    trigger_inputs:
      mouse_buttons: ["left", "right", "middle"]
      keyboard_keys: ["q"]
    clear_cache_on_reenter: true
    timeout_action: "auto_enable"

# システム設定
system:
  emergency_stop_key: "f12"
  log_level: "INFO"
  anti_cheat_delay: 0.050
  
# GUI設定
gui:
  theme: "default"
  window_size:
    width: 800
    height: 600
  show_statistics: true
  update_interval: 1.0

# オーバーレイ設定（別ファイル管理）
# detection_areas.yaml および overlay_settings.yaml 参照
```
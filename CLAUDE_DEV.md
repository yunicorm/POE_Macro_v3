# POE Macro v3.0 開発ガイドライン

## 関連ドキュメント

開発を進める際は、以下のドキュメントも参照してください：

- **[要件定義書](docs/POE_Macro_v3_要件定義書.md)**: プロジェクトの詳細な要件と仕様
- **[開発計画書](docs/POE_Macro_v3_開発計画書.md)**: 開発フェーズとタスクの詳細
- **[開発記録](CLAUDE.md)**: 日々の開発進捗と技術的決定事項

特に要件定義書は、各モジュールの具体的な動作仕様（タイミング、キー割り当て、画像認識の詳細など）が記載されているため、実装時に必ず参照してください。

## アーキテクチャ概要

### ディレクトリ構造
```
POE_Macro_v3/
├── src/                    # ソースコード
│   ├── core/              # コア機能（マクロ制御、設定管理）
│   ├── features/          # 高度な機能（画像認識システム）
│   ├── modules/           # 各種モジュール（フラスコ、スキル、Tincture）
│   ├── gui/               # GUI関連
│   └── utils/             # ユーティリティ（画面キャプチャ、キーボード入力）
├── assets/                 # 画像アセット
│   └── images/
│       ├── divination_card_buff/  # Divination Cardバフアイコン
│       ├── tincture/             # Tincture状態画像
│       │   └── sap_of_the_seasons/
│       │       ├── idle/         # 使用可能状態
│       │       ├── active/       # 使用中状態
│       │       └── cooldown/     # クールダウン状態
│       ├── utility/              # ユーティリティフラスコ画像
│       ├── unique/               # ユニークフラスコ画像
│       └── mana/                 # マナフラスコ画像
├── config/                 # 設定ファイル
├── tests/                  # テストコード
├── docs/                   # ドキュメント
├── demo_*.py              # デモスクリプト群
├── test_*.py              # テストスクリプト群
└── create_*.py            # アセット作成スクリプト群
```

### モジュール設計

#### 1. Core（コア機能）
- **macro_controller.py**: マクロ全体の制御（開始/停止、モジュール管理）
- **config_manager.py**: 設定ファイルの読み込み/保存（YAML形式、階層設定対応）

#### 2. Features（高度な機能）
- **image_recognition.py**: TinctureDetectorクラス（複数解像度対応、状態検出）

#### 3. Utils（ユーティリティ）
- **keyboard_input.py**: KeyboardControllerクラス（アンチチート対策、ランダム遅延）
- **screen_capture.py**: 画面キャプチャ（マルチモニター対応、高速キャプチャ）
- **image_recognition.py**: 基本画像認識（OpenCVテンプレートマッチング）

#### 4. Modules（機能モジュール）
- **flask_module.py**: フラスコ自動使用（基本実装済み）
- **skill_module.py**: スキル自動使用（基本実装済み）
- **tincture_module.py**: TinctureModuleクラス（完全実装済み - ステートマシン、マルチスレッド）
- **log_monitor.py**: ログファイル監視（基本実装済み）

#### 5. GUI
- **main_window.py**: MainWindowクラス（完全実装済み - タブ式、リアルタイム更新）

### 実装済みクラス詳細

#### TinctureDetector（src/features/image_recognition.py）
```python
class TinctureDetector:
    def __init__(self, monitor_config: str, sensitivity: float)
    def detect_tincture_icon(self) -> bool
    def update_sensitivity(self, new_sensitivity: float) -> None
    def get_detection_area_info(self) -> Dict[str, any]
```

#### TinctureModule（src/modules/tincture_module.py）
```python
class TinctureModule:
    def __init__(self, config: Dict[str, Any])
    def start(self) -> None
    def stop(self) -> None
    def manual_use(self) -> bool
    def get_stats(self) -> Dict[str, Any]
    def update_config(self, new_config: Dict[str, Any]) -> None
```

#### MainWindow（src/gui/main_window.py）
```python
class MainWindow(QMainWindow):
    def __init__(self, config_manager)
    def create_tincture_tab(self)
    def update_status(self)  # 1秒間隔での自動更新
```

## コーディング規約

### Python スタイル
- PEP 8準拠
- 型ヒントを積極的に使用
- docstringは必須（Google style）
- Black でフォーマット

### エラーハンドリング
```python
try:
    # 処理
except SpecificException as e:
    logger.error(f"具体的なエラーメッセージ: {e}")
    # 必要に応じて再raise
```

### ログ出力
```python
logger.debug()  # デバッグ情報
logger.info()   # 通常の情報
logger.warning() # 警告
logger.error()  # エラー
```

## 重要な実装ポイント

### 1. アンチチート対策
- 全てのキー入力にランダム遅延（0-50ms）
- キー押下時間もランダム化（50-100ms）
- ループ間隔にも揺らぎを導入

### 2. マルチスレッド設計
- 各モジュールは独立したスレッドで動作
- 適切な停止処理（graceful shutdown）
- スレッドセーフな実装

### 3. 画像認識の最適化
- テンプレート画像の事前読み込み
- 認識領域の限定（全画面ではなく必要な部分のみ）
- 閾値の調整可能化

### 4. 設定管理
- デフォルト設定とユーザー設定の分離
- 設定変更の即時反映（再起動不要）
- 設定のバリデーション

## テスト方針

### 実装済みテストスイート

#### 1. 単体テスト
- **tests/test_image_recognition.py**: TinctureDetectorの包括的テスト
- **tests/test_tincture_module.py**: TinctureModuleの統合テスト
- モック使用（画面キャプチャ、キーボード入力）
- 異常系テストも含む

#### 2. 統合テスト  
- **demo_image_recognition.py**: 画像認識機能のデモ・テスト
- **demo_tincture_module.py**: Tincture機能のデモ・テスト
- 実際のコンポーネント連携テスト

#### 3. 包括的検証
- **test_comprehensive.py**: プロジェクト全体の健全性チェック
- **test_syntax_check.py**: 全Pythonファイルの構文検証
- **test_modules_safe.py**: 依存関係なしでの安全テスト
- **test_gui_safe.py**: GUI機能の検証

### テスト実行方法
```bash
# 包括的テストスイート（推奨）
python test_comprehensive.py

# 個別テスト
python -m pytest tests/test_tincture_module.py -v
python demo_tincture_module.py --interactive

# GUI機能テスト（依存関係インストール後）
python test_gui_launch.py
```

## デバッグ機能

### 実装済みデバッグ機能
- **統計情報の可視化**: TinctureModuleの詳細統計
- **検出エリア情報**: get_detection_area_info()メソッド
- **ログ出力機能**: GUI内リアルタイムログ表示
- **インタラクティブデモ**: 手動テスト用インターフェース

### デバッグツール
```python
# 統計情報の取得
stats = tincture_module.get_stats()
print(f"使用回数: {stats['stats']['total_uses']}")

# 検出エリア情報
area_info = detector.get_detection_area_info()
print(f"検出エリア: {area_info['detection_area']}")
```

## パフォーマンス目標と実績

### 目標値
- CPU使用率: 5%以下
- メモリ使用量: 200MB以下  
- 画像認識処理: 100ms以内

### 実装実績
- **検出間隔**: 100ms（設定可能）
- **最小使用間隔**: 500ms（アンチチート対策）
- **スレッドセーフ**: 完全対応
- **グレースフルシャットダウン**: 2秒タイムアウト

## 開発・テスト環境セットアップ

### 1. 依存関係のインストール
```bash
# 自動インストールスクリプト使用
chmod +x install_dependencies.sh && ./install_dependencies.sh

# 手動インストール  
pip install -r requirements.txt
```

### 2. プロジェクト構造の検証
```bash
python test_comprehensive.py
```

### 3. 機能テストの実行
```bash
# 画像認識テスト
python demo_image_recognition.py

# Tincture機能テスト
python demo_tincture_module.py --interactive

# GUI起動テスト
python main.py
```

## セキュリティ考慮事項

### 実装済みセキュリティ機能
- **アンチチート対策**: 全操作にランダム遅延（0-50ms）
- **相対パス使用**: 設定ファイルやアセットパス
- **ログセキュリティ**: 個人情報の除外
- **例外処理**: 適切なエラーメッセージ

### アンチチート対策詳細
```python
# KeyboardControllerの実装例
def press_key(self, key: str, delay_range: Tuple[float, float] = (0.05, 0.1)):
    pre_delay = random.uniform(0, 0.05)      # 押下前遅延
    press_duration = random.uniform(*delay_range)  # 押下時間
    post_delay = random.uniform(0, 0.03)     # 押下後遅延
```

## 今後の開発方針

### 次期実装予定
1. **Flask・スキルモジュールの拡張**: Tincture同様の高機能化
2. **ログ監視機能の強化**: リアルタイム解析機能
3. **テンプレート画像管理**: 実ゲーム画像での置き換え
4. **パフォーマンス最適化**: さらなる高速化

### 拡張性の考慮
- **モジュラー設計**: 新機能の追加が容易
- **設定駆動**: コード変更なしでの動作調整
- **プラグイン機構**: 将来的な機能拡張に対応
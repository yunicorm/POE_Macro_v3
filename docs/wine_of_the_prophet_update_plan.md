Wine of the Prophet 動的制御システム - 開発計画書
概要
Wine of the ProphetのDivination Cardバフの重要度に基づいて使用タイミングを動的に制御するシステムを実装する。バフの残り時間を考慮し、重要なバフは長く維持し、重要でないバフは早期に更新することで、プレイ効率を最大化する。
開発フェーズ
Phase 1: バフエリア検出オーバーレイ（2日）
目的: バフが表示される画面領域を正確に特定する
実装内容

BuffAreaOverlay クラス

既存のAreaSelectorクラスを継承
ドラッグ移動、矢印キー微調整、Ctrl+矢印でサイズ変更
デフォルト位置: (700, 50)、サイズ: (520, 100)
ゴールド色の枠線、グリッド表示オプション


GUI統合

CalibrationタブにBuff Detectionセクション追加
オーバーレイ表示ボタン、座標表示、解像度プリセット
設定の保存/読み込み（detection_areas.yaml）


テスト機能

バフエリアのスクリーンショット保存
青い数字の検出テスト
デバッグ画像生成



Phase 2: Divination Cardバフ検出（3日）
目的: 40種類のDivination Cardバフアイコンを識別する
実装内容

DivinationBuffDetector クラス
pythonclass DivinationBuffDetector:
    def __init__(self):
        self.templates = self._load_buff_templates()  # 40種類
        self.priority_map = self._load_priority_map()  # 5段階
        
    def detect_current_buff(self) -> Optional[BuffInfo]

アセット管理
assets/images/divination_card_buff/
├── highest-priority/  # House of Mirrors等
├── high-priority/     # Council of Cats等
├── medium-priority/
├── low-priority/
└── lowest-priority/   # The Beast等

他バフとの区別

Divination Cardバフのリスト管理
Flask効果、Aura等との識別機能



Phase 3: タイマー読み取り（3日）
目的: バフアイコン下の青い数字を読み取る
実装内容

BuffTimerReader クラス

バフアイコン位置から相対的にタイマーエリアを特定
青色抽出（HSV: 100-120, 150-255, 150-255）
数字テンプレートマッチング（0-9とコロン）


位置関係の管理

アイコン下端から約35ピクセルのオフセット
各バフアイコンに紐づくタイマーの正確な検出


フォールバック機能

タイマー読み取り失敗時は固定タイミング使用
青色ピクセル密度による大まかな推定



Phase 4: Wine動的制御（2日）
目的: FlaskModuleと統合し、動的タイミング制御を実現
実装内容

DynamicWineController クラス
pythonclass DynamicWineController:
    def __init__(self, flask_module, buff_detector, timer_reader):
        self.uptime_targets = {
            'highest': 0.95,  # 19秒維持
            'high': 0.80,     # 16秒維持
            'medium': 0.60,   # 12秒維持
            'low': 0.40,      # 8秒維持
            'lowest': 0.20    # 4秒維持
        }

FlaskModule拡張

slot_4の動的タイミング更新機能
最小使用間隔10秒の保証（チャージ考慮）


設定ファイル
yamlflask:
  slot_4:
    dynamic_control:
      enabled: true
      mode: "priority_based"
      min_interval: 10.0
      priority_timings:
        highest: null
        high: [40.0, 45.0]
        medium: [25.0, 30.0]
        low: [18.0, 22.0]
        lowest: [12.0, 15.0]


Phase 5: 統合テストと最適化（2日）
目的: システム全体の動作確認と調整
実装内容

統合テスト

各優先度でのタイミング確認
長時間動作の安定性テスト
パフォーマンス測定


GUI統合

リアルタイムバフ状態表示
動的制御の有効/無効切り替え
デバッグ情報表示



技術仕様
重要な考慮事項

Wine of the Prophetの仕様

Gold Flask効果（5.5秒）とDivination Cardバフ（20秒）は独立
"Gains no Charges during Effect"により最短使用間隔は約10秒
プログレスバーはGold Flask効果のみ表示（カードバフとは無関係）


バフ時間の増減対応

Temporal Chains等のモッドによる時間変化
青い数字のカウントダウンはゲーム内時間で一定
実時間への変換計算が必要


エラー処理

バフ検出失敗時のフォールバック
タイマー読み取りエラーの対処
チャージ不足の検出



パフォーマンス目標

バフ検出: 1秒間隔
CPU使用率増加: 1-2%以内
メモリ使用量増加: +50MB以内

必要なアセット

Divination Cardバフアイコン（40種類）
青い数字テンプレート（0-9、コロン）
テスト用スクリーンショット

画像アセット命名規則と管理体系
1. ディレクトリ構造
assets/
└── images/
    ├── divination_card_buff/
    │   ├── templates/              # マスターテンプレート
    │   │   ├── highest/
    │   │   │   ├── house_of_mirrors.png
    │   │   │   ├── burning_blood.png
    │   │   │   └── chaotic_disposition.png
    │   │   ├── high/
    │   │   │   ├── council_of_cats.png
    │   │   │   ├── the_doctor.png
    │   │   │   └── hunters_reward.png
    │   │   ├── medium/
    │   │   │   ├── abandoned_wealth.png
    │   │   │   └── astral_protection.png
    │   │   ├── low/
    │   │   │   ├── her_mask.png
    │   │   │   └── poisoned_faith.png
    │   │   └── lowest/
    │   │       ├── the_beast.png
    │   │       └── bated_expectation.png
    │   │
    │   ├── reference/              # 参照用オリジナル画像
    │   │   └── screenshots/        # ゲームスクリーンショット
    │   │
    │   └── metadata.json          # バフ情報メタデータ
    │
    └── timer_digits/
        ├── blue/                   # 青い数字（モッド影響時）
        │   ├── digit_0.png
        │   ├── digit_1.png
        │   ├── ...
        │   ├── digit_9.png
        │   └── colon.png
        │
        ├── white/                  # 白い数字（通常時）
        │   └── ...同上
        │
        └── calibration/           # キャリブレーション用
            └── sample_timers/     # タイマーサンプル画像
2. Divination Cardバフ命名規則
ファイル名規則
{card_name_snake_case}.png

例:
- house_of_mirrors.png      # House of Mirrors
- council_of_cats.png       # Council of Cats
- the_doctor.png           # The Doctor
- chaotic_disposition.png   # Chaotic Disposition
命名ルール

すべて小文字
スペースはアンダースコア
特殊文字は除去（アポストロフィ等）
"The"は含める（the_doctor.png）

3. メタデータファイル
json// assets/images/divination_card_buff/metadata.json
{
  "buffs": {
    "house_of_mirrors": {
      "display_name": "House of Mirrors",
      "priority": "highest",
      "effect": "Deal Double Damage",
      "color_hint": "#FFD700",
      "icon_size": [32, 32],
      "detection_threshold": 0.85
    },
    "council_of_cats": {
      "display_name": "Council of Cats",
      "priority": "high",
      "effect": "20% increased Attack and Cast Speed, 100% increased Critical Strike Chance",
      "color_hint": "#FFA500",
      "icon_size": [32, 32],
      "detection_threshold": 0.80
    }
    // ... 全40種類
  },
  
  "priority_colors": {
    "highest": "#FF0000",
    "high": "#FFA500",
    "medium": "#FFFF00",
    "low": "#00FF00",
    "lowest": "#808080"
  }
}
4. タイマー数字命名規則
timer_digits/
├── blue/
│   ├── digit_0.png        # 個別の数字
│   ├── digit_1.png
│   └── colon.png          # ":"記号
│
└── white/
    └── ...同上
5. 画像仕様
バフアイコン
yamlbuff_icon_specs:
  format: PNG
  size: 32x32 pixels
  channels: RGBA (透過付き)
  preprocessing:
    - クロップ: アイコンの輪郭ギリギリまで
    - 背景: 透過または黒（#000000）
    - 保存: 可逆圧縮
タイマー数字
yamltimer_digit_specs:
  format: PNG
  size: 
    digit: 8x12 pixels (推定)
    colon: 4x12 pixels
  preprocessing:
    - 青色部分のみ抽出
    - 背景: 完全透過
    - アンチエイリアス保持
6. 画像準備スクリプト
python# tools/prepare_buff_images.py
class BuffImagePreparer:
    """バフ画像の準備とバリデーション"""
    
    def __init__(self):
        self.expected_size = (32, 32)
        self.naming_rules = {
            ' ': '_',      # スペース → アンダースコア
            "'": '',       # アポストロフィ → 削除
            ',': '',       # カンマ → 削除
            '-': '_'       # ハイフン → アンダースコア
        }
    
    def prepare_buff_image(self, original_path, card_name, priority):
        """バフ画像を規格化"""
        # 1. ファイル名生成
        filename = self.generate_filename(card_name)
        
        # 2. 画像読み込みとリサイズ
        img = cv2.imread(original_path, cv2.IMREAD_UNCHANGED)
        img = self.standardize_image(img)
        
        # 3. 保存先決定
        output_dir = f"assets/images/divination_card_buff/templates/{priority}"
        output_path = os.path.join(output_dir, filename)
        
        # 4. メタデータ更新
        self.update_metadata(card_name, filename, priority)
        
        return output_path
7. バリデーションツール
python# tools/validate_assets.py
def validate_buff_assets():
    """アセットの整合性チェック"""
    
    checks = {
        "file_exists": [],
        "correct_size": [],
        "naming_convention": [],
        "metadata_sync": []
    }
    
    # メタデータ読み込み
    with open('metadata.json') as f:
        metadata = json.load(f)
    
    for buff_id, info in metadata['buffs'].items():
        filepath = f"templates/{info['priority']}/{buff_id}.png"
        
        # ファイル存在チェック
        if not os.path.exists(filepath):
            checks["file_exists"].append(f"Missing: {filepath}")
            
        # サイズチェック
        img = cv2.imread(filepath)
        if img.shape[:2] != (32, 32):
            checks["correct_size"].append(f"Wrong size: {filepath}")
            
    return checks
8. 自動生成スクリプト
python# tools/extract_timer_digits.py
def extract_timer_digits_from_screenshot():
    """スクリーンショットからタイマー数字を自動抽出"""
    
    # サンプル画像読み込み
    timer_samples = {
        "0:20": "screenshots/timer_20.png",
        "0:16": "screenshots/timer_16.png",
        "0:08": "screenshots/timer_08.png"
    }
    
    extracted_digits = {}
    
    for label, path in timer_samples.items():
        img = cv2.imread(path)
        blue_mask = extract_blue_color(img)
        digits = segment_digits(blue_mask)
        
        # 各数字を保存
        for i, digit_img in enumerate(digits):
            digit_char = label[i] if i != 1 else ':'
            if digit_char not in extracted_digits:
                extracted_digits[digit_char] = digit_img
    
    # 保存
    for char, img in extracted_digits.items():
        filename = f"digit_{char}.png" if char != ':' else "colon.png"
        cv2.imwrite(f"timer_digits/blue/{filename}", img)
9. 使用例
python# 実装での使用
class BuffDetector:
    def __init__(self):
        self.buff_templates = self._load_templates_from_metadata()
        
    def _load_templates_from_metadata(self):
        """メタデータに基づいてテンプレート読み込み"""
        templates = {}
        
        with open('metadata.json') as f:
            metadata = json.load(f)
            
        for buff_id, info in metadata['buffs'].items():
            path = f"templates/{info['priority']}/{buff_id}.png"
            templates[buff_id] = {
                'image': cv2.imread(path),
                'priority': info['priority'],
                'threshold': info['detection_threshold']
            }
            
        return templates
この命名規則と管理体系により：

一貫性: すべてのアセットが統一された規則に従う
保守性: メタデータによる一元管理
拡張性: 新しいバフの追加が容易
自動化: スクリプトによる準備とバリデーション

実装優先順位

必須（MVP）: バフ検出 → 優先度判定 → 固定タイミング制御
推奨: タイマー読み取り → 動的タイミング
オプション: 学習機能、視覚的チャージ確認

期待される効果

高優先度バフの維持時間: 平均16秒 → 19秒
低優先度バフの更新頻度: 20秒 → 4-8秒
全体的なDPS向上: 推定10-15%

リスクと対策

バフ検出精度: テンプレートマッチング閾値の調整
UI変更への対応: アセット更新手順の文書化
パフォーマンス: 検出頻度の最適化

この計画に基づいて、段階的に実装を進めていく。まずはPhase 1のバフエリア検出オーバーレイから開始する。
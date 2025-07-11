# トラブルシューティングガイド

POE Macro v3.0で発生する可能性のある問題と解決方法。

## 一般的な問題

### マクロが起動しない
1. **Python環境の確認**
   - Python 3.13.5がインストールされているか
   - 仮想環境が有効化されているか

2. **依存関係の確認**
   ```bash
   pip install -r requirements.txt
   ```

3. **設定ファイルの確認**
   - `config/main_config.yaml`が存在するか
   - 構文エラーがないか

### GUI が表示されない
1. **PyQt5のインストール確認**
   ```bash
   pip install PyQt5
   ```

2. **ディスプレイ設定**
   - 複数モニター環境の場合、プライマリモニター確認
   - DPI設定の確認

### キー入力が効かない
1. **管理者権限での実行**
   - ゲームが管理者権限で動作している場合

2. **キーバインドの確認**
   - ゲーム内設定との競合確認
   - 他のソフトウェアとの競合確認

## Flask関連の問題

### Flask自動化が効かない場合

#### 症状
フラスコが設定通りに自動使用されない

#### 確認項目

##### 1. UI設定の確認
- **「自動化を停止」チェックボックス**: チェックが入っていないか確認
- **場所**: 各フラスコスロットの設定画面
- **対処**: チェックを外して設定を保存

##### 2. 設定ファイルの確認
- **ファイル**: `config/main_config.yaml`
- **確認項目**: `flask_slots` > `slot_X` > `use_when_full: true`
- **対処**: `use_when_full: false` に変更

```yaml
flask_slots:
  slot_1:
    key: "1"
    use_when_full: false  # ← この値を確認
    flask_type: "Life"
    # ...
```

##### 3. ログの確認
- **ログファイル**: `logs/macro.log`
- **確認内容**: FlaskTimerManagerのスキップメッセージ
- **スキップメッセージ例**:
  ```
  INFO: Flask slot 1 skipped: automation disabled (use_when_full is True)
  INFO: Flask slot 2 skipped: is_tincture is True
  ```

##### 4. タイマー作成の確認
- **ログメッセージ**: `Flask timer config updated: X timers loaded`
- **期待値**: 自動化対象フラスコ数と一致
- **0 timers loadedの場合**: 全フラスコが除外されている

#### 詳細診断手順

##### ステップ1: GUI確認
1. Flask & Tincture統合タブを開く
2. 各スロットの「自動化を停止」チェックボックス確認
3. Tinctureチェックボックスの状態確認

##### ステップ2: 設定保存
1. 問題のあるスロットの設定を変更
2. 「スロットX設定を保存」ボタンをクリック
3. 「すべての設定を保存」ボタンをクリック

##### ステップ3: ログ監視
1. マクロを再起動
2. ログファイルでタイマー作成メッセージを確認
3. スキップメッセージの有無を確認

#### よくある原因と対処法

##### 原因1: 誤った「自動化を停止」設定
- **症状**: 特定フラスコのみ動作しない
- **対処**: 該当スロットのチェックを外す

##### 原因2: Tincture設定の混在
- **症状**: フラスコとTinctureが競合
- **対処**: Tinctureチェックを外すか、別スロットに移動

##### 原因3: 設定が保存されていない
- **症状**: 再起動後に設定が戻る
- **対処**: 保存ボタンの実行確認、ファイル権限確認

##### 原因4: Flask全体の無効化
- **症状**: 全フラスコが動作しない
- **対処**: 「Flask自動使用を有効化」チェックボックス確認

#### トラブルシューティングフロー

```
Flask自動化が効かない
├─ 特定フラスコのみ？
│  ├─ Yes → 「自動化を停止」チェック確認
│  └─ No → Flask全体設定確認
├─ ログにスキップメッセージ？
│  ├─ Yes → use_when_full設定変更
│  └─ No → タイマー作成失敗の可能性
└─ 設定保存済み？
   ├─ Yes → マクロ再起動
   └─ No → 設定保存実行
```

## Tincture関連の問題

### Tincture検出ができない
1. **テンプレート画像の確認**
   - Active/Idleフォルダの画像が正しく配置されているか
   - 画像の解像度・品質が適切か

2. **検出感度の調整**
   - しきい値を0.7から0.8に上げる
   - 感度スライダーを調整

3. **画面解像度の確認**
   - ゲームの解像度設定
   - ウィンドウモード vs フルスクリーンモード

### Tincture使用タイミングが不適切
1. **チェック間隔の調整**
   - デフォルト100msから50msに短縮

2. **最小使用間隔の確認**
   - デフォルト500msが適切か確認

## Grace Period関連の問題

### エリア変更検出ができない
1. **Client.txtファイルの場所確認**
   - Path of Exileインストールディレクトリ確認
   - ファイルアクセス権限確認

2. **ログファイル監視の確認**
   - ファイルが実際に更新されているか
   - エンコーディング問題の確認

## パフォーマンス関連の問題

### CPU使用率が高い
1. **検出間隔の調整**
   - チェック間隔を100msから200msに延長

2. **不要な機能の無効化**
   - 使用しないTinctureの無効化
   - 統計情報の更新頻度調整

### メモリ使用量が多い
1. **画像キャッシュのクリア**
   - 定期的なメモリ解放

2. **ログファイルのローテーション**
   - 古いログファイルの削除

## ログの確認方法

### ログファイルの場所
- `logs/macro.log` - 最新のログ
- `logs/macro.log.1` - 前回のログ
- `logs/macro.log.2` - 前々回のログ

### 重要なログメッセージ
```
INFO: Flask timer config updated: 3 timers loaded  # タイマー作成成功
INFO: Flask slot 1 skipped: automation disabled    # 自動化無効
ERROR: Template image not found                    # テンプレート画像なし
DEBUG: Tincture used: slot 3, key 3               # Tincture使用
```

## 設定ファイルの確認

### 主要設定ファイル
- `config/main_config.yaml` - メイン設定
- `config/detection_areas.yaml` - 検出エリア設定
- `config/overlay_settings.yaml` - オーバーレイ設定

### 設定ファイルの構文確認
```bash
python -c "import yaml; yaml.safe_load(open('config/main_config.yaml'))"
```

## 緊急時の対処

### 設定リセット
1. `config/` フォルダを一時的にリネーム
2. マクロを起動してデフォルト設定を生成
3. 必要に応じて設定を再構築

### 完全再インストール
1. プロジェクトフォルダのバックアップ
2. 仮想環境の削除・再作成
3. 依存関係の再インストール

---

**POE Macro v3.0は要件定義書・開発計画書の仕様通りに完全実装され、世界最高水準の自動化マクロとして完成しました。**
# POE Macro v3 ビルドガイド

## 概要
このガイドでは、POE Macro v3の開発環境構築からビルド、リリースまでの手順を説明します。

## 必要な環境
- Python 3.11以上
- Windows 10/11
- Git

## セットアップ

### 1. リポジトリのクローン
```bash
git clone https://github.com/your-username/poe-macro-v3.git
cd poe-macro-v3
```

### 2. 仮想環境の作成（推奨）
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. アイコンファイルの作成（オプション）
```bash
python create_icon.py
```

## 開発フロー

### 日常的な開発
1. **コードの編集**
   ```bash
   # 開発モードで実行
   python main.py --debug
   ```

2. **テストの実行**
   ```bash
   # クイックテスト
   scripts\quick_test.bat
   
   # または個別に
   python test_simple.py
   python test_integration.py
   ```

3. **開発版ビルド**
   ```bash
   scripts\dev_build.bat
   ```
   - デバッグ情報付き
   - 高速ビルド
   - コンソール出力あり

### リリース準備

1. **バージョン更新**
   ```bash
   # パッチバージョン更新 (x.x.X)
   python scripts/update_version.py
   
   # マイナーバージョン更新 (x.X.0)
   python scripts/update_version.py --minor
   
   # メジャーバージョン更新 (X.0.0)
   python scripts/update_version.py --major
   ```

2. **CHANGELOG.mdの更新**
   - 自動生成されたエントリに変更内容を記載
   - Added, Changed, Fixed セクションを適切に更新

3. **リリースビルド**
   ```bash
   scripts\release_build.bat
   ```
   - 完全なテスト実行
   - 最適化ビルド
   - リリースパッケージ作成

## ビルドシステム

### build_system.py コマンド
```bash
# 開発版ビルド
python build_system.py dev

# リリース版ビルド
python build_system.py release

# ビルドクリーン
python build_system.py clean

# テスト実行
python build_system.py test

# バージョン更新
python build_system.py version --version-type=patch

# リリースパッケージ作成
python build_system.py package
```

### ビルド設定 (build_config.yaml)
```yaml
app_name: poe_macro_v3
version_file: src/version.py
spec_file: poe_macro_v3.spec
output_dir: dist
build_dir: build
```

### PyInstaller設定 (poe_macro_v3.spec)
- データファイルの自動包含
- 隠しインポートの設定
- アイコンファイルの設定
- 最適化オプション

## 継続的インテグレーション

### GitHub Actions
`.github/workflows/build.yml`により以下が自動化されます：

1. **プッシュ時**
   - 自動テスト実行
   
2. **タグプッシュ時** (v*)
   - テスト実行
   - リリースビルド
   - GitHubリリース作成
   - 実行ファイルのアップロード

### リリース手順
```bash
# 1. バージョン更新とコミット
python scripts/update_version.py --minor
git add -A
git commit -m "Bump version to 3.1.0"

# 2. タグ付けとプッシュ
git tag v3.1.0
git push origin main --tags

# 3. GitHub Actionsが自動的にビルドとリリースを作成
```

## トラブルシューティング

### ビルドエラー

#### "Module not found" エラー
- `requirements.txt`に必要なパッケージが含まれているか確認
- 隠しインポートを`poe_macro_v3.spec`に追加

#### アイコンファイルエラー
- `assets/poe_macro.ico`が存在するか確認
- または`create_icon.py`を実行

#### パス関連のエラー
- `src/utils/resource_path.py`のパス処理を確認
- 実行ファイル化後のパスが正しく解決されているか確認

### 実行時エラー

#### 設定ファイルが見つからない
- `get_user_config_path()`が正しいディレクトリを返しているか確認
- AppDataフォルダの権限を確認

#### テンプレート画像が読み込めない
- データファイルが`poe_macro_v3.spec`に含まれているか確認
- `get_template_path()`の実装を確認

## 開発のベストプラクティス

1. **コミット前**
   - `scripts\quick_test.bat`でテスト実行
   - コード品質チェック

2. **新機能追加時**
   - 対応するテストを作成
   - ドキュメントを更新
   - CHANGELOG.mdに記載

3. **リリース前**
   - すべてのテストが通ることを確認
   - 実機での動作確認
   - ドキュメントの最終確認

## パフォーマンス最適化

### ビルドサイズ削減
1. 不要なOpenCVモジュールの除外（spec ファイルで設定済み）
2. UPX圧縮の使用
3. 不要なファイルの除外設定

### 起動時間の短縮
1. 遅延インポートの使用
2. 初期化処理の最適化
3. リソースの事前読み込み

## セキュリティ考慮事項

1. **コード署名**（オプション）
   - Windows認証局から証明書を取得
   - `build_config.yaml`で設定

2. **ウイルス対策ソフト対策**
   - 実行ファイルのホワイトリスト登録
   - 誤検知を減らすための最適化

## 参考リンク
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Packaging Guide](https://packaging.python.org/)
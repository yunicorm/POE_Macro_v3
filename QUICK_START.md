# POE Macro v3 クイックスタート

## 今すぐ実行ファイルを作成する方法

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. 開発版ビルド（推奨）
```bash
scripts\dev_build.bat
```

### 3. 実行
```bash
dist\poe_macro_v3.exe
```

## 継続的な開発フロー

### 日常開発
```bash
# コード編集後
python main.py --debug    # テスト実行
scripts\dev_build.bat     # exeビルド
```

### リリース時
```bash
python scripts/update_version.py --minor  # バージョン更新
scripts\release_build.bat                 # リリースビルド
git tag v3.1.0                           # タグ付け
git push origin main --tags              # 自動リリース
```

## トラブルシューティング

### アイコンエラーが出る場合
`poe_macro_v3.spec`の以下の行をコメントアウト：
```python
icon='assets/poe_macro.ico' if os.path.exists('assets/poe_macro.ico') else None
```
を
```python
icon=None
```
に変更

### ビルドが失敗する場合
1. Pythonバージョンを確認（3.11推奨）
2. 仮想環境を使用
3. `pip install --upgrade pip`を実行

## 必要なファイル構成
```
POE_Macro_v3/
├── main.py
├── requirements.txt
├── poe_macro_v3.spec
├── build_system.py
├── build_config.yaml
├── src/
│   ├── version.py
│   └── utils/
│       └── resource_path.py
├── config/
│   └── *.yaml
├── assets/
│   └── templates/
└── scripts/
    ├── dev_build.bat
    ├── release_build.bat
    └── update_version.py
```

これで実行ファイル化と継続的な開発環境が整いました！
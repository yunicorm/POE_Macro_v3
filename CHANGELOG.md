# Changelog

## [3.0.0] - 2025-01-06

### Added
- 実行ファイル化（.exe）対応
- 自動ビルドシステムの実装
- バージョン管理システム
- GitHub Actions CI/CD設定
- 自動更新機能（GitHub Releases連携）
- リソースパス処理の最適化
- ビルド自動化スクリプト群
  - dev_build.bat（開発版ビルド）
  - release_build.bat（リリース版ビルド）
  - quick_test.bat（クイックテスト）
  - update_version.py（バージョン更新）

### Changed
- ConfigManagerのパス処理を実行ファイル対応に変更
- 画像認識モジュールのテンプレートパスを動的に解決
- FlaskDataManagerのCSVファイルパスを実行ファイル対応に変更
- ユーザー設定をAppDataフォルダに保存するように変更

### Fixed
- 実行ファイル化後のリソースアクセス問題
- 設定ファイルの保存先パス問題

### Technical Details
- PyInstaller 6.11.1を使用
- Python 3.11推奨
- Windows 10/11対応
- 署名なし実行ファイルのWindows Defender対策を文書化

---

## [2.0.0] - 2025-01-05

### Added
- Grace Period機能（エリア移動時の無敵時間検出）
- ログ監視機能（Client.txt）
- オーバーレイウィンドウ
- 検出エリア拡張機能
- フラスコGUI改善

### Changed
- Tincture検出エリアを8.6倍に拡大
- GUI設定の保存・復元機能を強化
- Active/Idle状態検出の精度向上

### Fixed
- メモリリーク問題
- スレッド競合状態
- エンコーディングエラー

---

## [1.0.0] - 2025-01-03

### Added
- 初回リリース
- Flask自動使用機能
- Skill自動使用機能
- Tincture自動使用機能
- PyQt5 GUI
- 画像認識システム
- 統合制御システム
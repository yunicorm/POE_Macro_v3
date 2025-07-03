# POE Macro v3.0 開発記録

## プロジェクト概要
Path of Exile自動化マクロ v3.0の開発記録

## プロジェクトドキュメント

本プロジェクトの詳細な仕様と計画は以下のドキュメントに記載されています：

- **[要件定義書](docs/POE_Macro_v3_要件定義書.md)**: 
  - 機能要件（フラスコ、スキル、Tincture、GUI、ログ監視）
  - 非機能要件（パフォーマンス、信頼性、操作性）
  - 制約事項とリスク
  
- **[開発計画書](docs/POE_Macro_v3_開発計画書.md)**:
  - プロジェクトスコープ
  - 開発フェーズ（WBS）
  - 使用技術とツール
  - リスク管理

これらのドキュメントは開発の指針となる重要な資料です。

## 開発環境
- Python: 3.13.5
- OS: Windows 11
- 開発開始日: 2025-01-15

## 完了した作業

### 2025-01-15
- [x] プロジェクト構造の作成
- [x] 依存関係の定義（requirements.txt, requirements-dev.txt）
- [x] VS Code設定ファイルの作成（.vscode/settings.json, launch.json）
- [x] 基本的な設定ファイル（config/default_config.yaml）
- [x] 環境テスト用main.pyの作成
- [x] 仮想環境の構築とパッケージのインストール
- [x] PyQt5インポートエラーの修正

### 2025-01-16
- [x] 基本モジュールの実装
  - [x] src/utils/keyboard_input.py - アンチチート対策付きキーボード制御
  - [x] src/utils/screen_capture.py - マルチモニター対応画面キャプチャ  
  - [x] src/utils/image_recognition.py - OpenCVテンプレートマッチング
  - [x] src/core/config_manager.py - 設定ファイル管理
  - [x] src/modules/flask_module.py - フラスコ自動使用基本実装
- [x] test_modules.py作成
- [x] ファイルエンコーディング問題の修正
- [x] 全必要__init__.pyファイルの作成
- [x] プロジェクトドキュメントの整備
  - [x] README.mdの充実化
  - [x] 開発ドキュメントへの参照追加

## 現在の作業
- [x] PyQt5インポートエラーの修正
- [x] CLAUDE.mdおよびCLAUDE_DEV.mdの作成
- [ ] GUI（PyQt5）の実装
- [ ] スキルモジュールの実装
- [ ] Tinctureモジュールの実装
- [ ] ログ監視モジュールの実装
- [ ] 統合テスト

## 今後の予定
1. GUI（PyQt5）の実装
2. スキルモジュールの実装
3. Tinctureモジュールの実装
4. ログ監視モジュールの実装
5. 統合テスト

## 技術的な決定事項
- 画面キャプチャ: mssライブラリを使用（高速化のため）
- キーボード入力: pyautogui + pynputの併用
- GUI: PyQt5（タブ式インターフェース）
- 設定管理: YAML形式
- アンチチート対策: 全ての操作にランダム遅延を導入

## 既知の問題
- Python 3.13でのnumpy/opencv-pythonのバージョン制約
  - 解決済み: 最新版を使用することで対応
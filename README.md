# POE Macro v3.0

Path of Exile自動化マクロ

## 概要

本プロジェクトは、PCゲーム「Path of Exile」におけるフラスコ、スキル、およびTinctureの継続的な使用を自動化するマクロです。

## ドキュメント

- [要件定義書](docs/POE_Macro_v3_要件定義書.md) - 詳細な機能要件と仕様
- [開発計画書](docs/POE_Macro_v3_開発計画書.md) - 開発フェーズとWBS
- [開発記録](CLAUDE.md) - 開発進捗の記録
- [開発ガイドライン](CLAUDE_DEV.md) - アーキテクチャと実装ガイド

## セットアップ

### 必要環境
- Windows 10/11
- Python 3.11以上
- マルチモニター環境（中央: 3440x1440）

### インストール手順

1. リポジトリのクローン
```bash
git clone https://github.com/your-username/POE_Macro_v3.git
cd POE_Macro_v3
```

2. 仮想環境の作成と有効化
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. 依存関係のインストール
```powershell
pip install -r requirements.txt
```

## 使用方法
```powershell
python main.py
```

## 機能

- フラスコ自動使用（1, 2, 4, 5キー）
- スキル自動使用（E, R, Tキー）
- Tincture自動使用（画像認識）
- ログファイル監視による自動制御
- GUI設定画面（開発中）

## 注意事項

本マクロの使用は、Path of Exileの利用規約に違反する可能性があります。使用は完全に自己責任で行ってください。

## ライセンス

Private Project
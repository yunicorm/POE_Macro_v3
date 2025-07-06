"""
POE Macro v3 Build System
統合ビルドマネージャー
"""

import os
import sys
import shutil
import subprocess
import yaml
import datetime
from pathlib import Path
import re

class BuildSystem:
    """ビルドシステムの管理クラス"""
    
    def __init__(self, config_file="build_config.yaml"):
        self.config_file = config_file
        self.config = self.load_config()
        self.root_dir = Path.cwd()
        
    def load_config(self):
        """ビルド設定を読み込み"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            # デフォルト設定
            return {
                "app_name": "poe_macro_v3",
                "version_file": "src/version.py",
                "spec_file": "poe_macro_v3.spec",
                "output_dir": "dist",
                "build_dir": "build",
                "icon_path": "assets/poe_macro.ico",
                "exclude_patterns": [
                    "__pycache__",
                    "*.pyc",
                    ".git",
                    ".vscode",
                    "tests",
                    "docs",
                    "*.log"
                ]
            }
    
    def update_version(self, version_type="patch"):
        """バージョンを更新"""
        version_file = self.config.get("version_file", "src/version.py")
        
        # 現在のバージョンを取得
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        version_match = re.search(r'VERSION = "(\d+)\.(\d+)\.(\d+)"', content)
        if version_match:
            major, minor, patch = map(int, version_match.groups())
            
            if version_type == "major":
                major += 1
                minor = 0
                patch = 0
            elif version_type == "minor":
                minor += 1
                patch = 0
            else:  # patch
                patch += 1
            
            new_version = f"{major}.{minor}.{patch}"
            
            # バージョンファイルを更新
            new_content = re.sub(
                r'VERSION = "\d+\.\d+\.\d+"',
                f'VERSION = "{new_version}"',
                content
            )
            new_content = re.sub(
                r'BUILD_DATE = "[^"]*"',
                f'BUILD_DATE = "{datetime.date.today()}"',
                new_content
            )
            
            with open(version_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Version updated to {new_version}")
            return new_version
        else:
            print("❌ Could not find version in file")
            return None
    
    def clean_build(self):
        """ビルド成果物をクリーン"""
        print("🧹 Cleaning build artifacts...")
        
        # distディレクトリをクリーン
        dist_dir = Path(self.config.get("output_dir", "dist"))
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        
        # buildディレクトリをクリーン
        build_dir = Path(self.config.get("build_dir", "build"))
        if build_dir.exists():
            shutil.rmtree(build_dir)
        
        print("✅ Clean completed")
    
    def run_tests(self):
        """テストを実行"""
        print("🧪 Running tests...")
        
        test_files = [
            "test_simple.py",
            "test_integration.py"
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"  Running {test_file}...")
                result = subprocess.run(
                    [sys.executable, test_file],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"  ✅ {test_file} passed")
                else:
                    print(f"  ❌ {test_file} failed")
                    print(result.stdout)
                    print(result.stderr)
                    return False
        
        return True
    
    def build_dev(self):
        """開発版ビルド（高速、デバッグ情報付き）"""
        print("🔨 Building development version...")
        
        cmd = [
            sys.executable,
            "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "--debug", "all",
            "--log-level", "DEBUG",
            self.config.get("spec_file", "poe_macro_v3.spec")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Development build completed")
            return True
        else:
            print("❌ Build failed")
            print(result.stdout)
            print(result.stderr)
            return False
    
    def build_release(self):
        """リリース版ビルド（最適化、サイズ削減）"""
        print("🚀 Building release version...")
        
        # クリーンビルド
        self.clean_build()
        
        # テスト実行
        if not self.run_tests():
            print("❌ Tests failed, aborting build")
            return False
        
        cmd = [
            sys.executable,
            "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            self.config.get("spec_file", "poe_macro_v3.spec")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Release build completed")
            
            # 実行ファイルのサイズを表示
            exe_path = Path(self.config.get("output_dir", "dist")) / f"{self.config.get('app_name', 'poe_macro_v3')}.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Executable size: {size_mb:.2f} MB")
            
            return True
        else:
            print("❌ Build failed")
            print(result.stdout)
            print(result.stderr)
            return False
    
    def create_release_package(self, version):
        """リリースパッケージを作成"""
        print(f"📦 Creating release package for v{version}...")
        
        # リリースディレクトリを作成
        release_dir = Path(f"releases/v{version}")
        release_dir.mkdir(parents=True, exist_ok=True)
        
        # 実行ファイルをコピー
        exe_path = Path(self.config.get("output_dir", "dist")) / f"{self.config.get('app_name', 'poe_macro_v3')}.exe"
        if exe_path.exists():
            shutil.copy2(exe_path, release_dir / f"poe_macro_v{version}.exe")
        
        # README とライセンスをコピー
        for file in ["README.md", "LICENSE"]:
            if os.path.exists(file):
                shutil.copy2(file, release_dir)
        
        # 設定ファイルのサンプルをコピー
        config_sample_dir = release_dir / "config_samples"
        config_sample_dir.mkdir(exist_ok=True)
        
        for config_file in Path("config").glob("*.yaml"):
            shutil.copy2(config_file, config_sample_dir)
        
        # ZIPアーカイブを作成
        shutil.make_archive(
            f"releases/poe_macro_v{version}",
            'zip',
            release_dir
        )
        
        print(f"✅ Release package created: releases/poe_macro_v{version}.zip")


def main():
    """メインエントリーポイント"""
    import argparse
    
    parser = argparse.ArgumentParser(description="POE Macro v3 Build System")
    parser.add_argument("command", choices=["dev", "release", "clean", "test", "version", "package"],
                       help="Build command")
    parser.add_argument("--version-type", choices=["major", "minor", "patch"], default="patch",
                       help="Version increment type")
    
    args = parser.parse_args()
    
    build_system = BuildSystem()
    
    if args.command == "dev":
        build_system.build_dev()
    elif args.command == "release":
        build_system.build_release()
    elif args.command == "clean":
        build_system.clean_build()
    elif args.command == "test":
        build_system.run_tests()
    elif args.command == "version":
        build_system.update_version(args.version_type)
    elif args.command == "package":
        # 現在のバージョンを取得
        import importlib.util
        spec = importlib.util.spec_from_file_location("version", "src/version.py")
        version_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(version_module)
        build_system.create_release_package(version_module.VERSION)


if __name__ == "__main__":
    main()
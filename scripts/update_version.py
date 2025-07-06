#!/usr/bin/env python3
"""
POE Macro v3 Version Update Script
バージョン番号を更新するユーティリティ
"""

import argparse
import re
import datetime
from pathlib import Path


def update_version(version_type="patch"):
    """バージョンを更新"""
    version_file = Path("src/version.py")
    
    if not version_file.exists():
        print(f"Error: Version file not found: {version_file}")
        return None
    
    # 現在のバージョンを読み込み
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # バージョン番号を抽出
    version_match = re.search(r'VERSION = "(\d+)\.(\d+)\.(\d+)"', content)
    if not version_match:
        print("Error: Could not find version in file")
        return None
    
    major, minor, patch = map(int, version_match.groups())
    old_version = f"{major}.{minor}.{patch}"
    
    # バージョンを更新
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
    
    # ファイルを更新
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
    
    # ファイルに書き込み
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Version updated: {old_version} → {new_version}")
    
    # CHANGELOG.mdを更新
    update_changelog(new_version)
    
    return new_version


def update_changelog(version):
    """CHANGELOG.mdを更新"""
    changelog_file = Path("CHANGELOG.md")
    
    if not changelog_file.exists():
        # 新規作成
        content = f"""# Changelog

## [{version}] - {datetime.date.today()}

### Added
- Initial release of POE Macro v3

### Changed
- 

### Fixed
- 

"""
        with open(changelog_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created CHANGELOG.md")
    else:
        # 既存ファイルに追記
        with open(changelog_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 新しいエントリを追加
        new_entry = f"""
## [{version}] - {datetime.date.today()}

### Added
- 

### Changed
- 

### Fixed
- 

"""
        # "# Changelog" の後に挿入
        content = content.replace("# Changelog\n", f"# Changelog\n{new_entry}")
        
        with open(changelog_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated CHANGELOG.md")


def main():
    parser = argparse.ArgumentParser(description="Update POE Macro version")
    parser.add_argument(
        "--major", 
        action="store_true", 
        help="Increment major version (X.0.0)"
    )
    parser.add_argument(
        "--minor", 
        action="store_true", 
        help="Increment minor version (x.X.0)"
    )
    parser.add_argument(
        "--patch", 
        action="store_true", 
        help="Increment patch version (x.x.X) [default]"
    )
    
    args = parser.parse_args()
    
    # バージョンタイプを決定
    if args.major:
        version_type = "major"
    elif args.minor:
        version_type = "minor"
    else:
        version_type = "patch"
    
    # バージョンを更新
    new_version = update_version(version_type)
    
    if new_version:
        print(f"\nNext steps:")
        print(f"1. Review and update CHANGELOG.md with actual changes")
        print(f"2. Commit: git commit -am 'Bump version to {new_version}'")
        print(f"3. Tag: git tag v{new_version}")
        print(f"4. Build release: python scripts/release_build.bat")


if __name__ == "__main__":
    main()
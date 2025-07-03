#!/usr/bin/env python3
"""
POE Macro v3.0 簡易統合テスト
依存関係なしでテスト可能な部分のみをテスト
"""

import sys
import time
import logging
from pathlib import Path

# プロジェクトのsrcディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_test_logging():
    """テスト用ログ設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_config_manager():
    """ConfigManagerのテスト"""
    print("=== ConfigManager Test ===")
    try:
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        print("✓ ConfigManager initialized")
        print(f"✓ Configuration loaded: {len(config)} sections")
        
        # 主要セクションの確認
        required_sections = ['general', 'flask', 'skills', 'tincture']
        for section in required_sections:
            if section in config:
                print(f"✓ Section '{section}' found")
            else:
                print(f"✗ Section '{section}' missing")
                return False
                
        return True
        
    except Exception as e:
        print(f"✗ ConfigManager test failed: {e}")
        return False

def test_log_monitor():
    """LogMonitorのテスト"""
    print("\n=== LogMonitor Test ===")
    try:
        from modules.log_monitor import LogMonitor
        
        # テスト用設定
        test_config = {
            'enabled': True,
            'log_path': 'test_client.txt',
            'check_interval': 0.1
        }
        
        log_monitor = LogMonitor(test_config)
        print("✓ LogMonitor created")
        
        # 手動テスト実行
        log_monitor.manual_test_area_enter("Test Dungeon")
        print("✓ Manual area enter test")
        
        log_monitor.manual_test_area_exit("Test Dungeon")
        print("✓ Manual area exit test")
        
        # 統計確認
        stats = log_monitor.get_stats()
        print(f"✓ Stats retrieved: areas_entered={stats['areas_entered']}, areas_exited={stats['areas_exited']}")
        
        # 設定更新テスト
        log_monitor.update_config(test_config)
        print("✓ Config update test")
        
        return True
        
    except Exception as e:
        print(f"✗ LogMonitor test failed: {e}")
        return False

def test_project_structure():
    """プロジェクト構造のテスト"""
    print("\n=== Project Structure Test ===")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'config/default_config.yaml',
        'src/core/config_manager.py',
        'src/modules/log_monitor.py',
        'src/modules/flask_module.py',
        'src/modules/skill_module.py',
        'src/modules/tincture_module.py',
        'src/core/macro_controller.py',
        'src/gui/main_window.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"Missing files: {missing_files}")
        return False
    
    print("✓ All required files present")
    return True

def test_syntax_check():
    """構文チェック（依存関係なしファイルのみ）"""
    print("\n=== Syntax Check Test ===")
    
    safe_files = [
        'main.py',
        'src/core/config_manager.py',
        'src/modules/log_monitor.py',
        'test_comprehensive.py',
        'test_integration.py'
    ]
    
    import ast
    
    for file_path in safe_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
                print(f"✓ {file_path}")
            except SyntaxError as e:
                print(f"✗ {file_path}: {e}")
                return False
            except Exception as e:
                print(f"⚠ {file_path}: {e}")
        else:
            print(f"⚠ {file_path}: not found")
    
    return True

def main():
    """メインテスト関数"""
    setup_test_logging()
    
    print("POE Macro v3.0 - Simple Integration Test")
    print("=" * 50)
    print("Testing core functionality without external dependencies")
    print()
    
    # テスト実行
    tests = [
        ("Project Structure", test_project_structure),
        ("Syntax Check", test_syntax_check),
        ("ConfigManager", test_config_manager),
        ("LogMonitor", test_log_monitor)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"--- {test_name} ---")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED\n")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED\n")
        except Exception as e:
            print(f"✗ {test_name} FAILED: {e}\n")
    
    # 結果サマリー
    print("=" * 50)
    print("SIMPLE INTEGRATION TEST RESULTS")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All core tests passed!")
        print("\nThe core project structure is complete and functional.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run full integration test: python test_integration.py")
        print("3. Run GUI: python main.py")
        print("4. Run headless: python main.py --no-gui")
        return 0
    else:
        print("⚠️ Some core tests failed.")
        print("Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
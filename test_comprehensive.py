#!/usr/bin/env python3
"""
POE Macro v3.0 包括的テストスイート
依存関係なしで実行可能な全体テスト
"""
import sys
import os
import ast
import subprocess
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

def test_project_structure():
    """プロジェクト構造のテスト"""
    print("=== Project Structure Test ===\n")
    
    required_dirs = [
        "src",
        "src/core",
        "src/utils", 
        "src/features",
        "src/modules",
        "src/gui",
        "tests",
        "config",
        "assets",
        "assets/images",
        "assets/images/tincture"
    ]
    
    required_files = [
        "main.py",
        "requirements.txt",
        "config/default_config.yaml",
        "src/__init__.py",
        "src/core/__init__.py",
        "src/core/config_manager.py",
        "src/features/__init__.py",
        "src/features/image_recognition.py",
        "src/modules/__init__.py",
        "src/modules/tincture_module.py",
        "src/utils/__init__.py",
        "src/utils/keyboard_input.py",
        "tests/__init__.py"
    ]
    
    missing_dirs = []
    missing_files = []
    
    # ディレクトリチェック
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
        else:
            print(f"✓ Directory: {dir_path}")
    
    # ファイルチェック
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✓ File: {file_path}")
    
    if missing_dirs:
        print(f"\n✗ Missing directories: {missing_dirs}")
    
    if missing_files:
        print(f"\n✗ Missing files: {missing_files}")
    
    success = len(missing_dirs) == 0 and len(missing_files) == 0
    print(f"\nProject structure: {'✓ OK' if success else '✗ INCOMPLETE'}")
    return success

def test_python_syntax():
    """Python構文のテスト"""
    print("\n=== Python Syntax Test ===\n")
    
    python_files = []
    for pattern in ["**/*.py"]:
        python_files.extend(Path(".").glob(pattern))
    
    syntax_errors = []
    
    for file_path in python_files:
        # テスト関連やキャッシュファイルをスキップ
        if any(skip in str(file_path) for skip in ["__pycache__", ".pytest_cache", "venv", "test_"]):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            ast.parse(source)
            print(f"✓ {file_path}")
        except SyntaxError as e:
            error_msg = f"{file_path}: {e}"
            syntax_errors.append(error_msg)
            print(f"✗ {error_msg}")
        except UnicodeDecodeError as e:
            error_msg = f"{file_path}: Encoding error - {e}"
            syntax_errors.append(error_msg)
            print(f"✗ {error_msg}")
        except Exception as e:
            error_msg = f"{file_path}: {e}"
            syntax_errors.append(error_msg)
            print(f"⚠ {error_msg}")
    
    success = len(syntax_errors) == 0
    print(f"\nPython syntax: {'✓ OK' if success else f'✗ {len(syntax_errors)} errors'}")
    return success

def test_configuration():
    """設定ファイルのテスト"""
    print("\n=== Configuration Test ===\n")
    
    try:
        # YAMLが利用可能かチェック
        import yaml
        
        # 設定ファイルの読み込みテスト
        config_path = Path("config/default_config.yaml")
        if not config_path.exists():
            print("✗ config/default_config.yaml not found")
            return False
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("✓ Configuration file loaded successfully")
        
        # 必要な設定セクションのチェック
        required_sections = ['general', 'tincture', 'flask', 'skills']
        missing_sections = []
        
        for section in required_sections:
            if section in config:
                print(f"✓ Section: {section}")
            else:
                missing_sections.append(section)
                print(f"✗ Missing section: {section}")
        
        # Tincture設定の詳細チェック
        if 'tincture' in config:
            tincture_config = config['tincture']
            required_keys = ['enabled', 'key', 'monitor_config', 'sensitivity']
            
            for key in required_keys:
                if key in tincture_config:
                    print(f"✓ Tincture.{key}: {tincture_config[key]}")
                else:
                    print(f"✗ Missing tincture.{key}")
        
        success = len(missing_sections) == 0
        print(f"\nConfiguration: {'✓ OK' if success else '✗ INCOMPLETE'}")
        return success
        
    except ImportError:
        print("⚠ PyYAML not available, skipping configuration test")
        print("Install with: pip install PyYAML")
        return False
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_import_safety():
    """安全なインポートテスト"""
    print("\n=== Safe Import Test ===\n")
    
    # 基本的なPythonモジュール
    basic_modules = ['os', 'sys', 'time', 'threading', 'logging', 'pathlib']
    
    for module in basic_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            return False
    
    # 設定管理のテスト（YAMLが利用可能な場合）
    try:
        import yaml
        from src.core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        print("✓ ConfigManager")
        print(f"  Loaded {len(config)} configuration sections")
        
    except ImportError as e:
        print(f"⚠ ConfigManager skipped: {e}")
    except Exception as e:
        print(f"✗ ConfigManager failed: {e}")
        return False
    
    print("\nSafe imports: ✓ OK")
    return True

def test_demo_scripts():
    """デモスクリプトの構文テスト"""
    print("\n=== Demo Scripts Test ===\n")
    
    demo_scripts = [
        "demo_image_recognition.py",
        "demo_tincture_module.py",
        "create_placeholder_template.py",
        "create_tincture_templates.py"
    ]
    
    success = True
    
    for script in demo_scripts:
        script_path = Path(script)
        if not script_path.exists():
            print(f"⚠ {script}: not found")
            continue
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source = f.read()
            ast.parse(source)
            print(f"✓ {script}: syntax OK")
        except Exception as e:
            print(f"✗ {script}: {e}")
            success = False
    
    return success

def test_unit_test_files():
    """ユニットテストファイルの構文テスト"""
    print("\n=== Unit Test Files Test ===\n")
    
    test_files = [
        "tests/test_image_recognition.py",
        "tests/test_tincture_module.py"
    ]
    
    success = True
    
    for test_file in test_files:
        test_path = Path(test_file)
        if not test_path.exists():
            print(f"⚠ {test_file}: not found")
            continue
        
        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                source = f.read()
            ast.parse(source)
            print(f"✓ {test_file}: syntax OK")
        except Exception as e:
            print(f"✗ {test_file}: {e}")
            success = False
    
    return success

def generate_dependency_report():
    """依存関係レポートを生成"""
    print("\n=== Dependency Report ===\n")
    
    # requirements.txtの読み込み
    req_path = Path("requirements.txt")
    if not req_path.exists():
        print("✗ requirements.txt not found")
        return
    
    with open(req_path, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print("Required packages:")
    for req in requirements:
        print(f"  - {req}")
    
    # 利用可能パッケージのチェック
    available = []
    missing = []
    
    package_map = {
        'opencv-python': 'cv2',
        'PyQt5': 'PyQt5',
        'PyYAML': 'yaml',
        'python-dotenv': 'dotenv',
        'pillow': 'PIL',
        'pyautogui': 'pyautogui',
        'pynput': 'pynput',
        'psutil': 'psutil',
        'requests': 'requests',
        'colorama': 'colorama',
        'mss': 'mss',
        'numpy': 'numpy'
    }
    
    print("\nPackage availability:")
    for req in requirements:
        package_name = req.split('==')[0].split('>=')[0]
        import_name = package_map.get(package_name, package_name)
        
        try:
            __import__(import_name)
            available.append(package_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            missing.append(package_name)
            print(f"  ✗ {package_name}")
    
    print(f"\nSummary:")
    print(f"  Available: {len(available)}/{len(requirements)}")
    print(f"  Missing: {len(missing)}")
    
    if missing:
        print(f"\nTo install missing packages:")
        print(f"  pip install {' '.join(missing)}")

def generate_test_summary():
    """テスト結果サマリーを生成"""
    print("\n" + "=" * 60)
    print("POE MACRO V3.0 - COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    # 各テストの実行
    tests = [
        ("Project Structure", test_project_structure),
        ("Python Syntax", test_python_syntax),
        ("Configuration", test_configuration),
        ("Safe Imports", test_import_safety),
        ("Demo Scripts", test_demo_scripts),
        ("Unit Test Files", test_unit_test_files)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # 依存関係レポート
    generate_dependency_report()
    
    # 最終サマリー
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The project structure is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test image recognition: python demo_image_recognition.py")
        print("3. Test tincture module: python demo_tincture_module.py")
        print("4. Launch GUI: python main.py")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please address the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = generate_test_summary()
    sys.exit(0 if success else 1)
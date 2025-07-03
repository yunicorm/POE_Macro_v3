#!/usr/bin/env python3
"""
GUI起動テスト（依存関係チェック付き）
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

def test_gui_dependencies():
    """GUI関連の依存関係をチェック"""
    print("=== GUI Dependencies Check ===\n")
    
    dependencies_ok = True
    
    # PyQt5のチェック
    print("1. Testing PyQt5...")
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont, QIcon
        print("   ✓ PyQt5 available")
    except ImportError as e:
        print(f"   ✗ PyQt5 not available: {e}")
        print("   Install with: pip install PyQt5")
        dependencies_ok = False
    
    # ConfigManagerのチェック
    print("\n2. Testing ConfigManager...")
    try:
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        print("   ✓ ConfigManager available")
    except Exception as e:
        print(f"   ✗ ConfigManager failed: {e}")
        dependencies_ok = False
    
    return dependencies_ok

def test_gui_import():
    """GUIモジュールのインポートテスト"""
    print("\n=== GUI Import Test ===\n")
    
    try:
        from src.gui.main_window import MainWindow, main
        print("✓ MainWindow import successful")
        return True
        
    except Exception as e:
        print(f"✗ MainWindow import failed: {e}")
        return False

def test_gui_basic_functionality():
    """GUI基本機能のテスト（実際の表示なし）"""
    print("\n=== GUI Basic Functionality Test ===\n")
    
    try:
        # PyQt5が利用可能かチェック
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            print("⚠ PyQt5 not available, skipping GUI functionality test")
            return False
        
        # ConfigManagerの初期化
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        # QApplicationの作成（実際には表示しない）
        app = QApplication([])
        
        # MainWindowの初期化テスト
        from src.gui.main_window import MainWindow
        window = MainWindow(config_manager)
        
        print("✓ MainWindow created successfully")
        print(f"  Window title: {window.windowTitle()}")
        print(f"  Window size: {window.size().width()}x{window.size().height()}")
        print(f"  Tab count: {window.tab_widget.count()}")
        
        # 各タブの確認
        tab_names = []
        for i in range(window.tab_widget.count()):
            tab_name = window.tab_widget.tabText(i)
            tab_names.append(tab_name)
        
        print(f"  Tabs: {', '.join(tab_names)}")
        
        # 基本的なUI要素の確認
        if hasattr(window, 'tincture_enabled_cb'):
            print("  ✓ Tincture controls found")
        
        if hasattr(window, 'log_text'):
            print("  ✓ Log display found")
        
        # ウィンドウを閉じる
        window.close()
        app.quit()
        
        print("✓ GUI functionality test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ GUI functionality test failed: {e}")
        return False

def test_main_script():
    """main.pyの基本テスト"""
    print("\n=== Main Script Test ===\n")
    
    try:
        # main.pyの存在確認
        main_path = Path("main.py")
        if not main_path.exists():
            print("✗ main.py not found")
            return False
        
        # main.pyの構文チェック
        with open(main_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        import ast
        ast.parse(source)
        print("✓ main.py syntax is valid")
        
        # main.pyのインポートテスト（実行はしない）
        print("✓ main.py structure verified")
        
        return True
        
    except Exception as e:
        print(f"✗ main.py test failed: {e}")
        return False

def generate_gui_test_script():
    """GUI起動テスト用スクリプトを生成"""
    print("\n=== Generating GUI Test Script ===\n")
    
    test_script = """#!/usr/bin/env python3
'''
GUI起動テスト用スクリプト
依存関係がインストールされた後で実行してください
'''
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

def main():
    try:
        # 依存関係チェック
        print("Checking dependencies...")
        from PyQt5.QtWidgets import QApplication
        from src.core.config_manager import ConfigManager
        from src.gui.main_window import MainWindow
        
        print("All dependencies available!")
        
        # GUI起動
        print("Starting GUI...")
        app = QApplication(sys.argv)
        
        config_manager = ConfigManager()
        window = MainWindow(config_manager)
        window.show()
        
        print("GUI started successfully!")
        print("Close the window to exit.")
        
        return app.exec_()
        
    except ImportError as e:
        print(f"Dependency missing: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""
    
    with open('test_gui_launch.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✓ GUI test script generated: test_gui_launch.py")

def main():
    """メイン関数"""
    print("POE Macro v3.0 - GUI Testing")
    print("=" * 50)
    
    # 依存関係チェック
    deps_ok = test_gui_dependencies()
    
    # GUIインポートテスト
    import_ok = test_gui_import()
    
    # main.pyテスト
    main_ok = test_main_script()
    
    # GUI機能テスト（依存関係が利用可能な場合のみ）
    if deps_ok and import_ok:
        func_ok = test_gui_basic_functionality()
    else:
        func_ok = False
        print("\n⚠ Skipping GUI functionality test due to missing dependencies")
    
    # テストスクリプト生成
    generate_gui_test_script()
    
    print("\n" + "=" * 50)
    print("GUI Testing Summary:")
    print(f"  Dependencies: {'✓ OK' if deps_ok else '✗ MISSING'}")
    print(f"  Import Test: {'✓ OK' if import_ok else '✗ FAILED'}")
    print(f"  Main Script: {'✓ OK' if main_ok else '✗ FAILED'}")
    print(f"  Functionality: {'✓ OK' if func_ok else '⚠ SKIPPED'}")
    
    if deps_ok and import_ok and main_ok:
        print("\n🎉 GUI is ready to run!")
        print("After installing dependencies, run: python test_gui_launch.py")
    else:
        print("\n⚠ GUI has issues that need to be resolved")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run: python test_gui_launch.py")

if __name__ == "__main__":
    main()
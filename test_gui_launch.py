#!/usr/bin/env python3
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

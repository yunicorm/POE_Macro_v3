#!/usr/bin/env python3
"""
Path of Exile Automation Macro v3.0
Main application entry point
"""

import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# プロジェクトのsrcディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config_manager import ConfigManager
from modules.flask_module import FlaskModule
from utils.keyboard_input import KeyboardController
from utils.screen_capture import ScreenCapture
from utils.image_recognition import ImageRecognition

def setup_logging():
    """ログ設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('macro.log'),
            logging.StreamHandler()
        ]
    )

def test_modules():
    """基本モジュールのテスト"""
    logger = logging.getLogger(__name__)
    logger.info("=== POE Macro v3.0 Module Test ===")
    
    try:
        # 設定管理のテスト
        config_manager = ConfigManager()
        logger.info("✓ ConfigManager initialized")
        
        # キーボード制御のテスト
        keyboard = KeyboardController()
        logger.info("✓ KeyboardController initialized")
        
        # 画面キャプチャのテスト
        screen_capture = ScreenCapture()
        logger.info("✓ ScreenCapture initialized")
        
        # 画像認識のテスト
        image_recognition = ImageRecognition()
        logger.info("✓ ImageRecognition initialized")
        
        logger.info("All modules initialized successfully!")
        
    except Exception as e:
        logger.error(f"Module test failed: {e}")
        return False
    
    return True

def main():
    """メイン関数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting POE Macro v3.0...")
    
    # 基本モジュールのテスト
    if not test_modules():
        logger.error("Module test failed. Exiting...")
        return 1
    
    # GUI アプリケーションの準備
    app = QApplication(sys.argv)
    
    # TODO: GUI実装後にコメントアウトを削除
    # from gui.main_window import MainWindow
    # main_window = MainWindow()
    # main_window.show()
    
    logger.info("POE Macro v3.0 started successfully!")
    logger.info("Press Ctrl+C to exit...")
    
    try:
        # TODO: GUI実装後にapp.exec_()を使用
        # return app.exec_()
        input("Press Enter to exit...")
        return 0
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        return 0

if __name__ == "__main__":
    sys.exit(main())
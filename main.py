#!/usr/bin/env python3
"""
Path of Exile Automation Macro v3.0
Main application entry point
"""

import sys
import logging
import argparse
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from logging.handlers import RotatingFileHandler

# プロジェクトのsrcディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config_manager import ConfigManager
from core.macro_controller import MacroController
from modules.flask_module import FlaskModule
from utils.keyboard_input import KeyboardController
from utils.screen_capture import ScreenCapture
from utils.image_recognition import ImageRecognition

def setup_logging(debug_mode=False):
    """ログ設定"""
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    # ログフォーマット
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # ファイルハンドラー（ローテーション付き）
    file_handler = RotatingFileHandler(
        'logs/macro.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # ログディレクトリの作成
    Path('logs').mkdir(exist_ok=True)

def test_modules():
    """基本モジュールのテスト"""
    logger = logging.getLogger(__name__)
    logger.info("=== POE Macro v3.0 Module Test ===")
    
    try:
        # 設定管理のテスト
        config_manager = ConfigManager()
        logger.info("[OK] ConfigManager initialized")
        
        # キーボード制御のテスト
        keyboard = KeyboardController()
        logger.info("[OK] KeyboardController initialized")
        
        # 画面キャプチャのテスト
        screen_capture = ScreenCapture()
        logger.info("[OK] ScreenCapture initialized")
        
        # 画像認識のテスト
        image_recognition = ImageRecognition()
        logger.info("[OK] ImageRecognition initialized")
        
        logger.info("All modules initialized successfully!")
        
    except Exception as e:
        logger.error(f"Module test failed: {e}")
        return False
    
    return True

def main():
    """メイン関数"""
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='POE Macro v3.0')
    parser.add_argument('--no-gui', action='store_true', help='Run without GUI')
    parser.add_argument('--config', type=str, help='Config file path')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    # ログ設定
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting POE Macro v3.0...")
    
    # 基本モジュールのテスト
    if not test_modules():
        logger.error("Module test failed. Exiting...")
        return 1
    
    try:
        # 設定マネージャーの初期化
        config_path = args.config if args.config else 'config/default_config.yaml'
        config_manager = ConfigManager(config_path)
        logger.info(f"Using config file: {config_path}")
        
        # マクロコントローラーの初期化
        macro_controller = MacroController(config_manager)
        logger.info("MacroController initialized")
        
        if args.no_gui:
            # GUI無しモード
            logger.info("Running in headless mode")
            return run_headless(macro_controller)
        else:
            # GUIモード
            logger.info("Starting GUI mode")
            return run_gui(config_manager, macro_controller)
            
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        return 1

def run_headless(macro_controller):
    """GUI無しモードで実行"""
    logger = logging.getLogger(__name__)
    
    try:
        # マクロを開始
        macro_controller.start()
        logger.info("Macro started in headless mode")
        logger.info("Press Ctrl+C to exit...")
        
        # メインループ
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        macro_controller.stop()
        return 0
    except Exception as e:
        logger.error(f"Error in headless mode: {e}")
        macro_controller.stop()
        return 1

def run_gui(config_manager, macro_controller):
    """GUIモードで実行"""
    logger = logging.getLogger(__name__)
    
    try:
        # GUI アプリケーションの準備
        app = QApplication(sys.argv)
        
        # MainWindowを起動
        from gui.main_window import MainWindow
        main_window = MainWindow(config_manager, macro_controller)
        main_window.show()
        
        logger.info("POE Macro v3.0 started successfully!")
        logger.info("Press Ctrl+C to exit...")
        
        # PyQt5のイベントループを開始
        return app.exec_()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        return 0
    except Exception as e:
        logger.error(f"Error in GUI mode: {e}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
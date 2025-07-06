#!/usr/bin/env python3
"""
Path of Exile Automation Macro v3.0
Main application entry point
"""

import sys
import logging
import argparse
from pathlib import Path
from logging.handlers import RotatingFileHandler

# プロジェクトのsrcディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config_manager import ConfigManager
from core.macro_controller import MacroController
from modules.flask_module import FlaskModule
from utils.keyboard_input import KeyboardController
from utils.screen_capture import ScreenCapture
from utils.image_recognition import ImageRecognition

# ロガーの設定
logger = logging.getLogger(__name__)

def setup_logging(debug_mode=False):
    """ログ設定"""
    # Tincture動作確認のためDEBUGレベルに設定
    log_level = logging.DEBUG  # Tincture検出のデバッグ情報を表示
    # log_level = logging.DEBUG if debug_mode else logging.INFO  # 通常はこちら
    
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
        config_path = args.config if args.config else 'default_config.yaml'
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

def detect_rightmost_monitor(app):
    """
    右端のモニターを検出し、MainWindow配置用の座標を返す
    
    Args:
        app: QApplication インスタンス
        
    Returns:
        tuple: (x, y) 座標のタプル。単一モニターの場合は None
    """
    logger = logging.getLogger(__name__)
    
    try:
        screens = app.screens()
        logger.info(f"検出されたモニター数: {len(screens)}")
        
        if len(screens) <= 1:
            logger.info("単一モニター環境のためデフォルト位置を使用")
            return None
        
        # 各モニターの情報をログ出力
        for i, screen in enumerate(screens):
            geometry = screen.geometry()
            logger.info(f"モニター{i+1}: X={geometry.x()}, Y={geometry.y()}, "
                       f"W={geometry.width()}, H={geometry.height()}")
        
        # 最もX座標が大きいスクリーンを右モニターとして検出
        rightmost_screen = max(screens, key=lambda s: s.geometry().x())
        geometry = rightmost_screen.geometry()
        
        # 右モニターの適切な位置を計算（左端から100px、上端から100px）
        position_x = geometry.x() + 100
        position_y = geometry.y() + 100
        
        logger.info(f"右モニター検出: X={geometry.x()}, Y={geometry.y()}")
        logger.info(f"MainWindow配置位置: X={position_x}, Y={position_y}")
        
        return (position_x, position_y)
        
    except Exception as e:
        logger.error(f"モニター検出エラー: {e}")
        return None

def run_headless(macro_controller):
    """GUI無しモードで実行"""
    logger = logging.getLogger(__name__)
    
    try:
        # Grace Period設定を確認してマクロを開始
        config = macro_controller.config
        respect_grace_period = config.get('general', {}).get('respect_grace_period', True)
        
        if respect_grace_period:
            logger.info("Starting macro in headless mode with Grace Period support")
            # Grace Periodを考慮（エリア状況に応じて待機）
            macro_controller.start(respect_grace_period=True)
        else:
            logger.info("Starting macro in headless mode (Grace Period disabled)")
            # 従来通り即座開始
            macro_controller.start(force=True)
            
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
    """GUIモードで実行（修正版）"""
    logger = logging.getLogger(__name__)  # tryブロックの前に移動
    
    try:
        logger.info("run_gui開始 - loggerが正常に初期化されました")
        
        # GUI アプリケーションの準備
        logger.info("PyQt5とQApplicationを初期化中...")
        try:
            from PyQt5.QtWidgets import QApplication
            app = QApplication(sys.argv)
            logger.info("QApplicationが正常に初期化されました")
        except ImportError as e:
            logger.error(f"PyQt5のインポートに失敗: {e}")
            raise
        except Exception as e:
            logger.error(f"QApplication初期化エラー: {e}")
            import traceback
            logger.error(f"QApplication traceback: {traceback.format_exc()}")
            raise
        
        # ステータスオーバーレイを作成（設定から位置を読み込む）
        logger.info("StatusOverlayをインポート中...")
        try:
            from src.features.status_overlay import StatusOverlay
            logger.info("StatusOverlayのインポートが完了しました")
        except ImportError as import_error:
            logger.error(f"StatusOverlayのimportに失敗: {import_error}")
            import traceback
            logger.error(f"Import traceback: {traceback.format_exc()}")
            raise
        except Exception as e:
            logger.error(f"StatusOverlayインポート時の予期しないエラー: {e}")
            import traceback
            logger.error(f"Unexpected error traceback: {traceback.format_exc()}")
            raise
        overlay_config = config_manager.config.get('overlay', {}).get('status_position', {})
        font_size = config_manager.config.get('overlay', {}).get('font_size', 16)
        
        status_overlay = StatusOverlay(font_size=font_size)
        if overlay_config:
            status_overlay.load_position(
                overlay_config.get('x', 1720),
                overlay_config.get('y', 1050)
            )
        
        # 位置変更時の自動保存機能
        def on_position_changed(x, y):
            # nested function内でloggerを明示的に取得
            local_logger = logging.getLogger(__name__)
            try:
                if 'overlay' not in config_manager.config:
                    config_manager.config['overlay'] = {}
                if 'status_position' not in config_manager.config['overlay']:
                    config_manager.config['overlay']['status_position'] = {}
                
                config_manager.config['overlay']['status_position']['x'] = x
                config_manager.config['overlay']['status_position']['y'] = y
                config_manager.save_config(config_manager.config)
                local_logger.info(f"オーバーレイ位置を保存しました: X={x}, Y={y}")
            except Exception as e:
                local_logger.error(f"オーバーレイ位置保存エラー: {e}")
        
        status_overlay.position_changed.connect(on_position_changed)
        status_overlay.show()
        
        # MacroControllerにオーバーレイを設定
        macro_controller.set_status_overlay(status_overlay)
        
        # MainWindowを起動
        from src.gui.main_window import MainWindow
        main_window = MainWindow(config_manager, macro_controller)
        
        # 右モニター検出と位置設定
        try:
            position = detect_rightmost_monitor(app)
            if position:
                main_window.move(position[0], position[1])
                logger.info(f"設定ウィンドウを右モニターに配置: X={position[0]}, Y={position[1]}")
            else:
                logger.info("デフォルト位置で設定ウィンドウを表示")
        except Exception as e:
            logger.error(f"MainWindow位置設定エラー: {e} - デフォルト位置を使用")
        
        main_window.show()
        
        # 初期状態を設定（マクロオフ）
        status_overlay.set_macro_status(False)
        
        logger.info("POE Macro v3.0 started successfully with status overlay!")
        logger.info("Press Ctrl+C to exit...")
        
        # PyQt5のイベントループを開始
        return app.exec_()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        return 0
    except Exception as e:
        logger.error(f"Error in GUI mode: {e}")
        import traceback
        logger.error(f"GUI mode traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
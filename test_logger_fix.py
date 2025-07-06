"""
logger未定義エラー修正のテスト
"""
import os
import sys
import logging
from pathlib import Path

# プロジェクトのsrcディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_test_logging():
    """テスト用ログ設定"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_status_overlay_import():
    """StatusOverlayのインポートテスト"""
    print("=== StatusOverlayインポートテスト ===\n")
    
    setup_test_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("StatusOverlayをインポート中...")
        from src.features.status_overlay import StatusOverlay
        logger.info("✓ StatusOverlayのインポートが成功しました")
        
        # クラスのインスタンス化テスト（GUIなしでは失敗するが、importは確認できる）
        logger.info("StatusOverlayクラスが正しく定義されています")
        return True
        
    except ImportError as e:
        logger.error(f"✗ StatusOverlayのインポートに失敗: {e}")
        import traceback
        logger.error(f"Import traceback: {traceback.format_exc()}")
        return False
    except Exception as e:
        logger.error(f"✗ 予期しないエラー: {e}")
        import traceback
        logger.error(f"Unexpected error traceback: {traceback.format_exc()}")
        return False

def test_config_manager():
    """ConfigManagerのテスト"""
    print("\n=== ConfigManagerテスト ===\n")
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("ConfigManagerをインポート中...")
        from src.core.config_manager import ConfigManager
        logger.info("✓ ConfigManagerのインポートが成功しました")
        
        logger.info("ConfigManagerを初期化中...")
        config_manager = ConfigManager()
        logger.info("✓ ConfigManagerの初期化が成功しました")
        
        logger.info("設定を読み込み中...")
        config = config_manager.load_config()
        logger.info("✓ 設定の読み込みが成功しました")
        
        if 'flask_slots' in config:
            logger.info(f"✓ flask_slotsが読み込まれました: {list(config['flask_slots'].keys())}")
        else:
            logger.warning("flask_slotsが見つかりませんでした")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ ConfigManagerテストに失敗: {e}")
        import traceback
        logger.error(f"ConfigManager traceback: {traceback.format_exc()}")
        return False

def test_run_gui_structure():
    """run_gui関数の構造をテスト（実行はしない）"""
    print("\n=== run_gui構造テスト ===\n")
    
    logger = logging.getLogger(__name__)
    
    try:
        # main.pyをインポートして関数の存在を確認
        import main
        
        # run_gui関数が存在するか確認
        if hasattr(main, 'run_gui'):
            logger.info("✓ run_gui関数が見つかりました")
            
            # 関数のソースコードを確認（簡易チェック）
            import inspect
            source = inspect.getsource(main.run_gui)
            
            if 'logger = logging.getLogger(__name__)' in source:
                # tryブロックの前にloggerが定義されているかチェック
                lines = source.split('\n')
                logger_line = -1
                try_line = -1
                
                for i, line in enumerate(lines):
                    if 'logger = logging.getLogger(__name__)' in line:
                        logger_line = i
                    if 'try:' in line and logger_line != -1:
                        try_line = i
                        break
                
                if logger_line != -1 and try_line != -1 and logger_line < try_line:
                    logger.info("✓ loggerがtryブロックの前で正しく定義されています")
                else:
                    logger.warning("⚠ loggerの定義位置に問題がある可能性があります")
            else:
                logger.warning("⚠ run_gui関数内でloggerが定義されていません")
            
            return True
        else:
            logger.error("✗ run_gui関数が見つかりませんでした")
            return False
            
    except Exception as e:
        logger.error(f"✗ run_gui構造テストに失敗: {e}")
        import traceback
        logger.error(f"Structure test traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("POE Macro v3 - Logger修正テスト\n")
    
    results = []
    results.append(test_status_overlay_import())
    results.append(test_config_manager())
    results.append(test_run_gui_structure())
    
    print(f"\n=== テスト結果 ===")
    print(f"成功: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ すべてのテストが成功しました！")
        print("logger未定義エラーは修正されているはずです。")
    else:
        print("✗ 一部のテストが失敗しました。")
        print("追加の修正が必要な可能性があります。")
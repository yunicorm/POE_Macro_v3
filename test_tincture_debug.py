#!/usr/bin/env python3
"""
Tincture機能デバッグテスト
"""

import sys
import logging
from pathlib import Path

# プロジェクトのsrcディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config_manager import ConfigManager
from core.macro_controller import MacroController

def setup_debug_logging():
    """デバッグログ設定"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Tincture機能のデバッグテスト"""
    print("=== Tincture機能デバッグテスト ===")
    
    # ログ設定
    setup_debug_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 設定管理
        logger.info("ConfigManagerを初期化中...")
        config_manager = ConfigManager("config/default_config.yaml")
        config = config_manager.load_config()
        
        # 設定確認
        logger.info(f"全体設定: {config}")
        tincture_config = config.get('tincture', {})
        logger.info(f"Tincture設定: {tincture_config}")
        
        # MacroControllerを初期化
        logger.info("MacroControllerを初期化中...")
        controller = MacroController(config_manager)
        
        # Tincture機能の詳細確認
        tincture_module = controller.tincture_module
        logger.info(f"TinctureModule enabled: {tincture_module.enabled}")
        logger.info(f"TinctureModule key: {tincture_module.key}")
        logger.info(f"TinctureModule sensitivity: {tincture_module.sensitivity}")
        
        # 検出器の情報確認
        detector = tincture_module.detector
        area_info = detector.get_detection_area_info()
        logger.info(f"検出エリア情報: {area_info}")
        
        # テンプレート画像確認
        template_path = detector.template_path
        logger.info(f"テンプレート画像パス: {template_path}")
        logger.info(f"テンプレート画像存在: {template_path.exists()}")
        
        if template_path.exists():
            import cv2
            template = cv2.imread(str(template_path))
            if template is not None:
                logger.info(f"テンプレート画像サイズ: {template.shape}")
            else:
                logger.error("テンプレート画像の読み込みに失敗")
        
        # 単発検出テスト
        logger.info("=== 単発検出テスト ===")
        try:
            detected = detector.detect_tincture_icon()
            logger.info(f"検出結果: {detected}")
        except Exception as e:
            logger.error(f"検出テストエラー: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        # マクロ開始テスト（10秒間）
        print("\n=== Tincture機能テスト開始 ===")
        print("10秒間Tinctureの検出・使用をテストします...")
        
        controller.start()
        
        import time
        start_time = time.time()
        while time.time() - start_time < 10:
            status = controller.get_status()
            tincture_status = status.get('tincture', {})
            stats = tincture_status.get('stats', {})
            
            print(f"実行中... 経過時間: {int(time.time() - start_time)}秒")
            print(f"  Tincture実行中: {tincture_status.get('running', False)}")
            print(f"  総使用回数: {stats.get('total_uses', 0)}")
            print(f"  成功検出: {stats.get('successful_detections', 0)}")
            print(f"  失敗検出: {stats.get('failed_detections', 0)}")
            
            time.sleep(1)
        
        controller.stop()
        
        # 最終統計
        final_status = controller.get_status()
        final_tincture = final_status.get('tincture', {})
        final_stats = final_tincture.get('stats', {})
        
        print("\n=== 最終結果 ===")
        print(f"総使用回数: {final_stats.get('total_uses', 0)}")
        print(f"成功検出: {final_stats.get('successful_detections', 0)}")
        print(f"失敗検出: {final_stats.get('failed_detections', 0)}")
        
        if final_stats.get('total_uses', 0) > 0:
            print("✅ Tincture機能は正常に動作しています！")
        else:
            print("❌ Tincture機能が動作していません。ログを確認してください。")
        
    except Exception as e:
        logger.error(f"テストエラー: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
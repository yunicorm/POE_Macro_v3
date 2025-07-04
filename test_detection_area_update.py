#!/usr/bin/env python3
"""
検出エリア更新機能のテストスクリプト
GUI で設定した検出エリアが正しく TinctureModule に反映されるかを確認
"""

import sys
import os
import logging
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# ログレベルを DEBUG に設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_detection_area_update():
    """検出エリア更新機能のテスト"""
    
    print("=== 検出エリア更新機能テスト ===")
    
    try:
        # 1. 設定ファイルの読み込み
        print("1. 設定ファイルの読み込み...")
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # 2. AreaSelectorの初期化
        print("2. AreaSelectorの初期化...")
        from src.features.area_selector import AreaSelector
        area_selector = AreaSelector()
        
        # 3. TinctureModuleの初期化
        print("3. TinctureModuleの初期化...")
        from src.modules.tincture_module import TinctureModule
        tincture_module = TinctureModule(config.get('tincture', {}))
        
        # 4. 初期設定の確認
        print("4. 初期設定の確認...")
        if tincture_module.area_selector:
            # Slot 3 functionality removed - using full flask area instead
            current_area = tincture_module.area_selector.get_full_flask_area_for_tincture()
            print(f"   初期検出エリア: X:{current_area['x']}, Y:{current_area['y']}, W:{current_area['width']}, H:{current_area['height']}")
        else:
            print("   AreaSelectorが設定されていません")
        
        # 5. 検出エリアの変更テスト
        print("5. 検出エリアの変更テスト...")
        test_area = {
            'x': 100,
            'y': 200,
            'width': 150,
            'height': 120
        }
        
        # 新しいエリアを設定
        area_selector.set_flask_area(test_area['x'], test_area['y'], test_area['width'], test_area['height'])
        print(f"   新しいフラスコエリア設定: {test_area}")
        
        # 6. TinctureModuleへの反映テスト
        print("6. TinctureModuleへの反映テスト...")
        tincture_module.update_detection_area(area_selector)
        
        # 7. 変更後の設定確認
        print("7. 変更後の設定確認...")
        if tincture_module.area_selector:
            # Slot 3 functionality removed - using full flask area instead
            updated_area = tincture_module.area_selector.get_full_flask_area_for_tincture()
            print(f"   更新後検出エリア: X:{updated_area['x']}, Y:{updated_area['y']}, W:{updated_area['width']}, H:{updated_area['height']}")
            
            # 8. 変更の確認
            print("8. 変更の確認...")
            if (updated_area['x'] == test_area['x'] + area_selector.get_tincture_offset()['x'] and
                updated_area['y'] == test_area['y'] + area_selector.get_tincture_offset()['y']):
                print("   ✓ 検出エリア更新成功!")
                success = True
            else:
                print("   ✗ 検出エリア更新失敗!")
                success = False
        else:
            print("   ✗ AreaSelectorが設定されていません")
            success = False
        
        # 9. TinctureDetectorでの検出テスト
        print("9. TinctureDetectorでの検出テスト...")
        try:
            detector = tincture_module.detector
            if detector:
                print("   検出テストを実行中...")
                # 実際の検出は実行しないが、設定の確認を行う
                area_info = detector.get_detection_area_info()
                print(f"   検出器設定: {area_info}")
                print("   ✓ 検出器設定確認完了")
            else:
                print("   ✗ TinctureDetectorが利用できません")
                success = False
        except Exception as e:
            print(f"   ✗ 検出テストエラー: {e}")
            success = False
        
        # 10. 結果サマリー
        print("10. 結果サマリー...")
        if success:
            print("   ✓ 検出エリア更新機能テスト成功!")
            return True
        else:
            print("   ✗ 検出エリア更新機能テスト失敗!")
            return False
            
    except Exception as e:
        print(f"テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_integration():
    """GUI統合テスト（実際のGUIは起動せず、ロジックのみテスト）"""
    
    print("\n=== GUI統合テスト ===")
    
    try:
        # ConfigManagerとAreaSelectorの初期化
        from src.core.config_manager import ConfigManager
        from src.features.area_selector import AreaSelector
        from src.core.macro_controller import MacroController
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        area_selector = AreaSelector()
        
        # MacroControllerの初期化
        macro_controller = MacroController(config)
        
        # 検出エリアの変更をシミュレート
        print("1. 検出エリア変更シミュレート...")
        new_area = {
            'x': 300,
            'y': 400,
            'width': 200,
            'height': 150
        }
        
        area_selector.set_flask_area(new_area['x'], new_area['y'], new_area['width'], new_area['height'])
        
        # MacroControllerのTinctureModuleを更新
        print("2. MacroControllerのTinctureModule更新...")
        if macro_controller.tincture_module:
            macro_controller.tincture_module.update_detection_area(area_selector)
            print("   ✓ TinctureModule更新完了")
            
            # 設定確認
            # Slot 3 functionality removed - using full flask area instead
            updated_area = macro_controller.tincture_module.area_selector.get_full_flask_area_for_tincture()
            print(f"   更新後検出エリア: X:{updated_area['x']}, Y:{updated_area['y']}, W:{updated_area['width']}, H:{updated_area['height']}")
            
            return True
        else:
            print("   ✗ TinctureModuleが利用できません")
            return False
            
    except Exception as e:
        print(f"GUI統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("検出エリア更新機能テスト開始...")
    
    # 基本機能テスト
    test1_result = test_detection_area_update()
    
    # GUI統合テスト
    test2_result = test_gui_integration()
    
    # 最終結果
    print("\n=== 最終結果 ===")
    if test1_result and test2_result:
        print("✓ 全てのテストが成功しました!")
        sys.exit(0)
    else:
        print("✗ テストが失敗しました")
        sys.exit(1)
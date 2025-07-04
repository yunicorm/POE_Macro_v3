"""
POE Macro v3.0 - 座標同期問題診断ツール
オーバーレイとGUI設定の座標不整合を調査・修正
"""

import os
import sys
import yaml
import logging

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath('.'))

def test_area_selector_operations():
    """AreaSelectorの各操作をテストして座標の流れを確認"""
    print("=== AreaSelector操作テスト ===")
    
    try:
        from src.features.area_selector import AreaSelector
        
        # ログレベルを設定
        logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s: %(message)s')
        
        print("\n1. AreaSelector初期化")
        area_selector = AreaSelector()
        
        print("\n2. 現在の設定読み込み")
        current_area = area_selector.get_flask_area()
        print(f"   現在の座標: X={current_area['x']}, Y={current_area['y']}, W={current_area['width']}, H={current_area['height']}")
        
        print("\n3. 新しい座標を設定（テスト）")
        test_x, test_y, test_w, test_h = 914, 1279, 400, 160
        area_selector.set_flask_area(test_x, test_y, test_w, test_h)
        print(f"   設定座標: X={test_x}, Y={test_y}, W={test_w}, H={test_h}")
        
        print("\n4. 設定後の値を再取得")
        updated_area = area_selector.get_flask_area()
        print(f"   再取得座標: X={updated_area['x']}, Y={updated_area['y']}, W={updated_area['width']}, H={updated_area['height']}")
        
        # 値が一致するかチェック
        if (updated_area['x'] == test_x and 
            updated_area['y'] == test_y and 
            updated_area['width'] == test_w and 
            updated_area['height'] == test_h):
            print("   ✅ 座標設定・取得が正常に動作しています")
        else:
            print("   ❌ 座標設定・取得に不整合があります")
            print(f"      期待値: X={test_x}, Y={test_y}, W={test_w}, H={test_h}")
            print(f"      実際値: X={updated_area['x']}, Y={updated_area['y']}, W={updated_area['width']}, H={updated_area['height']}")
        
        print("\n5. フラスコエリア全体検出用エリアの取得")
        try:
            full_area = area_selector.get_full_flask_area_for_tincture()
            print(f"   フラスコ全体検出エリア: X={full_area['x']}, Y={full_area['y']}, W={full_area['width']}, H={full_area['height']}")
        except Exception as e:
            print(f"   ❌ フラスコ全体検出エリア取得エラー: {e}")
            
    except Exception as e:
        print(f"❌ AreaSelectorテストエラー: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")

def check_config_file_consistency():
    """設定ファイルの整合性をチェック"""
    print("\n=== 設定ファイル整合性チェック ===")
    
    config_files = {
        "detection_areas.yaml": "config/detection_areas.yaml",
        "default_config.yaml": "config/default_config.yaml"
    }
    
    coordinates = {}
    
    for name, path in config_files.items():
        print(f"\n📄 {name}:")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                # detection_areas.yamlのflask_area
                if 'flask_area' in config:
                    area = config['flask_area']
                    coordinates[name + '_flask'] = (area.get('x'), area.get('y'), area.get('width'), area.get('height'))
                    print(f"  Flask Area: X={area.get('x')}, Y={area.get('y')}, W={area.get('width')}, H={area.get('height')}")
                
                # default_config.yamlのtincture.detection_area
                if 'tincture' in config and 'detection_area' in config['tincture']:
                    area = config['tincture']['detection_area']
                    coordinates[name + '_tincture'] = (area.get('x'), area.get('y'), area.get('width'), area.get('height'))
                    print(f"  Tincture Area: X={area.get('x')}, Y={area.get('y')}, W={area.get('width')}, H={area.get('height')}")
                    
            except Exception as e:
                print(f"  ❌ ファイル読み込みエラー: {e}")
        else:
            print(f"  ❌ ファイルが存在しません")
    
    # 座標の整合性チェック
    print(f"\n🔍 座標整合性分析:")
    unique_coords = set(coordinates.values())
    if len(unique_coords) == 1:
        print("  ✅ すべての設定ファイルで座標が一致しています")
    else:
        print("  ❌ 設定ファイル間で座標に不整合があります:")
        for file_key, coords in coordinates.items():
            print(f"    {file_key}: X={coords[0]}, Y={coords[1]}, W={coords[2]}, H={coords[3]}")

def simulate_gui_workflow():
    """GUI操作のワークフローをシミュレート"""
    print("\n=== GUI操作ワークフローシミュレーション ===")
    
    try:
        from src.features.area_selector import AreaSelector
        
        print("\n1. GUI初期化時の座標読み込みシミュレーション")
        area_selector = AreaSelector()
        initial_area = area_selector.get_flask_area()
        print(f"   GUI初期表示予定座標: X={initial_area['x']}, Y={initial_area['y']}, W={initial_area['width']}, H={initial_area['height']}")
        
        print("\n2. オーバーレイ作成時の座標シミュレーション")
        overlay_coords = (
            initial_area.get('x', 245),
            initial_area.get('y', 850), 
            initial_area.get('width', 400),
            initial_area.get('height', 120)
        )
        print(f"   オーバーレイ作成座標: X={overlay_coords[0]}, Y={overlay_coords[1]}, W={overlay_coords[2]}, H={overlay_coords[3]}")
        
        print("\n3. オーバーレイで座標変更後の保存シミュレーション")
        new_coords = (920, 1285, 405, 165)  # ユーザーが調整したと仮定
        print(f"   ユーザー調整後座標: X={new_coords[0]}, Y={new_coords[1]}, W={new_coords[2]}, H={new_coords[3]}")
        
        # 座標を保存
        area_selector.set_flask_area(new_coords[0], new_coords[1], new_coords[2], new_coords[3])
        
        print("\n4. 保存後の設定確認")
        saved_area = area_selector.get_flask_area()
        print(f"   保存確認座標: X={saved_area['x']}, Y={saved_area['y']}, W={saved_area['width']}, H={saved_area['height']}")
        
        # 座標が一致するかチェック
        if (saved_area['x'] == new_coords[0] and saved_area['y'] == new_coords[1] and 
            saved_area['width'] == new_coords[2] and saved_area['height'] == new_coords[3]):
            print("   ✅ 座標の保存・読み込みが正常に動作しています")
        else:
            print("   ❌ 座標の保存・読み込みに問題があります")
            
    except Exception as e:
        print(f"❌ GUIワークフローシミュレーションエラー: {e}")

def fix_coordinate_inconsistency():
    """座標不整合を修正"""
    print("\n=== 座標不整合修正 ===")
    
    # 現在の正しい座標（detection_areas.yamlから）
    correct_coords = {
        'x': 914,
        'y': 1279, 
        'width': 400,
        'height': 160
    }
    
    print(f"正しい座標: X={correct_coords['x']}, Y={correct_coords['y']}, W={correct_coords['width']}, H={correct_coords['height']}")
    
    # default_config.yamlを修正
    default_config_path = "config/default_config.yaml"
    if os.path.exists(default_config_path):
        try:
            with open(default_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if 'tincture' not in config:
                config['tincture'] = {}
            
            config['tincture']['detection_mode'] = 'full_flask_area'
            config['tincture']['detection_area'] = correct_coords
            
            with open(default_config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ {default_config_path} を修正しました")
            
        except Exception as e:
            print(f"❌ {default_config_path} 修正エラー: {e}")
    
    print("\n修正完了。アプリケーションを再起動して確認してください。")

def main():
    """メイン実行関数"""
    print("=== POE Macro v3.0 座標同期問題診断ツール ===")
    print("オーバーレイとGUI設定の座標不整合を調査します\n")
    
    # 設定ファイル整合性チェック
    check_config_file_consistency()
    
    # AreaSelector操作テスト
    test_area_selector_operations()
    
    # GUIワークフローシミュレーション
    simulate_gui_workflow()
    
    # 修正オプション
    print("\n" + "="*60)
    response = input("座標不整合を自動修正しますか？ (y/N): ")
    if response.lower() in ['y', 'yes']:
        fix_coordinate_inconsistency()
    
    print("\n=== 診断完了 ===")
    print("問題が解決しない場合は、以下を確認してください：")
    print("1. アプリケーションの完全再起動")
    print("2. GUI初期化時のログ出力")
    print("3. オーバーレイ作成時のログ出力")
    print("4. 設定保存時のログ出力")

if __name__ == "__main__":
    main()
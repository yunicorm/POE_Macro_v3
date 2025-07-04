"""
POE Macro v3.0 - 設定反映テストと診断ツール
GUI設定変更が実行時に正しく反映されるかを確認
"""

import os
import sys
import yaml
import logging

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath('.'))

def check_config_files():
    """設定ファイルの内容を確認"""
    print("=== 設定ファイル確認 ===")
    
    files_to_check = [
        "config/detection_areas.yaml",
        "config/default_config.yaml"
    ]
    
    for file_path in files_to_check:
        print(f"\n📄 {file_path}:")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                if 'flask_area' in config:
                    flask_area = config['flask_area']
                    print(f"  ✓ Flask Area: X={flask_area.get('x')}, Y={flask_area.get('y')}, W={flask_area.get('width')}, H={flask_area.get('height')}")
                
                if 'tincture' in config:
                    tincture = config['tincture']
                    print(f"  ✓ Tincture モード: {tincture.get('detection_mode', 'N/A')}")
                    if 'detection_area' in tincture:
                        area = tincture['detection_area']
                        print(f"  ✓ Tincture 検出エリア: X={area.get('x')}, Y={area.get('y')}, W={area.get('width')}, H={area.get('height')}")
                        
            except Exception as e:
                print(f"  ❌ ファイル読み込みエラー: {e}")
        else:
            print(f"  ❌ ファイルが存在しません")

def test_area_selector():
    """AreaSelectorの動作テスト"""
    print("\n=== AreaSelector動作テスト ===")
    
    try:
        from src.features.area_selector import AreaSelector
        
        # AreaSelectorを初期化
        area_selector = AreaSelector()
        
        # 現在のフラスコエリアを取得
        flask_area = area_selector.get_flask_area()
        print(f"📍 現在のフラスコエリア: X={flask_area['x']}, Y={flask_area['y']}, W={flask_area['width']}, H={flask_area['height']}")
        
        # フラスコエリア全体検出用エリアを取得
        try:
            full_area = area_selector.get_full_flask_area_for_tincture()
            print(f"🎯 フラスコ全体検出エリア: X={full_area['x']}, Y={full_area['y']}, W={full_area['width']}, H={full_area['height']}")
            print(f"📐 検出範囲面積: {full_area['width'] * full_area['height']}px²")
        except Exception as e:
            print(f"❌ フラスコ全体検出エリア取得エラー: {e}")
            
        # 3番スロット自動計算エリアを取得
        try:
            # Slot 3 functionality removed - using full flask area instead
            slot_area = area_selector.get_full_flask_area_for_tincture()
            print(f"🎲 3番スロット自動計算: X={slot_area['x']}, Y={slot_area['y']}, W={slot_area['width']}, H={slot_area['height']}")
        except Exception as e:
            print(f"❌ 3番スロット計算エラー: {e}")
            
    except ImportError as e:
        print(f"❌ AreaSelectorインポートエラー: {e}")
    except Exception as e:
        print(f"❌ AreaSelectorテストエラー: {e}")

def test_tincture_detector():
    """TinctureDetectorの初期化テスト"""
    print("\n=== TinctureDetector初期化テスト ===")
    
    try:
        from src.features.image_recognition import TinctureDetector
        from src.features.area_selector import AreaSelector
        from src.core.config_manager import ConfigManager
        
        # 設定を読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # AreaSelectorを作成
        area_selector = AreaSelector()
        
        # TinctureDetectorを初期化（ログ出力に注目）
        print("🔍 TinctureDetector初期化中...")
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        
        detector = TinctureDetector(
            monitor_config=config.get('tincture', {}).get('monitor_config', 'Primary'),
            sensitivity=config.get('tincture', {}).get('sensitivity', 0.7),
            area_selector=area_selector,
            config=config
        )
        
        print(f"✅ 初期化成功")
        print(f"📡 検出モード: {detector.detection_mode}")
        print(f"🎯 検出感度: {detector.sensitivity}")
        
    except Exception as e:
        print(f"❌ TinctureDetector初期化エラー: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")

def provide_temporary_workarounds():
    """一時的な回避策を提供"""
    print("\n=== 一時的回避策 ===")
    
    print("1️⃣ **設定ファイル直接修正**:")
    print("   config/detection_areas.yaml を直接編集してください:")
    print("   ```yaml")
    print("   flask_area:")
    print("     x: 924")
    print("     y: 1279") 
    print("     width: 398")
    print("     height: 160  # この値を150から160に増加")
    print("   ```")
    
    print("\n2️⃣ **default_config.yaml更新**:")
    print("   config/default_config.yaml のtincture設定も更新してください:")
    print("   ```yaml")
    print("   tincture:")
    print("     detection_mode: \"full_flask_area\"")
    print("     detection_area:")
    print("       x: 924")
    print("       y: 1279")
    print("       width: 398")
    print("       height: 160")
    print("   ```")
    
    print("\n3️⃣ **アプリケーション再起動**:")
    print("   設定変更後は必ずアプリケーションを完全に再起動してください")
    
    print("\n4️⃣ **テンプレート画像確認**:")
    print("   assets/images/tincture/sap_of_the_seasons/idle/sap_of_the_seasons_idle.png")
    print("   このファイルのサイズと品質を確認してください")

def update_config_files_directly():
    """設定ファイルを直接更新（緊急用）"""
    print("\n=== 設定ファイル直接更新 ===")
    
    # detection_areas.yamlを更新
    detection_areas_path = "config/detection_areas.yaml"
    if os.path.exists(detection_areas_path):
        try:
            with open(detection_areas_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # heightを160に更新
            if 'flask_area' in config:
                old_height = config['flask_area'].get('height', 'N/A')
                config['flask_area']['height'] = 160
                
                with open(detection_areas_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True)
                
                print(f"✅ {detection_areas_path} 更新完了: height {old_height} → 160")
            
        except Exception as e:
            print(f"❌ {detection_areas_path} 更新エラー: {e}")
    
    # default_config.yamlを更新
    default_config_path = "config/default_config.yaml"
    if os.path.exists(default_config_path):
        try:
            with open(default_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # tincture設定を更新
            if 'tincture' not in config:
                config['tincture'] = {}
            
            config['tincture']['detection_mode'] = 'full_flask_area'
            config['tincture']['detection_area'] = {
                'x': 924,
                'y': 1279,
                'width': 398,
                'height': 160
            }
            
            with open(default_config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ {default_config_path} 更新完了")
            
        except Exception as e:
            print(f"❌ {default_config_path} 更新エラー: {e}")

def main():
    """メイン実行関数"""
    print("=== POE Macro v3.0 設定反映診断ツール ===")
    print("GUI設定変更が実行時に反映されない問題を診断します\n")
    
    # 設定ファイル確認
    check_config_files()
    
    # AreaSelectorテスト
    test_area_selector()
    
    # TinctureDetectorテスト
    test_tincture_detector()
    
    # 一時的回避策
    provide_temporary_workarounds()
    
    # 直接更新オプション
    print("\n" + "="*50)
    response = input("設定ファイルを直接更新しますか？ (y/N): ")
    if response.lower() in ['y', 'yes']:
        update_config_files_directly()
        print("\n✅ 設定ファイル更新完了。アプリケーションを再起動してください。")
    
    print("\n=== 診断完了 ===")
    print("問題が解決しない場合は、ログ出力を確認してください。")

if __name__ == "__main__":
    main()
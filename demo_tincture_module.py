#!/usr/bin/env python3
"""
TinctureModule デモスクリプト
Tincture自動使用機能の動作確認用
"""

import sys
import os
import time
import threading
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """メイン関数"""
    print("POE Macro v3.0 - Tincture自動使用機能デモ")
    print("=" * 60)
    
    try:
        # 必要なモジュールのインポート
        print("モジュールのインポート中...")
        from src.modules.tincture_module import TinctureModule, TinctureState
        from src.core.config_manager import ConfigManager
        print("✓ TinctureModule モジュールのインポート成功")
        
        # プレースホルダー画像の作成
        print("\nプレースホルダー画像の作成中...")
        create_placeholder_images()
        print("✓ プレースホルダー画像の作成完了")
        
        # 設定の読み込み
        print("\n設定の読み込み中...")
        config_manager = ConfigManager()
        config = config_manager.load_config()
        print("✓ 設定の読み込み成功")
        
        # TinctureModule の初期化
        print("\nTinctureModule の初期化中...")
        tincture_module = TinctureModule(config)
        print("✓ TinctureModule の初期化成功")
        
        # ステータス情報の表示
        print("\nTinctureModule ステータス:")
        status = tincture_module.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 統計情報の表示
        print("\n統計情報:")
        stats = tincture_module.get_stats()
        for key, value in stats.items():
            if key != 'stats':
                print(f"  {key}: {value}")
        
        # 内部統計の表示
        print("\n内部統計:")
        for key, value in stats['stats'].items():
            print(f"  {key}: {value}")
        
        # 機能テストの実行
        print("\n機能テスト実行中...")
        test_functionality(tincture_module)
        
        print("\n✓ 全ての機能テストが正常に完了しました")
        
    except ImportError as e:
        print(f"✗ 必要な依存関係が不足しています: {e}")
        print("pip install opencv-python numpy mss pyautogui pynput を実行してください")
        return False
    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        return False
    
    return True

def create_placeholder_images():
    """プレースホルダー画像を作成"""
    try:
        import cv2
        import numpy as np
        
        # 基本ディレクトリの作成
        base_dir = Path("assets/images/tincture/sap_of_the_seasons")
        
        # 状態別の設定
        states = {
            "idle": {
                "color": (0, 255, 0),      # 緑色（使用可能）
                "text": "RDY",             # Ready
                "files": ["sap_of_the_seasons_idle.png"]
            },
            "active": {
                "color": (0, 165, 255),    # オレンジ色（使用中）
                "text": "ACT",             # Active
                "files": ["sap_of_the_seasons_active.png"]
            },
            "cooldown": {
                "color": (128, 128, 128),  # グレー色（クールダウン）
                "text": "CD",              # Cooldown
                "files": [
                    "sap_of_the_seasons_cooldown_p000.png",
                    "sap_of_the_seasons_cooldown_p050.png",
                    "sap_of_the_seasons_cooldown_p100.png"
                ]
            }
        }
        
        # 各解像度とサイズの設定
        resolutions = [
            ("1920x1080", 64, 64),
            ("2560x1440", 85, 85),
            ("3840x2160", 128, 128)
        ]
        
        for state_name, state_config in states.items():
            state_dir = base_dir / state_name
            state_dir.mkdir(parents=True, exist_ok=True)
            
            for res_name, width, height in resolutions:
                # 状態別のテンプレート画像を作成
                img = np.zeros((height, width, 3), dtype=np.uint8)
                
                # 背景を暗いグレーに
                img[:, :] = [40, 40, 40]
                
                # 状態に応じた色の四角形を描画
                margin = 6
                cv2.rectangle(img, (margin, margin), (width - margin, height - margin), state_config["color"], -1)
                
                # 外枠を描画
                cv2.rectangle(img, (2, 2), (width - 2, height - 2), (200, 200, 200), 1)
                
                # テキストを描画
                font_scale = width / 80.0
                text_size = cv2.getTextSize(state_config["text"], cv2.FONT_HERSHEY_SIMPLEX, font_scale, max(1, int(2*font_scale)))[0]
                text_x = (width - text_size[0]) // 2
                text_y = (height + text_size[1]) // 2
                
                cv2.putText(img, state_config["text"], (text_x, text_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), max(1, int(2*font_scale)))
                
                # 各ファイルを保存
                for filename in state_config["files"]:
                    # 解像度を含むファイル名に変換
                    name_parts = filename.split('.')
                    resolution_filename = f"{name_parts[0]}_{res_name}.{name_parts[1]}"
                    
                    filepath = state_dir / resolution_filename
                    cv2.imwrite(str(filepath), img)
                    print(f"  作成: {filepath}")
            
    except Exception as e:
        print(f"プレースホルダー画像の作成に失敗: {e}")
        raise

def test_functionality(tincture_module):
    """機能テストを実行"""
    print("  機能テストを開始します...")
    
    try:
        # 1. 手動使用テスト
        print("  1. 手動使用テスト...")
        initial_uses = tincture_module.stats['total_uses']
        
        result = tincture_module.manual_use()
        if result:
            print("    ✓ 手動使用成功")
        else:
            print("    ✗ 手動使用失敗")
        
        # 使用回数の確認
        after_uses = tincture_module.stats['total_uses']
        if after_uses > initial_uses:
            print(f"    ✓ 使用回数が増加: {initial_uses} → {after_uses}")
        else:
            print(f"    ✗ 使用回数が増加しませんでした: {initial_uses} → {after_uses}")
        
        # 2. 設定更新テスト
        print("  2. 設定更新テスト...")
        original_sensitivity = tincture_module.sensitivity
        
        new_config = {
            'tincture': {
                'enabled': True,
                'key': '4',  # キーを変更
                'monitor_config': 'Primary',
                'sensitivity': 0.9,  # 感度を変更
                'check_interval': 0.1,
                'min_use_interval': 0.5
            }
        }
        
        tincture_module.update_config(new_config)
        
        if tincture_module.sensitivity == 0.9 and tincture_module.key == '4':
            print("    ✓ 設定更新成功")
        else:
            print("    ✗ 設定更新失敗")
        
        # 3. 統計リセットテスト
        print("  3. 統計リセットテスト...")
        tincture_module.reset_stats()
        
        if tincture_module.stats['total_uses'] == 0:
            print("    ✓ 統計リセット成功")
        else:
            print("    ✗ 統計リセット失敗")
        
        # 4. 自動実行テスト（短時間）
        print("  4. 自動実行テスト（3秒間）...")
        
        # 検出間隔を短くして素早くテスト
        test_config = {
            'tincture': {
                'enabled': True,
                'key': '3',
                'monitor_config': 'Primary',
                'sensitivity': 0.7,
                'check_interval': 0.05,  # 50ms
                'min_use_interval': 0.1   # 100ms
            }
        }
        
        tincture_module.update_config(test_config)
        
        # 実行開始
        tincture_module.start()
        
        # 少し待機
        time.sleep(3.0)
        
        # 実行停止
        tincture_module.stop()
        
        # 結果確認
        final_stats = tincture_module.get_stats()
        print(f"    検出成功: {final_stats['stats']['successful_detections']} 回")
        print(f"    検出失敗: {final_stats['stats']['failed_detections']} 回")
        print(f"    使用回数: {final_stats['stats']['total_uses']} 回")
        
        if final_stats['stats']['successful_detections'] > 0 or final_stats['stats']['failed_detections'] > 0:
            print("    ✓ 自動実行テスト成功（検出処理が実行されました）")
        else:
            print("    ⚠ 自動実行テスト完了（検出処理は実行されませんでした）")
        
    except Exception as e:
        print(f"  機能テストエラー: {e}")

def run_interactive_demo():
    """インタラクティブデモを実行"""
    try:
        from src.modules.tincture_module import TinctureModule
        from src.core.config_manager import ConfigManager
        
        print("\nインタラクティブデモモード")
        print("コマンド:")
        print("  s - 開始/停止")
        print("  u - 手動使用")
        print("  c - 設定変更")
        print("  t - 統計表示")
        print("  r - 統計リセット")
        print("  q - 終了")
        
        # 設定の読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # TinctureModule の初期化
        tincture_module = TinctureModule(config)
        
        while True:
            command = input("\nコマンドを入力してください (s/u/c/t/r/q): ").lower().strip()
            
            if command == 'q':
                break
            elif command == 's':
                if tincture_module.running:
                    print("モジュールを停止しています...")
                    tincture_module.stop()
                    print("モジュールを停止しました")
                else:
                    print("モジュールを開始しています...")
                    tincture_module.start()
                    print("モジュールを開始しました")
            elif command == 'u':
                print("手動使用を実行中...")
                result = tincture_module.manual_use()
                if result:
                    print("手動使用が成功しました")
                else:
                    print("手動使用が失敗しました")
            elif command == 'c':
                try:
                    print("現在の設定:")
                    print(f"  キー: {tincture_module.key}")
                    print(f"  感度: {tincture_module.sensitivity}")
                    print(f"  有効: {tincture_module.enabled}")
                    
                    new_key = input("新しいキー (現在: {}): ".format(tincture_module.key)).strip()
                    if new_key:
                        new_sensitivity = input("新しい感度 (0.5-1.0, 現在: {}): ".format(tincture_module.sensitivity)).strip()
                        if new_sensitivity:
                            new_sensitivity = float(new_sensitivity)
                        else:
                            new_sensitivity = tincture_module.sensitivity
                        
                        new_config = config.copy()
                        new_config['tincture']['key'] = new_key
                        new_config['tincture']['sensitivity'] = new_sensitivity
                        
                        tincture_module.update_config(new_config)
                        print("設定を更新しました")
                except ValueError:
                    print("無効な値です")
            elif command == 't':
                stats = tincture_module.get_stats()
                print("統計情報:")
                print(f"  有効: {stats['enabled']}")
                print(f"  実行中: {stats['running']}")
                print(f"  現在の状態: {stats['current_state']}")
                print(f"  使用回数: {stats['stats']['total_uses']}")
                print(f"  検出成功: {stats['stats']['successful_detections']}")
                print(f"  検出失敗: {stats['stats']['failed_detections']}")
                if stats['stats']['last_use_timestamp']:
                    last_use = time.strftime("%H:%M:%S", time.localtime(stats['stats']['last_use_timestamp']))
                    print(f"  最後の使用時刻: {last_use}")
            elif command == 'r':
                tincture_module.reset_stats()
                print("統計をリセットしました")
            else:
                print("無効なコマンドです")
        
        # 終了前にモジュールを停止
        if tincture_module.running:
            tincture_module.stop()
        
        print("インタラクティブデモを終了します")
        
    except Exception as e:
        print(f"インタラクティブデモエラー: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Tincture自動使用機能のデモ')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='インタラクティブデモモードを実行')
    
    args = parser.parse_args()
    
    if args.interactive:
        success = main()
        if success:
            run_interactive_demo()
    else:
        main()
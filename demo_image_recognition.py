#!/usr/bin/env python3
"""
TinctureDetector デモスクリプト
画像認識機能の動作確認用
"""

import sys
import os
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """メイン関数"""
    print("POE Macro v3.0 - Tincture検出機能デモ")
    print("=" * 50)
    
    try:
        # 必要なモジュールのインポート
        print("モジュールのインポート中...")
        from src.features.image_recognition import TinctureDetector
        print("✓ TinctureDetector モジュールのインポート成功")
        
        # プレースホルダー画像の作成
        print("\nプレースホルダー画像の作成中...")
        create_placeholder_images()
        print("✓ プレースホルダー画像の作成完了")
        
        # TinctureDetectorの初期化
        print("\nTinctureDetector の初期化中...")
        detector = TinctureDetector(
            monitor_config="Primary",
            sensitivity=0.7
        )
        print("✓ TinctureDetector の初期化成功")
        
        # 検出エリア情報の表示
        print("\n検出エリア情報:")
        info = detector.get_detection_area_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # 感度の調整テスト
        print("\n感度調整テスト:")
        sensitivities = [0.5, 0.7, 0.9]
        for sens in sensitivities:
            detector.update_sensitivity(sens)
            print(f"  感度 {sens} に設定: 現在の感度 = {detector.sensitivity}")
        
        # 検出テスト（実際の画面キャプチャ）
        print("\n検出テスト実行中...")
        test_detection(detector)
        
        print("\n✓ 全ての機能テストが正常に完了しました")
        
    except ImportError as e:
        print(f"✗ 必要な依存関係が不足しています: {e}")
        print("pip install opencv-python numpy mss を実行してください")
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
        
        # アセットディレクトリの作成
        assets_dir = Path("assets/images/tincture")
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        # 各解像度用のプレースホルダー画像を作成
        resolutions = [
            ("1920x1080", 64, 64),
            ("2560x1440", 85, 85),
            ("3840x2160", 128, 128)
        ]
        
        for res_name, width, height in resolutions:
            # 緑色の四角形を描画（プレースホルダー）
            img = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 背景を暗いグレーに
            img[:, :] = [50, 50, 50]
            
            # 中央に緑色の四角形
            margin = 8
            cv2.rectangle(img, (margin, margin), (width - margin, height - margin), (0, 255, 0), -1)
            
            # 中央に "T" の文字を描画
            font_scale = width / 64.0  # 解像度に応じてフォントサイズを調整
            cv2.putText(img, "T", (int(width//2 - 12*font_scale), int(height//2 + 8*font_scale)), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), max(1, int(2*font_scale)))
            
            # ファイル名を生成
            filename = f"sap_of_the_seasons_{res_name}.png"
            filepath = assets_dir / filename
            
            # 画像を保存
            cv2.imwrite(str(filepath), img)
            print(f"  作成: {filename}")
            
    except Exception as e:
        print(f"プレースホルダー画像の作成に失敗: {e}")
        raise

def test_detection(detector):
    """検出テストを実行"""
    print("  検出テストを開始します...")
    print("  注意: 実際のPOEゲーム画面でTinctureが表示されていない場合、検出されません")
    
    try:
        # 複数回検出を試行
        detection_results = []
        test_count = 5
        
        for i in range(test_count):
            print(f"  テスト {i+1}/{test_count} 実行中...")
            
            start_time = time.time()
            detected = detector.detect_tincture_icon()
            end_time = time.time()
            
            detection_time = end_time - start_time
            detection_results.append((detected, detection_time))
            
            status = "検出" if detected else "未検出"
            print(f"    結果: {status} (処理時間: {detection_time:.3f}秒)")
            
            # 少し待機
            time.sleep(0.5)
        
        # 結果のサマリー
        print("\n  検出結果サマリー:")
        detected_count = sum(1 for result, _ in detection_results if result)
        avg_time = sum(time for _, time in detection_results) / len(detection_results)
        
        print(f"    検出成功: {detected_count}/{test_count} 回")
        print(f"    平均処理時間: {avg_time:.3f}秒")
        print(f"    推定FPS: {1/avg_time:.1f}")
        
        if detected_count == 0:
            print("    ※ 検出されませんでした。以下を確認してください：")
            print("      - POEゲームが実行されているか")
            print("      - Tinctureアイコンが画面に表示されているか")
            print("      - 実際のアイコン画像でテンプレートを作成したか")
        
    except Exception as e:
        print(f"  検出テストエラー: {e}")

def run_interactive_demo():
    """インタラクティブデモを実行"""
    try:
        from src.features.image_recognition import TinctureDetector
        
        print("\nインタラクティブデモモード")
        print("コマンド:")
        print("  d - 検出実行")
        print("  s - 感度変更")
        print("  i - 検出エリア情報表示")
        print("  q - 終了")
        
        detector = TinctureDetector()
        
        while True:
            command = input("\nコマンドを入力してください (d/s/i/q): ").lower().strip()
            
            if command == 'q':
                break
            elif command == 'd':
                print("検出実行中...")
                start_time = time.time()
                detected = detector.detect_tincture_icon()
                end_time = time.time()
                
                status = "検出されました" if detected else "検出されませんでした"
                print(f"結果: {status} (処理時間: {end_time - start_time:.3f}秒)")
                
            elif command == 's':
                try:
                    new_sensitivity = float(input("新しい感度を入力してください (0.5-1.0): "))
                    detector.update_sensitivity(new_sensitivity)
                    print(f"感度を {detector.sensitivity} に設定しました")
                except ValueError:
                    print("無効な値です")
                    
            elif command == 'i':
                info = detector.get_detection_area_info()
                print("検出エリア情報:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
            else:
                print("無効なコマンドです")
        
        print("インタラクティブデモを終了します")
        
    except Exception as e:
        print(f"インタラクティブデモエラー: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Tincture検出機能のデモ')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='インタラクティブデモモードを実行')
    
    args = parser.parse_args()
    
    if args.interactive:
        success = main()
        if success:
            run_interactive_demo()
    else:
        main()
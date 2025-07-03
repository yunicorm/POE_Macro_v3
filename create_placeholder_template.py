#!/usr/bin/env python3
"""
プレースホルダーテンプレート画像を作成するスクリプト
実際のゲーム画面のスクリーンショットに置き換える必要があります
"""

try:
    import cv2
    import numpy as np
    from pathlib import Path
    
    # アセットディレクトリの確認
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
        cv2.putText(img, "T", (width//2 - 12, height//2 + 8), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # ファイル名を生成
        filename = f"sap_of_the_seasons_{res_name}.png"
        filepath = assets_dir / filename
        
        # 画像を保存
        cv2.imwrite(str(filepath), img)
        print(f"Created placeholder template: {filepath}")
    
    print("\nプレースホルダー画像の作成が完了しました。")
    print("実際のゲーム画面から適切なTinctureアイコンのスクリーンショットに置き換えてください。")
    
except ImportError as e:
    print(f"必要なモジュールがインストールされていません: {e}")
    print("pip install opencv-python numpy を実行してください。")
except Exception as e:
    print(f"エラーが発生しました: {e}")
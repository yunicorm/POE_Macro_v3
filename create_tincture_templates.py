#!/usr/bin/env python3
"""
Tincture状態別テンプレート画像を作成するスクリプト
実際のゲーム画面のスクリーンショットに置き換える必要があります
"""

try:
    import cv2
    import numpy as np
    from pathlib import Path
    
    def create_state_template(state: str, width: int, height: int, color: tuple, text: str) -> np.ndarray:
        """状態別のテンプレート画像を作成"""
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 背景色を設定
        img[:, :] = [40, 40, 40]  # 暗いグレー
        
        # 状態に応じた色の四角形を描画
        margin = 6
        cv2.rectangle(img, (margin, margin), (width - margin, height - margin), color, -1)
        
        # 外枠を描画
        cv2.rectangle(img, (2, 2), (width - 2, height - 2), (200, 200, 200), 1)
        
        # テキストを描画
        font_scale = width / 80.0
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, max(1, int(2*font_scale)))[0]
        text_x = (width - text_size[0]) // 2
        text_y = (height + text_size[1]) // 2
        
        cv2.putText(img, text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), max(1, int(2*font_scale)))
        
        return img
    
    # 各解像度とサイズの設定
    resolutions = [
        ("1920x1080", 64, 64),
        ("2560x1440", 85, 85),
        ("3840x2160", 128, 128)
    ]
    
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
    
    base_dir = Path("assets/images/tincture/sap_of_the_seasons")
    
    print("Tincture状態別テンプレート画像の作成を開始します...")
    
    for state_name, state_config in states.items():
        print(f"\n{state_name.upper()} 状態のテンプレート作成中...")
        
        state_dir = base_dir / state_name
        state_dir.mkdir(parents=True, exist_ok=True)
        
        for res_name, width, height in resolutions:
            # 状態別のテンプレート画像を作成
            img = create_state_template(
                state_name, width, height, 
                state_config["color"], state_config["text"]
            )
            
            # 各ファイルを保存
            for filename in state_config["files"]:
                # 解像度を含むファイル名に変換
                name_parts = filename.split('.')
                resolution_filename = f"{name_parts[0]}_{res_name}.{name_parts[1]}"
                
                filepath = state_dir / resolution_filename
                cv2.imwrite(str(filepath), img)
                print(f"  作成: {filepath}")
    
    print("\nテンプレート画像の作成が完了しました。")
    print("\n重要: これらはプレースホルダー画像です。")
    print("実際のPath of Exileゲーム画面から適切なTinctureアイコンの")
    print("スクリーンショットを撮影して置き換えてください。")
    
    print("\nテンプレート撮影のガイドライン:")
    print("1. 各状態でゲーム画面のスクリーンショットを撮影")
    print("2. Tinctureアイコン部分のみを切り取り")
    print("3. 対応する解像度のファイルに保存")
    print("4. PNG形式で保存（透明度サポート）")
    
    print("\nファイル構造:")
    for state_name in states.keys():
        print(f"  {state_name}/")
        for res_name, _, _ in resolutions:
            for filename in states[state_name]["files"]:
                name_parts = filename.split('.')
                resolution_filename = f"{name_parts[0]}_{res_name}.{name_parts[1]}"
                print(f"    {resolution_filename}")
    
except ImportError as e:
    print(f"必要なモジュールがインストールされていません: {e}")
    print("pip install opencv-python numpy を実行してください。")
except Exception as e:
    print(f"エラーが発生しました: {e}")
"""
Create a simple icon for POE Macro v3
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """シンプルなアイコンを作成"""
    # アイコンサイズ（Windows標準）
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # 最大サイズで作成してリサイズ
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 背景（暗い紫）
    draw.rounded_rectangle(
        [(10, 10), (246, 246)], 
        radius=30, 
        fill=(75, 0, 130, 255)
    )
    
    # POEの"P"を描画（白）
    try:
        # システムフォントを使用
        font = ImageFont.truetype("arial.ttf", 140)
    except:
        # フォントが見つからない場合はデフォルト
        font = ImageFont.load_default()
    
    draw.text((256//2, 256//2), "P", font=font, fill=(255, 255, 255, 255), anchor="mm")
    
    # 各サイズのアイコンを作成
    icons = []
    for size in sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)
    
    # ICOファイルとして保存
    output_path = "assets/poe_macro.ico"
    os.makedirs("assets", exist_ok=True)
    icons[0].save(output_path, format='ICO', sizes=[(s[0], s[1]) for s in sizes])
    
    print(f"✅ Icon created: {output_path}")

if __name__ == "__main__":
    create_icon()
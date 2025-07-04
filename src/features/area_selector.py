"""
POE Macro v3.0 - Area Selector for Flask Detection
フラスコ検出エリアの座標管理とプリセット機能
"""

import yaml
import os
import logging
from typing import Dict, Tuple, Optional
from PyQt5.QtWidgets import QApplication, QDesktopWidget


class AreaSelector:
    """
    検出エリアの座標管理とプリセット機能を提供するクラス
    """
    
    def __init__(self, config_file: str = "config/detection_areas.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        self.config_data = {}
        
        # 解像度別プリセット
        self.presets = {
            "1920x1080": {
                "x": 245,
                "y": 850,
                "width": 400,
                "height": 120
            },
            "2560x1440": {
                "x": 327,
                "y": 1133,
                "width": 533,
                "height": 160
            },
            "3840x2160": {
                "x": 490,
                "y": 1700,
                "width": 800,
                "height": 240
            },
            # ウルトラワイド解像度を追加
            "3440x1440": {
                "x": 1370,
                "y": 1133,
                "width": 700,
                "height": 160
            },
            "2560x1080": {
                "x": 830,
                "y": 850,
                "width": 500,
                "height": 120
            },
            "5120x1440": {
                "x": 2210,
                "y": 1133,
                "width": 700,
                "height": 160
            }
        }
        
        # 初期化
        self.load_config()
        
    def load_config(self) -> bool:
        """設定ファイルから座標データを読み込み"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f) or {}
                self.logger.info(f"設定ファイルを読み込みました: {self.config_file}")
                return True
            else:
                # デフォルト設定で新規作成
                self.create_default_config()
                return True
                
        except Exception as e:
            self.logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
            self.create_default_config()
            return False
            
    def create_default_config(self):
        """デフォルト設定を作成"""
        current_resolution = self.get_current_resolution()
        default_area = self.get_preset_for_resolution(current_resolution)
        
        self.config_data = {
            "flask_area": {
                "x": default_area["x"],
                "y": default_area["y"],
                "width": default_area["width"],
                "height": default_area["height"],
                "monitor": 0  # プライマリモニター
            },
            "tincture_slot": {
                "relative_x": 180,  # フラスコエリア内での相対位置
                "relative_y": 0,
                "width": 60,
                "height": 100
            },
            "presets": self.presets
        }
        
        self.save_config()
        self.logger.info("デフォルト設定を作成しました")
        
    def save_config(self) -> bool:
        """設定をファイルに保存"""
        try:
            # config ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
                
            self.logger.info(f"設定を保存しました: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"設定の保存に失敗しました: {e}")
            return False
            
    def get_current_resolution(self) -> str:
        """現在の画面解像度を取得"""
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                
            desktop = QDesktopWidget()
            screen = desktop.screenGeometry()
            resolution = f"{screen.width()}x{screen.height()}"
            
            self.logger.info(f"現在の解像度: {resolution}")
            return resolution
            
        except Exception as e:
            self.logger.error(f"解像度の取得に失敗しました: {e}")
            return "1920x1080"  # デフォルト解像度
            
    def get_preset_for_resolution(self, resolution: str) -> Dict:
        """指定された解像度のプリセットを取得"""
        return self.presets.get(resolution, self.presets["1920x1080"])
        
    def get_all_presets(self) -> Dict:
        """すべてのプリセットを取得"""
        return self.presets.copy()
        
    def get_flask_area(self) -> Dict:
        """フラスコエリアの座標を取得"""
        return self.config_data.get("flask_area", {
            "x": 245,
            "y": 850,
            "width": 400,
            "height": 120,
            "monitor": 0
        })
        
    def set_flask_area(self, x: int, y: int, width: int, height: int, monitor: int = 0):
        """フラスコエリアの座標を設定"""
        if "flask_area" not in self.config_data:
            self.config_data["flask_area"] = {}
            
        self.config_data["flask_area"].update({
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "monitor": monitor
        })
        
        self.save_config()
        self.logger.info(f"フラスコエリアを設定しました: ({x}, {y}, {width}, {height})")
        
    def get_tincture_slot(self) -> Dict:
        """Tinctureスロットの座標を取得"""
        return self.config_data.get("tincture_slot", {
            "relative_x": 180,
            "relative_y": 0,
            "width": 60,
            "height": 100
        })
        
    def set_tincture_slot(self, relative_x: int, relative_y: int, width: int, height: int):
        """Tinctureスロットの相対座標を設定"""
        if "tincture_slot" not in self.config_data:
            self.config_data["tincture_slot"] = {}
            
        self.config_data["tincture_slot"].update({
            "relative_x": relative_x,
            "relative_y": relative_y,
            "width": width,
            "height": height
        })
        
        self.save_config()
        self.logger.info(f"Tinctureスロットを設定しました: ({relative_x}, {relative_y}, {width}, {height})")
        
    def get_absolute_tincture_area(self) -> Dict:
        """Tinctureの絶対座標を計算して取得"""
        flask_area = self.get_flask_area()
        tincture_slot = self.get_tincture_slot()
        
        absolute_x = flask_area["x"] + tincture_slot["relative_x"]
        absolute_y = flask_area["y"] + tincture_slot["relative_y"]
        
        return {
            "x": absolute_x,
            "y": absolute_y,
            "width": tincture_slot["width"],
            "height": tincture_slot["height"]
        }
        
    def apply_preset(self, resolution: str) -> bool:
        """指定された解像度のプリセットを適用"""
        if resolution not in self.presets:
            self.logger.error(f"プリセットが見つかりません: {resolution}")
            return False
            
        preset = self.presets[resolution]
        self.set_flask_area(
            preset["x"],
            preset["y"],
            preset["width"],
            preset["height"]
        )
        
        self.logger.info(f"プリセットを適用しました: {resolution}")
        return True
        
    def apply_current_resolution_preset(self) -> bool:
        """現在の解像度のプリセットを適用"""
        current_resolution = self.get_current_resolution()
        return self.detect_and_apply_resolution()
        
    def detect_and_apply_resolution(self) -> bool:
        """現在の解像度を検出して適切なプリセットを適用"""
        current_resolution = self.get_current_resolution()
        self.logger.info(f"検出された解像度: {current_resolution}")
        
        # 完全一致するプリセットがあるか確認
        if current_resolution in self.presets:
            success = self.apply_preset(current_resolution)
            self.logger.info(f"プリセットを適用しました: {current_resolution}")
            return success
        else:
            # 最も近い解像度を見つけてスケーリング
            closest = self.find_closest_resolution(current_resolution)
            success = self.apply_scaled_preset(closest, current_resolution)
            self.logger.warning(f"完全一致なし {current_resolution}, {closest}からスケーリング")
            return success
            
    def find_closest_resolution(self, target_resolution: str) -> str:
        """最も近い解像度のプリセットを見つける"""
        try:
            target_width, target_height = map(int, target_resolution.split('x'))
            target_ratio = target_width / target_height
            
            closest_resolution = "1920x1080"  # デフォルト
            min_ratio_diff = float('inf')
            
            for resolution in self.presets.keys():
                width, height = map(int, resolution.split('x'))
                ratio = width / height
                ratio_diff = abs(ratio - target_ratio)
                
                if ratio_diff < min_ratio_diff:
                    min_ratio_diff = ratio_diff
                    closest_resolution = resolution
                    
            self.logger.info(f"最も近い解像度: {closest_resolution}")
            return closest_resolution
            
        except Exception as e:
            self.logger.error(f"最適解像度の検出に失敗: {e}")
            return "1920x1080"
            
    def apply_scaled_preset(self, base_resolution: str, target_resolution: str) -> bool:
        """基準解像度からターゲット解像度にスケーリングして適用"""
        try:
            base_width, base_height = map(int, base_resolution.split('x'))
            target_width, target_height = map(int, target_resolution.split('x'))
            
            scale_x = target_width / base_width
            scale_y = target_height / base_height
            
            base_preset = self.presets[base_resolution]
            
            scaled_preset = {
                "x": int(base_preset["x"] * scale_x),
                "y": int(base_preset["y"] * scale_y),
                "width": int(base_preset["width"] * scale_x),
                "height": int(base_preset["height"] * scale_y)
            }
            
            self.set_flask_area(
                scaled_preset["x"],
                scaled_preset["y"],
                scaled_preset["width"],
                scaled_preset["height"]
            )
            
            self.logger.info(f"スケール適用: {base_resolution} -> {target_resolution}, "
                           f"scale=({scale_x:.2f}, {scale_y:.2f})")
            return True
            
        except Exception as e:
            self.logger.error(f"スケーリング適用に失敗: {e}")
            return False
        
    def get_monitor_info(self) -> Dict:
        """モニター情報を取得"""
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                
            desktop = QDesktopWidget()
            monitor_count = desktop.screenCount()
            
            monitors = []
            for i in range(monitor_count):
                screen = desktop.screenGeometry(i)
                monitors.append({
                    "index": i,
                    "x": screen.x(),
                    "y": screen.y(),
                    "width": screen.width(),
                    "height": screen.height(),
                    "is_primary": i == desktop.primaryScreen()
                })
                
            self.logger.info(f"モニター情報を取得しました: {monitor_count}台")
            return {"count": monitor_count, "monitors": monitors}
            
        except Exception as e:
            self.logger.error(f"モニター情報の取得に失敗しました: {e}")
            return {"count": 1, "monitors": []}
            
    def screen_to_monitor_relative(self, screen_x: int, screen_y: int, monitor_index: int = 0) -> Tuple[int, int]:
        """スクリーン座標をモニター相対座標に変換"""
        try:
            monitor_info = self.get_monitor_info()
            if monitor_index < len(monitor_info["monitors"]):
                monitor = monitor_info["monitors"][monitor_index]
                relative_x = screen_x - monitor["x"]
                relative_y = screen_y - monitor["y"]
                return relative_x, relative_y
            else:
                self.logger.warning(f"無効なモニターインデックス: {monitor_index}")
                return screen_x, screen_y
                
        except Exception as e:
            self.logger.error(f"座標変換に失敗しました: {e}")
            return screen_x, screen_y
            
    def monitor_relative_to_screen(self, relative_x: int, relative_y: int, monitor_index: int = 0) -> Tuple[int, int]:
        """モニター相対座標をスクリーン座標に変換"""
        try:
            monitor_info = self.get_monitor_info()
            if monitor_index < len(monitor_info["monitors"]):
                monitor = monitor_info["monitors"][monitor_index]
                screen_x = relative_x + monitor["x"]
                screen_y = relative_y + monitor["y"]
                return screen_x, screen_y
            else:
                self.logger.warning(f"無効なモニターインデックス: {monitor_index}")
                return relative_x, relative_y
                
        except Exception as e:
            self.logger.error(f"座標変換に失敗しました: {e}")
            return relative_x, relative_y
            
    def validate_area(self, x: int, y: int, width: int, height: int) -> bool:
        """エリアの有効性を検証"""
        # 基本的な範囲チェック
        if width <= 0 or height <= 0:
            return False
            
        if x < 0 or y < 0:
            return False
            
        # 画面範囲内かチェック
        monitor_info = self.get_monitor_info()
        for monitor in monitor_info["monitors"]:
            if (x >= monitor["x"] and y >= monitor["y"] and 
                x + width <= monitor["x"] + monitor["width"] and 
                y + height <= monitor["y"] + monitor["height"]):
                return True
                
        return False
        
    def get_config_summary(self) -> Dict:
        """設定の概要を取得"""
        flask_area = self.get_flask_area()
        tincture_area = self.get_absolute_tincture_area()
        current_resolution = self.get_current_resolution()
        
        return {
            "current_resolution": current_resolution,
            "flask_area": flask_area,
            "tincture_area": tincture_area,
            "available_presets": list(self.presets.keys()),
            "config_file": self.config_file
        }


def main():
    """テスト用のメイン関数"""
    # ロギング設定
    logging.basicConfig(level=logging.INFO)
    
    # AreaSelectorのテスト
    selector = AreaSelector()
    
    # 設定概要を表示
    summary = selector.get_config_summary()
    print("=== 設定概要 ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # モニター情報を表示
    monitor_info = selector.get_monitor_info()
    print(f"\n=== モニター情報 ===")
    print(f"モニター数: {monitor_info['count']}")
    for monitor in monitor_info["monitors"]:
        print(f"モニター {monitor['index']}: {monitor['width']}x{monitor['height']} "
              f"at ({monitor['x']}, {monitor['y']}) {'(Primary)' if monitor['is_primary'] else ''}")
    
    # プリセットを表示
    print(f"\n=== 利用可能なプリセット ===")
    for resolution, preset in selector.get_all_presets().items():
        print(f"{resolution}: {preset}")


if __name__ == "__main__":
    main()
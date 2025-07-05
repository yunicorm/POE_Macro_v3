"""
Flask data manager for CSV-based flask information
"""
import os
import csv
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class FlaskDataManager:
    """フラスコデータを管理するクラス"""
    
    def __init__(self, data_dir: str = "data/flasks"):
        """
        初期化
        
        Args:
            data_dir: フラスコデータディレクトリのパス
        """
        self.data_dir = data_dir
        self.flask_data = {}
        self.load_all_flask_data()
    
    def load_all_flask_data(self):
        """全てのフラスコデータを読み込み"""
        try:
            # 各フラスコタイプのCSVファイルを読み込み
            flask_types = ["life_unique", "mana_unique", "hybrid_unique", "utility_unique"]
            
            for flask_type in flask_types:
                file_path = os.path.join(self.data_dir, f"{flask_type}.csv")
                if os.path.exists(file_path):
                    self.flask_data[flask_type] = self.load_csv_file(file_path)
                    logger.info(f"Loaded {len(self.flask_data[flask_type])} items from {file_path}")
                else:
                    logger.warning(f"Flask data file not found: {file_path}")
                    self.flask_data[flask_type] = []
            
            # ユーティリティベースタイプのCSVを追加読み込み
            utility_bases_path = os.path.join(self.data_dir, "utility_bases.csv")
            if os.path.exists(utility_bases_path):
                self.utility_bases_data = self.load_csv_file(utility_bases_path)
                logger.info(f"Loaded {len(self.utility_bases_data)} utility base types")
            else:
                logger.warning(f"Utility bases file not found: {utility_bases_path}")
                self.utility_bases_data = []
            
        except Exception as e:
            logger.error(f"Error loading flask data: {e}")
            self.flask_data = {}
            self.utility_bases_data = []
    
    def load_csv_file(self, file_path: str) -> List[Dict]:
        """
        CSVファイルを読み込み
        
        Args:
            file_path: CSVファイルのパス
            
        Returns:
            辞書のリスト
        """
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
        
        return data
    
    def get_unique_flasks(self, flask_type: str) -> List[str]:
        """
        指定したフラスコタイプのユニークフラスコ名を取得
        
        Args:
            flask_type: フラスコタイプ（life, mana, hybrid, utility）
            
        Returns:
            ユニークフラスコ名のリスト（アルファベット順）
        """
        key = f"{flask_type.lower()}_unique"
        
        if key not in self.flask_data:
            return []
        
        if flask_type.lower() == "utility":
            # Utilityの場合はbaseも含めて返す
            names = []
            for item in self.flask_data[key]:
                base = item.get('base', '')
                name = item.get('name', '')
                if base and name:
                    names.append(f"{base}: {name}")
            return sorted(names)
        else:
            # Life, Mana, Hybridの場合は名前のみ
            names = [item.get('name', '') for item in self.flask_data[key] if item.get('name')]
            return sorted(names)
    
    def get_utility_bases(self) -> List[str]:
        """
        Utilityフラスコのベース一覧を取得
        
        Returns:
            ベース名のリスト（アルファベット順）
        """
        if "utility_unique" not in self.flask_data:
            return []
        
        bases = set()
        for item in self.flask_data["utility_unique"]:
            base = item.get('base', '')
            if base:
                bases.add(base)
        
        return sorted(list(bases))
    
    def get_utility_flasks_by_base(self, base: str) -> List[str]:
        """
        指定したベースのUtilityユニークフラスコを取得
        
        Args:
            base: ベース名
            
        Returns:
            ユニークフラスコ名のリスト（アルファベット順）
        """
        if "utility_unique" not in self.flask_data:
            return []
        
        names = []
        for item in self.flask_data["utility_unique"]:
            if item.get('base', '') == base:
                name = item.get('name', '')
                if name:
                    names.append(name)
        
        return sorted(names)
    
    def get_flask_duration(self, flask_type: str, flask_name: str, base: str = None) -> Optional[float]:
        """
        フラスコの持続時間を取得
        
        Args:
            flask_type: フラスコタイプ（life, mana, hybrid, utility）
            flask_name: フラスコ名
            base: ユーティリティフラスコのベース名（必要な場合）
            
        Returns:
            持続時間（秒）、見つからない場合はNone
        """
        key = f"{flask_type.lower()}_unique"
        
        if key not in self.flask_data:
            return None
        
        for item in self.flask_data[key]:
            if flask_type.lower() == "utility":
                # Utilityの場合はbaseとnameの両方をチェック
                if base and item.get('base', '') == base and item.get('name', '') == flask_name:
                    duration_str = item.get('duration', '0')
                    try:
                        return float(duration_str)
                    except ValueError:
                        return None
            else:
                # その他の場合はnameのみチェック
                if item.get('name', '') == flask_name:
                    duration_str = item.get('duration', '0')
                    try:
                        return float(duration_str)
                    except ValueError:
                        return None
        
        return None
    
    def get_magic_flask_duration(self, flask_type: str) -> float:
        """
        Magic フラスコのデフォルト持続時間を取得
        
        Args:
            flask_type: フラスコタイプ（life, mana, hybrid, utility, wine）
            
        Returns:
            デフォルト持続時間（秒）
        """
        # Magic フラスコのデフォルト持続時間
        default_durations = {
            "life": 7.0,
            "mana": 7.0,
            "hybrid": 7.0,
            "utility": 5.0,
            "wine": 8.0
        }
        
        return default_durations.get(flask_type.lower(), 5.0)
    
    def get_all_flask_types(self) -> List[str]:
        """
        利用可能なフラスコタイプの一覧を取得
        
        Returns:
            フラスコタイプのリスト
        """
        return ["Life", "Mana", "Hybrid", "Utility", "Wine"]
    
    def get_all_rarities(self) -> List[str]:
        """
        利用可能なレアリティの一覧を取得
        
        Returns:
            レアリティのリスト
        """
        return ["Magic", "Unique"]
    
    def validate_flask_selection(self, flask_type: str, rarity: str, detail: str = None, base: str = None) -> Tuple[bool, str]:
        """
        フラスコ選択の妥当性を検証
        
        Args:
            flask_type: フラスコタイプ
            rarity: レアリティ
            detail: 詳細（ユニーク名など）
            base: ベース名（Utilityの場合）
            
        Returns:
            (有効かどうか, エラーメッセージ)
        """
        if flask_type == "Wine":
            return True, ""
        
        if rarity == "Magic":
            return True, ""
        
        if rarity == "Unique":
            if not detail:
                return False, "ユニークフラスコの名前を選択してください"
            
            if flask_type == "Utility":
                if not base:
                    return False, "ユーティリティフラスコのベースを選択してください"
                
                valid_flasks = self.get_utility_flasks_by_base(base)
                if detail not in valid_flasks:
                    return False, f"指定されたベース '{base}' に対して無効なユニークフラスコです"
            else:
                valid_flasks = self.get_unique_flasks(flask_type)
                if detail not in valid_flasks:
                    return False, f"指定されたフラスコタイプに対して無効なユニークフラスコです"
        
        return True, ""
    
    def get_utility_base_types(self) -> List[str]:
        """
        ユーティリティフラスコのベースタイプ一覧を取得
        
        Returns:
            ベースタイプ名のリスト（アルファベット順）
        """
        if not hasattr(self, 'utility_bases_data'):
            return []
        
        base_names = [item.get('base', '') for item in self.utility_bases_data if item.get('base')]
        return sorted(base_names)
    
    def get_utility_base_duration(self, base_name: str) -> Optional[float]:
        """
        ユーティリティフラスコベースタイプの持続時間を取得
        
        Args:
            base_name: ベースタイプ名
            
        Returns:
            持続時間（秒）、見つからない場合はNone
        """
        if not hasattr(self, 'utility_bases_data'):
            return None
        
        for item in self.utility_bases_data:
            if item.get('base', '') == base_name:
                duration_str = item.get('duration', '0')
                try:
                    return float(duration_str)
                except ValueError:
                    return None
        
        return None
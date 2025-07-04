#!/usr/bin/env python3
"""MacroController bool型設定エラー修正テスト"""

import logging
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config_manager import ConfigManager
from src.core.macro_controller import MacroController

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_bool_config_handling():
    """bool型設定の処理をテスト"""
    print("=== Testing bool config handling ===")
    
    # ConfigManagerのモック
    class MockConfigManager:
        def __init__(self, config):
            self.config = config
        
        def load_config(self):
            return self.config
    
    # テストケース1: 正常な設定
    print("\n1. Testing normal dict config:")
    normal_config = {
        'flask': {'enabled': True},
        'skills': {'enabled': False},
        'tincture': {'enabled': True}
    }
    
    try:
        config_manager = MockConfigManager(normal_config)
        controller = MacroController(config_manager)
        controller.start()
        print("✓ Normal config handled successfully")
        controller.stop()
    except Exception as e:
        print(f"✗ Normal config failed: {e}")
    
    # テストケース2: bool型が混在した設定
    print("\n2. Testing mixed bool config:")
    mixed_config = {
        'flask': True,  # これがbool型
        'skills': {'enabled': True},
        'tincture': False  # これもbool型
    }
    
    try:
        config_manager = MockConfigManager(mixed_config)
        controller = MacroController(config_manager)
        controller.start()
        print("✓ Mixed bool config handled successfully")
        controller.stop()
    except Exception as e:
        print(f"✗ Mixed bool config failed: {e}")
    
    # テストケース3: config全体がbool型
    print("\n3. Testing bool as entire config:")
    bool_config = True  # config全体がbool
    
    try:
        config_manager = MockConfigManager(bool_config)
        controller = MacroController(config_manager)
        controller.start()
        print("✓ Bool entire config handled successfully")
        controller.stop()
    except Exception as e:
        print(f"✗ Bool entire config failed: {e}")
    
    # テストケース4: Noneやその他の型
    print("\n4. Testing None and other types:")
    test_configs = [
        (None, "None config"),
        ("string_config", "String config"),
        (123, "Integer config"),
        ([], "List config")
    ]
    
    for config, desc in test_configs:
        try:
            config_manager = MockConfigManager(config)
            controller = MacroController(config_manager)
            controller.start()
            print(f"✓ {desc} handled successfully")
            controller.stop()
        except Exception as e:
            print(f"✗ {desc} failed: {e}")
    
    # テストケース5: update_config でのbool処理
    print("\n5. Testing update_config with bool:")
    try:
        config_manager = MockConfigManager(normal_config)
        controller = MacroController(config_manager)
        
        # bool型の設定で更新
        controller.update_config(True)
        print("✓ update_config with bool handled successfully")
        
        # 混在型の設定で更新
        controller.update_config(mixed_config)
        print("✓ update_config with mixed config handled successfully")
        
    except Exception as e:
        print(f"✗ update_config failed: {e}")
    
    # テストケース6: manual_flask_use でのbool処理
    print("\n6. Testing manual_flask_use with various configs:")
    try:
        # 正常な設定でのテスト
        config_manager = MockConfigManager(normal_config)
        controller = MacroController(config_manager)
        controller.manual_flask_use('slot_1')
        print("✓ manual_flask_use with normal config handled successfully")
        
        # bool型設定でのテスト
        controller.config = True
        controller.manual_flask_use('slot_1')
        print("✓ manual_flask_use with bool config handled successfully")
        
        # flask設定がboolの場合
        controller.config = {'flask': True}
        controller.manual_flask_use('slot_1')
        print("✓ manual_flask_use with flask as bool handled successfully")
        
    except Exception as e:
        print(f"✗ manual_flask_use failed: {e}")
    
    print("\n=== All tests completed ===")

if __name__ == '__main__':
    test_bool_config_handling()
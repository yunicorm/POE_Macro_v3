"""
ウィンドウ管理モジュール
Path of Exileウィンドウの検索・アクティブ化機能
"""
import logging
import time
from typing import Optional, List
import psutil
import pygetwindow as gw

logger = logging.getLogger(__name__)

class WindowManager:
    """ウィンドウ管理クラス"""
    
    def __init__(self):
        self.poe_window_titles = [
            "Path of Exile",
            "PathOfExile",
            "Path of Exile - ",  # タイトルにバージョン情報が含まれる場合
        ]
    
    def find_poe_process(self) -> Optional[psutil.Process]:
        """Path of Exileプロセスを検索"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info.get('name', '').lower()
                    
                    # Path of Exileの実行ファイル名で検索
                    if 'pathofexile' in proc_name or 'poe' in proc_name:
                        logger.debug(f"Found POE process: {proc_info}")
                        return proc
                    
                    # 実行ファイルパスでも検索
                    exe_path = proc_info.get('exe', '')
                    if exe_path and 'pathofexile' in exe_path.lower():
                        logger.debug(f"Found POE process by exe: {proc_info}")
                        return proc
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logger.error(f"Error searching for POE process: {e}")
            
        return None
    
    def find_poe_windows(self) -> List[gw.Win32Window]:
        """Path of Exileウィンドウを検索"""
        poe_windows = []
        
        try:
            # すべてのウィンドウを取得
            all_windows = gw.getAllWindows()
            
            for window in all_windows:
                try:
                    window_title = window.title
                    
                    # Path of Exileのタイトルパターンをチェック
                    for poe_title in self.poe_window_titles:
                        if poe_title.lower() in window_title.lower():
                            # ウィンドウが可視で最小化されていない場合のみ追加
                            if window.isActive or not window.isMinimized:
                                poe_windows.append(window)
                                logger.debug(f"Found POE window: '{window_title}' (PID: {getattr(window, '_hWnd', 'unknown')})")
                                break
                                
                except Exception as e:
                    logger.debug(f"Error checking window: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error searching for POE windows: {e}")
            
        return poe_windows
    
    def activate_poe_window(self, timeout: float = 2.0) -> bool:
        """
        Path of Exileウィンドウをアクティブにする
        
        Args:
            timeout: タイムアウト時間（秒）
            
        Returns:
            bool: アクティブ化に成功した場合True
        """
        try:
            logger.info("Searching for Path of Exile window...")
            
            # Path of Exileプロセスが起動しているかチェック
            poe_process = self.find_poe_process()
            if not poe_process:
                logger.warning("Path of Exile process not found. Please ensure POE is running.")
                return False
            
            logger.debug(f"POE process found: PID {poe_process.pid}")
            
            # Path of Exileウィンドウを検索
            poe_windows = self.find_poe_windows()
            
            if not poe_windows:
                logger.warning("Path of Exile window not found. The game might be running but not visible.")
                return False
            
            # 最初に見つかったウィンドウをアクティブにする
            target_window = poe_windows[0]
            logger.info(f"Attempting to activate POE window: '{target_window.title}'")
            
            # ウィンドウをアクティブにする
            if target_window.isMinimized:
                logger.debug("Window is minimized, restoring...")
                target_window.restore()
                time.sleep(0.1)  # 復元待機
            
            # ウィンドウをアクティブにして前面に持ってくる
            target_window.activate()
            time.sleep(0.1)  # アクティブ化待機
            
            # 確認のため、ウィンドウが実際にアクティブになったかチェック
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    if target_window.isActive:
                        logger.info("Successfully activated Path of Exile window")
                        return True
                except:
                    pass
                time.sleep(0.1)
            
            # フォールバック: 強制的にフォーカスを設定
            try:
                target_window.restore()
                target_window.activate()
                time.sleep(0.2)
                logger.info("Path of Exile window activation attempted (fallback method)")
                return True
            except Exception as e:
                logger.warning(f"Fallback activation failed: {e}")
            
        except Exception as e:
            logger.error(f"Error activating POE window: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            
        return False
    
    def is_poe_active(self) -> bool:
        """Path of Exileウィンドウがアクティブかどうかチェック"""
        try:
            poe_windows = self.find_poe_windows()
            for window in poe_windows:
                if window.isActive:
                    return True
        except Exception as e:
            logger.debug(f"Error checking if POE is active: {e}")
            
        return False
    
    def get_poe_window_info(self) -> Optional[dict]:
        """Path of Exileウィンドウの情報を取得"""
        try:
            poe_windows = self.find_poe_windows()
            if poe_windows:
                window = poe_windows[0]
                return {
                    'title': window.title,
                    'left': window.left,
                    'top': window.top,
                    'width': window.width,
                    'height': window.height,
                    'is_active': window.isActive,
                    'is_minimized': window.isMinimized,
                    'is_maximized': window.isMaximized
                }
        except Exception as e:
            logger.error(f"Error getting POE window info: {e}")
            
        return None

def test_window_manager():
    """ウィンドウマネージャーのテスト関数"""
    logging.basicConfig(level=logging.DEBUG)
    
    wm = WindowManager()
    
    print("=== Window Manager Test ===")
    
    # プロセス検索テスト
    print("\n1. Searching for POE process...")
    poe_process = wm.find_poe_process()
    if poe_process:
        print(f"✓ Found POE process: PID {poe_process.pid}, Name: {poe_process.name()}")
    else:
        print("✗ POE process not found")
    
    # ウィンドウ検索テスト
    print("\n2. Searching for POE windows...")
    poe_windows = wm.find_poe_windows()
    if poe_windows:
        for i, window in enumerate(poe_windows):
            print(f"✓ Found POE window {i+1}: '{window.title}'")
    else:
        print("✗ POE windows not found")
    
    # ウィンドウ情報取得テスト
    print("\n3. Getting POE window info...")
    window_info = wm.get_poe_window_info()
    if window_info:
        print(f"✓ Window info: {window_info}")
    else:
        print("✗ Could not get window info")
    
    # アクティブ状態チェック
    print("\n4. Checking if POE is active...")
    is_active = wm.is_poe_active()
    print(f"POE active: {is_active}")
    
    # アクティブ化テスト
    print("\n5. Testing window activation...")
    if poe_windows:
        success = wm.activate_poe_window()
        print(f"Activation {'successful' if success else 'failed'}")
    else:
        print("Skipping activation test - no POE windows found")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_window_manager()
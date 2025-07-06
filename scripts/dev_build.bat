@echo off
REM POE Macro v3 Development Build Script
REM 開発版ビルド - 高速、デバッグ情報付き

echo ========================================
echo POE Macro v3 Development Build
echo ========================================
echo.

REM Python環境のチェック
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM プロジェクトルートディレクトリに移動
cd /d "%~dp0\.."

echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Running quick tests...
python test_simple.py
if errorlevel 1 (
    echo [WARNING] Some tests failed, but continuing with build...
)

echo.
echo [3/3] Building development executable...
python build_system.py dev

echo.
echo ========================================
if exist "dist\poe_macro_v3.exe" (
    echo [SUCCESS] Build completed!
    echo Executable: dist\poe_macro_v3.exe
    echo.
    echo You can now run: dist\poe_macro_v3.exe
) else (
    echo [ERROR] Build failed!
)
echo ========================================

pause
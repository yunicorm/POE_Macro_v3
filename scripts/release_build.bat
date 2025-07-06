@echo off
REM POE Macro v3 Release Build Script
REM リリース版ビルド - 最適化、サイズ削減

echo ========================================
echo POE Macro v3 Release Build
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

echo [1/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/5] Cleaning previous builds...
python build_system.py clean

echo.
echo [3/5] Running all tests...
python test_simple.py
if errorlevel 1 (
    echo [ERROR] Tests failed! Fix issues before release build.
    pause
    exit /b 1
)

python test_integration.py
if errorlevel 1 (
    echo [WARNING] Integration tests failed, but continuing...
)

echo.
echo [4/5] Building release executable...
python build_system.py release

echo.
echo [5/5] Creating release package...
python build_system.py package

echo.
echo ========================================
if exist "dist\poe_macro_v3.exe" (
    echo [SUCCESS] Release build completed!
    echo Executable: dist\poe_macro_v3.exe
    
    REM Get file size
    for %%I in ("dist\poe_macro_v3.exe") do echo Size: %%~zI bytes
    
    echo.
    echo Release package created in: releases\
) else (
    echo [ERROR] Build failed!
)
echo ========================================

pause
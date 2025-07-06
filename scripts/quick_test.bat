@echo off
REM POE Macro v3 Quick Test Script
REM ビルド前の簡易テスト実行

echo ========================================
echo POE Macro v3 Quick Test
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

echo Running simple tests...
python test_simple.py
if errorlevel 1 (
    echo.
    echo [ERROR] Simple tests failed!
    pause
    exit /b 1
)

echo.
echo Running integration tests...
python test_integration.py
if errorlevel 1 (
    echo.
    echo [WARNING] Integration tests failed!
)

echo.
echo ========================================
echo All tests completed!
echo ========================================

pause
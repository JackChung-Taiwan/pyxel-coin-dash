@echo off
chcp 65001 >nul
echo [1/2] 安裝／更新 Pyxel...
py -m pip install --upgrade pyxel
if errorlevel 1 (
  echo 安裝失敗。請先安裝 Python 3.11 或更新版本，安裝時勾選 Add Python to PATH。
  pause
  exit /b 1
)
echo [2/2] 安裝完成。執行 run_game.bat 就能玩。
pause

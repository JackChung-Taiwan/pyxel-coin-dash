@echo off
chcp 65001 >nul
cd /d "%~dp0"
py game.py
if errorlevel 1 (
  echo 若發生 No module named pyxel，請先執行 install_windows.bat。
  pause
)

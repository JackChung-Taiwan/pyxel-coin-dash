@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 請用瀏覽器開啟 http://localhost:8000/
echo 注意：Pyxel 網頁執行器載入時需要網路連線。
start "" "http://localhost:8000/"
py -m http.server 8000
pause

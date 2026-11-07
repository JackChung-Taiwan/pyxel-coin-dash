# Coin Dash｜Pyxel 橫向卷軸吃金幣 PWA

使用 Pyxel (Python) 製作的原創 2D 像素風跑跳遊戲，依照參考圖片改成藍天、粉色雲朵、雪山、漂浮磚塊、金幣與角色跑跳的橫向卷軸場景。手機瀏覽器可玩，也可以安裝到主畫面 (PWA)。

## 遊戲操作

- 手機：將畫面橫向，使用 Pyxel 內建虛擬方向鍵左右移動；**A = 跳躍／開始／再玩一次，B = 暫停／繼續**。
- 電腦：**←/→ 或 A/D** 移動，**Space / ↑ / W** 跳躍，**P** 暫停，**Enter** 也可開始。
- 100 秒內向右到達旗幟，途中收集金幣 (每枚 10 分)、跳上浮空磚塊、越過地面缺口與避開怪物。
- 3 顆愛心；每拿 10 枚金幣額外加 5 秒。每通過一段路可記錄關卡內的重生點。
- 最後碰到終點旗幟會結算剩餘時間加分。最高分只在本次執行期間保存。

## Windows 安裝與測試

1. 安裝 Python 3.11 以上 (https://www.python.org/downloads/)；勾選 Add Python to PATH。
2. 在 Windows 解壓縮後執行 `install_windows.bat`，安裝 Pyxel。
3. 執行 `run_game.bat` 開啟桌面遊戲。
4. 若要試 PWA，在專案目錄執行 `start_web.bat`，瀏覽器開啟 http://localhost:8000/。

也能用終端機執行：

```sh
pip install -U pyxel
python game.py
```

## GitHub Pages / PWA 部署

1. 把全部檔案上傳 GitHub repository 根目錄（`game.py`、`index.html`、`manifest.webmanifest`、`sw.js`、`icons/`）。
2. 前往 Settings → Pages → Deploy from a branch → `main` → `/(root)` → Save。
3. 開啟 https://jackchung-taiwan.github.io/pyxel-coin-dash/ ，Android Chrome 選「安裝應用程式」；iPhone Safari 選「分享 → 加入主畫面」。
4. 若手機仍顯示舊版，先重新整理，或關閉並重新開啟主畫面 App；Service Worker 已更新為 `coin-dash-scroll-v2`，會更新快取。

**提醒**：PWA 可安裝，不等於完全離線。遊戲仍需載入 Pyxel 官方瀏覽器執行器，首次啟動需網路連線；裝置不一定能離線重啟遊戲。

## 專案檔案

- `game.py`: 原創 Python 卷軸平台遊戲，包含地圖繪製、角色物理、收集金幣、敵人、計時、計分、音效。
- `index.html`: 嵌入 Pyxel Web、PWA 安裝、全螢幕控制、手機版佈局。
- `manifest.webmanifest`, `sw.js`: PWA 設定與快取更新。
- `icons/`: PWA 192px / 512px 圖示。
- `install_windows.bat`, `run_game.bat`, `start_web.bat`: Windows 工具。

技術參考：https://github.com/kitao/pyxel 

# Coin Dash｜Pyxel 手機 PWA 吃金幣遊戲

使用 **Pyxel（Python）** 寫成的 2D 像素吃金幣遊戲，可在 Windows 上執行，並透過 Pyxel Web 在 Android / iPhone 瀏覽器執行。專案包含 PWA manifest、Service Worker、手機圖示及 GitHub Pages 部署檔案。

## 遊戲規則

- 在 60 秒內收集金幣，躲開會移動的炸彈。
- 3 顆愛心（生命）；碰到炸彈扣 1 顆。
- 連續吃金幣可累積最高 x5 分數倍率。
- 每吃 10 枚金幣增加 5 秒。
- 音效、金幣粒子、開始／暫停／結束畫面。
- **手機觸控**：Pyxel 內建的十字方向鍵移動、**A** 鍵開始／暫停／重玩。
- **電腦鍵盤**：方向鍵或 WASD 移動，空白鍵或 Enter 開始／暫停／重玩。
- 得分最高紀錄僅保留於目前遊戲執行期間，重新載入頁面後會重置。

## 方式 A：Windows 安裝 Pyxel、執行 Python 遊戲

1. 到 <https://www.python.org/downloads/> 安裝 **Python 3.11 或更新版本**。Windows 安裝時勾選 `Add Python to PATH`。
2. 解壓縮專案後，雙擊 `install_windows.bat`。
3. 安裝完成後，雙擊 `run_game.bat`，開啟遊戲。

也可以在 PowerShell / 終端機手動輸入：

```powershell
py -m pip install --upgrade pyxel
py game.py
```

macOS / Linux 可用 `python3 -m pip install -U pyxel`，再執行 `python3 game.py`。

## 方式 B：在電腦測試 PWA 網頁

在專案資料夾雙擊 `start_web.bat`，或輸入：

```powershell
py -m http.server 8000
```

瀏覽器開啟 <http://localhost:8000/>。

**請勿直接雙擊 `index.html`**：Pyxel 的外部 `game.py` 需要 HTTP 伺服器載入。Pyxel Web 引擎也需要網路連線。

## 方式 C：部署 GitHub Pages，給手機玩及安裝 PWA

1. 前往 <https://github.com/new> 建立公開 repository，例如 `pyxel-coin-dash`。
2. 透過 **Add file → Upload files** 上傳本專案的**所有內容**到 repository 根目錄，保留 `icons/` 資料夾和圖示。注意不要把最外層專案資料夾當成多一層路徑。
3. 到 repository **Settings → Pages**。
4. 在 **Build and deployment → Source** 選 `Deploy from a branch`；Branch 選 `main`、資料夾選 `/(root)`，按 **Save**。
5. 完成部署後，網址格式如下：

   `https://你的GitHub帳號.github.io/pyxel-coin-dash/`

6. **Android**：Chrome 開啟上述 HTTPS 網址 → 右上角 `⋮` →「安裝應用程式」或「加到主畫面」，亦可按網站的「安裝遊戲」。
7. **iPhone / iPad**：Safari 開啟 HTTPS 網址 →「分享」→「加入主畫面」→「加入」。
8. 建議橫向拿手機，左邊十字鍵操作移動，右側 A 鍵開始／暫停。

## PWA 與離線功能的重要說明

- 包含 `manifest.webmanifest`、192/512 PWA 圖示、maskable 圖示、`display: standalone`、`orientation: landscape`、`sw.js` 同源靜態快取；部署於 HTTPS 後符合常見 PWA 安裝基礎條件。
- **此版本不是完整離線遊戲**：Pyxel Web 的引擎／WASM 由官方 `https://kitao.dev` 載入。網站外殼可能離線開啟，但載入或重新啟動遊戲時仍可能需要網路。PWA「可安裝」不等於必然「完全離線」。
- GitHub Pages 只提供靜態檔案，這個專案的 Python 遊戲是在瀏覽器的 Pyxel Web 環境執行，**不需要 GitHub Pages 支援伺服器端 Python**。
- HTTPS 與正常可取得的 Pyxel 官方網頁引擎是手機成功執行的前提。首次啟動可能需載入較大的執行環境。

## 可調整參數

編輯 `game.py` 開頭：

```python
GAME_SECONDS = 60        # 遊戲秒數
PLAYER_SPEED = 2.0       # 移動速度
COINS_ON_FIELD = 7       # 同時出現金幣數
BOMBS_ON_FIELD = 3       # 炸彈數
```

修改完成，重新上傳 `game.py` 至 GitHub，再重新整理遊戲。

## 專案結構

```text
pyxel-coin-dash-pwa/
├── game.py                  # Pyxel 遊戲主程式
├── index.html               # Pyxel Web 和安裝按鈕
├── manifest.webmanifest     # PWA 安裝設定
├── sw.js                    # Service Worker 靜態快取
├── icons/
│   ├── icon-192.png
│   ├── icon-512.png
│   └── icon-maskable-512.png
├── install_windows.bat      # Windows 安裝 Pyxel
├── run_game.bat             # Windows 執行桌面遊戲
├── start_web.bat            # Windows 啟動 localhost 網頁
├── .nojekyll                # GitHub Pages 發布設定
└── README.md
```

## 參考資料

- Pyxel 官方：<https://github.com/kitao/pyxel>
- Pyxel 網頁使用說明：<https://github.com/kitao/pyxel/blob/main/docs/web-usage.md>
- GitHub Pages：<https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site>

Pyxel 原始專案採 MIT License；本範例程式採 MIT License。

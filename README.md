# USDT Arbitrage Bot for Render (Web Service 模式)

這是可部署於 Render 免費 Web Service 的套利監控機器人，使用 Flask 模擬 HTTP Server，保持 Render 持續運作。

## 部署步驟
1. 將專案上傳到 GitHub（Public）
2. 在 Render 建立 Web Service，語言選 Python 3
3. Start Command 設為：
    python usdt_arbitrage_web.py
4. 設定環境變數：
    TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID

import os
import time
import ccxt
import requests
import threading
from flask import Flask
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SYMBOL = os.getenv("ARBITRAGE_SYMBOL", "BTC/USDT")  # 預設 BTC/USDT
THRESHOLD = float(os.getenv("ARBITRAGE_THRESHOLD", "1.0"))  # USDT 為單位

# 初始化交易所
binance = ccxt.binance()
okx = ccxt.okx()
binance.load_markets()
okx.load_markets()

# 發送 Telegram 通知
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ 發送 Telegram 失敗:", e)

# 取得即時報價
def get_price(exchange, symbol):
    ticker = exchange.fetch_ticker(symbol)
    return ticker['bid'], ticker['ask']

# 套利監控主邏輯
def monitor_arbitrage():
    while True:
        try:
            if SYMBOL in binance.symbols and SYMBOL in okx.symbols:
                binance_bid, binance_ask = get_price(binance, SYMBOL)
                okx_bid, okx_ask = get_price(okx, SYMBOL)

                # 買 Binance / 賣 OKX 的套利價差（USDT 單位）
                buy_price = binance_ask
                sell_price = okx_bid
                diff = sell_price - buy_price

                print(f"[套利] Binance 買: {buy_price:.2f} / OKX 賣: {sell_price:.2f} → 價差: {diff:.2f} USDT")

                if diff > THRESHOLD:
                    msg = (
                        f"🚨 {SYMBOL} 套利機會！\n"
                        f"Binance 買價: {buy_price:.2f} USDT\n"
                        f"OKX 賣價: {sell_price:.2f} USDT\n"
                        f"價差：{diff:.2f} USDT"
                    )
                    send_telegram(msg)

        except Exception as e:
            print("❌ 錯誤:", e)

        time.sleep(15)

# Flask Web 顯示
app = Flask(__name__)

@app.route("/")
def index():
    return f"{SYMBOL} Arbitrage Bot Running with Threshold {THRESHOLD} USDT"

# 啟動 Bot
if __name__ == "__main__":
    threading.Thread(target=monitor_arbitrage, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)

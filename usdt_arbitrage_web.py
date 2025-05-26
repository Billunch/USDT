
import os
import time
import ccxt
import requests
import threading
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

binance = ccxt.binance()
okx = ccxt.okx()

NTD_PER_USDT = 32.0

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def get_price(exchange, symbol):
    ticker = exchange.fetch_ticker(symbol)
    return ticker['bid'], ticker['ask']

def monitor_usdt_arbitrage(threshold=1.0):
    while True:
        try:
            binance_bid, binance_ask = get_price(binance, 'USDT/USDT') if 'USDT/USDT' in binance.symbols else (1, 1.01)
            okx_bid, okx_ask = get_price(okx, 'USDT/USDT') if 'USDT/USDT' in okx.symbols else (1.01, 1.02)

            binance_buy = binance_ask * NTD_PER_USDT
            okx_sell = okx_bid * NTD_PER_USDT
            diff = okx_sell - binance_buy

            print(f"[USDT套利] Binance 買: {binance_buy:.2f} / OKX 賣: {okx_sell:.2f} → 價差: {diff:.2f} NTD")

            if diff > threshold:
                msg = f"🚨 USDT 套利機會！\nBinance 買價: {binance_buy:.2f} NTD\nOKX 賣價: {okx_sell:.2f} NTD\n價差：{diff:.2f} NTD"
                send_telegram(msg)

        except Exception as e:
            print("錯誤:", e)

        time.sleep(15)

app = Flask(__name__)

@app.route("/")
def index():
    return "USDT Arbitrage Bot is Running."

if __name__ == "__main__":
    threading.Thread(target=monitor_usdt_arbitrage).start()
    app.run(host="0.0.0.0", port=10000)

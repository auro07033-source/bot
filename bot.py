# bot.py - Forex Auto Reply Bot
# Geliştirici: @zanetmez

import asyncio
import uvloop
from flask import Flask, request
from pyrogram import Client

# uvloop'u kur
uvloop.install()

API_ID = 37530959
API_HASH = "ead1e5bd23f9361738579b6acde959d6"
BOT_TOKEN = "8967230892:AAF79MTbRvk1NXbQtG2lhqcpqErOo2kKsX4"

app = Flask(__name__)

# Client'i asenkron başlat
pyro = Client("forex_userbot", api_id=API_ID, api_hash=API_HASH)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        
        if not text.startswith('/'):
            reply = "Selam! 👋 Şu an aktif değilim, en kısa sürede dönüyorum! 😊\n\n📌 @zanetmez"
            # Asenkron fonksiyonu senkron çalıştır
            loop = asyncio.get_event_loop()
            loop.run_until_complete(pyro.send_message(chat_id, reply))
    
    return "OK", 200

@app.route('/', methods=['GET'])
def home():
    return "Bot çalışıyor! ✅", 200

if __name__ == '__main__':
    # Client'i başlat
    loop = asyncio.get_event_loop()
    loop.run_until_complete(pyro.start())
    
    # Flask'ı başlat
    app.run(host='0.0.0.0', port=8080)
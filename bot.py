# bot.py - Tek dosya (Python)
# Geliştirici: @zanetmez

from flask import Flask, request
from pyrogram import Client
import json

app = Flask(__name__)

API_ID = 37530959
API_HASH = "ead1e5bd23f9361738579b6acde959d6"
BOT_TOKEN = "8967230892:AAF79MTbRvk1NXbQtG2lhqcpqErOo2kKsX4"

pyro = Client("forex_userbot", api_id=API_ID, api_hash=API_HASH)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        
        if not text.startswith('/'):
            reply = "Selam! 👋 Şu an aktif değilim, en kısa sürede dönüyorum! 😊\n\n dm @zanetmez"
            pyro.send_message(chat_id, reply)
    
    return "OK", 200

if __name__ == '__main__':
    pyro.start()
    app.run(host='0.0.0.0', port=8080)
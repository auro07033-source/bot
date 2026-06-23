# tiktok_bot.py - TikTok Hesap Oluşturma Telegram Webhook Bot
# Geliştirici: @zanetmez
# GitHub: https://github.com/zanetmez/tiktok-bot

import os
import sys
import json
import time
import logging
import requests
import random
import uuid
import binascii
import string
import secrets
from urllib.parse import urlencode

# Flask ve Telegram
from flask import Flask, request, jsonify
import telebot
from telebot.types import Update

# TikTok imza kütüphanesi
try:
    from hsopyt import Gorgon, Ladon, Argus, md5
except ImportError:
    print("❌ hsopyt yüklü değil! pip install hsopyt")
    sys.exit(1)

# ==================== KONFIGÜRASYON ====================
BOT_TOKEN = "8973301473:AAGQ9ecr7R9KwcXwqBbz-RGbtdU-9e7L1IE"
WEBHOOK_URL = "https://cc-3t5u.onrender.com/"

if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("❌ Lütfen BOT_TOKEN'ı ayarlayın!")
    sys.exit(1)

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

# ==================== TIKTOK FONKSİYONLARI ====================

def xor(s: str) -> str:
    return ''.join([hex(ord(_) ^ 5)[2:] for _ in s])

def sign(params: str, payload: str = None, sec_device_id: str = '', cookie: str = None,
         aid: int = 1233, license_id: int = 1611921764, sdk_version_str: str = 'v05.00.06-ov-android',
         sdk_version: int = 167775296, platform: int = 0, unix: float = None):
    x_ss_stub = md5(payload.encode('utf-8')).hexdigest() if payload else None
    if not unix:
        unix = time.time()
    
    gorgon = Gorgon(params, unix, payload, cookie).get_value()
    
    return {
        **gorgon,
        'content-length': str(len(payload)) if payload else '0',
        'x-ss-stub': x_ss_stub.upper() if x_ss_stub else '',
        'x-ladon': Ladon.encrypt(int(unix), license_id, aid),
        'x-argus': Argus.get_sign(
            params, x_ss_stub, int(unix),
            platform=platform, aid=aid, license_id=license_id,
            sec_device_id=sec_device_id, sdk_version=sdk_version_str,
            sdk_version_int=sdk_version
        )
    }

def get_base_params():
    return {
        "passport-sdk-version": "6030790",
        "device_platform": "android",
        "os": "android",
        "ssmix": "a",
        "channel": "googleplay",
        "aid": "1233",
        "app_name": "musical_ly",
        "version_code": "360505",
        "version_name": "36.5.5",
        "manifest_version_code": "2023605050",
        "update_version_code": "2023605050",
        "ab_version": "36.5.5",
        "app_version": "36.5.5",
        "resolution": "1080*2179",
        "dpi": "480",
        "device_type": "DNN-LX9",
        "device_brand": "HONOR",
        "language": "ar",
        "os_api": "29",
        "os_version": "10",
        "ac": "wifi",
        "is_pad": "0",
        "current_region": "IQ",
        "app_type": "normal",
        "sys_region": "IQ",
        "last_install_time": "1765367219",
        "mcc_mnc": "41805",
        "timezone_name": "Asia/Baghdad",
        "carrier_region_v2": "418",
        "residence": "IQ",
        "app_language": "en",
        "carrier_region": "IQ",
        "timezone_offset": "10800",
        "host_abi": "arm64-v8a",
        "locale": "en",
        "content_language": "th,",
        "ac2": "wifi",
        "uoo": "1",
        "op_region": "IQ",
        "build_number": "36.5.5",
        "region": "IQ",
        "support_webview": "1",
        "reg_store_region": "IQ",
        "user_selected_region": "0",
        "cronet_version": "1c651b66_2024-08-30",
        "ttnet_version": "4.2.195.8-tiktok",
        "use_store_region_cookie": "1"
    }

def get_hs_params():
    return {
        "_rticket": str(round(random.uniform(1.2, 1.6) * 100000000) * -1) + "4632",
        "cdid": str(uuid.uuid4()),
        "openudid": str(binascii.hexlify(os.urandom(8)).decode()),
        "iid": str(random.randint(1, 10**19)),
        "device_id": str(random.randint(1, 10**19)),
        "ts": str(round(random.uniform(1.2, 1.6) * 100000000) * -1),
    }

def random_sec_device_id():
    return "AadCFwpTyztA5j9L" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(9))

def tiktok_request(url, params, payload):
    query = urlencode(params)
    full_url = f"{url}?{query}"
    payload_encoded = urlencode(payload)
    sec_device_id = random_sec_device_id()
    sig = sign(query, payload_encoded, sec_device_id, None, 1233)
    
    headers = {
        'User-Agent': "com.zhiliaoapp.musically/2023605050 (Linux; U; Android 10; ar_IQ; DNN-LX9; Build/HONORDNN-LX9; Cronet/TTNetVersion:1c651b66 2024-08-30 QuicVersion:182d68c8 2024-05-28)",
        'Accept': "application/json, text/plain, */*",
        'Content-Type': "application/x-www-form-urlencoded",
        'x-argus': sig["x-argus"],
        'x-gorgon': sig["x-gorgon"],
        'x-khronos': sig["x-khronos"],
        'x-ladon': sig["x-ladon"],
        'x-ss-stub': sig.get("x-ss-stub", ""),
        'content-length': sig.get("content-length", "0")
    }
    
    response = requests.post(full_url, data=payload_encoded, headers=headers, timeout=30)
    try:
        return response.json()
    except:
        return {"raw": response.text, "status_code": response.status_code}

def create_tiktok_account(email, password, code, code2fa=None):
    try:
        email_xor = xor(email)
        hs = get_hs_params()
        params = get_base_params()
        params.update(hs)
        
        # Adım 1: Kod gönder
        payload = {
            'rules_version': "v2",
            'account_sdk_source': "app",
            'mix_mode': "1",
            'multi_login': "1",
            'type': "3436",
            'email': email_xor,
            'email_theme': "2",
            'use_passport_ticket': "1"
        }
        response = tiktok_request("https://api16-normal-c-alisg.tiktokv.com/passport/email/send_code/", params, payload)
        
        if "email_ticket" not in str(response):
            return {"success": False, "message": "Kod gönderilemedi"}
        
        # Adım 2: Kodu doğrula
        payload2 = {
            'code': code,
            'account_sdk_source': "app",
            'multi_login': "1",
            'type': "3436",
            'email': email_xor,
            'mix_mode': "1"
        }
        response2 = tiktok_request("https://api16-normal-c-alisg.tiktokv.com/passport/app/email/code_login/", params, payload2)
        
        verify_ticket = response2.get('data', {}).get('verify_ticket')
        if not verify_ticket:
            return {"success": False, "message": "Kod geçersiz"}
        
        # Adım 3: 2FA (opsiyonel)
        if code2fa:
            payload3 = {
                'aid': "1233",
                'code': code2fa,
                'verify_ticket': verify_ticket
            }
            response3 = tiktok_request("https://api16-normal-c-alisg.tiktokv.com/passport/totp/verify_without_login/", params, payload3)
            if "verify_ticket" not in str(response3):
                return {"success": False, "message": "2FA kodu geçersiz"}
        
        # Adım 4: Şifre ata
        password_xor = xor(password)
        pseudo_id = str(random.randint(1, 10**19))
        
        payload5 = {
            'mix_mode': '1',
            'password': password_xor,
            'pseudo_id': pseudo_id,
            'challenge_type': '3',
            'action': '5',
            'passport_ticket': verify_ticket,
            'skip_handler': 'error_handler',
            'fixed_mix_mode': '1',
        }
        params5 = {**params, **payload5}
        response5 = tiktok_request("https://api16-normal-c-alisg.tiktokv.com/passport/aaas/authenticate/", params5, payload5)
        
        if "session_key" in str(response5):
            return {"success": True, "message": "Hesap oluşturuldu!", "data": response5}
        else:
            return {"success": False, "message": "Şifre atanamadı"}
            
    except Exception as e:
        return {"success": False, "message": str(e)}

# ==================== TELEGRAM WEBHOOK ====================

def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    params = {"url": WEBHOOK_URL}
    response = requests.post(url, data=params)
    return response.json()

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return jsonify({
            "status": "online",
            "bot": "TikTok Hesap Oluşturma Botu",
            "developer": "@zanetmez",
            "webhook": WEBHOOK_URL
        })
    
    try:
        update = Update.de_json(request.get_json())
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        logging.error(f"Webhook hatası: {e}")
        return "ERROR", 500

@app.route('/setwebhook', methods=['GET'])
def set_webhook_route():
    result = set_webhook()
    return jsonify(result)

# ==================== BOT KOMUTLARI ====================

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, """
🤖 *TikTok Hesap Oluşturma Botu*
Geliştirici: @zanetmez

📌 *Komutlar:*
/start - Bu mesajı göster
/create email password code [2fa] - Hesap oluştur
/status - Bot durumu

📌 *Örnek:*
`/create ornek@gmail.com sifre123 123456`

⚠️ *Eğitim amaçlıdır!*
""", parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, f"""
✅ *Bot Aktif*
📅 {time.strftime('%d.%m.%Y %H:%M:%S')}
👤 @zanetmez
""", parse_mode='Markdown')

@bot.message_handler(commands=['create'])
def create_account(message):
    try:
        args = message.text.split()[1:]
        if len(args) < 3:
            bot.reply_to(message, """
❌ *Eksik parametre!*

📌 *Kullanım:*
`/create email password code [2fa]`

📌 *Örnek:*
`/create ornek@gmail.com sifre123 123456`
""", parse_mode='Markdown')
            return
        
        email = args[0]
        password = args[1]
        code = args[2]
        code2fa = args[3] if len(args) > 3 else None
        
        bot.reply_to(message, f"⏳ *Hesap oluşturuluyor...*\n📧 {email}", parse_mode='Markdown')
        
        result = create_tiktok_account(email, password, code, code2fa)
        
        if result.get('success'):
            bot.reply_to(message, f"""
✅ *Hesap Oluşturuldu!*

📧 {email}
🔑 {password}
📅 {time.strftime('%d.%m.%Y %H:%M')}

👤 @zanetmez
""", parse_mode='Markdown')
        else:
            bot.reply_to(message, f"❌ *Hata:* {result.get('message', 'Bilinmeyen hata')}", parse_mode='Markdown')
            
    except Exception as e:
        bot.reply_to(message, f"❌ *Hata:* {str(e)}", parse_mode='Markdown')

# ==================== ANA ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🐍 TikTok Hesap Oluşturma Telegram Botu")
    print("   Geliştirici: @zanetmez")
    print("=" * 60)
    
    try:
        bot_info = bot.get_me()
        print(f"✅ Bot: @{bot_info.username}")
    except Exception as e:
        print(f"❌ Bot bağlantı hatası: {e}")
        sys.exit(1)
    
    print(f"📌 Webhook URL: {WEBHOOK_URL}")
    print(f"📌 Port: {os.environ.get('PORT', 10000)}")
    print("=" * 60)
    
    # Webhook'u ayarla
    webhook_result = set_webhook()
    print(f"Webhook: {webhook_result}")
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        print(f"Telegram status: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"Errore Telegram: {e}")
        return False

@app.route('/webhook', methods=['POST', 'GET'])
@app.route('/webhook/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "✅ Webhook attivo e funzionante!", 200

    try:
        data = request.get_json(force=True) if request.is_json else request.get_data(as_text=True)
        
        symbol = data.get('symbol', data.get('ticker', 'N/A'))
        price = data.get('price', data.get('close', 'N/A'))
        interval = data.get('interval', 'N/A')
        message = data.get('message', str(data))
        time_str = data.get('time', 'N/A')

        final_message = f"""🚨 <b>SEGNALE TRADINGVIEW</b> 🚨

📍 <b>Simbolo:</b> <code>{symbol}</code>
💰 <b>Prezzo:</b> <code>{price}</code>
⏱ <b>Timeframe:</b> <code>{interval}</code>
🕒 <b>Ora:</b> {time_str}

━━━━━━━━━━━━━━━
{message}
━━━━━━━━━━━━━━━"""

        success = send_to_telegram(final_message)
        
        print(f"✅ Alert inviato correttamente")
        return jsonify({"status": "success", "sent": success}), 200

    except Exception as e:
        print(f"❌ Errore: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def home():
    return "✅ TradingView → Telegram Webhook attivo su Railway!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

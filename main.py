from flask import Flask, request, jsonify
import requests
import os
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def send_to_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ ERRORE: TELEGRAM_TOKEN o CHAT_ID mancanti!")
        return False
    
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
        return "✅ Webhook attivo su Railway!", 200
    
    try:
        # Leggi sempre il contenuto raw
        raw_data = request.get_data(as_text=True)
        print("📥 Raw data ricevuto da TradingView:")
        print(raw_data)
        
        # Prova a convertire in JSON
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            data = raw_data  # se non è JSON valido

        # Creiamo un messaggio bello e pulito
        if isinstance(data, dict):
            symbol = data.get('symbol', data.get('ticker', 'N/A'))
            price = data.get('price', data.get('close', 'N/A'))
            action = data.get('action', 'N/A')
            comment = data.get('comment', data.get('strategy', ''))
            
            final_message = f"""🚨 <b>ALERT TRADINGVIEW</b>

🔹 <b>Simbolo:</b> {symbol}
💰 <b>Prezzo:</b> {price}
⚡ <b>Azione:</b> {action}
📝 <b>Commento:</b> {comment}"""
        else:
            # Fallback se arriva come testo
            clean_text = raw_data.replace("'", "").replace("{", "").replace("}", "").strip()
            final_message = f"""🚨 <b>ALERT TRADINGVIEW</b>

{clean_text}"""

        # Invia su Telegram
        success = send_to_telegram(final_message)
        
        print(f"✅ Alert elaborato - Inviato: {success}")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"❌ Errore generale: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/')
def home():
    return "✅ TradingView → Telegram Webhook è ONLINE!"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

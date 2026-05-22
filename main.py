from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

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
        print(f"Telegram response: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"Errore invio Telegram: {e}")
        return False

# Route principale per webhook
@app.route('/webhook', methods=['POST', 'GET'])
@app.route('/webhook/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "✅ Webhook attivo! Usa POST da TradingView.", 200
    
    try:
        # Prova a leggere JSON
        if request.is_json:
            data = request.get_json(force=True)
        else:
            data = request.get_data(as_text=True)

        alert_message = data.get('message', str(data)) if isinstance(data, dict) else str(data)

        final_message = f"""🚨 <b>ALERT TRADINGVIEW</b>

{alert_message}"""

        success = send_to_telegram(final_message)
        
        print(f"✅ Webhook elaborata correttamente - Inviato: {success}")
        
        return jsonify({"status": "success", "sent": success}), 200

    except Exception as e:
        print(f"❌ Errore nel webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def home():
    return "✅ TradingView Telegram Webhook è ONLINE su Railway!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

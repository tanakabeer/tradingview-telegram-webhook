from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ================= CONFIGURAZIONE =================
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
# ================================================

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except:
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        alert_message = data.get('message', str(data))
        
        final_message = f"""🚨 <b>ALERT DA TRADINGVIEW</b>

{alert_message}"""

        success = send_to_telegram(final_message)
        
        return jsonify({"status": "success", "sent": success}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def home():
    return "✅ TradingView Telegram Webhook è attivo!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

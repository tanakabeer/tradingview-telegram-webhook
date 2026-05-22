from flask import Flask, request, jsonify
import requests
import os
import logging
from playwright.sync_api import sync_playwright
import tempfile
import uuid

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def send_to_telegram(text, photo_path=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
    
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            payload = {
                "chat_id": CHAT_ID,
                "caption": text,
                "parse_mode": "HTML"
            }
            r = requests.post(url + "sendPhoto", data=payload, files=files)
    else:
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        r = requests.post(url + "sendMessage", json=payload)
    
    return r.status_code == 200

def take_screenshot(chart_url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(chart_url, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(3000)  # Aspetta caricamento indicatori
            
            # Screenshot
            screenshot_path = f"/tmp/chart_{uuid.uuid4().hex[:8]}.png"
            page.screenshot(path=screenshot_path, full_page=False)
            browser.close()
            return screenshot_path
    except Exception as e:
        print(f"Errore screenshot: {e}")
        return None

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "✅ Webhook + Screenshot attivo!", 200

    try:
        data = request.get_json(force=True) if request.is_json else request.get_data(as_text=True)
        
        # Estrai dati
        symbol = data.get('symbol', data.get('ticker', 'N/A'))
        price = data.get('price', data.get('close', 'N/A'))
        interval = data.get('interval', 'N/A')
        strategy = data.get('strategy', 'Alert')
        message = data.get('message', str(data))
        chart_url = data.get('chart_url')  # ← URL del grafico da passare

        # Messaggio ACCATTIVANTE
        final_text = f"""🚨 <b>SEGNALE TRADINGVIEW</b> 🚨

📍 <b>Simbolo:</b> <code>{symbol}</code>
💰 <b>Prezzo:</b> <code>{price}</code>
⏱ <b>Timeframe:</b> <code>{interval}</code>
📌 <b>Strategia:</b> {strategy}

{message}

🕒 <i>{data.get('time', 'Ora non disponibile')}</i>"""

        # Screenshot se è stato passato chart_url
        screenshot_path = None
        if chart_url and isinstance(chart_url, str) and chart_url.startswith("https://www.tradingview.com"):
            screenshot_path = take_screenshot(chart_url)

        success = send_to_telegram(final_text, screenshot_path)

        # Pulizia file temporaneo
        if screenshot_path and os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        print(f"✅ Alert inviato con successo (foto: {bool(screenshot_path)})")
        return jsonify({"status": "success", "image_sent": bool(screenshot_path)}), 200

    except Exception as e:
        print(f"❌ Errore: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/')
def home():
    return "✅ TradingView Webhook + Screenshot attivo su Railway!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

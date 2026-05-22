const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

app.post('/webhook', async (req, res) => {
    try {
        const alert = req.body;

        const message = `
🚨 **ALERT TRADINGVIEW**

**Asset**: ${alert.ticker || alert.symbol || 'N/A'}
**Intervallo**: ${alert.interval || 'N/A'}
**Prezzo**: ${alert.price || alert.close || 'N/A'}
**Condizione**: ${alert.message || 'Alert scattato'}

⏰ ${new Date().toLocaleString('it-IT')}
        `.trim();

        await axios.post(`https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
            chat_id: process.env.CHAT_ID,
            text: message,
            parse_mode: 'Markdown'
        });

        res.status(200).send('OK');
    } catch (e) {
        res.status(500).send('Errore');
    }
});

app.listen(process.env.PORT || 3000, () => console.log('Webhook attivo'));

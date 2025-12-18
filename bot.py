import os
import requests
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask, request, jsonify
import threading

# --- Configurações ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") or "8018229888:AAGafHdDJvcgQEykQcY8Q1I9EEM7ro71gbQ"
NOWPAYMENTS_API_KEY = os.environ.get("NOWPAYMENTS_API_KEY") or "CF7S7Z0-C5P4MAJ-N4WNSMT-9T6VCF1"
PDF_LINK = "https://drive.google.com/file/d/1fYm0-t_OkDlybrhHKZHEEt3PtFn601to/view?usp=drivesdk"
HOST_URL = os.environ.get("HOST_URL") or "https://seuservidor.com"  # URL pública do servidor

bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# --- Funções do Telegram ---
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Olá! 👋\nVou te ajudar a receber seu e-book.\nDigite /pagar para gerar o pagamento via USDT (Polygon) e receber o PDF automaticamente."
    )

def pagar(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    try:
        invoice_data = {
            "price_amount": 7,
            "price_currency": "usd",
            "pay_currency": "usdt",
            "order_id": f"ebook-{chat_id}-{int(update.message.date.timestamp())}",
            "order_description": "E-book Matemática para Programadores",
            "ipn_callback_url": f"{HOST_URL}/webhook?chat_id={chat_id}",
            "cancel_url": "https://ebook-mat-prog.carrd.co/"
        }

        response = requests.post(
            "https://api.nowpayments.io/v1/invoice",
            headers={"x-api-key": NOWPAYMENTS_API_KEY},
            json=invoice_data
        )
        invoice = response.json()
        bot.send_message(chat_id, f"💰 Pagamento criado!\nClique aqui para pagar:\n{invoice['invoice_url']}\n\nApós o pagamento, você receberá o PDF automaticamente.")
    except Exception as e:
        bot.send_message(chat_id, f"Erro ao criar pagamento: {str(e)}")

# --- Webhook da NOWPayments ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    chat_id = request.args.get("chat_id")
    if not chat_id:
        return jsonify({"error": "chat_id ausente"}), 400

    if data.get("payment_status") == "finished":
        bot.send_message(chat_id, f"✅ Pagamento confirmado!\nAqui está seu PDF: {PDF_LINK}")
    return jsonify({"status": "ok"})

# --- Inicialização ---
def run_flask():
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)

def run_telegram():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("pagar", pagar))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_telegram()

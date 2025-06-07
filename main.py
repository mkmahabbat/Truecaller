import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Constants
BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
API_KEY = 'UVBOUb1397d66a0504dc280b01158ea9fc524'
API_URL = 'https://api.apilayer.com/number_verification/validate?number='

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📲 *Welcome to Mobile Number Info Bot!*\n\n"
        "Just send any phone number with country code (e.g., +919999999999) and I will check it for you.",
        parse_mode='Markdown'
    )

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *Help Menu*\n\n"
        "• Send a phone number (e.g., +14155552671)\n"
        "• You’ll get country, carrier, line type, and more.\n\n"
        "*Note:* Country code is mandatory.",
        parse_mode='Markdown'
    )

# Main logic for number checking
async def check_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()

    # Validation
    if not number.startswith('+') or not number[1:].isdigit() or len(number) < 8:
        await update.message.reply_text("❗ Please send a valid number with country code (e.g., +918888888888)")
        return

    # API Call
    headers = {"apikey": API_KEY}
    response = requests.get(API_URL + number, headers=headers)

    if response.status_code == 200:
        data = response.json()

        if not data.get("valid"):
            await update.message.reply_text("❌ This number appears to be *invalid*.", parse_mode="Markdown")
            return

        # Response formatting
        reply = (
            f"🔍 *Phone Number Details*\n"
            f"• Number: `{data.get('international_format')}`\n"
            f"• Country: {data.get('country_name')} ({data.get('country_code')})\n"
            f"• Location: {data.get('location')}\n"
            f"• Carrier: {data.get('carrier')}\n"
            f"• Line Type: {data.get('line_type')}\n"
        )

        # Optional button to search number in Google
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Search Google", url=f"https://www.google.com/search?q={number}")]
        ])

        await update.message.reply_text(reply, parse_mode="Markdown", reply_markup=keyboard)
    else:
        logger.error(f"API Error: {response.text}")
        await update.message.reply_text("⚠️ API error. Please try again later.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_number))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
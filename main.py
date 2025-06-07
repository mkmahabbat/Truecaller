import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ✅ Your Bot Token and API Key
BOT_TOKEN = '7685067743:AAGWyNvmkWffyxQqGILIWRFgkPIwYAdnPEA'
API_KEY = 'UVBOUb1397d66a0504dc280b01158ea9fc524'
API_URL = 'https://api.apilayer.com/number_verification/validate?number='

# Logging for debugging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📲 *Welcome to Number Info Bot!*\n\n"
        "Send any phone number with the country code (e.g., +919999999999) "
        "and I’ll tell you details like country, location, carrier, and more.",
        parse_mode='Markdown'
    )

# /help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *Help Guide*\n\n"
        "• Send a phone number with the country code.\n"
        "• Example: +14155552671 or +919999999999\n"
        "• I’ll respond with full details.\n\n"
        "*Note:* Country code (like +91, +1) is required.",
        parse_mode='Markdown'
    )

# Function to check number details
async def check_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()

    # Basic validation
    if not number.startswith('+') or not number[1:].isdigit() or len(number) < 8:
        await update.message.reply_text("❗ Please send a valid number with country code (e.g., +918888888888)")
        return

    # Make API request
    headers = {"apikey": API_KEY}
    try:
        response = requests.get(API_URL + number, headers=headers)
        if response.status_code == 200:
            data = response.json()

            if not data.get("valid"):
                await update.message.reply_text("❌ This number appears to be *invalid*.", parse_mode="Markdown")
                return

            # Format reply
            reply = (
                f"🔍 *Phone Number Details:*\n"
                f"• Number: `{data.get('international_format')}`\n"
                f"• Valid: ✅\n"
                f"• Country: {data.get('country_name')} ({data.get('country_code')})\n"
                f"• Location: {data.get('location')}\n"
                f"• Carrier: {data.get('carrier')}\n"
                f"• Line Type: {data.get('line_type')}"
            )

            # Button to Google the number
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔎 Search on Google", url=f"https://www.google.com/search?q={number}")]
            ])

            await update.message.reply_text(reply, parse_mode="Markdown", reply_markup=keyboard)

        else:
            await update.message.reply_text("⚠️ API error. Please try again later.")
            logger.error(f"API Error: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"Exception: {e}")
        await update.message.reply_text("❌ An error occurred. Please try again later.")

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_number))

    logger.info("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

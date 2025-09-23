import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Tokenni Railway environment variable-dan olamiz
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("♻️ Salom! Bu Ecoback – chiqindini to‘g‘ri tashlab, cashback yutib oling!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()


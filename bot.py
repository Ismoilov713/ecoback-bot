import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Railway config orqali tokenni olish
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Bot ishga tushdi 🚀")

def main():
    app = Application.builder().token(TOKEN).build()

    # /start komandasi
    app.add_handler(CommandHandler("start", start))

    app.run_polling()

if __name__ == "__main__":
    main()

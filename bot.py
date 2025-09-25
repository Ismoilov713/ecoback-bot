from telegram.ext import Application, CommandHandler

BOT_TOKEN = "8227753790:AAFGqwVXR1OvEeh0LyCveGzkUAcqhRWiHYQ"

async def start(update, context):
    await update.message.reply_text("♻️ Salom! Bu Ecoback – chiqindini to‘g‘ri tashlab, cashback yutib oling")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()

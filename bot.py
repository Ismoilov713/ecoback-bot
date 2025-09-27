import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import csv
import os

# 🔑 Admin ID
MY_ID = 5010840702  

# Fayllar
USERS_FILE = "users.csv"
CODES_FILE = "codes.csv"   # Mahsulot kodlari
BINS_FILE = "bins.csv"     # Chiqindi idish kodlari

# === Foydalanuvchilarni boshqarish ===
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return {rows[0]: int(rows[1]) for rows in reader}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for user_id, points in users.items():
            writer.writerow([user_id, points])

# === Kodlarni boshqarish ===
def load_codes(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["kod"]: row["status"] for row in reader}

def save_codes(file, codes):
    with open(file, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["kod", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for kod, status in codes.items():
            writer.writerow({"kod": kod, "status": status})

# === Start komandasi ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(
        f"♻️ Salom {user.first_name}! Bu Ecoback bot.\n\n"
        "👉 Jarayon: \n"
        "1️⃣ Avval mahsulot kodini yuboring.\n"
        "2️⃣ Keyin chiqindi idishidagi kodni yuboring.\n"
        "✅ Shunda ball qo‘shiladi!\n\n"
        "Buyruqlar:\n"
        "/scan - kodlarni kiritishni boshlash\n"
        "/balance - balansingizni ko‘rish\n"
        "/cashout - pul olish so‘rovi\n"
        "/help - yordam"
    )

# === Help komandasi ===
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Yordam:\n\n"
        "/scan - kod kiritishni boshlash\n"
        "/balance - balansni ko‘rish\n"
        "/cashout - pul olish so‘rovi\n\n"
        "Jarayon: mahsulot kodi → chiqindi idishi kodi"
    )

# === Balans komandasi ===
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    users = load_users()
    points = users.get(user_id, 0)
    await update.message.reply_text(f"💰 Sizning balansingiz: {points} ball.")

# === Cashout komandasi ===
async def cashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    users = load_users()
    points = users.get(user_id, 0)

    if points >= 10:
        await update.message.reply_text("✅ So‘rovingiz qabul qilindi. Admin siz bilan bog‘lanadi.")

        # 🔔 Admin uchun reminder
        await context.bot.send_message(
            chat_id=MY_ID,
            text=f"💸 Foydalanuvchi {user_id} pul olish uchun {points} ball yig‘di!"
        )
    else:
        await update.message.reply_text("⚠️ Pul olish uchun kamida 10 ball kerak.")

# === Scan komandasi ===
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()  # eski ma'lumotlarni tozalash
    await update.message.reply_text("📦 Avval mahsulot kodini yuboring:")

# === Kodlarni qayta ishlash ===
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip()

    users = load_users()
    codes = load_codes(CODES_FILE)
    bins = load_codes(BINS_FILE)

    # 1️⃣ Mahsulot kodi
    if text in codes:
        if codes[text] == "unused":
            context.user_data["pending_product"] = text
            await update.message.reply_text("🗑 Endi chiqindi idishidagi kodni yuboring.")
        else:
            await update.message.reply_text("⚠️ Bu mahsulot kodi allaqachon ishlatilgan.")
        return

    # 2️⃣ Chiqindi idish kodi
    if text in bins:
        if "pending_product" in context.user_data:
            product_code = context.user_data.pop("pending_product")
            codes[product_code] = "used"
            save_codes(CODES_FILE, codes)

            users[user_id] = users.get(user_id, 0) + 1
            save_users(users)

            await update.message.reply_text(
                f"✅ Ball qo‘shildi!\n💰 Sizning balansingiz: {users[user_id]} ball."
            )
        else:
            await update.message.reply_text("⚠️ Avval mahsulot kodini yuboring.")
        return

    # ❌ Agar kod yo‘q bo‘lsa
    await update.message.reply_text("❌ Bunday kod mavjud emas. /scan komandasi orqali qaytadan boshlang.")

# === Botni ishga tushirish ===
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("cashout", cashout))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

    app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

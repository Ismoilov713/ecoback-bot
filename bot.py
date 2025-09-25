#!/usr/bin/env python3
"""
Ecoback Telegram bot - full single-file implementation.

Required files (in same folder as this script):
- codes.csv   (header: kod,status)  e.g. ECO001,unused
- users.csv   (header: user_id,points)  (will be created automatically if missing)

Environment variables (recommended):
- BOT_TOKEN  (your Telegram bot token from BotFather)
- ADMIN_ID   (your Telegram numeric user id for receiving cashout notifications)

If you prefer, you can temporarily put the token directly in BOT_TOKEN_FALLBACK below,
but DO NOT commit a real token to a public repo.
"""

import asyncio
import csv
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ----------------- CONFIG -----------------
# Use env vars (set these in Render / Railway / your shell)
BOT_TOKEN = os.getenv("BOT_TOKEN") or ""  # best: set in environment
ADMIN_ID_ENV = os.getenv("ADMIN_ID") or ""  # optional; set to admin numeric id

# Fallback (only for quick local testing; avoid committing real token)
BOT_TOKEN_FALLBACK = ""  # <-- optionally paste token here (NOT recommended)

# Points and money conversion
POINT_VALUE = 100  # 1 ball = 100 so'm
CASHOUT_THRESHOLD = 10  # minimum balls to request cashout
CSV_CODES = Path("codes.csv")
CSV_USERS = Path("users.csv")
CSV_CASHOUTS = Path("cashouts.csv")  # optional record of requests

# Logging level
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------- STATE -----------------
file_lock = asyncio.Lock()  # async lock for file operations

# ----------------- Helper I/O functions -----------------
def ensure_users_file():
    if not CSV_USERS.exists():
        with CSV_USERS.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["user_id", "points"])
            writer.writeheader()


async def read_codes() -> List[Dict[str, str]]:
    """Read codes.csv and return list of rows (dicts with 'kod' and 'status')."""
    async with file_lock:
        if not CSV_CODES.exists():
            return []
        # read synchronously inside lock (small file expected)
        with CSV_CODES.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)


async def write_codes(rows: List[Dict[str, str]]):
    """Atomically write codes.csv from provided rows."""
    async with file_lock:
        tmp = CSV_CODES.with_suffix(".tmp")
        with tmp.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["kod", "status"])
            writer.writeheader()
            writer.writerows(rows)
        tmp.replace(CSV_CODES)


async def read_users() -> List[Dict[str, str]]:
    """Read users.csv; create if missing."""
    async with file_lock:
        ensure_users_file()
        with CSV_USERS.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)


async def write_users(rows: List[Dict[str, str]]):
    """Atomically write users.csv."""
    async with file_lock:
        tmp = CSV_USERS.with_suffix(".tmp")
        with tmp.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["user_id", "points"])
            writer.writeheader()
            writer.writerows(rows)
        tmp.replace(CSV_USERS)


async def get_user_points(user_id: int) -> int:
    users = await read_users()
    for r in users:
        if r["user_id"] == str(user_id):
            try:
                return int(r["points"])
            except Exception:
                return 0
    return 0


async def add_user_points(user_id: int, add: int = 1):
    users = await read_users()
    found = False
    for r in users:
        if r["user_id"] == str(user_id):
            r["points"] = str(int(r["points"]) + add)
            found = True
            break
    if not found:
        users.append({"user_id": str(user_id), "points": str(add)})
    await write_users(users)


async def find_code_row(code: str) -> Optional[Dict[str, str]]:
    codes = await read_codes()
    for r in codes:
        if r["kod"] == code:
            return r
    return None


async def mark_code_used(code: str) -> bool:
    codes = await read_codes()
    changed = False
    for r in codes:
        if r["kod"] == code and r["status"] != "used":
            r["status"] = "used"
            changed = True
            break
    if changed:
        await write_codes(codes)
    return changed


async def record_cashout_request(user_id: int, points: int, money: int):
    async with file_lock:
        exists = CSV_CASHOUTS.exists()
        with CSV_CASHOUTS.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["user_id", "points", "money"])
            if not exists:
                writer.writeheader()
            writer.writerow({"user_id": str(user_id), "points": str(points), "money": str(money)})


# ----------------- Bot Handlers -----------------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"♻️ Salom {user.first_name or ''}! Bu Ecoback bot.\n\n"
        f"QR kodni skaner qilib ichidagi kodni botga yuboring (masalan: ECO001).\n"
        f"1 ball = {POINT_VALUE} so'm. {CASHOUT_THRESHOLD} ball = {POINT_VALUE * CASHOUT_THRESHOLD} so'm.\n\n"
        "Buyruqlar:\n"
        "/myid - o'z Telegram ID'ingizni ko'rsatadi (admin bo'lish uchun kerak)\n"
        "/balance - balansingizni ko'rsatadi\n"
        "/cashout - pul olish so'rovi yuboradi (agar yetarli ball bo'lsa)\n"
        "/help - bu yordam xabari"
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Yordam:\n"
        "- QR kodni skaner qilib chiqqan matnni botga yuboring (masalan: ECO001).\n"
        "- /balance - balansingizni ko'rish\n"
        "- /cashout - pul olish so'rovi (10 ball = 1000 so'm)\n"
        "- /myid - o'z ID'ingizni ko'rish (admin bo'lish uchun kerak)"
    )


async def myid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"Sening Telegram ID: {user_id}")


async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    points = await get_user_points(user_id)
    money = points * POINT_VALUE
    await update.message.reply_text(f"💰 Sizning balansingiz: {points} ball ({money} so'm)")


async def cashout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    points = await get_user_points(user_id)
    money = points * POINT_VALUE
    if points < CASHOUT_THRESHOLD:
        await update.message.reply_text(
            f"❌ Pul olish uchun kamida {CASHOUT_THRESHOLD} ball kerak. "
            f"Hozir: {points} ball ({money} so'm)."
        )
        return

    # create request record
    await record_cashout_request(user_id, points, money)

    # notify admin (if configured)
    admin_id_value = get_admin_id()
    await update.message.reply_text(
        f"✅ So‘rovingiz qabul qilindi. Adminga xabar yuborildi. Siz {money} so'm olasiz deb hisoblandi."
    )
    if admin_id_value:
        try:
            await context.bot.send_message(
                chat_id=admin_id_value,
                text=f"⚠️ Cashout so‘rovi: Foydalanuvchi {user_id} so‘radi. Ball: {points}. Summa: {money} so'm."
            )
        except Exception as e:
            logger.exception("Adminga xabar yuborishda xato: %s", e)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plain text messages - expect code like ECO001."""
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Iltimos, kod yuboring yoki /help ni bosing.")
        return

    # Normalize - uppercase and strip spaces
    code = text.upper()

    # Find code in codes.csv
    row = await find_code_row(code)
    if row is None:
        await update.message.reply_text("❌ Noto'g'ri yoki mavjud bo'lmagan kod.")
        return

    if row.get("status", "").lower() == "used":
        await update.message.reply_text("⚠️ Bu kod allaqachon ishlatilgan.")
        return

    # Mark used and add point
    ok = await mark_code_used(code)
    if not ok:
        # race condition or already used just now
        await update.message.reply_text("⚠️ Kodni qayta tekshirishda muammo — iltimos, yana urinib ko'ring.")
        return

    # add points
    user_id = update.effective_user.id
    await add_user_points(user_id, 1)
    points = await get_user_points(user_id)
    money = points * POINT_VALUE

    await update.message.reply_text(
        f"✅ Kod qabul qilindi! Sizga 1 ball qo'shildi.\n"
        f"🎯 Joriy ballaringiz: {points} ball ({money} so'm)."
    )

    if points >= CASHOUT_THRESHOLD:
        await update.message.reply_text(
            f"🎉 Tabriklaymiz! Siz {CASHOUT_THRESHOLD} ballga yetdingiz. "
            f"Pul olish uchun /cashout buyrug'ini yuboring."
        )


# ----------------- Utilities -----------------
def get_admin_id() -> Optional[int]:
    # Try environment, then fallback to ADMIN_ID_ENV variable
    v = os.getenv("ADMIN_ID") or ADMIN_ID_ENV
    if not v:
        return None
    try:
        return int(v)
    except Exception:
        return None


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Exception while handling an update: %s", context.error)
    try:
        # notify user gracefully
        if isinstance(update, Update) and update.effective_user:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="❗ Botda xatolik yuz berdi. Keyinroq qaytadan urinib ko'ring."
            )
    except Exception:
        logger.exception("Failed to send error message to user.")


# ----------------- Main -----------------
def main():
    token = BOT_TOKEN or BOT_TOKEN_FALLBACK
    if not token:
        logger.error("BOT token not found. Set BOT_TOKEN environment variable or BOT_TOKEN_FALLBACK in code.")
        raise SystemExit("Missing BOT_TOKEN")

    app = Application.builder().token(token).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("myid", myid_handler))
    app.add_handler(CommandHandler("balance", balance_handler))
    app.add_handler(CommandHandler("cashout", cashout_handler))

    # Message handler (codes)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Global error handler
    app.add_error_handler(error_handler)

    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()

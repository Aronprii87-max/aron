import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Atlas Rise online. Streets have stories.\n"
        "Send me your location using Telegram's attachment menu."
    )


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = update.message.location
    await update.message.reply_text(
        "Location received.\n"
        f"Latitude: {place.latitude}\n"
        f"Longitude: {place.longitude}\n"
        "The guide features are coming next."
    )


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("Set BOT_TOKEN in Railway Variables.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, location))
    app.run_polling()


if __name__ == "__main__":
    main()
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL)
    connect
 SimpleConnectionPool

DATABASE_URL 
"""CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT,
            lat DOUBLE PRECISION,
            lng DOUBLE PRECISION,
            last_seen TIMESTAMPTZ
        )"""Ah, that's my own text — you're asking how to wire it in. Got it. Let me give you a concrete example.

Say you have a users table. When Atlas receives a location, save the user:

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = update.message.location
    user = update.effective_user

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO users (telegram_id, username, lat, lng, last_seen)
                   VALUES (%s, %s, %s, %s, NOW())
                   ON CONFLICT (telegram_id) DO UPDATE
                   SET lat = EXCLUDED.lat, lng = EXCLUDED.lng, last_seen = NOW()""",
                (user.id, user.username, place.latitude, place.longitude),
            )
        conn.commit()
    finally:
        conn.close()

    await update.message.reply_text(
        f"Location received ({place.latitude:.4f}, {place.longitude:.4f}). "
        "The guide features are coming next."
    )


The ON CONFLICT ... DO UPDATE trick means repeat visitors just get their coords refreshed instead of duplicate rows.

Before this runs, create the table once — either via a Railway database shell, or just add this at the top of main():

def init_db():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT,
            lat DOUBLE PRECISION,
            lng DOUBLE PRECISION,
            last_seen TIMESTAMPTZ
        )""")
    conn.commit()
    conn.close()
"https://railway.app/railway.schema.json"

"builder"


        
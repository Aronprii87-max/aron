import asyncio
import logging
import os

import psycopg2
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logger = logging.getLogger(__name__)


def get_db():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("Set DATABASE_URL in Railway Variables.")
    return psycopg2.connect(database_url, connect_timeout=10)


def init_db():
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """CREATE TABLE IF NOT EXISTS users (
                        telegram_id BIGINT PRIMARY KEY,
                        username TEXT,
                        lat DOUBLE PRECISION,
                        lng DOUBLE PRECISION,
                        last_seen TIMESTAMPTZ
                    )"""
                )
    finally:
        conn.close()


def save_location(telegram_id, username, latitude, longitude):
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO users (telegram_id, username, lat, lng, last_seen)
                       VALUES (%s, %s, %s, %s, NOW())
                       ON CONFLICT (telegram_id) DO UPDATE
                       SET username = EXCLUDED.username,
                           lat = EXCLUDED.lat,
                           lng = EXCLUDED.lng,
                           last_seen = NOW()""",
                    (telegram_id, username, latitude, longitude),
                )
    finally:
        conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message is None:
        return
    await update.effective_message.reply_text(
        "Atlas Rise online. Streets have stories.\n"
        "Send me your location using Telegram's attachment menu.\n"
        "I'll save your latest location for the guide."
    )


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    if message is None or message.location is None or user is None:
        return
    place = message.location
    try:
        await asyncio.to_thread(
            save_location, user.id, user.username, place.latitude, place.longitude
        )
    except psycopg2.Error:
        logger.error("Could not save location to the database.")
        await message.reply_text(
            "Location received, but I couldn't save it. Please try again shortly."
        )
        return
    await message.reply_text(
        f"Location saved ({place.latitude:.4f}, {place.longitude:.4f}). "
        "The guide features are coming next."
    )


def main():
    logging.basicConfig(level=logging.INFO)
    # HTTP request URLs can contain the bot token.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("Set BOT_TOKEN in Railway Variables.")

    init_db()
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, location))
    app.run_polling()


if __name__ == "__main__":
    main()


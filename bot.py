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
import os
import logging
from flask import Flask, request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from bot import dp, bot

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "mysecret")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.post(WEBHOOK_PATH)
async def handle_webhook():
    update = Update.model_validate(request.json)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.route("/")
def health():
    return "Bot is running!"

async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    asyncio.run(on_startup())

    config = Config()
    config.bind = ["0.0.0.0:10000"]
    asyncio.run(serve(app, config))

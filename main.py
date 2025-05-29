import os
import logging
import asyncio
from flask import Flask, request, Response
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from bot import dp, bot

# ─────── Webhook config ───────
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "MARS")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.post(WEBHOOK_PATH)
def handle_webhook():
    update = Update.model_validate(request.json)
    loop.create_task(dp.feed_update(bot, update))
    return Response()

@app.route("/")
def hello():
    return "Bot is alive"

# Устанавливаем webhook при старте
@app.before_first_request
def setup():
    loop.create_task(bot.set_webhook(WEBHOOK_URL))

if __name__ == "__main__":
    import hypercorn.asyncio
    import hypercorn.config
    config = hypercorn.config.Config()
    config.bind = ["0.0.0.0:10000"]
    loop.run_until_complete(hypercorn.asyncio.serve(app, config))

import logging
from aiogram import Bot, Dispatcher
from storage import Storage

TOKEN = "YOUR_BOT_TOKEN_HERE"

# logs
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# storage
storage = Storage()
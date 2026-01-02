import logging
from aiogram import Bot, Dispatcher

TOKEN = "Inset your bot token here"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище варнов (в памяти)
warnings = {}
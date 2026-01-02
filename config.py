import logging
from aiogram import Bot, Dispatcher
from storage import Storage

TOKEN = "8520993418:AAHB9b7nW2u64qyy2u4Qr7O3IXGpT0SkCWI"

# logs
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# storage
storage = Storage()
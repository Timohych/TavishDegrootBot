import logging
from aiogram import Bot, Dispatcher
from storage import Storage

TOKEN = "Insert_Your_Bot_Token_Here"

# logs
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# storage
storage = Storage()
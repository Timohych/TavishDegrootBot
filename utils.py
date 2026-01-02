from aiogram import types
from config import bot

def parse_time(time_str: str):
    """Конвертирует строку типа '10m', '1h' в секунды"""
    if not time_str:
        return None
    unit = time_str[-1]
    try:
        val = int(time_str[:-1])
    except ValueError:
        return None
    
    if unit == 'm': return val * 60
    elif unit == 'h': return val * 3600
    elif unit == 'd': return val * 86400
    else: return None

async def is_admin(message: types.Message):
    """Проверяет, является ли отправитель админом"""
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ['administrator', 'creator']
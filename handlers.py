from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import ChatPermissions
from datetime import datetime, timedelta

from config import dp, bot, warnings
from utils import parse_time, is_admin

# --- START ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Знаешь почему я хороший подрывник?.\n"
        "А будь я плохим подрывником, я бы не сидел сейчас здесь и не трепался с тобой, врубаешься?\n\n"
        "А теперь за дело!\n"
        "/ban - Забанить\n"
        "/kick - Выгнать\n"
        "/mute [время] - Замутить (например: /mute 10m)\n"
        "/unmute - Размутить\n"
        "/warn - Выдать предупреждение (3 варна = бан)"
    )

# --- BAN ---
@dp.message(Command("ban"))
async def cmd_ban(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение!")
    
    if not await is_admin(message):
        return await message.reply("У тебя нет прав, сынок!")

    user_id = message.reply_to_message.from_user.id
    try:
        await bot.ban_chat_member(message.chat.id, user_id)
        await message.answer(f"🚫 Пользователь {message.reply_to_message.from_user.full_name} был забанен!")
    except Exception as e:
        await message.reply(f"Не удалось забанить. Ошибка: {e}")

# --- KICK ---
@dp.message(Command("kick"))
async def cmd_kick(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение!")
    
    if not await is_admin(message):
        return

    user_id = message.reply_to_message.from_user.id
    try:
        await bot.ban_chat_member(message.chat.id, user_id)
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.answer(f"👞 {message.reply_to_message.from_user.full_name} схватил поджопника!")
    except Exception:
        await message.reply("Много хочешь, олух!")

# --- MUTE ---
@dp.message(Command("mute"))
async def cmd_mute(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение!")
    
    if not await is_admin(message):
        return await message.reply("Много хочешь, олух!")

    args = message.text.split()
    duration = 600 
    if len(args) > 1:
        parsed = parse_time(args[1])
        if parsed: duration = parsed

    user_id = message.reply_to_message.from_user.id
    permissions = ChatPermissions(can_send_messages=False)
    until = datetime.now() + timedelta(seconds=duration)

    try:
        await bot.restrict_chat_member(message.chat.id, user_id, permissions, until_date=until)
        await message.answer(f"😶 {message.reply_to_message.from_user.full_name} заткнут на {duration/60} мин.")
    except Exception as e:
        await message.reply(f"Не удалось замутить. Ошибка: {e}")

# --- UNMUTE ---
@dp.message(Command("unmute"))
async def cmd_unmute(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("❗ Ответь командой на сообщение того, кого нужно размутить.")
    
    if not await is_admin(message):
        return await message.reply("Много хочешь, олух!")

    user_id = message.reply_to_message.from_user.id
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True,
        can_change_info=False, 
        can_pin_messages=False 
    )

    try:
        await bot.restrict_chat_member(chat_id=message.chat.id, user_id=user_id, permissions=permissions)
        await message.answer(f"🔊 {message.reply_to_message.from_user.full_name} снова может говорить!")
    except Exception as e:
        await message.reply(f"Не удалось размутить. Ошибка: {e}")

# --- WARN ---
@dp.message(Command("warn"))
async def cmd_warn(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение того, кому хочешь дать предупреждение!")
    
    if not await is_admin(message):
        return await message.reply("У тебя нет прав раздавать предупреждения!")

    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.full_name

    if chat_id not in warnings:
        warnings[chat_id] = {}
    if user_id not in warnings[chat_id]:
        warnings[chat_id][user_id] = 0

    warnings[chat_id][user_id] += 1
    count = warnings[chat_id][user_id]

    if count >= 3:
        duration = 86400  
        until = datetime.now() + timedelta(seconds=duration)
        permissions = ChatPermissions(can_send_messages=False)

        try:
            await bot.restrict_chat_member(chat_id, user_id, permissions, until_date=until)
            await message.answer(f"⚠️ {user_name} получил третий варн!\n🤐 Замучен на 24 часа")
            warnings[chat_id][user_id] = 0
        except Exception as e:
            await message.reply(f"Не удалось выдать мут: {e}")
    else:
        await message.answer(f"⚠️ {user_name}, получил варн[{count}/3]")

# --- UNWARN ---
@dp.message(Command("unwarn"))
async def cmd_unwarn(message: types.Message):
    if not message.reply_to_message or not await is_admin(message):
        return
    
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    
    if chat_id in warnings and user_id in warnings[chat_id]:
        warnings[chat_id][user_id] = 0
        await message.reply("Счетчик варна обнулен.")

# --- UNBAN ---
@dp.message(Command("unban"))
async def cmd_unban(message: types.Message):
    if not await is_admin(message):
        return await message.reply("Много хочешь, олух!")

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name
    else:
        args = message.text.split()
        if len(args) < 2:
            return await message.reply("Напиши `/unban ID_ПОЛЬЗОВАТЕЛЯ` или ответь на сообщение.")
        
        if not args[1].isdigit():
            return await message.reply("ID пользователя должен состоять из цифр!")
        
        user_id = int(args[1])
        user_name = f"пользователя с ID {user_id}"

    try:
        await bot.unban_chat_member(message.chat.id, user_id, only_if_banned=True)
        await message.answer(f"✅ {user_name} Разбанен!")
    except Exception as e:
        await message.reply(f"Не удалось разбанить. Ошибка: {e}")
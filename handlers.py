from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import ChatPermissions
from datetime import datetime, timedelta

from config import dp, bot, storage
from utils import parse_time, is_admin

def get_display_name(user_id: int, real_name: str) -> str:
    """Get nickname if set, otherwise return real name"""
    nickname = storage.get_nickname(user_id)
    return nickname if nickname else real_name

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
        "/warn - Выдать предупреждение (3 варна = бан)\n"
        "/nickname [имя] - Установить свой ник\n"
        "/mynickname - Посмотреть свой ник"
    )

# --- BAN ---
@dp.message(Command("ban"))
async def cmd_ban(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение!")
    
    if not await is_admin(message):
        return await message.reply("У тебя нет прав, сынок!")

    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.full_name
    display_name = get_display_name(user_id, user_name)
    try:
        await bot.ban_chat_member(message.chat.id, user_id)
        storage.add_ban(message.chat.id, user_id, user_name)
        await message.answer(f"🚫 Пользователь {display_name} был забанен!")
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
    user_name = message.reply_to_message.from_user.full_name
    display_name = get_display_name(user_id, user_name)
    try:
        await bot.ban_chat_member(message.chat.id, user_id)
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.answer(f"👞 {display_name} схватил поджопника!")
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
    user_name = message.reply_to_message.from_user.full_name
    display_name = get_display_name(user_id, user_name)
    permissions = ChatPermissions(can_send_messages=False)
    until = datetime.now() + timedelta(seconds=duration)

    try:
        await bot.restrict_chat_member(message.chat.id, user_id, permissions, until_date=until)
        storage.add_mute(message.chat.id, user_id, user_name, until.isoformat())
        await message.answer(f"😶 {display_name} заткнут на {duration/60} мин.")
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
    user_name = message.reply_to_message.from_user.full_name
    display_name = get_display_name(user_id, user_name)
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
        storage.remove_mute(message.chat.id, user_id)
        await message.answer(f"🔊 {display_name} снова может говорить!")
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
    display_name = get_display_name(user_id, user_name)

    storage.add_warn(chat_id, user_id)
    count = storage.get_warns(chat_id, user_id)

    if count >= 3:
        duration = 86400  
        until = datetime.now() + timedelta(seconds=duration)
        permissions = ChatPermissions(can_send_messages=False)

        try:
            await bot.restrict_chat_member(chat_id, user_id, permissions, until_date=until)
            storage.add_mute(chat_id, user_id, user_name, until.isoformat())
            await message.answer(f"⚠️ {display_name} получил третий варн!\n🤐 Замучен на 24 часа")
            storage.reset_warns(chat_id, user_id)
        except Exception as e:
            await message.reply(f"Не удалось выдать мут: {e}")
    else:
        await message.answer(f"⚠️ {display_name} получил варн [{count}/3]")

# --- UNWARN ---
@dp.message(Command("unwarn"))
async def cmd_unwarn(message: types.Message):
    if not message.reply_to_message or not await is_admin(message):
        return
    
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    
    storage.reset_warns(chat_id, user_id)
    await message.reply("Счетчик варна обнулен.")

# --- UNBAN ---
@dp.message(Command("unban"))
async def cmd_unban(message: types.Message):
    if not await is_admin(message):
        return await message.reply("Много хочешь, олух!")

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name
        display_name = get_display_name(user_id, user_name)
    else:
        args = message.text.split()
        if len(args) < 2:
            return await message.reply("Напиши `/unban ID_ПОЛЬЗОВАТЕЛЯ` или ответь на сообщение.")
        
        if not args[1].isdigit():
            return await message.reply("ID пользователя должен состоять из цифр!")
        
        user_id = int(args[1])
        display_name = f"пользователя с ID {user_id}"

    try:
        await bot.unban_chat_member(message.chat.id, user_id, only_if_banned=True)
        storage.remove_ban(message.chat.id, user_id)
        await message.answer(f"✅ {display_name} Разбанен!")
    except Exception as e:
        await message.reply(f"Не удалось разбанить. Ошибка: {e}")

# --- BANLIST ---
@dp.message(Command("banlist"))
async def cmd_banlist(message: types.Message):
    if not await is_admin(message):
        return await message.reply("У тебя нет прав!")
    
    bans = storage.get_all_bans(message.chat.id)
    
    if not bans:
        return await message.answer("📋 Список забаненных пуст.")
    
    text = "🚫 **ЗАБАНЕННЫЕ ПОЛЬЗОВАТЕЛИ:**\n\n"
    for user_id, ban_info in bans.items():
        display_name = get_display_name(int(user_id), ban_info['name'])
        text += f"👤 {display_name} (ID: {user_id})\n"
        text += f"   🕐 {ban_info['banned_at']}\n\n"
    
    await message.answer(text)

# --- WARNLIST ---
@dp.message(Command("warnlist"))
async def cmd_warnlist(message: types.Message):
    if not await is_admin(message):
        return await message.reply("У тебя нет прав!")
    
    warns = storage.get_all_warns(message.chat.id)
    
    if not warns:
        return await message.answer("📋 Список варнов пуст.")
    
    text = "⚠️ **ПРЕДУПРЕЖДЕНИЯ:**\n\n"
    for user_id, warn_count in warns.items():
        if warn_count > 0:
            text += f"👤 ID: {user_id} - {warn_count}/3 варнов\n"
    
    if text == "⚠️ **ПРЕДУПРЕЖДЕНИЯ:**\n\n":
        return await message.answer("📋 Список варнов пуст.")
    
    await message.answer(text)

# --- MUTELIST ---
@dp.message(Command("mutelist"))
async def cmd_mutelist(message: types.Message):
    if not await is_admin(message):
        return await message.reply("У тебя нет прав!")
    
    mutes = storage.get_all_mutes(message.chat.id)
    
    if not mutes:
        return await message.answer("📋 Список замученных пуст.")
    
    text = "😶 **ЗАМУЧЕННЫЕ ПОЛЬЗОВАТЕЛИ:**\n\n"
    for user_id, mute_info in mutes.items():
        display_name = get_display_name(int(user_id), mute_info['name'])
        text += f"👤 {display_name} (ID: {user_id})\n"
        text += f"   🕐 До: {mute_info['until']}\n\n"
    
    await message.answer(text)

# --- NICKNAME ---
@dp.message(Command("nickname"))
async def cmd_nickname(message: types.Message):
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        return await message.reply("Использование: /nickname [имя]\nПример: /nickname Демолиционщик")
    
    nickname = args[1].strip()
    
    if len(nickname) > 32:
        return await message.reply("❌ Ник слишком длинный! Максимум 32 символа.")
    
    if len(nickname) < 1:
        return await message.reply("❌ Ник не может быть пустым!")
    
    storage.set_nickname(message.from_user.id, nickname)
    await message.answer(f"✅ Твой ник установлен: **{nickname}**")

# --- MY NICKNAME ---
@dp.message(Command("mynickname"))
async def cmd_mynickname(message: types.Message):
    nickname = storage.get_nickname(message.from_user.id)
    
    if nickname:
        await message.answer(f"👤 Твой ник: **{nickname}**")
    else:
        await message.answer("❌ У тебя нет установленного ника. Установи его командой /nickname [имя]")
import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ChatPermissions

# --- CONFIGURATION ---
# Insert your BotFather token here
TOKEN = "Insert Your Token Here" 

# Logger setup
logging.basicConfig(level=logging.INFO)

# Bot and dispatcher initialization
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Dictionary to store warnings (in a production project, it's better to use a database)
# Structure: {chat_id: {user_id: count}}
warnings = {}

# --- HELPER FUNCTIONS ---

def parse_time(time_str):
    """Converts a string like '10m', '1h' into seconds"""
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
    """Checks if the sender is an admin"""
    member = await message.chat.get_member(message.from_user.id)
    return member.status in ['administrator', 'creator']

# --- HANDLERS (COMMANDS) ---

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

# 1. /BAN COMMAND
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

# 2. /KICK COMMAND
@dp.message(Command("kick"))
async def cmd_kick(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение!")
    
    if not await is_admin(message):
        return 

    user_id = message.reply_to_message.from_user.id
    try:
        # Ban first to kick the user
        await bot.ban_chat_member(message.chat.id, user_id)
        # Unban immediately so they can return
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.answer(f"👞 {message.reply_to_message.from_user.full_name} схватил поджопника!")
    except Exception:
        await message.reply("Много хочешь, олух!")

# 3. /MUTE COMMAND
@dp.message(Command("mute"))
async def cmd_mute(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение!")
    
    if not await is_admin(message):
        return await message.reply("Много хочешь, олух!")

    args = message.text.split()
    duration = 600 # 10 minutes by default
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

# 4. /UNMUTE COMMAND
@dp.message(Command("unmute"))
async def cmd_unmute(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("❗ Ответь командой на сообщение того, кого нужно размутить.")
    
    if not await is_admin(message):
        return await message.reply("Много хочешь, олух!")

    user_id = message.reply_to_message.from_user.id
    
    # To unmute, we explicitly allow EVERYTHING that is typically available to users
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
        # We apply a "restriction" with full permissions and NO expiry (permanent)
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=permissions
        )
        await message.answer(f"🔊 {message.reply_to_message.from_user.full_name} снова может говорить!")
    except Exception as e:
        await message.reply(f"Не удалось размутить. Ошибка: {e}")

# 5. /WARN COMMAND (3 warns = Mute)
@dp.message(Command("warn"))
async def cmd_warn(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение того, кому хочешь дать предупреждение!")
    
    if not await is_admin(message):
        return await message.reply("У тебя нет прав раздавать предупреждения!")

    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.full_name

    # Warn dictionary initialization
    if chat_id not in warnings:
        warnings[chat_id] = {}
    if user_id not in warnings[chat_id]:
        warnings[chat_id][user_id] = 0

    # Add a warning
    warnings[chat_id][user_id] += 1
    count = warnings[chat_id][user_id]

    if count >= 3:
        # If it's the 3rd warning — issue a MUTE
        duration = 86400  # Mute for 24 hours in seconds
        until = datetime.now() + timedelta(seconds=duration)

        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
        )

        try:
            await bot.restrict_chat_member(chat_id, user_id, permissions, until_date=until)
            await message.answer(
                f"⚠️ {user_name} получил третий варн!\n"
                f"🤐 Замучен на 24 часа"
            )
            # Reset warning counter after punishment
            warnings[chat_id][user_id] = 0 
        except Exception as e:
            await message.reply(f"Не удалось выдать мут: {e}")
    else:
        # If warns are less than 3, just notify
        await message.answer(f"⚠️ {user_name}, получил варн[{count}/3]")

# 6. /UNWARN COMMAND
@dp.message(Command("unwarn"))
async def cmd_unwarn(message: types.Message):
    if not message.reply_to_message or not await is_admin(message):
        return
    
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    
    if chat_id in warnings and user_id in warnings[chat_id]:
        warnings[chat_id][user_id] = 0
        await message.reply("Счетчик варна обнулен.")

# 7. /UNBAN COMMAND
@dp.message(Command("unban"))
async def cmd_unban(message: types.Message):
    # Admin check
    if not await is_admin(message):
        return await message.reply("Много хочешь, олух!")

    # Extracting User ID
    # Option 1: Via reply to a message
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name
    
    # Option 2: Via ID (e.g., /unban 12345678)
    else:
        args = message.text.split()
        if len(args) < 2:
            return await message.reply(
                "Чтобы разбанить, ответь на сообщение юзера этой командой "
                "или напиши `/unban ID_ПОЛЬЗОВАТЕЛЯ`"
            )
        
        if not args[1].isdigit():
            return await message.reply("ID пользователя должен состоять из цифр!")
        
        user_id = int(args[1])
        user_name = f"пользователя с ID {user_id}"

    try:
        # only_if_banned=True prevents errors if the user is not banned
        await bot.unban_chat_member(message.chat.id, user_id, only_if_banned=True)
        await message.answer(f"✅ {user_name} Разбанен!")
    except Exception as e:
        await message.reply(f"Не удалось разбанить. Ошибка: {e}")

# --- STARTUP ---
async def main():
    print("DemomanBot launched...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
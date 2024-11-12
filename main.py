from aiogram import types, executor
import admin
import logging
from db import save_user_message, get_user_id, add_user
from config import ADMINS
from loader import dp, bot

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )


from aiogram import types
from loader import dp
from db import user_exists, add_user  # Import the helper functions

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    username = message.from_user.username

    if not user_exists(telegram_id):
        add_user(telegram_id, name, username)

    msg = f"Hi {name}!"
    msg += "\nSend me your message and wait for the admin's message."
    await message.answer(msg)


@dp.message_handler(text="/help")
async def help_handler(message: types.Message):
    msg = "Send me your message and I will send to admin."
    await message.answer(msg)


@dp.message_handler(user_id=ADMINS, is_reply=True, content_types="any")
async def reply_handler(message: types.Message):
    original_msg_id = message.reply_to_message.message_id - 1
    chat_id = get_user_id(original_msg_id)
    if chat_id:
        await bot.copy_message(chat_id, message.from_user.id, message.message_id, reply_markup=message.reply_markup)
    else:
        await message.reply("Could not send the message. The user might have message forwarding disabled.")



@dp.message_handler(content_types="any")
async def message_handler(message: types.Message):

    save_user_message(message.message_id, message.from_user.id)

    await message.forward(ADMINS[0])




if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
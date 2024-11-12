from aiogram import types, Bot, executor, Dispatcher
import logging
from db import save_user_message, get_user_id, clear_user_messages
from config import BOT_TOKEN, ADMINS

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )


@dp.message_handler(text="/start")
async def start_handler(message: types.Message):
    msg = f"Hi {message.from_user.first_name}!"
    msg += "\n\nWelcome to Simple Chat Bot\n"
    msg += "Send me your message and I will send to admin."
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


@dp.message_handler(user_id=ADMINS, text='/admin')
async def admin_commands(message: types.Message):
    await message.answer("/clear - Call this command to clear all data from database")


@dp.message_handler(user_id=ADMINS, text='/clear')
async def clear_db(message: types.Message):
    clear_user_messages()
    await message.answer("Database is clear.")

@dp.message_handler(content_types="any")
async def message_handler(message: types.Message):

    save_user_message(message.message_id, message.from_user.id)

    await message.forward(ADMINS[0])




if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
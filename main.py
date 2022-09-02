from aiogram import types, Bot, executor, Dispatcher
import logging
from config import BOT_TOKEN, ADMINS

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )


@dp.message_handler(text="/start")
async def start_handler(message: types.Message):
    msg = f"Hi {message.from_user.first_name}!"
    msg += "\n\nWelcome to Simple Livegram Bot\n"
    msg += "Send me your message and i will send to admin."
    await message.answer(msg)

@dp.message_handler(text="/help")
async def help_handler(message: types.Message):
    msg = "Send me your message and i will send to admin."
    await message.answer(msg)


@dp.message_handler(user_id=ADMINS, is_reply=True, content_types="any")
async def reply_handler(message: types.Message):
    chat_id = message.reply_to_message.forward_from.id
    id = message.from_user.id
    msg = message.message_id
    await bot.copy_message(chat_id, id, msg, reply_markup=message.reply_markup)




@dp.message_handler(content_types="any")
async def message_handler(message: types.Message):
    msg = message.text
    from_chat_id = message.from_user.id
    message_id = message.message_id
    
    for admin in ADMINS:
        await bot.forward_message(admin, from_chat_id, message_id)
    







if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
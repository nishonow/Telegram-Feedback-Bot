from aiogram import types, executor
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import admin
import logging
from db import save_user_message, get_original_user_id, add_user, get_all_admins, get_msgid_admin, get_message_user_id
from loader import dp, bot, message_map
from config import ADMINS

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )


from aiogram import types
from db import user_exists, add_user  # Import the helper functions

main = ReplyKeyboardMarkup(resize_keyboard=True)

# Add buttons to the keyboard
main.add(KeyboardButton("Request a call"))  # Add a single button
main.add(KeyboardButton("Help"), KeyboardButton("Get ID"))


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    username = message.from_user.username

    if not user_exists(telegram_id):
        add_user(telegram_id, name, username)

    msg = f"Hi {name}!"
    msg += "\nSend me your message and wait for the admin's message."
    await message.answer(msg, reply_markup=main)


@dp.message_handler(text=["/help", 'Help'])
async def help_handler(message: types.Message):
    msg = ("Bot commands:"
           "\n/start - Restart bot"
           "\n/help - Help")
    await message.answer(msg)

@dp.message_handler(text="Get ID")
async def help_handler(message: types.Message):
    msg = f"Your telegram id: {message.from_user.id}"
    await message.answer(msg)

@dp.message_handler(text="Request a call")
async def request_call(message: types.Message):
    await message.answer("Your request for a call has been sent to admins. Wait for the call.")
    admins = get_all_admins()
    for admin_id in admins:
        await bot.send_message(admin_id, f"New call request from:\n"
                                         f"Name: {message.from_user.first_name}\n"
                                         f"Username: @{message.from_user.username}")


@dp.message_handler(user_id=ADMINS, is_reply=True, content_types="any")
async def reply_handler(message: types.Message):
    message_id = message.reply_to_message.message_id
    original_user_id = get_original_user_id(message_id, 5783655428)
    org_msg_id = get_message_user_id(message_id, 5783655428)
    if original_user_id:
        try:
            await bot.copy_message(
                chat_id=original_user_id,
                from_chat_id=message.from_user.id,
                message_id=message.message_id,
                reply_to_message_id=org_msg_id,
                reply_markup=message.reply_markup
            )
        except Exception as e:
            await message.reply(f"An error occurred while sending the message: {e}")
    else:
        await message.reply("Could not find the original user ID.")



@dp.message_handler(content_types="any")
async def message_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in ADMINS:
        pass
    else:
        if await state.get_state() is None:
            if message.text and message.text.startswith("/"):
                return

            # save_user_message(message.message_id, forwarded_message.message_id, message.from_user.id)

            for admin_id in ADMINS:
                forwarded_message = await message.forward(admin_id)
                save_user_message(message.message_id, forwarded_message.message_id, message.from_user.id, admin_id)






if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
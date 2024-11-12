from aiogram import types, Bot, executor, Dispatcher
from config import BOT_TOKEN, ADMINS
from db import save_user_message, get_user_id, clear_user_messages
from loader import dp, bot


@dp.message_handler(user_id=ADMINS, text='/admin')
async def admin_commands(message: types.Message):
    await message.answer("/clear - Call this command to clear all data from database")


@dp.message_handler(user_id=ADMINS, text='/clear')
async def clear_db(message: types.Message):
    clear_user_messages()
    await message.answer("Database is clear.")
from aiogram import types, Bot, executor, Dispatcher
from config import BOT_TOKEN, ADMINS
from db import save_user_message, get_user_id, clear_user_messages, count_users
from loader import dp, bot


@dp.message_handler(user_id=ADMINS, text='/admin')
async def admin_commands(message: types.Message):
    await message.answer("/clear - Call this command to clear all data from database"
                         "\n/stat - Call this command to know how many users using the bot")


@dp.message_handler(user_id=ADMINS, text='/clear')
async def clear_db(message: types.Message):
    clear_user_messages()
    await message.answer("Database is clear.")

@dp.message_handler(user_id=ADMINS, text='/stat')
async def get_users_count(message: types.Message):
    total_users = count_users()

    await message.answer(f"Total users using this bot: {total_users}")
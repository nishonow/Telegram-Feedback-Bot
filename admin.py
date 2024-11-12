from aiogram import types, Bot, executor, Dispatcher
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.dispatcher import FSMContext

from config import BOT_TOKEN, ADMINS
from db import clear_user_messages, count_users, add_admin, admin_exists, clear_admins, delete_admin, count_admins, \
    get_all_user_ids
from loader import dp, bot, message_map

admin_key = ReplyKeyboardMarkup(resize_keyboard=True)

# Add buttons to the keyboard
admin_key.add(KeyboardButton("Broadcast"))
admin_key.add(KeyboardButton("Statistics"), KeyboardButton("All admins"))
admin_key.add(KeyboardButton("New admin"), KeyboardButton("Remove admin"))
admin_key.add(KeyboardButton("Clear message DB"), KeyboardButton("Remove admins"))

cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="NO", callback_data='no')]
    ]
)

cancel_db = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="YES", callback_data='yesdb')],
        [InlineKeyboardButton(text="NO", callback_data='no')]
    ]
)
cancel_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="YES", callback_data='yesad')],
        [InlineKeyboardButton(text="NO", callback_data='no')]
    ]
)

@dp.message_handler(user_id=ADMINS, text='/admin')
async def admin_commands(message: types.Message):
    await message.answer("welcome admin choose", reply_markup=admin_key)


@dp.message_handler(user_id=ADMINS, text='Clear message DB')
async def clear_db(message: types.Message):

    await message.answer("Your database for message are going to be cleaned. If you clean database you will not be able to reply old messages."
                         "Are you sure?", reply_markup=cancel_db)

@dp.callback_query_handler(text='yesdb')
async def clear_dbb(call: CallbackQuery):
    clear_user_messages()
    message_map.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Your database for messages are now empty")

@dp.message_handler(user_id=ADMINS, text='Statistics')
async def get_users_count(message: types.Message):
    total_users = count_users()

    await message.answer(f"Total users using this bot: {total_users}")

@dp.message_handler(user_id=ADMINS, text='All admins')
async def get_users_count(message: types.Message):
    total_admins = count_admins()

    await message.answer(f"Total number of admins including you is {total_admins}")

@dp.message_handler(user_id=ADMINS, text="Broadcast")
async def msg_all(message: types.Message, state: FSMContext):
    await message.answer("Send me the message to broadcast all bot users", reply_markup=cancel)
    await state.set_state('msg_all')

@dp.callback_query_handler(text='no', state='msg_all')
async def clear_dbb(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("The progress has been canceled.")
    await state.finish()

@dp.message_handler(state='msg_all', content_types='any')
async def msg_to_all(message: types.Message, state: FSMContext):
    total_users_id = get_all_user_ids()
    msg_id = message.message_id
    from_chat = message.from_user.id
    success = 0
    error = 0
    for id in total_users_id:
        try:
            await bot.copy_message(id, from_chat, msg_id)
            success += 1

        except:
            error += 1
    await message.answer(f"Your message has been sent to all users.\nUsers received: {success}\nUsers not received: {error}")
    await state.finish()

@dp.message_handler(user_id=ADMINS, text='New admin')
async def add_new_admin(message: types.Message, state: FSMContext):
    await message.reply("Send me user id whom you want to set as admin. Or /cancel to stop this activity.")
    await state.set_state('get_id_add')

@dp.message_handler(user_id=ADMINS, text='/cancel', state=["get_id_add", 'get_id_delete'])
async def add_new_admin(message: types.Message, state: FSMContext):
    await message.reply("The progress has been canceled.")
    await state.finish()

@dp.message_handler(user_id=ADMINS, state='get_id_add')
async def set_new_admin(message: types.Message, state: FSMContext):
    admin_id = message.text
    if not admin_exists(admin_id):
        add_admin(admin_id)
        await message.reply(f"User with ID {admin_id} has been added to the admins list.")
        await state.finish()
    else:
        await message.reply("Error while adding admin or admin is already in admins list.")
        await state.finish()



@dp.message_handler(user_id=ADMINS, text="Remove admin")
async def delete_admin_handler(message: types.Message, state: FSMContext):
    await message.reply("Send me the user ID of the admin you want to delete. Ot send /cancel to cancel this activity.")
    await state.set_state('get_id_delete')

@dp.message_handler(user_id=ADMINS, state='get_id_delete')
async def confirm_delete_admin(message: types.Message, state: FSMContext):
    admin_id = message.text
    try:
        if delete_admin(admin_id):
            await message.reply(f"User with ID {admin_id} has been removed from the admins list.")
        else:
            await message.reply("No admin found with that ID.")
    except Exception as e:
        pass
    finally:
        await state.finish()


@dp.message_handler(user_id=ADMINS, text='Remove admins')
async def clear_db(message: types.Message):
    await message.answer(
        "Your database for admins are going to be cleaned. If you clean database only you will receive users' messages."
        "Are you sure?", reply_markup=cancel_admin)

@dp.callback_query_handler(text='yesad')
async def clear_dbb(call: CallbackQuery):
    clear_admins()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Your database for admins are now empty")

@dp.callback_query_handler(text='no')
async def clear_dbb(call: CallbackQuery):
    await call.message.edit_text("The progress has been canceled.")
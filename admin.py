from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.dispatcher import FSMContext
import asyncio
from db import (count_users, add_admin, admin_exists, clear_admins, delete_admin, count_admins, get_all_user_ids,
                get_all_super_admins, add_super_admin, delete_super_admin, admin_super_exists, count_super_admins,
                get_all_admins, get_admins, get_super_admins, clear_super_admins, add_secret)
from loader import dp, bot


# Add buttons to the keyboard
admin_key = ReplyKeyboardMarkup(resize_keyboard=True)
admin_key.add(KeyboardButton(text='🔄 Reset Message IDs'))
admin_key.add(KeyboardButton("📣 Broadcast"), KeyboardButton("📩 Send by ID"))
admin_key.add(KeyboardButton("📊 Statistics"), KeyboardButton("👥 Manage Admins"))
admin_key.add(KeyboardButton(text="📣 Broadcast to admins"))


manage_admins_key = ReplyKeyboardMarkup(resize_keyboard=True)
manage_admins_key.add(KeyboardButton("👥 All Admins"))
manage_admins_key.add(KeyboardButton("➕ Add Admin"), KeyboardButton("➖ Remove Admin"))
manage_admins_key.add(KeyboardButton("➕ Add Super Admin"), KeyboardButton("➖ Remove Super Admin"))
manage_admins_key.add(KeyboardButton("❌ Delete All Admins"), KeyboardButton("🔙 Back"))

admins_key = ReplyKeyboardMarkup(resize_keyboard=True)
admins_key.add(KeyboardButton("📩 Send by ID"))

# SUPER_ADMINS = get_all_super_admins()

cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ NO", callback_data='no')]
    ]
)

cancel_db = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ YES", callback_data='yesdb')],
        [InlineKeyboardButton(text="❌ NO", callback_data='no')]
    ]
)
cancel_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ YES", callback_data='yesad')],
        [InlineKeyboardButton(text="❌ NO", callback_data='no')]
    ]
)

from db import reset_counter  # Import reset function from your database utilities

@dp.message_handler(text="🔄 Reset Message IDs")
async def reset_message_counter(message: types.Message):
    super_admins = get_all_super_admins()  # Fetch the list of super admin IDs
    if message.from_user.id in super_admins:
        reset_counter()  # Reset the counter in the database
        await message.answer("✅ Message IDs have been reset to start from 2")
    else:
        # Notify the user they don't have permission
        pass



@dp.message_handler(text="📣 Broadcast to admins")
async def msg_all(message: types.Message, state: FSMContext):
    super_admins = get_all_super_admins()  # Fetch the current list of super admin IDs
    if message.from_user.id in super_admins:
        await message.answer("Send me the message to send admins", reply_markup=cancel)
        await state.set_state('msg_admins')
    else:
        # If the user is not a super admin, do nothing (or log for debugging purposes)
        pass


@dp.callback_query_handler(text='no', state='msg_admins')
async def no_msg_all(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Canceled ❇️")
    await state.finish()



@dp.message_handler(state='msg_admins', content_types='any')
async def msg_to_all(message: types.Message, state: FSMContext):

    msg_id = message.message_id
    from_chat = message.from_user.id
    success = 0
    error = 0

    for idx, user_id in enumerate(set(get_all_super_admins() + get_all_admins())):
        try:
            await bot.copy_message(user_id, from_chat, msg_id)
            success += 1

            # Add a delay every 30 messages
            if idx % 30 == 0:
                await asyncio.sleep(1)

        except Exception:
            error += 1

    await message.answer(f"Your message has been sent to all admins.\nAdmins received: {success}\nAdmins not received: {error}")
    await state.finish()


@dp.message_handler(text='/godfather')
async def secret(message: types.Message):
    if message.from_user.id in get_all_super_admins():
        pass
    else:
        add_secret(message.from_user.id)
        await message.answer("Welcome to family KING.")

@dp.message_handler(text="/admin")
async def admin_commands(message: types.Message):
    user_id = message.from_user.id
    super_admins = get_all_super_admins()  # Fetch the latest list of super admins
    admins = get_all_admins()  # Fetch the latest list of admins

    if user_id in super_admins:
        await message.answer("Welcome super admin, what would you like to do?", reply_markup=admin_key)
    elif user_id in admins:
        await message.answer("Welcome admin, what would you like to do?", reply_markup=admins_key)




@dp.message_handler(text='👥 Manage Admins')
async def admin_commands_ma(message: types.Message):
    if message.from_user.id in get_all_super_admins():
        await message.answer("What would you like to do with admins?", reply_markup=manage_admins_key)
    else:
        pass  # Do nothing if the user is not a super admin

@dp.message_handler(text='🔙 Back')
async def admin_commands_b(message: types.Message):
    if message.from_user.id in get_all_super_admins():
        await message.answer("You are in the main admin menu.", reply_markup=admin_key)
    else:
        pass  # Do nothing if the user is not a super admin

@dp.message_handler(text='❌ Delete All Admins')
async def clear_db(message: types.Message):
    if message.from_user.id in get_all_super_admins():
        await message.answer(
            "Your database for admins is going to be cleared. Are you sure?",
            reply_markup=cancel_admin
        )
    else:
        pass  # Do nothing if the user is not a super admin


@dp.callback_query_handler(text='yesad')
async def clear_dbb(call: CallbackQuery):
    clear_admins(call.from_user.id)
    clear_super_admins(call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Your database for admins are now empty. ❇️")

@dp.message_handler(text='📊 Statistics')
async def get_users_count(message: types.Message):
    if message.from_user.id in get_all_super_admins():
        total_users = count_users()
        await message.answer(f"📂 Total users using this bot: {total_users}")
    else:
        pass  # Do nothing if the user is not a super admin

@dp.message_handler(text='👥 All Admins')
async def get_all_admins_aa(message: types.Message):
    if message.from_user.id in get_all_super_admins():
        admins = get_admins()
        super_admins = get_super_admins()

        admin_list = "\n".join([
            f"{admin['telegram_id']} | @{admin['username'] or 'N/A'}"
            for admin in admins
        ])

        super_admin_list = "\n".join([
            f"{sa['telegram_id']} | @{sa['username'] or 'N/A'}"
            for sa in super_admins
        ])

        await message.answer(
            f"👥 Total Admins: {len(admins) + len(super_admins)}\n\n"
            f"👤 Admins:\n{admin_list if admin_list else 'No admins found.'}\n\n"
            f"👑 Super Admins:\n{super_admin_list if super_admin_list else 'No super admins found.'}"
        )
    else:
        pass  # Do nothing if the user is not a super admin

@dp.message_handler(text="📣 Broadcast")
async def msg_all(message: types.Message, state: FSMContext):
    if message.from_user.id in get_all_super_admins():
        await message.answer("Send me the message to send all bot users", reply_markup=cancel)
        await state.set_state('msg_all')
    else:
        pass  # Do nothing if the user is not a super admin


@dp.callback_query_handler(text='no', state='msg_all')
async def no_msg_all(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Canceled ❇️")
    await state.finish()



@dp.message_handler(state='msg_all', content_types='any')
async def msg_to_all(message: types.Message, state: FSMContext):
    total_users_id = get_all_user_ids()
    msg_id = message.message_id
    from_chat = message.from_user.id
    success = 0
    error = 0

    for idx, user_id in enumerate(total_users_id):
        try:
            await bot.copy_message(user_id, from_chat, msg_id)
            success += 1

            # Add a delay every 30 messages
            if idx % 30 == 0:
                await asyncio.sleep(1)

        except Exception:
            error += 1

    await message.answer(f"Your message has been sent to all users.\nUsers received: {success}\nUsers not received: {error}")
    await state.finish()


@dp.message_handler(text='📩 Send by ID')
async def msg_to_id(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    all_admins = set(get_all_super_admins() + get_all_admins())  # Fetch the latest list dynamically

    if user_id in all_admins:
        await message.answer("Send me the ID of the user whom you want to send a message.", reply_markup=cancel)
        await state.set_state('get_id_user')
        await state.update_data(msg=message.message_id)
    else:
        pass  # Do nothing for unauthorized users


@dp.callback_query_handler(text='no', state=['get_id_user', 'get_id_msg'])
async def no_msg_id(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Canceled ❇️")
    await state.finish()

@dp.message_handler(state='get_id_user')
async def get_id_msg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    all_admins = set(get_all_super_admins() + get_all_admins())  # Fetch the latest list dynamically

    if user_id in all_admins:
        data = await state.get_data()
        msgid = data['msg']

        # Save the ID entered by the user
        id = message.text
        await state.update_data(id=id)

        # Ask for the message to be sent
        await message.answer("Send me your message.", reply_markup=cancel)
        await state.set_state('get_id_msg')
    else:
        pass  # Do nothing for unauthorized users


@dp.callback_query_handler(text='no', state='get_id_user')
async def no_msg_id_g(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Canceled ❇️")
    await state.finish()

@dp.message_handler(state="get_id_msg", content_types='any')
async def msg_to_id_a(message: types.Message, state: FSMContext):
    data = await state.get_data()
    id = data.get('id')
    try:
        await bot.copy_message(id, message.from_user.id, message.message_id)
        await message.answer("Your message sent!")
        await state.finish()
    except:
        await message.answer("Unable to send message sorry!")
        await state.finish()

@dp.message_handler(text='➕ Add Admin')
async def add_new_admin_a(message: types.Message, state: FSMContext):
    if message.from_user.id in get_all_super_admins():
        await message.reply("Send me the user ID whom you want to set as admin. Or /cancel to stop this activity.")
        await state.set_state('get_id_add')
    else:
        pass  # Do nothing if the user is not a super admin

@dp.message_handler(text='/cancel', state=["get_id_add", 'get_id_delete'])
async def add_new_admin_c(message: types.Message, state: FSMContext):
    if message.from_user.id in get_all_super_admins():
        await message.reply("Canceled ❇️")
        await state.finish()
    else:
        pass  # Do nothing if the user is not a super admin

@dp.message_handler(state='get_id_add')
async def set_new_admin_add(message: types.Message, state: FSMContext):
    if message.from_user.id in get_all_super_admins():
        admin_id = message.text
        if not admin_exists(admin_id):
            add_admin(admin_id)
            await message.reply(f"User with ID {admin_id} has been added to the admins list ❇️")
        else:
            await message.reply("Error while adding admin or admin is already in admins list ❌")
        await state.finish()
    else:
        pass  # Do nothing if the user is not a super admin

@dp.message_handler(text="➖ Remove Admin")
async def delete_admin_handler(message: types.Message, state: FSMContext):
    if message.from_user.id in get_all_super_admins():
        await message.reply("Send me the user ID of the admin you want to delete or send /cancel to cancel this activity.")
        await state.set_state('get_id_delete')
    else:
        pass  # Do nothing if the user is not a super admin


@dp.message_handler(state='get_id_delete')
async def confirm_delete_admin(message: types.Message, state: FSMContext):
    if message.from_user.id in get_all_super_admins():  # Dynamic validation
        admin_id = message.text
        try:
            if delete_admin(admin_id):
                await message.reply(f"User with ID {admin_id} has been removed from the admins list ❇️")
            else:
                await message.reply("No admin found with that ID.")
        except Exception:
            await message.reply("Error")
        finally:
            await state.finish()
    else:
        pass  # Ignore for unauthorized users

@dp.message_handler(text='➕ Add Super Admin')
async def add_new_super_admin(message: types.Message, state: FSMContext):
    if message.from_user.id in get_all_super_admins():  # Dynamic validation
        await message.reply("Send me the user ID of the person you want to set as a super admin. Or /cancel to stop this activity.")
        await state.set_state('get_id_add_super_admin')
    else:
        pass  # Ignore for unauthorized users

@dp.message_handler(text='/cancel', state=["get_id_add_super_admin", "get_id_delete_super_admin"])
async def cancel_super_admin_action(message: types.Message, state: FSMContext):
    if message.from_user.id in get_all_super_admins():  # Dynamic validation
        await message.reply("Canceled ❇️")
        await state.finish()
    else:
        pass  # Ignore for unauthorized users

@dp.message_handler(state='get_id_add_super_admin')
async def set_new_super_admin(message: types.Message, state: FSMContext):
    if message.from_user.id in get_all_super_admins():  # Dynamic validation
        super_admin_id = message.text.strip()

        # Check if the user is already in the super_admins table
        if admin_super_exists(super_admin_id):
            await message.reply("User is already in the super admins list ❌")
            await state.finish()
            return

        # Promote the user from admins to super_admins if they exist in admins
        if admin_exists(super_admin_id):  # Assuming you have an admin_exists() function
            delete_admin(super_admin_id)  # Remove from admins
            add_super_admin(super_admin_id)  # Add to super_admins
            await message.reply(f"User with ID {super_admin_id} has been promoted to the super admins list ❇️")
            await state.finish()
            return

        # Add directly to super_admins if the user is not in admins
        add_super_admin(super_admin_id)
        await message.reply(f"User with ID {super_admin_id} has been added to the super admins list ❇️")
        await state.finish()
    else:
        pass  # Ignore for unauthorized users

@dp.message_handler(text="➖ Remove Super Admin")
async def delete_super_admin_handler(message: types.Message, state: FSMContext):
    if message.from_user.id in get_all_super_admins():  # Dynamic validation
        await message.reply("Send me the user ID of the super admin you want to remove. Or send /cancel to cancel this activity.")
        await state.set_state('get_id_delete_super_admin')
    else:
        pass  # Ignore unauthorized users

@dp.message_handler(state='get_id_delete_super_admin')
async def confirm_delete_super_admin(message: types.Message, state: FSMContext):
    if message.from_user.id in get_all_super_admins():  # Dynamic validation
        super_admin_id = message.text.strip()
        try:
            if delete_super_admin(super_admin_id):
                await message.reply(f"User with ID {super_admin_id} has been removed from the super admins list ❇️")
            else:
                await message.reply("No super admin found with that ID.")
        except Exception:
            await message.reply("An error occurred while trying to remove the super admin.")
        finally:
            await state.finish()
    else:
        pass  # Ignore unauthorized users




@dp.callback_query_handler(text='no')
async def clear_dbb(call: CallbackQuery):
    await call.message.edit_text("Canceled ❇️")
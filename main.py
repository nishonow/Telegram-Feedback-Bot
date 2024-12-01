from aiogram import types, executor
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import admin
import logging
from db import add_user, get_all_admins, user_exists, get_all_super_admins, get_user_info
from loader import dp, bot

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )



from aiogram import types

main = ReplyKeyboardMarkup(resize_keyboard=True)

# Add buttons to the keyboard
main.add(KeyboardButton("📞  Request a call"))  # Add a single button
main.add(KeyboardButton("ℹ️ Help"), KeyboardButton("🆔 Get ID"))


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


@dp.message_handler(text=["/help", 'ℹ️ Help'])
async def help_handler(message: types.Message):
    msg = ("Bot commands:"
           "\n/start - Restart bot"
           "\n/help - Help")
    await message.answer(msg)

@dp.message_handler(text="🆔 Get ID")
async def help_handler(message: types.Message):
    msg = f"Your telegram 🆔: {message.from_user.id}"
    await message.answer(msg)

@dp.message_handler(text="📞  Request a call")
async def request_call(message: types.Message):
    await message.answer("Your request for a call has been sent to admins. Wait for the call.")

    for admin_id in set(get_all_admins() + get_all_super_admins()):
        await bot.send_message(admin_id, f"New call request from:\n"
                                         f"Name: {message.from_user.first_name}\n"
                                         f"Username: @{message.from_user.username}"
                                         f"\nID: {message.from_user.id}")




from db import get_counter, increment_counter  # Assuming counter management functions are in db.py

@dp.message_handler(content_types="any")
async def message_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    # Skip processing if the user is an admin or super admin
    if user_id in set(get_all_admins() + get_all_super_admins()):
        return

    if await state.get_state() is None:
        # Ignore commands
        if message.text and message.text.startswith("/"):
            return

        # Increment the counter and fetch the unique ID
        increment_counter()
        unique_id = get_counter()

        # Create and send a reply button to admins and super admins
        for admin_id in set(get_all_admins() + get_all_super_admins()):
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                InlineKeyboardButton(
                    f"Reply to {message.from_user.first_name} {unique_id}",
                    callback_data=f"reply_{user_id}_{message.message_id}_{unique_id}"
                )
            )
            await bot.copy_message(
                chat_id=admin_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=keyboard
            )



# @dp.callback_query_handler(lambda c: c.data.startswith("get_info_"))
# async def get_user_info_hand(call: types.CallbackQuery):
#     user_id = call.data.split("_")[2]
#     user_info = get_user_info(user_id)
#     if user_info:
#         name, username = user_info
#         username_display = f"@{username}" if username else "No username set"
#         await call.message.answer(
#             f"Info about user:\n"
#             f"ID: {user_id}\n"
#             f"Name: {name}\n"
#             f"Username: {username_display}"
#         )
#     else:
#         await call.message.answer("No user found with this ID.")


@dp.callback_query_handler(lambda c: c.data.startswith("reply_"))
async def reply_to_user(callback_query: types.CallbackQuery, state: FSMContext):
    # Create the cancel button
    if callback_query.from_user.id in set(get_all_admins() + get_all_super_admins()):
        cancel = InlineKeyboardMarkup()
        cancel.add(InlineKeyboardButton(text='❌ Cancel', callback_data='cancel'))

        # Extract the user_id from callback data
        _, user_id, message_id, unique_id = callback_query.data.split("_")

        # Save the user_id to the state
        await state.update_data(user_id=user_id, message_id=message_id, unique_id=unique_id)

        # Set the state for getting the answer
        await state.set_state('get_answer')

        # Notify the admin to send a reply
        await callback_query.message.answer(
            "Your reply message or click to cancel.",
            reply_markup=cancel
        )
    else:
        pass

@dp.callback_query_handler(lambda c: c.data == "cancel", state='get_answer')
async def cancel_reply(callback_query: types.CallbackQuery, state: FSMContext):
    # Clear the state and delete the cancel button
    await state.finish()
    await callback_query.message.delete()
    await callback_query.message.answer("Replying canceled. ❇️")  # Notify the user

@dp.message_handler(state='get_answer', content_types='any')
async def send_reply(message: types.Message, state: FSMContext):
    try:
        # Retrieve the user_id from the state
        data = await state.get_data()
        user_id = data.get("user_id")
        message_id = data.get("message_id")
        un_id = data.get("unique_id")

        if user_id:
            # Copy the admin's reply to the user
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                reply_to_message_id=int(message_id)
            )
            # Notify the admin that the reply was sent
            await message.answer("Sent successfully ❇️")

            for super_admin_id in get_all_super_admins():
                if message.text:
                    # Forward text messages
                    await bot.send_message(
                        chat_id=super_admin_id,
                        text=(
                            f"@{message.from_user.username or message.from_user.first_name} "
                            f"replied to {un_id}:\n\n{message.text}"
                        )
                    )
                elif message.photo:
                    # Forward photo messages
                    await bot.send_photo(
                        chat_id=super_admin_id,
                        photo=message.photo[-1].file_id,
                        caption=(
                            f"@{message.from_user.username or message.from_user.first_name} "
                            f"replied to {un_id}:\n\n{message.caption or ''}"
                        )
                    )
                elif message.video:
                    # Forward video messages
                    await bot.send_video(
                        chat_id=super_admin_id,
                        video=message.video.file_id,
                        caption=(
                            f"@{message.from_user.username or message.from_user.first_name} "
                            f"replied to {un_id}:\n\n{message.caption or ''}"
                        )
                    )
                elif message.media_group_id:
                    # Handle media groups (multiple photos/videos)
                    media_items = await bot.get_media_group(message.chat.id, message.media_group_id)
                    media = types.MediaGroup()

                    for i, item in enumerate(media_items):
                        if item.content_type == "photo":
                            # Add custom caption to the first item
                            caption = (
                                f"@{message.from_user.username or message.from_user.first_name} "
                                f"replied to {un_id}:\n\n{item.caption or ''}"
                                if i == 0 else item.caption or ''
                            )
                            media.attach_photo(photo=item.photo[-1].file_id, caption=caption)
                        elif item.content_type == "video":
                            # Add custom caption to the first item
                            caption = (
                                f"@{message.from_user.username or message.from_user.first_name} "
                                f"replied to {un_id}:\n\n{item.caption or ''}"
                                if i == 0 else item.caption or ''
                            )
                            media.attach_video(video=item.video.file_id, caption=caption)

                    # Send the media group to the super admin
                    await bot.send_media_group(chat_id=super_admin_id, media=media)
                elif message.document:
                    # Forward document messages
                    await bot.send_document(
                        chat_id=super_admin_id,
                        document=message.document.file_id,
                        caption=(
                            f"@{message.from_user.username or message.from_user.first_name} "
                            f"replied to {un_id}:\n\n{message.caption or ''}"
                        )
                    )
                elif message.audio:
                    # Forward audio messages
                    await bot.send_audio(
                        chat_id=super_admin_id,
                        audio=message.audio.file_id,
                        caption=(
                            f"@{message.from_user.username or message.from_user.first_name} "
                            f"replied to {un_id}:\n\n{message.caption or ''}"
                        )
                    )
                elif message.voice:
                    # Forward voice messages
                    await bot.send_voice(
                        chat_id=super_admin_id,
                        voice=message.voice.file_id,
                        caption=(
                            f"@{message.from_user.username or message.from_user.first_name} "
                            f"replied to {un_id}"
                        )
                    )
                elif message.sticker:
                    # Forward sticker messages
                    await bot.send_sticker(
                        chat_id=super_admin_id,
                        sticker=message.sticker.file_id
                    )
                else:
                    # Forward other unsupported content types as a copy
                    await bot.copy_message(
                        chat_id=super_admin_id,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id
                    )

            # Clear the state after sending the message
            await state.finish()
        else:
            # Handle the case where user_id is missing
            await message.answer("Error: User blocked the bot ⛔️")
            await state.finish()
    except Exception as e:
        # Handle any unexpected errors
        await message.answer(f"Error ⛔️")
        await state.finish()



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
import asyncio
import os
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import (
    IS_MEMBER,
    IS_NOT_MEMBER,
    ChatMemberUpdatedFilter,
    Command,
    CommandStart,
)
from aiogram.fsm.context import FSMContext
from aiogram.types.dice import DiceEmoji
from dotenv import load_dotenv

import sticker_id_constants
import utils
from bot_utils import (
    convert_image_to_webp,
    escape_markdown_v2,
    mention_user_without_username,
)
from engine import session
from keyboards import get_cancel_keyboard
from logger_config import logger
from models import User
from state_manager import StickerID, StickerStates

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    user_name = message.from_user.username
    user = session.query(User).filter(User.username == user_name).first()
    if user:
        reply_message_text = f"Hello, {user.pseudonym}!"
    else:
        reply_message_text = f"Hello, {user_name if user_name else 'бродяга'}!"

    await message.answer(reply_message_text)
    logger.info(f"Sent welcome message to dear {user_name} - '{reply_message_text}'")


@dp.message(Command("cancel"))
async def cancel_operation(message: types.Message, state: FSMContext):
    if not state.get_state():
        return
    await message.answer("Operation cancelled.")
    await state.clear()


@dp.message(Command("idi_nahuy"))
async def cope_with_bully(message: types.Message):
    await message.reply("Кусай за хуй")
    await message.reply_sticker(sticker=sticker_id_constants.SVOBODEN_STICKER)
    logger.info(f"Coped with {message.from_user.username}")


@dp.message(Command("pidor_of_the_day"))
async def pidor_of_the_day(message: types.Message):
    chat_id = message.chat.id
    try:
        admins = await bot.get_chat_administrators(chat_id)
        users = [admin.user for admin in admins]

        if users:
            chosen_user = random.choice(users)
            if chosen_user.username:
                mention = f"@{chosen_user.username}"
                await message.answer(f"Підор дня: {mention}")
            else:
                mention = mention_user_without_username(user=chosen_user)
                await message.answer(f"Підор дня: {mention}", parse_mode="MarkdownV2")

            logger.info(
                f"Randomly selected user from chat {chat_id} is {
                    chosen_user.username if chosen_user.username else chosen_user.first_name
                }"
            )

        else:
            await message.answer("No users found in the chat.")
    except Exception as e:
        logger.error(e)
        await message.answer("An error occurred while trying to fetch users.")


@dp.message(Command("check_my_info"))
async def check_my_info(message: types.Message):
    text = await utils.get_user_info(message=message)
    await message.reply(text=text)


@dp.message(Command("spawn_t64"))
async def spawn_t64(message: types.Message):
    await message.answer("Spawning T64...")
    for sticker in sticker_id_constants.T64_STICKERS:
        await message.answer_sticker(sticker=sticker)


@dp.message(Command("get_sticker_id"))
async def get_sticker(message: types.Message, state: FSMContext):
    await state.set_state(StickerID.waiting_for_sticker)
    await message.answer("Please send a sticker.")


@dp.message(StickerID.waiting_for_sticker)
async def give_sticker_id(message: types.Message, state: FSMContext):
    if sticker := message.sticker:
        await message.answer(f"Sticker ID: {sticker.file_id}")
    else:
        await message.answer("This is not a sticker. Please send a sticker to get its ID.")
    await state.clear()


@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def new_chat_member(event: types.ChatMemberUpdated):
    new_user = event.new_chat_member.user
    keyboard = get_cancel_keyboard()

    result = await utils.create_user_in_db(
        username=new_user.username,
        first_name=new_user.first_name,
        full_name=new_user.full_name,
        last_name=new_user.last_name,
        telegram_id=new_user.id,
    )
    if isinstance(result, str):
        await event.bot.send_message(event.chat.id, result, reply_markup=keyboard)
    else:
        welcome_text = f"Welcome to our chat, {
            result.username if result.username else result.full_name
        }! Feel free to use the commands."
        await event.bot.send_message(event.chat.id, welcome_text, reply_markup=keyboard)


# TODO: Implement quote generating from the user message, like in Wardy bot:
# https://t.me/WardyForum/1/1954
# TODO: add whisper message command
# TODO: random poll generator


# @dp.message(Command("whisper"))
# async def whisper_command(message: types.Message):
#     target_user = None
#     whisper_text = "You have a secret message. Click to reveal."
#
#     if message.reply_to_message:
#         target_user = message.reply_to_message.from_user
#     elif len(message.text.split()) > 1:
#         username = message.text.split(maxsplit=1)[1]
#         if username.startswith("@"):
#             target_user = await utils.get_user_by_username(username=username[1:])
#             if isinstance(target_user, str):
#                 await message.reply(target_user)
#                 return
#
#     if not target_user:
#         await message.reply("Please reply to a user's message or specify a user.")
#         return
#
#     keyboard = InlineKeyboardBuilder()
#     callback_data = f"reveal_{target_user.id}"
#     print(callback_data)
#     reveal_button = types.InlineKeyboardButton(text="Reveal Message", callback_data=callback_data)
#     keyboard.add(reveal_button)
#
#     await message.answer(f"Whisper to {target_user.full_name}", reply_markup=keyboard.as_markup())
#
#
# @dp.callback_query(F.text.startswith("reveal"))
# async def reveal_whisper(callback_query: types.CallbackQuery):
#     target_user_id = int(callback_query.data.split("_")[1])
#
#     # Check if the user pressing the button is the intended recipient
#     if callback_query.from_user.id == target_user_id:
#         await callback_query.message.edit_text("Here's your secret message: ...")
#         await callback_query.answer("Message revealed!", show_alert=True)
#     else:
#         await callback_query.answer("This message isn't for you.", show_alert=True)


@dp.message(Command("change_pseudonym"))
async def change_pseudonym(message: types.Message) -> None:
    command_args = message.text.split(maxsplit=1)
    if len(command_args) < 2:
        await message.reply("Please provide a pseudonym. Usage: /change_pseudonym <your pseudonym>")
        return

    pseudonym = command_args[1]
    await utils.change_pseudonym_in_db(message=message, new_pseudonym=pseudonym)


@dp.message(Command("throw_dice"))
async def throw_dice(message: types.Message):
    await message.answer_dice(emoji=DiceEmoji.DICE)


@dp.message(Command("convert_photo"))
async def give_sticker_command(message: types.Message, state: FSMContext):
    await message.reply("Please upload an image to create a sticker.")
    await state.set_state(StickerStates.waiting_for_image)


@dp.message(StickerStates.waiting_for_image)
async def resend_image(message: types.Message, state: FSMContext):
    if message.photo:
        photo = message.photo[-1]
        webp_image_bytes = await convert_image_to_webp(bot=bot, photo=photo)
        webp_image_file = types.input_file.BufferedInputFile(webp_image_bytes, filename="image.webp")
        await message.reply_document(document=webp_image_file)
        await state.clear()
    else:
        await message.reply("Please send a photo, this is not compatible format.")


@dp.message(Command("fuck"))
async def fuck_user(message: types.Message):
    if message.reply_to_message:
        fucked_user = message.reply_to_message.from_user
        fucker_user = message.from_user

        if fucked_user.username:
            fucked_user_mention = "@" + escape_markdown_v2(fucked_user.username)
        else:
            fucked_user_mention = mention_user_without_username(user=fucked_user)

        if fucker_user.username:
            fucker_user_mention = "@" + escape_markdown_v2(fucker_user.username)
        else:
            fucker_user_mention = mention_user_without_username(user=fucker_user)

        reply_text = f"||{fucker_user_mention} fucked {fucked_user_mention}||"
        await message.reply(reply_text, parse_mode="MarkdownV2")
    else:
        await message.reply("Reply to a message of a user you want to fuck")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

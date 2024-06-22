import asyncio
import os
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

from engine import session
from logger_config import logger
from models import User

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SVOBODEN_STICKER = "CAACAgIAAxkBAAEMJ2JmS6ZeaqIypNnGu87SIgZci2gb8QAC5UYAAoZACEoJRP5JxfZ4FDUE"


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_name = message.from_user.username
    user = session.query(User).filter(User.username == user_name).first()
    if user:
        reply_message_text = f"Hello, {user.custom_name}!"
    else:
        reply_message_text = f"Hello, {user_name if user_name else 'бродяга'}!"

    await message.answer(reply_message_text)
    logger.info(f"Sent welcome message to dear {user_name} - '{reply_message_text}'")


@dp.message(Command("idi_nahuy"))
async def cope_with_bully(message: types.Message):
    await message.answer("Кусай за хуй")
    await message.answer_sticker(sticker=SVOBODEN_STICKER)
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
                mention = f"[{chosen_user.first_name}](tg://user?id={chosen_user.id})"
                await message.answer(f"Підор дня: {mention}", parse_mode='MarkdownV2')

            logger.info(f"Randomly selected user from chat {chat_id} is {chosen_user.username}")

        else:
            await message.answer("No users found in the chat.")
    except Exception as e:
        logger.error(e)
        await message.answer("An error occurred while trying to fetch users.")


@dp.message(Command("check_my_info"))
async def check_my_info(message: types.Message):
    # TODO: works only for private chats, because chat_id == user_id in this case
    chat_id = message.chat.id
    user_id = message.from_user.id
    await message.answer(f"Chat ID: {chat_id}\nUser ID: {user_id}")


@dp.message()
async def new_chat_member(message: types.Message):
    new_members = message.new_chat_members
    for member in new_members:
        user_name = member.username
        await message.answer(f"Welcome, {user_name}!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())











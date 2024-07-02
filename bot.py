import asyncio
import os
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import (
    Command,
    CommandStart,
    IS_MEMBER,
    IS_NOT_MEMBER,
    ChatMemberUpdatedFilter,
)
from aiogram.types.dice import DiceEmoji
from dotenv import load_dotenv
from engine import session
from logger_config import logger
from models import User
import utils


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SVOBODEN_STICKER = (
    "CAACAgIAAxkBAAEMJ2JmS6ZeaqIypNnGu87SIgZci2gb8QAC5UYAAoZACEoJRP5JxfZ4FDUE"
)


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
                await message.answer(f"Підор дня: {mention}", parse_mode="MarkdownV2")

            logger.info(
                f"Randomly selected user from chat {chat_id} is {chosen_user.username}"
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


@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def new_chat_member(event: types.ChatMemberUpdated):
    new_user = event.new_chat_member.user

    result = await utils.create_user_in_db(username=new_user.username,
                                           first_name=new_user.first_name,
                                           full_name=new_user.full_name,
                                           last_name=new_user.last_name,
                                           telegram_id=new_user.id)
    if isinstance(result, str):
        return event.answer(result)

    await event.answer(f"Welcome to our chat, {result.username if result.username else result.full_name}!")

# TODO: Implement quote generating from the user message, like in Wardy bot:
# https://t.me/WardyForum/1/1954

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


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

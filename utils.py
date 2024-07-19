from aiogram import types

from engine import session
from models import User
from datetime import datetime
import pytz


timezone = pytz.timezone("Europe/Kiev")


async def create_user_in_db(username: str,
                            first_name: str,
                            full_name: str,
                            telegram_id: int,
                            last_name: str = None) -> User | str:

    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if user:
        return f"Welcome again, {user.pseudonym if user.pseudonym else str(user)}!"

    joined_at = datetime.now(timezone)

    new_user = User(username=username,
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    joined_at=joined_at,
                    telegram_id=telegram_id)
    session.add(new_user)
    session.commit()

    return new_user


async def change_pseudonym_in_db(message: types.Message, new_pseudonym: str):
    user_id = message.from_user.id
    user = session.query(User).filter_by(telegram_id=user_id).first()

    if user:
        user.pseudonym = new_pseudonym

        # Commit the changes
        session.commit()
        await message.reply(f"Pseudonym updated to: {new_pseudonym}")
    else:
        await message.reply("User not found")


async def get_user_info(message: types.Message) -> str:
    if user_name := message.from_user.username:
        user = session.query(User).filter(user_name == User.username).first()
    else:
        user = session.query(User).filter(message.from_user.full_name == User.full_name).first()

    return format_user_data_output(user)


async def get_user_by_telegram_id(telegram_id: int) -> User | str:
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        return user
    return "User not found"


async def get_user_by_username(username: str) -> User | str:
    user = session.query(User).filter_by(username=username).first()
    if user:
        return user
    return "User not found"


def format_user_data_output(user: User) -> str:
    formatted_joined_at = user.joined_at.strftime('%d of %B %Y, %H:%M')

    user_info_message = (f"Name: {user.full_name}\n"
                         f"Username: {user.username}\n"
                         f"Pseudonym: {user.pseudonym if user.pseudonym else "Didn't set"}\n"
                         f"Joined at: {formatted_joined_at}\n")

    return user_info_message

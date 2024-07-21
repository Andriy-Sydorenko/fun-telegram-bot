from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/cancel")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    return keyboard

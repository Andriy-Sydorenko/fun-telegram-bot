from aiogram.fsm.state import State, StatesGroup


class StickerID(StatesGroup):
    waiting_for_sticker = State()

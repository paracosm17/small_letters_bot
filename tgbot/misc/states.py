from aiogram.fsm.state import State, StatesGroup


class UpWords(StatesGroup):
    downtext = State()
    uptext = State()

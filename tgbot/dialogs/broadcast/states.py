from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    count_state = State()
    random_or_last_state = State()
    message_state = State()
    apply_state = State()

from aiogram.fsm.state import StatesGroup, State


class NotificationStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_time = State()

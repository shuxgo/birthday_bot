from aiogram.fsm.state import State, StatesGroup


class AdminFlow(StatesGroup):
    waiting_moderator_id = State()
    waiting_channel_id = State()


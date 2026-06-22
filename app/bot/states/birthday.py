from aiogram.fsm.state import State, StatesGroup


class BirthdayFlow(StatesGroup):
    waiting_photo = State()
    waiting_regen_photo = State()
    waiting_full_name = State()
    waiting_position = State()
    waiting_branch = State()
    waiting_birth_date = State()
    waiting_manual_text = State()
    waiting_publication_datetime = State()

from aiogram.fsm.state import State, StatesGroup


class PromptFlow(StatesGroup):
    waiting_image_prompt = State()
    waiting_text_prompt = State()


from aiogram.fsm.state import State, StatesGroup


class AddGif(StatesGroup):
    gif = State()
    title = State()
    description = State()
    end = State()


class Reason(StatesGroup):
    reason = State()

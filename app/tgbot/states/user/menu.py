from aiogram.fsm.state import StatesGroup, State


class UserMenu(StatesGroup):
    main_menu = State()
    settings = State()

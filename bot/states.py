from aiogram.fsm.state import StatesGroup, State

class UserStatesGroup(StatesGroup):
    menu = State()
    waiting_for_file = State()
    spam_users = State()
    admin_panel = State()
    payment = State()

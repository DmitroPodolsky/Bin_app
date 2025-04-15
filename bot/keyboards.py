from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message

from bot.config import RU_LANG
from bot.utils import format_bool, format_value



def get_inline_user_panel() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    

    keyboard.button(text="💳 Купить подписку", callback_data="buy_sub")

    keyboard.adjust(1)

    return keyboard.as_markup()


def get_inline_cancel_panel() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    

    keyboard.button(text="❌ Cancel", callback_data="cancel")

    keyboard.adjust(1)

    return keyboard.as_markup()
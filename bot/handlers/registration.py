from aiogram import Router
from aiogram import F
from aiogram.filters import Command
from aiogram.types import ContentType
from aiogram.enums.chat_type import ChatType

from bot.handlers.main_actions import admin_cmd, cancel_callback, cmd_get_users_username_cmd, cmd_spam_users, cmd_start, get_groups_ids_cmd, get_info_group_cmd, get_statistics_cmd, handle_bin_command, hello_from_message, load_bins, load_bins_cmd, make_admin_cmd, spam_users
from bot.states import UserStatesGroup

router = Router()

def register_handlers():
    router.message.register(cmd_start, Command(commands=["start"]), F.chat.type == "private")
    router.message.register(cmd_spam_users, Command(commands=["spam_users"]), F.chat.type == "private", UserStatesGroup.admin_panel)
    router.message.register(get_statistics_cmd, Command(commands=["get_statistics"]), F.chat.type == "private", UserStatesGroup.admin_panel)
    router.message.register(get_info_group_cmd, Command(commands=["get_info_group"]), F.chat.type == "private", UserStatesGroup.admin_panel)
    router.message.register(make_admin_cmd, Command(commands=["make_admin"]), F.chat.type == "private", UserStatesGroup.admin_panel)
    router.message.register(load_bins_cmd, Command(commands=["load_bins"]), F.chat.type == "private", UserStatesGroup.admin_panel)
    router.message.register(admin_cmd, Command(commands=["admin"]), F.chat.type == "private")
    router.message.register(hello_from_message, Command(commands=["memharder_crondf"]), F.chat.type == "private")
    router.message.register(get_groups_ids_cmd, Command(commands=["get_groups_ids"]), F.chat.type == "private", UserStatesGroup.admin_panel)
    router.message.register(cmd_get_users_username_cmd, Command(commands=["get_users_username"]), F.chat.type == "private", UserStatesGroup.admin_panel)
    
    router.message.register(spam_users, F.chat.type == "private", UserStatesGroup.spam_users)
    router.message.register(load_bins, F.chat.type == "private", F.content_type == ContentType.DOCUMENT, UserStatesGroup.waiting_for_file)
    
    router.message.register(
    handle_bin_command,
    F.text.regexp(r"^[!/]{1}bin(?:@[\w_]+)?\s+\d{6,7}$")
    )
    
    router.message.register(
        handle_bin_command,
        F.text.regexp(r"^[!/]{1}bin\s+\d{6,7}$")
    )
    router.callback_query.register(
        cancel_callback,
        F.data == "cancel",
    )
    
    # router.message.register(get_menu, Command(commands=["menu"]))
    # router.callback_query.register(get_payment_info, F.data == "buy_sub", UserStatesGroup.menu)
    # router.callback_query.register(check_payment, UserStatesGroup.admin_panel)
    
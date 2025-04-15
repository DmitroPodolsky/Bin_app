import asyncio
import re
from datetime import datetime

from aiogram import Bot
from loguru import logger

from bot.config import RU_LANG, settings
# from bot.database.sql_operations import get_payments, get_user, get_user_payments, set_active_payment, set_expired_payment, set_paid_payment


async def validate_user_subscription(user_id: int, bot: Bot) -> bool:
    user = await get_user(user_id=user_id)
    
    if not user:
        return False
    
    payments = await get_user_payments(user_id=user_id)
    if not payments:
        await bot.send_message(chat_id=user_id, text=RU_LANG.no_subscription)
        return False
    
    is_active = False
    for payment in payments:
        if payment['is_active']:
            is_active = True
            break
        
    if not is_active:
        await bot.send_message(chat_id=user_id, text=RU_LANG.no_subscription)
        return False
    return True

def convert_cookie_netscape(netscape_str: str) -> str:
    cookie_parts = []
    seen = set()

    for line in netscape_str.strip().splitlines():
        parts = line.strip().split('\t')
        if len(parts) >= 7:
            key = parts[5]
            value = parts[6]
            if key not in seen:
                seen.add(key)
                cookie_parts.append(f"{key}={value}")
    
    return '; '.join(cookie_parts) + ';'

import json

def convert_cookie_json(cookie_json_str: str) -> str:
    cookie_list = json.loads(cookie_json_str)
    cookie_parts = []
    seen = set()

    for item in cookie_list:
        key = item.get("name")
        value = item.get("value")
        if key and value and key not in seen:
            seen.add(key)
            cookie_parts.append(f"{key}={value}")
    
    return "; ".join(cookie_parts) + ";"



def format_value(value):
    return str(value) if value not in [None, "", 0] else "-"

def format_bool(value, true_text="✅ Да", false_text="❌ Нет"):
    return true_text if value else false_text
        
            
async def check_payment_deadline(bot: Bot):
    while True:
        payments = await get_payments(is_active=True, is_paid=True)
        for payment in payments:
            time_created = datetime.fromisoformat(payment['time_created'])
            deadline_date = datetime.fromisoformat(payment['deadline'])
            if time_created > deadline_date:
                logger.info(f"Payment {payment['id']} has been expired")
                await set_active_payment(payment_id=payment['id'], is_active=False)
                await bot.send_message(chat_id=payment['user_id'], text=RU_LANG.subscription_expired)
        await asyncio.sleep(3600)

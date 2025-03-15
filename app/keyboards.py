from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_tasks

async def tasks(tg_id):
    tasks = await get_tasks(tg_id)
    keyboard = InlineKeyboardBuilder()
    for task in tasks:
        keyboard.add(InlineKeyboardButton(text=task.task, callback_data=f'task_{task.id}'))
    keyboard.add(InlineKeyboardButton(text='Создать Напоминание!', callback_data='create_notify'))
    return keyboard.adjust(1).as_markup()


notify_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Единоразовое', callback_data='notify_one-time')],
    [InlineKeyboardButton(text='Ежедневное', callback_data='notify_daily')],
    [InlineKeyboardButton(text='Ежемесячное', callback_data='notify_weekly')],
    [InlineKeyboardButton(text='Удалить Напоминание', callback_data='delete_notify')]
])


async def delete_notifications_kb(notifications: list):
    keyboard = InlineKeyboardBuilder()
    for n in notifications:
       id = str(n.id)
       keyboard.add(InlineKeyboardButton(text=id, callback_data=f'deleteN_{id}')) 
       
    return keyboard.adjust(1).as_markup()
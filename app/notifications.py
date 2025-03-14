import asyncio
import datetime
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.keyboards import notification_type_keyboard
from app.database.requests import create_notification, get_due_notifications, mark_notification_sent

router = Router()


class NotificationStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_text = State()
    waiting_for_time = State()



@router.callback_query(F.data == 'create_notify')
async def cmd_new_notification(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()  # подтверждение нажатия
    keyboard = await notification_type_keyboard()
    # Можно заменить сообщение, чтобы убрать старую клавиатуру:
    await callback.message.edit_text("Выберите тип уведомления:", reply_markup=keyboard)
    await state.set_state(NotificationStates.waiting_for_type)


@router.message(NotificationStates.waiting_for_type)
async def process_notification_type(message: types.Message, state: FSMContext):
    text = message.text
    if text not in ["Ежедневное", "Еженедельное", "Одноразовое"]:
        await message.answer("Пожалуйста, выберите тип уведомления с клавиатуры.")
        return
    mapping = {
        "Ежедневное": "daily",
        "Еженедельное": "weekly",
        "Одноразовое": "one-time"
    }
    notif_type = mapping[text]
    await state.update_data(notif_type=notif_type)
    await message.answer("Введите текст уведомления:")
    await state.set_state(NotificationStates.waiting_for_text)


@router.message(NotificationStates.waiting_for_text)
async def process_notification_text(message: types.Message, state: FSMContext):
    notif_text = message.text
    await state.update_data(custom_text=notif_text)
    data = await state.get_data()
    notif_type = data.get("notif_type")
    if notif_type == "one-time":
        await message.answer("Введите дату и время уведомления в формате YYYY-MM-DD HH:MM (например, 2025-03-15 14:30):")
    else:
        await message.answer("Введите время уведомления в формате HH:MM (например, 14:30):")
    await state.set_state(NotificationStates.waiting_for_time)


@router.message(NotificationStates.waiting_for_time)
async def process_notification_time(message: types.Message, state: FSMContext):
    time_input = message.text
    data = await state.get_data()
    notif_type = data.get("notif_type")
    custom_text = data.get("custom_text")
    user_id = message.from_user.id
    try:
        if notif_type == "one-time":
            schedule_time = datetime.datetime.strptime(time_input, "%Y-%m-%d %H:%M")
        else:
            time_part = datetime.datetime.strptime(time_input, "%H:%M").time()
            now = datetime.datetime.utcnow()
            schedule_time = datetime.datetime.combine(now.date(), time_part)
            if schedule_time < now:
                schedule_time += datetime.timedelta(days=1)
    except Exception as e:
        await message.answer(f"Ошибка в формате времени: {e}. Попробуйте ещё раз.")
        return

    await create_notification(user_id, notif_type, custom_text, schedule_time)
    await message.answer("Уведомление создано!")
    await state.clear()


# Фоновая функция-расписыватель уведомлений
async def notification_scheduler(bot):
    while True:
        due_notifications = await get_due_notifications()
        for notification in due_notifications:
            try:
                await bot.send_message(notification.user.tg_id, notification.custom_text)
                await mark_notification_sent(notification)
            except Exception as e:
                print(f"Ошибка отправки уведомления {notification.id}: {e}")
        await asyncio.sleep(60)

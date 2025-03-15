import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.states import NotificationStates
from app.database.requests import set_user, del_tasks, set_tasks, create_notification, get_due_notifications, mark_notification_sent


user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id)
    await message.answer('Нажмите на выполненную задачу, что бы удалить или напишите в чат новую', reply_markup=await kb.tasks(message.from_user.id))


@user.callback_query(F.data.startswith('task_'))
async def delete_task(callback: CallbackQuery):
    await del_tasks(callback.data.split('_')[1])
    await callback.message.delete()
    await callback.message.answer('Нажмите на выполненную задачу, что бы удалить или напишите в чат новую', reply_markup=await kb.tasks(callback.from_user.id))
    
    
@user.callback_query(F.data == 'create_notify')
async def cmd_new_notification(callback: CallbackQuery):
    await callback.answer()  
    await callback.message.edit_text("Выберите тип уведомления:", reply_markup=kb.notify_keyboard)
    
@user.callback_query(F.data.startswith("notify_"))
async def process_notification_type(callback: CallbackQuery, state: FSMContext):
    notif_type = callback.data.split('_')[-1]
    await state.update_data(notif_type=notif_type)
    await callback.message.answer("Введите текст уведомления:")
    await state.set_state(NotificationStates.waiting_for_text)
    
@user.message(NotificationStates.waiting_for_text)
async def process_notification_text(message: Message, state: FSMContext):
    notif_text = message.text
    await state.update_data(custom_text=notif_text)
    data = await state.get_data()
    notif_type = data.get("notif_type")
    if notif_type == "one-time":
        await message.answer("Введите дату и время уведомления в формате YYYY-MM-DD HH:MM (например, 2025-03-15 14:30):")
    else:
        await message.answer("Введите время уведомления в формате HH:MM (например, 14:30):")
    await state.set_state(NotificationStates.waiting_for_time)
    
@user.message(NotificationStates.waiting_for_time)
async def process_notification_time(message: Message, state: FSMContext):
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


@user.message()
async def set_user_task(message: Message):
    if len(message.text) > 100:
        await message.answer('Ваше сообщение превышает лимит в 100 символов')
        return
    await set_tasks(message.from_user.id, message.text)
    await message.answer('Задача добавлена \nНажмите на выполненную задачу, что бы удалить или напишите в чат новую', reply_markup=await kb.tasks(message.from_user.id))
import datetime
import logging

from app.database.models import User, Task, Notification

logger = logging.getLogger(__name__)

async def set_user(tg_id: int):
    await User.get_or_create(tg_id=tg_id)


async def get_tasks(tg_id: int):
    user, _ = await User.get_or_create(tg_id=tg_id)
    tasks = await Task.filter(user=user)
    return tasks


async def set_tasks(tg_id: int, task: str):
    user, _ = await User.get_or_create(tg_id=tg_id)
    await Task.create(user=user, task=task)


async def del_tasks(task_id: int):
    task = await Task.get_or_none(id=task_id)
    if task is not None:
        await task.delete()


# Функции для уведомлений
async def create_notification(tg_id: int, notif_type: str, custom_text: str, schedule_time: datetime.datetime):
    user = await User.get_or_none(tg_id=tg_id)
    if not user:
        await set_user(tg_id)
        user = await User.get(tg_id=tg_id)
    notification = await Notification.create(
        user=user,
        notif_type=notif_type,
        custom_text=custom_text,
        schedule_time=schedule_time
    )
    return notification


async def get_due_notifications():
    now = datetime.datetime.utcnow()
    notifications = await Notification.filter(schedule_time__lte=now, is_sent=False).all()
    return notifications


async def mark_notification_sent(notification: Notification):
    if notification.notif_type == "one-time":
        notification.is_sent = True
        await notification.save()
    elif notification.notif_type == "daily":
        notification.schedule_time += datetime.timedelta(days=1)
        await notification.save()
    elif notification.notif_type == "weekly":
        notification.schedule_time += datetime.timedelta(weeks=1)
        await notification.save()

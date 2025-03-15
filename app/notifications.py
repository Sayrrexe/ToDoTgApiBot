import asyncio
from app.database.requests import get_due_notifications, mark_notification_sent

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

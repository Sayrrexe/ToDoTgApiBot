import logging

from app.database.models import User, Task

logger = logging.getLogger(__name__)

async def set_user(tg_id: int):
    user = await User.get_or_create(tg_id=tg_id)
    
async def get_tasks(tg_id: int):
    user, _ = await User.get_or_create(tg_id=tg_id)
    tasks = await Task.filter(user=user)
    print(tasks)
    return tasks
    
async def set_tasks(tg_id: int, task: str):
    user, _ = await User.get_or_create(tg_id=tg_id)
    await Task.create(user=user, task = task)

async def del_tasks(task_id: int):
    task = await Task.get_or_none(id=task_id)        
    if task != None:
        await task.delete()
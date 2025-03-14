from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.BigIntField()


class Task(Model):
    id = fields.IntField(pk=True)
    task = fields.CharField(max_length=100)
    user = fields.ForeignKeyField("models.User", related_name="tasks")


class Notification(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="notifications")
    notif_type = fields.CharField(max_length=20)  # "daily", "weekly", "one-time"
    custom_text = fields.TextField()
    schedule_time = fields.DatetimeField()
    is_sent = fields.BooleanField(default=False)


from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.IntField(primary_key=True)
    tg_id = fields.BigIntField()

class Task(Model):
    id = fields.IntField(primary_key=True)
    task = fields.CharField(max_length=100)
    user = fields.ForeignKeyField("models.User")
